# -*- coding: utf-8 -*-
import locale
from django.db import models

from MCD.produto.models import Produto

class Item(models.Model):
    produto = models.ForeignKey(
        Produto,
        verbose_name="Produto")

    qtde = models.IntegerField(
        verbose_name="Quantidade",
        default=1)
    
    valor_item = models.FloatField(
        verbose_name="Valor do item",
        null=True)

    valor_total = models.FloatField(
        verbose_name="Valor do item",
        null=True)
    
    def valor_item_display(self):
        if self.valor_item:
            return locale.format('%0.2f', self.valor_item, 1)

    def valor_item_cartao_display(self):
        if self.valor_item:
            return locale.format('%0.2f', self.valor_item * 1.04, 1)


    def valor_total_display(self):
        if self.valor_total:
            return locale.format('%0.2f', self.valor_total, 1)

    def valor_total_cartao_display(self):
        if self.valor_total:
            return locale.format('%0.2f', self.valor_total * 1.04, 1)
