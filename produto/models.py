# -*- coding: utf-8 -*-

from django.db import models
from django.core.validators import RegexValidator

codigo_validator = RegexValidator('\w+$',
                                  "Código não pode conter espaços nem simbolos especiais")
class Categoria(models.Model):
    nome = models.CharField(max_length=50)

    @property
    def consigs(self):
        from joiarara.consignacao.models import Consignacao
        return Consignacao.objects.filter(produto__cat=self)

    @property
    def total(self):
        return self.consigs.count()

    @property
    def valor_total(self):
        from joiarara.consignacao.models import Consignacao
        from django.db.models import Sum
        data = Consignacao.objects.filter(produto__cat=self).aggregate(Sum('produto__valor'))
        return data['produto__valor__sum']

    def __unicode__(self):
        return self.nome

class Produto(models.Model):
    codigo = models.CharField(max_length=50,
                              unique=True,
                              validators=[codigo_validator],
                              verbose_name=u"Código")
    desc = models.CharField(max_length=100,
                            verbose_name="Descrição")
    valor = models.FloatField()
    cat =  models.ForeignKey(Categoria, null=True,
                             verbose_name="Categoria")

    def valor_display(self):
        return "%0.2f" % self.valor
