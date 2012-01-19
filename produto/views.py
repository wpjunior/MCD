# Create your views here.
from responses import HybridListView
from models import Produto

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView


class ProdutoListView(HybridListView):
    json_object_list_fields = ['id', 'codigo', 'desc', 'get_cat_display', 'valor_display']
    sort_fields = ['id', 'codigo', 'desc', 'valor', 'cat']
    filter_fields = []
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

