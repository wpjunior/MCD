from django.db import models
from joiarara.produto.models import Produto
# Create your models here.
class Consignacao(models.Model):
    produto = models.ForeignKey(Produto)
