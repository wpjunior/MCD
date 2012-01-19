# -*- coding: utf-8 -*-

from django.db import models
from django.core.validators import RegexValidator

codigo_validator = RegexValidator('\w+$',
                                  "Código não pode conter espaços nem simbolos especiais")
class Categoria(object):
    def __init__(self, name):
        self.name = name

    @property
    def consigs(self):
        from joiarara.consignacao.models import Consignacao
        return Consignacao.objects.filter(produto__cat=self.name)

    @property
    def total(self):
        return self.consigs.count()

    @property
    def valor_total(self):
        from joiarara.consignacao.models import Consignacao
        from django.db.models import Sum
        data = Consignacao.objects.filter(produto__cat=self.name).aggregate(Sum('produto__valor'))
        return data['produto__valor__sum']

class Produto(models.Model):
    codigo = models.CharField(max_length=50,
                              unique=True,
                              validators=[codigo_validator],
                              verbose_name=u"Código")
    desc = models.CharField(max_length=100,
                            verbose_name="Descrição")
    valor = models.FloatField()
    cat = models.CharField(max_length=2,
                           choices=(("br", "Brincos"),
                                    ("an", u"Anéis"),
                                    ("co", "Correntes"),
                                    ("pu", "Pulseiras"),
                                    ("pi", "Pingentes")),
                           verbose_name="Categoria")

    def valor_display(self):
        return "%0.2f" % self.valor
