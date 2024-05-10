from django.urls import path

from .views import DespesasAPIView, DespesaDashboardView, DespesasPorContaAPIView, DespesasPorCategoriaAPIView, \
    DespesasPorSubcategoriaAPIView, DespesasPorFormaPagamentoAPIView, ContaListAPIView, CategoriaListAPIView, \
    SubcategoriaListAPIView, FormaPagamentoListAPIView, Atualiza_total, DespesasPorAnoAPIView, DespesasPorMesAPIView

app_name = 'dashboard'
urlpatterns = [
    # API endpoints
    path('api/despesas/', DespesasAPIView.as_view(), name='api-despesas'),
    path('api/despesas-por-conta/', DespesasPorContaAPIView.as_view(), name='api-despesas-por-conta'),
    path('api/despesas-por-categoria/', DespesasPorCategoriaAPIView.as_view(), name='api-despesas-por-categoria'),
    path('api/despesas-por-subcategoria/', DespesasPorSubcategoriaAPIView.as_view(), name='api-despesas-por-subcategoria'),
    path('api/despesas-por-forma-pagamento/', DespesasPorFormaPagamentoAPIView.as_view(), name='api-despesas-por-forma-pagamento'),
    path('api/atualiza-total/', Atualiza_total.as_view(), name='api-atualiza-total'),
    path('api/despesas-por-ano/', DespesasPorAnoAPIView.as_view(), name='api-despesas-por-ano'),
    path('api/despesas-por-mes/', DespesasPorMesAPIView.as_view(), name='api-despesas-por-mes'),


    # Serialisers
    path('api/contas/', ContaListAPIView.as_view(), name='api-contas'),
    path('api/categorias/', CategoriaListAPIView.as_view(), name='api-categorias'),
    path('api/subcategorias/', SubcategoriaListAPIView.as_view(), name='api-subcategorias'),
    path('api/formas-pagamento/', FormaPagamentoListAPIView.as_view(), name='api-formas-pagamento'),


    path('despesa/', DespesaDashboardView.as_view(), name='despesa-dashboard'),
]
