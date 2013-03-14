from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

from joiarara.produto.views import *
from joiarara.consignacao.views import *
from joiarara.pastas.views import *

urlpatterns = patterns(
    '',
    url(r'^$', ProdutoListView.as_view()),
    url(r'^add/$', ProdutoAddView.as_view()),
    url(r'^(?P<pk>\d+)/$', ProdutoUpdateView.as_view()),
    url(r'^delete/(?P<pk>\d+)/$', ProdutoDeleteView.as_view()),
    url(r'^stock/(?P<pk>\d+)/$', ProdutoStockView.as_view()),

    url(r'^entrada/$', EntradaProdutoView.as_view()),

    url(r'^consignacoes/$', ConsignacaoListView.as_view()),
    url(r'^consignacoes/add/$', ConsignacaoAddView.as_view()),
    url(r'^consignacoes/produtos/(?P<pk>\d+)/$',
        ConsignacaoProdutosView.as_view()),
    url(r'^consignacoes/print/(?P<pk>\d+)/$',
        ConsignacaoPrintView.as_view()),

    url(r'^consignacoes/finish/(?P<pk>\d+)/$',
        ConsignacaoFinishView.as_view()),

    url(r'^consignacoes/detail/(?P<pk>\d+)/$',
        ConsignacaoDetailView.as_view()),

    url(r'^pastas/$', ListPastaView.as_view()),
    url(r'^pastas/add/$', AddPastaView.as_view()),

    url(r'^static/(.*)','django.views.static.serve',
        {'document_root':settings.STATIC_ROOT, 'show_indexes': True})
    )
