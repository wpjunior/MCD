# -*- coding: utf-8 -*-

__all__ = ('ConsignacaoForm', 'ConsignacaoFinishForm')

from django import forms

from .models import Consignacao
from joiarara.pastas.models import Pasta
from joiarara.produto.models import ProdutoEstoque

class ConsignacaoForm(forms.ModelForm):
    pasta = forms.ModelChoiceField(
        queryset=Pasta.objects.filter(status='d'))

    def save(self, *args, **kwargs):
        obj = super(ConsignacaoForm, self).save(*args, **kwargs)

        # Coloca a pasta em uso
        obj.pasta.status = 'u'
        obj.pasta.save()

        return obj

    class Meta:
        model = Consignacao
        exclude = ('status',)

class ConsignacaoFinishForm(forms.Form):
    def __init__(self, instance, *args, **kwargs):
        super(ConsignacaoFinishForm, self).__init__(*args, **kwargs)

        self.instance = instance

        for item in instance.items:
            self.fields['item_%d' % item.id] = forms.BooleanField(
                label=item.produto.desc,
                required=False)

    def iter_produto_items(self):
        for item in self.instance.items:
            yield item, self['item_%d' % item.id]

    def save(self, *args, **kwargs):
        for item in self.instance.items:
            item.vendido = self.cleaned_data['item_%d' % item.id]
            item.save()

            if not item.vendido:
                try:
                    estoque = ProdutoEstoque.objects.get(
                        produto=item.produto,
                        pasta=None)
                    estoque.qtde += 1
                    estoque.save()
                except ProdutoEstoque.DoesNotExist:
                    estoque = ProdutoEstoque(
                        produto=item.produto,
                        pasta=None,
                        qtde=1)
                    estoque.save()

            try:
                estoque = ProdutoEstoque.objects.get(
                    produto=item.produto,
                    pasta=self.instance.pasta)
                estoque.qtde -= 1
                estoque.save()
            except ProdutoEstoque.DoesNotExist:
                estoque = ProdutoEstoque(
                    produto=produto,
                    pasta=consignacao.pasta,
                    qtde=0)
                estoque.save()

        self.instance.status = 'f'

        self.instance.pasta.status = 'd'
        self.instance.pasta.save()

        self.instance.save()

        return self.instance
