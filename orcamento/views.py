# -*- coding: utf-8 -*-

import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

from django.views.generic import TemplateView
from django.shortcuts import render
from django.db.models import Q, Sum

from MCD.produto.models import Produto
from MCD.common.decorators import json_response
from MCD.common.fields import MoneyInput
from output import PDFView
from .models import Item

class OrcamentoView(TemplateView):
    template_name = "orcamento/main.html"
    get_services = ('auto_complete_produto', 'get_valores',
                    'preview_orcamento', 'print_orcamento')
    post_services = ('add_produto', 'remove_item', 'clear_items')

    def get(self, *args, **kwargs):
        cmd = self.request.GET.get('cmd')

        if cmd and cmd in self.get_services:
            return getattr(self, "_%s" % cmd)()

        return super(OrcamentoView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        cmd = self.request.POST.get('cmd')

        if cmd and cmd in self.post_services:
            return getattr(self, "_%s" % cmd)()

        return super(OrcamentoView, self).post(*args, **kwargs)

    @json_response
    def _auto_complete_produto(self):
        term = self.request.GET.get('term')

        return [(p.pk, p.get_autocomplete_display())
                for p in Produto.objects.filter(
                Q(marca__icontains=term)|Q(desc__icontains=term))]

    @json_response
    def _get_valores(self):
        produto_id = self.request.GET.get('produto_id')
        produto = Produto.objects.get(pk=produto_id)

        return {
            'valor_venda': produto.valor_venda_display(),
            'valor_compra': produto.valor_compra_display()
            }

    def _preview_orcamento(self):
        items = Item.objects.all().order_by('-pk')

        
        valor_total = items.aggregate(Sum(
            'valor_total')).get('valor_total__sum', 0)
        if valor_total:
            valor_total = locale.format(
                '%0.2f', valor_total, 1)
        
        return render(
            self.request, "orcamento/preview.html", locals())

    @json_response
    def _add_produto(self):
        produto_id = self.request.POST.get('produto')
        produto = Produto.objects.get(pk=produto_id)

        qtde = int(self.request.POST.get('qtde', '1'))

        custom_valor_venda = self.request.POST.get('preco_venda')

        
        item = Item()
        item.produto = produto
        item.qtde = qtde or 1

        if custom_valor_venda:
            item.valor_item = MoneyInput().clean(custom_valor_venda)
        else:
            item.valor_item = item.produto.valor_venda
            
        item.valor_total = item.qtde * item.valor_item
        item.save()

        return {'ok': True}

    @json_response
    def _remove_item(self):
        _id = self.request.POST.get('id')
        
        item = Item.objects.get(pk=_id)
        item.delete()
        return {'ok': True}
        

    @json_response
    def _clear_items(self):
        Item.objects.all().delete()

        return {'ok': True}

    def _print_orcamento(self):
        items = Item.objects.all().order_by('-pk')

        
        valor_total = items.aggregate(Sum(
            'valor_total')).get('valor_total__sum', 0)
        if valor_total:
            valor_total = locale.format(
                '%0.2f', valor_total, 1)
            
        v = PDFView(locals(), "orcamento/pdf.html")

        return v.render()
