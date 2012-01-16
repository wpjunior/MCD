#!/usr/bin/env python
# -*- coding: utf-8 -*-


import datetime
from django.template import RequestContext
from django.contrib import messages
from django.utils import simplejson as json
from django import http
from django.core.paginator import InvalidPage
from django.utils.dateformat import format
from django.views.generic import ListView
from django.http import HttpResponse

class JSONResponse(HttpResponse):
    """ JSON response class """
    def __init__(self,content='',json_opts={},mimetype="application/json",*args,**kwargs):
        
        if content:
            content = json.dumps(content,**json_opts)
        else:
            content = json.dumps([],**json_opts)

        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)

class DataTableResponseMixin(object):
    """
    Classe que mescla saida de uma view em modo json, compreendido pelo datatable
    ela trata o contexto que seria enviado ao render_template
    """

    json_object_list_fields = []
    datatime_format = "%x"
    all_objects = None

    def _find_attr(self, obj, field):
        """
        Função recursiva especial para a procura de atributos de atributos
        exemplo de uso
        self._find_attr(obj, "action.module.id")
        """
        if hasattr(obj, field):
            attr = getattr(obj, field)
            return (attr, True)

        else:
            if '.' in field:
                at, pt = field.split('.', 1)

                if hasattr(obj, at):
                    return self._find_attr(getattr(obj, at), pt)
                else:
                    return (None, False)
            else:
                return (None, False)

    def _render_obj_list(self, obj, fields):
        """
        methodo usado para rendererizar um objeto nao suportado pelo simplejson
        parametros
        obj: é o objeto em si
        list_fields: os atributos desse objeto que serão renderizados
        a diferença do anterior que tudo vai ser realizado em forma de lista
        """

        list_obj = []

        for field in fields:
            attr, attrfound = self._find_attr(obj, field)

            if not attrfound:
                list_obj.append(None)
                continue

            if callable(attr):
                attr = attr()

            if isinstance(attr, datetime.datetime):
                attr = format(attr, DATETIME_FORMAT)

            if isinstance(attr, datetime.date):
                attr = format(attr, DATE_FORMAT)
                
            if hasattr(attr, "__unicode__"):
                attr = unicode(attr)

            list_obj.append(attr)

        return list_obj

    def get_paginate_by(self, queryset):
        """
        busca pelo tamanho predefido de uma pagina
        """
        if self.request.GET.has_key('iDisplayLength'):
            return min(int(self.request.GET.get('iDisplayLength', 20)), 100)
        
        return self.paginate_by

    def paginate_queryset(self, queryset, page_size):
        """
        Mudado para atender sorting, e filtering
        """
        self.all_objects = queryset._clone() #backup dos objetos

        queryset = self.filter_queryset(queryset) #filtra os dados
        queryset = self.sort_queryset(queryset) #ordena os dados
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        page = self.kwargs.get('page') or self.request.GET.get('page') or 1

        # Hacking o datatable trabalha com inicio e nao com pagina :-(
        if self.request.GET.has_key('iDisplayStart'):
            try:
                start = int(self.request.GET.get('iDisplayStart', 0))
            except ValueError:
                start = 1

            page = (start // page_size) + 1

        try:
            page_number = int(page)
        except ValueError:
            if page == 'last':
                page_number = paginator.num_pages
            else:
                raise Http404
        try:
            page = paginator.page(page_number)
            return (paginator, page, page.object_list, page.has_other_pages())
        except InvalidPage:
            raise Http404('Invalid page (%(page_number)s)' % {
                                'page_number': page_number
            })
    
    def get_object_list_fields(self):
        return self.json_object_list_fields

    def render_to_response(self, context):
        """
        renderiza os dados da resposta em formato
        que pode ser compreendido pela datable
        """

        data = {}
        object_list = []
        objs = context['object_list'] #objetos filtrados

        list_fields = self.get_object_list_fields()
        for obj in objs :
            object_list.append(self._render_obj_list(obj,
                                                     list_fields))

        data['aaData'] = object_list

        data['iTotalRecords'] = len(object_list) #objs.count()
        data['iTotalDisplayRecords'] =  self.all_objects.count()

        # para que as messagens do sistema sejam recebidas pelo listbuilder
        dump_msgs = []

        storage = messages.get_messages(self.request)
        for message in storage:
            dump_msgs.append(self._render_message(message))

        data['messages'] = dump_msgs
        data['sEcho'] = int(self.request.GET.get('sEcho', 0))

        return self.get_json_response(json.dumps(data))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def _render_message(self, message):
        """
        renderiza uma message do django em modo que possa ser transformada em json
        """
        return {'message': message.message,
                'tags': message.tags,
                'extra_tags': message.extra_tags,
                'level': message.level }

    def filter_queryset(self, queryset):
        """
        filtra a queryset pela string recebida do cliente
        """
        customSearch = self.request.GET.get('sSearch', '').encode('utf-8');

        if hasattr(self, 'get_filter_fields'):
            filter_fields = self.get_filter_fields()

        elif hasattr(self, 'filter_fields'):
            filter_fields = self.filter_fields

        else:
            filter_fields = None

        if customSearch != '' and filter_fields:
            outputQ = None
            first = True

            for searchableColumn in filter_fields:
                kwargz = {searchableColumn+"__icontains" : customSearch}
                outputQ = outputQ | Q(**kwargz) if outputQ else Q(**kwargz)
     
            queryset = queryset.filter(outputQ)
                
        return queryset
    
    def sort_queryset(self, queryset):
        """
        usado para ordenar a queryset
        """
        # Ordering data
        iSortingCols =  int(self.request.GET.get('iSortingCols',0))
        asortingCols = []

        # se nao possui restricao ordena pelos campos normais
        if hasattr(self, 'get_sort_fields'):
            sf = self.get_sort_fields()

        elif hasattr(self, 'sort_fields'):
            sf = self.sort_fields

        else:
            sf = self.get_object_list_fields()
        
        if iSortingCols:
            for i in range(0, iSortingCols):
                sortedColID = int(self.request.GET.get('iSortCol_' + str(i), 0))

                if self.request.GET.get('bSortable_{0}'.format(i), 'false')  == 'true':  # make sure the column is sortable first
                    sortedColName = sf[sortedColID]
                    sortingDirection = self.request.GET.get('sSortDir_' + str(i), 'asc')

                    if not sortedColName:
                        continue

                    # se for uma coluna derivada
                    if isinstance(sortedColName, tuple):
                        if sortingDirection == 'desc':
                            asortingCols.extend(['-'+a for a in sortedColName])

                        asortingCols.extend(sortedColName)

                    else:
                        if sortingDirection == 'desc':
                            sortedColName = '-'+sortedColName

                        asortingCols.append(sortedColName) 

            if asortingCols:
                queryset = queryset.order_by(*asortingCols)

        return queryset


class HybridListView(DataTableResponseMixin, ListView):
    """
    Classe Hibrida
    que suporta paginas atraves da herança do MultipleObjectMixin
    que suporta saida em json tratada para o datatable
    atraves da herança do DataTableResponseMixin

    CVS: suporta a saida em cvs atraves do attributos:
    * csv_template_name -> template que sera usado para exportar
    * csv_template_filename -> arquivo de saida para csv

    que tambem é uma classe de vizualização do ListView
    """

    def post(self, request, *args, **kwargs):
        """
        ao invez de usarmos uma url para o action
        podemos reaproveitar o post do listview
        que esta livre
        """
        if not hasattr(self, 'action'):
            raise Http404

        act = self.action()
        return act.dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        # Look for a 'format=json' GET argument
        format = self.request.GET.get('format','html')

        if hasattr(self, "get_extra_context"):
            context.update(self.get_extra_context())

        if format == 'data':
            return DataTableResponseMixin.render_to_response(self, context)

        # Exportar para csv
        elif format == 'csv' and hasattr(self, "csv_template_name"):
            return render_to_csv(output = self.csv_filename,
                                 template = self.csv_template_name,
                                 context = context)

        # Exportar para pdf
        elif format == 'pdf' and hasattr(self, "pdf_template_name"):
            return render_to_pdf(output = self.pdf_filename,
                                 template = self.pdf_template_name,
                                 context = context)

        else:
            context['request'] = self.request

            return ListView.render_to_response(self,
                                               RequestContext(self.request, context))
