__all__ = ('PastaForm',)

from django.forms import ModelForm

from .models import Pasta

class PastaForm(ModelForm):
    class Meta:
        model = Pasta
        exclude = ('status',)
