# -*- coding: utf-8 -*-

from django.db import models
from joiarara.produto.models import Produto
from joiarara.pastas.models import Pasta

from .constants import *

class Consignacao(models.Model):
    pasta = models.ForeignKey(
        Pasta,
        verbose_name="Pasta")

    status = models.CharField(
        max_length=2,
        choices=CONSIGNACAO_STATUS_CHOICES,
        default='a')

    def nome(self):
        return "Consignação %d" % self.pk

    def __unicode__(self):
        return self.nome

    def get_produtos_url(self):
        return '/consignacoes/produtos/%d/' % self.pk

    def get_print_url(self):
        return '/consignacoes/print/%d/' % self.pk

    def get_detail_url(self):
        return '/consignacoes/detail/%d/' % self.pk

    @property
    def items(self):
        return ConsignacaoItem.objects.filter(
            consignacao=self)

    @property
    def total_vendidos(self):
        return self.items.filter(
            vendido=True).count()

    @property
    def total_nao_vendidos(self):
        return self.items.filter(
            vendido=False).count()

    @property
    def valor_total_vendidos(self):
        return self.items.filter(
            vendido=True).aggregate(
            models.Sum('produto__valor'))['produto__valor__sum']
    
    @property
    def valor_total_bruto_vendidos(self):
        return self.items.filter(
            vendido=True).aggregate(
            models.Sum('produto__valor_compra'))[
            'produto__valor_compra__sum']

    @property
    def lucro(self):
        valor_vendidos = self.valor_total_vendidos
        valor_bruto = self.valor_total_bruto_vendidos

        if not valor_bruto:
            return

        return valor_vendidos - valor_bruto

    class Meta:
        ordering = ['-id']

class ConsignacaoItem(models.Model):
    produto = models.ForeignKey(
        Produto,
        verbose_name="Produto")

    consignacao = models.ForeignKey(
        Consignacao,
        verbose_name=u"Consignação")

    vendido = models.BooleanField(
        default=False)
