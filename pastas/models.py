# -*- coding: utf-8 -*-

from django.db import models

from .constants import *

class Pasta(models.Model):
    status = models.CharField(
        choices=PASTA_STATUS_CHOICES,
        max_length=1,
        default='d')

    @property
    def nome(self):
        return "Pasta %d" % self.pk

    def __unicode__(self):
        return self.nome
