from django.forms import ModelForm

from .models import Produto

from MCD.common.fields import MoneyInput
from MCD.common.widgets import MoneyWidget

class ProdutoForm(ModelForm):
    valor_compra = MoneyInput(
        label="Valor de compra",
        required=False,
        widget=MoneyWidget(attrs={'class' : 'money'}))
    
    valor_venda = MoneyInput(
        label="Valor de venda",
        required=True,
        widget=MoneyWidget(attrs={'class' : 'money'}))
    
    class Meta:
        model = Produto
