# -*- coding: utf-8 -*-

import itertools
from django.db.models import Q
from django.views.generic.base import TemplateView, View
from joiarara.produto.models import Produto, Categoria
from joiarara.produto.responses import JSONResponse, HybridListView
from models import Consignacao
from output import PDFView

class ConsigView(HybridListView):
    template_name = "consig.html"
    json_object_list_fields = ['id', 'produto.codigo',
                               'produto.desc', 'produto.get_cat_display',
                               'produto.valor_display']
    filter_fields = ['produto__codigo', 'produto__desc']
    model = Consignacao

    def _auto_complete(self):
        term = self.request.GET.get('term')

        data = [p.codigo
                for p in Produto.objects.filter(Q(codigo__startswith=term)|Q(desc__startswith=term))]

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
    def __init__(self, labels, cats, r1=None, r2=None, r3=None):
        self.r1 = r1
        self.r2 = r2
        self.r3 = r3
        self.labels = labels
        
        self.c1, self.c2, self.c3 = cats

        if self.c1:
            self.c1 = Categoria(self.c1)

        if self.c2:
            self.c2 = Categoria(self.c2)

        if self.c3:
            self.c3 = Categoria(self.c3)

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
                
class GenerateConsigView(View):
    pdf_template = "consig/generate.html"
    def get(self, *args, **kwargs):
        v = PDFView(self, self.pdf_template)
        return v.render()

    def row_set1(self):
        count = Consignacao.objects.filter(produto__cat="br").count()

        if (count % 2) == 0:
            s = count / 2
        else:
            s = (count/2)+1

        p1 = (Consignacao.objects.filter(produto__cat="br")[0:s],
              Consignacao.objects.filter(produto__cat="br")[s:count],
              Consignacao.objects.filter(produto__cat="an"))

        return RowSet(("Brincos", "Brincos", u"Anéis"),
                      ('br', None, 'an'), *p1)

    def row_set2(self):
        p2 = (Consignacao.objects.filter(produto__cat="co"),
              Consignacao.objects.filter(produto__cat="pu"),
              Consignacao.objects.filter(produto__cat="pi"))
        
        return RowSet(("Correntes", "Pulseiras", "Pingentes"),
                      ('co', 'pu', 'pi'), *p2)
