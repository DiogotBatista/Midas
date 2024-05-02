from django.urls import path
from .views import RelatorioListView, GeneratePDFReport, GenerateExcelReport, subcategorias_por_categoria_relatorio

urlpatterns = [
    path('relatorio/', RelatorioListView.as_view(), name='relatorio'),
    path('relatorio/pdf/', GeneratePDFReport.as_view(), name='export_pdf'),
    path('relatorio/excel/', GenerateExcelReport, name='export_excel'),

    # API
    path('api/subcategorias/', subcategorias_por_categoria_relatorio, name='subcategorias_por_categoria_relatorio'),
]
