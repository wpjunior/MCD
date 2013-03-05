# Create your views here.

__all__ = ("ListPastaView", 'AddPastaView')

from django.views.generic.edit import CreateView
from joiarara.produto.responses import HybridListView

from .models import Pasta
from .forms import PastaForm

class ListPastaView(HybridListView):
    json_object_list_fields = [
        'id', 'nome', 'get_status_display']
    sort_fields = ['id', 'id', 'status']
    filter_fields = []

    paginate_by = 20
    allow_empty = True
    model = Pasta

class AddPastaView(CreateView):
    model = Pasta
    success_url = '/pastas/'
    form_class = PastaForm
