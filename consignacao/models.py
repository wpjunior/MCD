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
