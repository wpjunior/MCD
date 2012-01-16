from django.conf.urls.defaults import patterns, include, url

from joiarara.produto.views import *
from joiarara.consignacao.views import *

urlpatterns = patterns('',
                       url(r'^$', ProdutoListView.as_view()),
                       url(r'^add/$', ProdutoAddView.as_view()),
                       url(r'^(?P<pk>\d+)/$', ProdutoUpdateView.as_view()),
                       url(r'^delete/(?P<pk>\d+)/$', ProdutoDeleteView.as_view()),
                       url(r'^consig/$', ConsigView.as_view()),
                       url(r'^consig/generate/$', GenerateConsigView.as_view())
)
