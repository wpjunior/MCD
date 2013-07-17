# -*- coding: utf-8 -*

import re

from django.forms.fields import DecimalField
from .widgets import *

MONEY_RE = re.compile(r'(R\$)? (?P<value>.*)')

class MoneyInput(DecimalField):
    """
    Campo usado para guardar dinheiro em Decimal
    """
    widget = MoneyWidget

    def clean(self, value):
        if not value and not self.required:
            return None
        
        o = MONEY_RE.match(value)
        
        if not o and not value.isdigit():
            if not self.required:
                return None

            raise ValidationError(u"Formatação Inválida")

        if o:
            value = o.group('value').replace('.', '').replace(',', '.')

        return super(MoneyInput, self).clean(value)
