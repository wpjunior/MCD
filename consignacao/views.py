# -*- coding: utf-8 -*-

__all__ = ('ConsignacaoListView', 'ConsignacaoAddView',
           'ConsignacaoProdutosView', 'ConsignacaoPrintView',
           'ConsignacaoFinishView', 'ConsignacaoDetailView')

import itertools

from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.views.generic import (
    TemplateView, View, CreateView, UpdateView,
    DetailView)

from joiarara.common.decorators import json_response
from joiarara.produto.models import (
    Produto, ProdutoEstoque, Categoria)
from joiarara.produto.responses import JSONResponse, HybridListView
from models import Consignacao, ConsignacaoItem
from .forms import *
from output import PDFView

class ConsignacaoListView(HybridListView):
    model = Consignacao
    json_object_list_fields = ['id', 'nome',
                               'pasta.nome', 'get_status_display']

class ConsignacaoAddView(CreateView):
    model = Consignacao
    form_class = ConsignacaoForm

    def get_success_url(self):
        return self.object.get_produtos_url()

class ConsignacaoDetailView(DetailView):
    model = Consignacao

    def get(self, *args, **kwargs):
        object = self.get_object()
        
        if object.status != 'f':
            return render(self.request,
                          "consignacao/not_finish.html", locals())

        return super(ConsignacaoDetailView, self).get(*args, **kwargs)

