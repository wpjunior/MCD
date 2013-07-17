# -*- coding: utf-8 -*-
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
from django.db import models

class Produto(models.Model):
    desc = models.CharField(
        max_length=150,
        verbose_name="Descrição")

    marca = models.CharField(
        max_length=150,
        null=True, blank=True,
        verbose_name="Marca")

    valor_compra = models.FloatField(
        verbose_name="Valor de compra",
        null=True)

    valor_venda = models.FloatField(
        verbose_name="Valor de venda")

    def valor_venda_display(self):
        if self.valor_venda:
            return locale.format('%0.2f', self.valor_venda, 1)


    def valor_compra_display(self):
        if self.valor_compra:
            return locale.format('%0.2f', self.valor_compra, 1)

    def get_autocomplete_display(self):
        if self.desc and self.marca:
            return u"%s - %s" % (self.desc, self.marca)

        return self.desc
        
