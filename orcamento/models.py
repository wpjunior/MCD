# -*- coding: utf-8 -*-
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
from django.db import models
from MCD.produto.models import Produto

class Orcamento(models.Model):
    cliente = models.CharField(
        verbose_name="Cliente",
        max_length=250)

    telefone = models.CharField(
        verbose_name="Telefone",
        max_length=20,
        blank=True, null=True)

    endr = models.CharField(
        verbose_name=u"Endereço",
        max_length=300,
        blank=True, null=True)

    condicao_pagto = models.CharField(
        verbose_name="Condição pagto",
        max_length=1,
        default='v',
        choices=(
            ('v', "à vista"),
            ('p', "a prazo"),
            ('c', "cartão"))
    )

    data = models.DateTimeField(auto_now=True)
    
    def get_absolute_url(self):
        return '/orcamento/%d/' % self.id

    def items(self, *args, **kwargs):
        return Item.objects.filter(
            orcamento=self).order_by('-pk')

    def valor_total(self, *args, **kwargs):
        valor_total = self.items().aggregate(models.Sum(
            'valor_total')).get('valor_total__sum', 0)

        if valor_total:
            if self.condicao_pagto == 'c':
                valor_total = valor_total * 1.04
                
            return locale.format(
                '%0.2f', valor_total, 1)
        
    
class Item(models.Model):
    orcamento = models.ForeignKey(
        Orcamento,
        verbose_name=u"Orçamento")
    
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
