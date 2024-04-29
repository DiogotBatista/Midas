from django.urls import path

from .views_configuracao import CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView, \
    SubCategoriaListView, SubCategoriaCreateView, SubCategoriaUpdateView, SubCategoriaDeleteView, \
    CongiguracaoView, SubcategoriaPorCategoriaView, FormaPagamentoListView, FormaPagamentoCreateView, \
    FormaPagamentoUpdateView, FormaPagamentoDeleteView
from .views_contas import ContaCreateView, ContaUpdateView, ContaListView, ContaDeleteView
from .views_despesas import DespesaListView, DespesaDetailView, DespesaUpdateView, DespesaDeleteView, \
    subcategorias_por_categoria, DespesasPorContaView, DespesaCreateView

urlpatterns = [
    # Despesas URLs
    path('', DespesaListView.as_view(), name='despesa-list'),
    path('despesas/', DespesaListView.as_view(), name='despesa-list'),
    path('<int:pk>/', DespesaDetailView.as_view(), name='despesa-detail'),
    path('create/', DespesaCreateView.as_view(), name='despesa-create'),
    path('despesas/create/<int:conta_id>/', DespesaCreateView.as_view(), name='despesa-create-with-account'),
    path('<int:pk>/update/', DespesaUpdateView.as_view(), name='despesa-update'),
    path('<int:pk>/delete/', DespesaDeleteView.as_view(), name='despesa-delete'),

    path('contas/<int:conta_id>/despesas/', DespesasPorContaView.as_view(), name='despesas-por-conta'),

    # Contas URLs
    path('contas/nova/', ContaCreateView.as_view(), name='conta-create'),
    path('contas/', ContaListView.as_view(), name='conta-list'),
    path('contas/editar/<int:pk>/', ContaUpdateView.as_view(), name='conta-update'),
    path('contas/<int:pk>/delete/', ContaDeleteView.as_view(), name='conta-delete'),

    # Categorias URLs
    path('categorias/', CategoriaListView.as_view(), name='categoria-list'),
    path('categorias/create/', CategoriaCreateView.as_view(), name='categoria-create'),
    path('categorias/<int:pk>/edit/', CategoriaUpdateView.as_view(), name='categoria-update'),
    path('categorias/<int:pk>/delete/', CategoriaDeleteView.as_view(), name='categoria-delete'),

    #Subcategorias URLs
    path('subcategorias/', SubCategoriaListView.as_view(), name='subcategoria-list'),
    path('categorias/<int:categoria_id>/subcategorias/', SubcategoriaPorCategoriaView.as_view(), name='subcategoria-por-categoria'),
    path('subcategorias/create/', SubCategoriaCreateView.as_view(), name='subcategoria-create'),
    path('subcategorias/<int:pk>/edit/', SubCategoriaUpdateView.as_view(), name='subcategoria-update'),
    path('subcategorias/<int:pk>/delete/', SubCategoriaDeleteView.as_view(), name='subcategoria-delete'),

    # Configurações
    path('configuracoes/', CongiguracaoView.as_view(), name='configuracao'),

    # API
    path('api/subcategorias/', subcategorias_por_categoria, name='subcategorias_por_categoria'),

    # Formas de pagamentos

    path('formas-pagamento/', FormaPagamentoListView.as_view(), name='forma-pagamento-list'),
    path('formas-pagamento/create/', FormaPagamentoCreateView.as_view(), name='forma-pagamento-create'),
    path('formas-pagamento/<int:pk>/edit/', FormaPagamentoUpdateView.as_view(), name='forma-pagamento-update'),
    path('formas-pagamento/<int:pk>/delete/', FormaPagamentoDeleteView.as_view(), name='forma-pagamento-delete'),

]
