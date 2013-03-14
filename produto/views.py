# Create your views here.

__all__ = ('ProdutoListView', 'ProdutoAddView',
           'ProdutoUpdateView', 'ProdutoDeleteView',
           'ProdutoStockView', 'EntradaProdutoView')

from joiarara.common.decorators import json_response
from responses import HybridListView
from models import Produto, ProdutoEstoque

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.generic import (
    CreateView, UpdateView, DeleteView,
    TemplateView)

from .forms import *

class ProdutoListView(HybridListView):
    json_object_list_fields = [
        'id', 'codigo', 'desc', 'get_cat_display',
        'valor_compra_display',
        'valor_display']
    sort_fields = ['id', 'codigo', 'desc', 'valor_compra',
                   'valor', 'cat']
    filter_fields = ['codigo', 'desc']
    paginate_by = 20
    allow_empty = True
    model = Produto

class ProdutoAddView(CreateView):
    model = Produto
    success_url = '/'

class ProdutoUpdateView(UpdateView):
    model = Produto
    success_url = '/'
    
class ProdutoDeleteView(DeleteView):
    model = Produto
    success_url = '/'

class ProdutoStockView(UpdateView):
    template_name = 'produto/stock.html'
    form_class = ProdutoStockForm
    model = Produto
    success_url = '/'

class EntradaProdutoView(TemplateView):
    template_name = 'produto/entrada.html'
    get_services = ('auto_complete_produto', 'get_estoque')
    post_services = ('add_produto',)

    def get(self, *args, **kwargs):
        cmd = self.request.GET.get('cmd')

        if cmd and cmd in self.get_services:
            return getattr(self, "_%s" % cmd)()

        return super(EntradaProdutoView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        cmd = self.request.POST.get('cmd')

        if cmd and cmd in self.post_services:
            return getattr(self, "_%s" % cmd)()

        return super(EntradaProdutoView, self).post(*args, **kwargs)

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
        qtde = int(self.request.POST.get('produto_qtde', '0'))

        try:
            estoque = ProdutoEstoque.objects.get(
                produto=produto,
                pasta=None)
            estoque.qtde += qtde
            estoque.save()
        except ProdutoEstoque.DoesNotExist:
            estoque = ProdutoEstoque(
                produto=produto,
                pasta=None,
                qtde=qtde)
            estoque.save()

        return {'added': True, 'total': estoque.qtde,
                'nome': produto.desc}