class ConsignacaoFinishView(UpdateView):
    model = Consignacao
    form_class = ConsignacaoFinishForm
    success_url = '/consignacoes/'
    template_name = "consignacao/finish.html"

    def get(self, *args, **kwargs):
        object = self.get_object()
        
        if object.status == 'f':
            return render(self.request,
                          "consignacao/already_finish.html", locals())

        return super(ConsignacaoFinishView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        object = self.get_object()
        
        if object.status == 'f':
            return render(self.request,
                          "consignacao/already_finish.html", locals())

        return super(ConsignacaoFinishView, self).post(*args, **kwargs)

class ConsignacaoProdutosView(HybridListView):
    json_object_list_fields = [
        'id', 'produto.codigo',
        'produto.desc', 'produto.get_cat_display',
        'produto.valor_display']
    consignacao = None
    get_services = ('auto_complete_produto', 'get_estoque')
    post_services = ('add_produto', 'remove_item', 'clear_items')

    def get(self, *args, **kwargs):
        object = self.get_consignacao()
        
        if object.status == 'f':
            return render(self.request,
                          "consignacao/already_finish.html", locals())

        cmd = self.request.GET.get('cmd')

        if cmd and cmd in self.get_services:
            return getattr(self, "_%s" % cmd)()

        return super(ConsignacaoProdutosView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        object = self.get_consignacao()
        
        if object.status == 'f':
            return render(self.request,
                          "consignacao/already_finish.html", locals())

        cmd = self.request.POST.get('cmd')

        if cmd and cmd in self.post_services:
            return getattr(self, "_%s" % cmd)()

        return super(ConsignacaoProdutosView, self).post(*args, **kwargs)

    def get_consignacao(self):
        if not self.consignacao:
            self.consignacao = get_object_or_404(
                Consignacao, pk=self.kwargs['pk'])

        return self.consignacao

    def get_queryset(self):
        return ConsignacaoItem.objects.filter(
            consignacao=self.get_consignacao())

    def get_context_data(self, *args, **kwargs):
        ctx = super(ConsignacaoProdutosView, self).get_context_data(
            *args, **kwargs)

        ctx['object'] = self.get_consignacao()
        return ctx


    @json_response
    def _auto_complete_produto(self):
        term = self.request.GET.get('term')
        if not term:
            return []

        return [(p.codigo, "%s - %s" % (p.codigo, p.desc))
                for p in Produto.objects.filter(
                Q(codigo__startswith=term)|Q(desc__startswith=term))]

    @json_response
    def _get_estoque(self):
        produto = get_object_or_404(
            Produto, codigo=self.request.GET['produto_id'])

        try:
            estoque = ProdutoEstoque.objects.get(
                produto=produto,
                pasta=None)
            return {'qtde': estoque.qtde}
        except ProdutoEstoque.DoesNotExist:
            return {'qtde': 0}

    @json_response
    def _add_produto(self):
        produto = get_object_or_404(
            Produto, codigo=self.request.POST['produto_id'])
        consignacao = self.get_consignacao()

        obj = ConsignacaoItem()
        obj.produto = produto
        obj.consignacao = consignacao
        obj.save()

        try:
            estoque = ProdutoEstoque.objects.get(
                produto=produto,
                pasta=None)
            estoque.qtde -= 1
            estoque.save()
        except ProdutoEstoque.DoesNotExist:
            estoque = ProdutoEstoque(
                produto=produto,
                pasta=None,
                qtde=-1)
            estoque.save()

        try:
            estoque = ProdutoEstoque.objects.get(
                produto=produto,
                pasta=consignacao.pasta)
            estoque.qtde += 1
            estoque.save()
        except ProdutoEstoque.DoesNotExist:
            estoque = ProdutoEstoque(
                produto=produto,
                pasta=consignacao.pasta,
                qtde=1)
            estoque.save()
        
        return {'added': True}
    
    def process_remove_item(self, con):
        """
        Remove um item em si
        con: ConsignacaoItem object
        """
        try:
            estoque = ProdutoEstoque.objects.get(
                produto=con.produto,
                pasta=None)
            estoque.qtde += 1
            estoque.save()
        except ProdutoEstoque.DoesNotExist:
            estoque = ProdutoEstoque(
                produto=con.produto,
                pasta=None,
                qtde=1)
            estoque.save()

        try:
            estoque = ProdutoEstoque.objects.get(
                produto=con.produto,
                pasta=con.consignacao.pasta)
            estoque.qtde -= 1
            estoque.save()
        except ProdutoEstoque.DoesNotExist:
            pass

        con.delete()

    @json_response
    def _remove_item(self):
        id = int(self.request.POST['id'])

        try:
            con = ConsignacaoItem.objects.get(id=id)
        except Consignacao.DoesNotExist:
            con = None

        if not con:
            return {'removed': False}

        self.process_remove_item(con)
        return {'removed': True}

    @json_response
    def _clear_items(self):
        queryset = ConsignacaoItem.objects.filter(
            consignacao=self.get_consignacao())

        for con in queryset:
            self.process_remove_item(con)

        return {'cleaned': True}

class Row(object):
    def __init__(self, p1=None, p2=None, p3=None):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

class RowSet(object):
    def __init__(self, consignacao, labels, cats, r1=None, r2=None, r3=None):
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.labels = labels
        self.consignacao = consignacao
        
        self.c1, self.c2, self.c3 = cats

        if self.c1:
            self.c1 = Categoria(consignacao, self.c1)

        if self.c2:
            self.c2 = Categoria(consignacao, self.c2)

        if self.c3:
            self.c3 = Categoria(consignacao, self.c3)

    def get_rows(self):
        if self.r1:
            i1 = iter(self.r1)
        else:
            i1 = itertools.cycle([None])
        
        if self.r2:
            i2 = iter(self.r2)
        else:
            i2 = itertools.cycle([None])
        
        if self.r3:
            i3 = iter(self.r3)
        else:
            i3 = itertools.cycle([None])

        while True:
            try:
                v1 = i1.next()
            except StopIteration:
                v1 = None

            try:
                v2 = i2.next()
            except StopIteration:
                v2 = None

            try:
                v3 = i3.next()
            except StopIteration:
                v3 = None

            if not any((v1, v2, v3)):
                break

            yield Row(v1, v2, v3)

class ConsignacaoPrintView(View):
    pdf_template = "consignacao/pdf.html"
    consignacao = None

    def get(self, *args, **kwargs):
        self.get_consignacao() #Pre carrega a consignaçao
        v = PDFView(self, self.pdf_template)

        return v.render()

    def get_consignacao(self):
        if not self.consignacao:
            self.consignacao = get_object_or_404(
                Consignacao, pk=self.kwargs['pk'])

        return self.consignacao

    def row_set1(self):
        consignacao = self.get_consignacao()

        count = ConsignacaoItem.objects.filter(
            produto__cat="br",
            consignacao=consignacao).count()

        if (count % 2) == 0:
            s = count / 2
        else:
            s = (count/2)+1

        p1 = (ConsignacaoItem.objects.filter(consignacao=consignacao,
                                         produto__cat="br")[0:s],

              ConsignacaoItem.objects.filter(consignacao=consignacao,
                                         produto__cat="br")[s:count],

              ConsignacaoItem.objects.filter(consignacao=consignacao,
                                         produto__cat="an"))

        return RowSet(consignacao,
                      ("Brincos", "Brincos", u"Anéis"),
                      ('br', None, 'an'), *p1)

    def row_set2(self):
        consignacao = self.get_consignacao()

        p2 = (
            ConsignacaoItem.objects.filter(consignacao=consignacao,
                                           produto__cat="co"),
            
            ConsignacaoItem.objects.filter(consignacao=consignacao,
                                           produto__cat="pu"),

            ConsignacaoItem.objects.filter(consignacao=consignacao,
                                           produto__cat="pi"))
        
        return RowSet(consignacao,
                      ("Correntes", "Pulseiras", "Pingentes"),
                      ('co', 'pu', 'pi'), *p2)
