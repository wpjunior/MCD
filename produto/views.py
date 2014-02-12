# Create your views here.

__all__ = ('ProdutoListView', 'ProdutoAddView',
           'ProdutoUpdateView', 'ProdutoDeleteView')

from MCD.common.decorators import json_response
from responses import HybridListView
from models import Produto

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.views.generic import (
    CreateView, UpdateView, DeleteView,
    TemplateView)

from .forms import *

class ProdutoListView(HybridListView):
    json_object_list_fields = [
        'id', 'desc', 'marca',
        'valor_compra_display',
        'valor_venda_display',
        'qtde']
    
    sort_fields = ['id', 'desc', 'marca', 'valor_compra',
                   'valor_venda', 'qtde']
    filter_fields = ['desc', 'marca']
    paginate_by = 20
    allow_empty = True
    model = Produto

class ProdutoMixInView(object):
    model = Produto
    success_url = '/'
    form_class = ProdutoForm
    
class ProdutoAddView(ProdutoMixInView, CreateView):
    pass

class ProdutoUpdateView(ProdutoMixInView, UpdateView):
    pass
    
class ProdutoDeleteView(DeleteView):
    model = Produto
    success_url = '/'
