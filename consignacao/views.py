# Create your views here.
import itertools
from django.views.generic.base import TemplateView, View
from joiarara.produto.models import Produto, Categoria
from joiarara.produto.responses import JSONResponse, HybridListView
from models import Consignacao
from output import PDFView

class ConsigView(HybridListView):
    template_name = "consig.html"
    json_object_list_fields = ['id', 'produto.codigo',
                               'produto.desc', 'produto.cat.nome',
                               'produto.valor_display']
    model = Consignacao

    def _auto_complete(self):
        term = self.request.GET.get('term')

        data = [p.codigo
                for p in Produto.objects.filter(codigo__startswith=term)]

        return JSONResponse(data)

    def get(self, *args, **kwargs):
        cmd = self.request.GET.get('cmd')

        if cmd == 'auto_complete':
            return self._auto_complete()

        return super(ConsigView, self).get(*args, **kwargs)

    def _add_produto(self, p):
        try:
            prod = Produto.objects.get(codigo=p)
            con = Consignacao(produto=prod)
            con.save()
            return JSONResponse({'added': True})
        except Produto.DoesNotExist, e:
            return JSONResponse({'added': False})

    def _remove_produto(self, id):
        try:
            con = Consignacao.objects.get(id=id)
            con.delete()
            return JSONResponse({'removed': True})
        except Consignacao.DoesNotExist, e:
            return JSONResponse({'removed': False})

    def _clear_produtos(self):
        Consignacao.objects.filter().delete()
        return JSONResponse({'cleanned': True})

    def post(self, *args, **kwargs):
        p = self.request.POST.get('add_produto')
        
        if p:
            return self._add_produto(p)

        p =self.request.POST.get('remove_produto')
        if p:
            return self._remove_produto(p)

        if self.request.POST.get('clear_produtos'):
            return self._clear_produtos();
        
        return JSONResponse({'error': "Request invalid"})

class Row(object):
    def __init__(self, p1=None, p2=None, p3=None):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

class RowSet(object):
    def __init__(self, r1=None, r2=None, r3=None):
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3

    def get_rows(self):
        if self.r1:
            r1 = self.r1.consigs
        else:
            r1 = itertools.cycle([None])

        if self.r2:
            r2 = self.r2.consigs
        else:
            r2 = itertools.cycle([None])

        if self.r3:
            r3 = self.r3.consigs
        else:
            r3 = itertools.cycle([None])

        for r in itertools.izip_longest(r1, r2, r3, fillvalue=None):
            yield Row(*r)
                
class GenerateConsigView(View):
    pdf_template = "consig/generate.html"
    def get(self, *args, **kwargs):
        v = PDFView(self, self.pdf_template)
        return v.render()

    def get_row_set(self):
        for i in xrange(1, Categoria.objects.count(), 3):
            rows = list(Categoria.objects.all()[i-1:i+2])
            yield RowSet(*rows)

    def get_categorias(self):
        return Categoria.objects.all()
