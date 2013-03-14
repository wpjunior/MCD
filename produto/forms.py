__all__ = ('ProdutoStockForm',)

from django import forms

from joiarara.pastas.models import Pasta
from .models import ProdutoEstoque

class ProdutoStockForm(forms.Form):
    loja = forms.IntegerField(
        initial=0,
        label = "Estoque em loja")

    

    

    def __init__(self, instance, *args, **kwargs):
        super(ProdutoStockForm, self).__init__(*args, **kwargs)

        try:
            obj = ProdutoEstoque.objects.get(
                produto=instance,
                pasta=None)
        except ProdutoEstoque.DoesNotExist:
            obj = None

        if obj:
            self.initial['loja'] = obj.qtde

        for pasta in Pasta.objects.all():
            self.fields['pasta_%d' % pasta.pk] = forms.IntegerField(
                initial=0,
                label= "Estoque na pasta %d" % pasta.pk)


            try:
                obj = ProdutoEstoque.objects.get(
                    produto=instance,
                    pasta=pasta)
            except ProdutoEstoque.DoesNotExist:
                obj = None
                
            if obj:
                self.initial['pasta_%d' % pasta.pk] = obj.qtde

        self.instance = instance

    def save(self, *args, **kwargs):
        ProdutoEstoque.objects.filter(produto=self.instance).delete()
        
        obj = ProdutoEstoque(
            produto=self.instance,
            qtde=self.cleaned_data['loja'])

        obj.save()

        for pasta in Pasta.objects.all():
            obj = ProdutoEstoque(
                produto=self.instance,
                pasta = pasta,
                qtde=self.cleaned_data['pasta_%d' % pasta.pk])
            obj.save()
            
        return self.instance
