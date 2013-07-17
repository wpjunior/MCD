# -*- coding: utf-8 -*

__all__ = ('MoneyWidget',)

from django.forms.widgets import TextInput

class MoneyWidget(TextInput):
    """
    Widget de entrada de dinheiro (reais).
    """
    def __init__(self, *args, **kwargs):
        super(MoneyWidget, self).__init__(*args, **kwargs)

        if not self.attrs.has_key('class'):
            self.attrs['class'] = 'money input-medium'

    def _format_value(self, value):
        if isinstance (value, basestring):
            return value

        return ("R$ %0.2f" % value).replace('.', ',')

    class Media:
        js = ('js/jquery.price_format.js',)
