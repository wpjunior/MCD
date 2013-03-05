#! /usr/bin/python
# -*- encoding: utf-8 -*-

import os
import re
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
import ho.pisa as pisa
from django.core.files.temp import NamedTemporaryFile

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = ('PDFView',)

ImageRegex = re.compile(r'/images/(?P<pk>\w{24})/')

class PDFView(object):
    def __init__(self, object, template):
        self.object = object
        self.template = template
        self.open_images = []

    def fetch_resources(self, uri, rel):
        return

    def render(self):
        temp = get_template(self.template)
        html  = temp.render(
            Context({'object': self.object,
                     'exclude_links': True}))

        result = StringIO()
        pdf = pisa.pisaDocument(
            StringIO(html.encode("UTF-8")),
            result,
            link_callback=self.fetch_resources,
            encoding="utf-8")
        
        for image in self.open_images:
            os.unlink(image.name)
        
        if pdf.err:
            return HttpResponse('Erro ao gerar pdf')

        return HttpResponse(result.getvalue(), mimetype='application/pdf')
