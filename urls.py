from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

from MCD.produto.views import *
from MCD.orcamento.views import *

urlpatterns = patterns(
    '',
    url(r'^$', ProdutoListView.as_view()),
    url(r'^add/$', ProdutoAddView.as_view()),
    url(r'^(?P<pk>\d+)/$', ProdutoUpdateView.as_view()),
    url(r'^delete/(?P<pk>\d+)/$', ProdutoDeleteView.as_view()),

    url(r'^orcamento/$', ListOrcamentoView.as_view()),
    url(r'^orcamento/(?P<pk>\d+)/$', OrcamentoView.as_view()),
    url(r'^orcamento/add/$', AddOrcamentoView.as_view()),
    #url(r'^consignacoes/add/$', ConsignacaoAddView.as_view()),
    #url(r'^consignacoes/produtos/(?P<pk>\d+)/$',
    #    ConsignacaoProdutosView.as_view()),
    #url(r'^consignacoes/print/(?P<pk>\d+)/$',
    #    ConsignacaoPrintView.as_view()),

    #url(r'^consignacoes/finish/(?P<pk>\d+)/$',
    #    ConsignacaoFinishView.as_view()),

    #url(r'^consignacoes/detail/(?P<pk>\d+)/$',
    #    ConsignacaoDetailView.as_view()),

    url(r'^static/(.*)','django.views.static.serve',
        {'document_root':settings.STATIC_ROOT, 'show_indexes': True})
    )
