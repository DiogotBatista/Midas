import pandas as pd
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from django.views.generic.list import ListView
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

from despesas.models import Despesa, Conta, Categoria, SubCategoria, FormaPagamento


class RelatorioListView(ListView):
    model = Despesa
    template_name = 'relatorios/relatorios.html'
    context_object_name = 'despesas'
    paginate_by = 20

    def get_queryset(self):
        queryset = Despesa.objects.filter(usuario=self.request.user)
        id_conta = self.request.GET.get('id_conta')
        id_categoria = self.request.GET.get('id_categoria')
        id_subcategoria = self.request.GET.get('id_subcategoria')
        id_forma_pagamento = self.request.GET.get('id_forma_pagamento')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')

        if data_inicio:
            data_inicio = parse_date(data_inicio)
            if data_inicio:
                queryset = queryset.filter(data__gte=data_inicio)

        if data_fim:
            data_fim = parse_date(data_fim)
            if data_fim:
                queryset = queryset.filter(data__lte=data_fim)

        if id_conta:
            queryset = queryset.filter(conta_id=id_conta)
        if id_categoria:
            queryset = queryset.filter(categoria_id=id_categoria)
        if id_subcategoria:
            queryset = queryset.filter(subcategoria_id=id_subcategoria)
        if id_forma_pagamento:
            queryset = queryset.filter(forma_pagamento_id=id_forma_pagamento)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['contas'] = Conta.objects.filter(usuario=user)
        context['categorias'] = Categoria.objects.filter(Q(usuario=user) | Q(padrao=True))
        context['subcategorias'] = SubCategoria.objects.filter(Q(usuario=user) | Q(padrao=True))
        context['formas_pagamento'] = FormaPagamento.objects.filter(Q(usuario=user) | Q(padrao=True))
        context['filtro_conta'] = self.request.GET.get('id_conta', '')
        context['filtro_categoria'] = self.request.GET.get('id_categoria', '')
        context['filtro_subcategoria'] = self.request.GET.get('id_subcategoria', '')
        context['filtro_forma_pagamento'] = self.request.GET.get('id_forma_pagamento', '')
        context['filtro_data_inicio'] = self.request.GET.get('data_inicio', '')
        context['filtro_data_fim'] = self.request.GET.get('data_fim', '')
        return context


class GeneratePDFReport(View):
    def get(self, request, *args, **kwargs):
        # Definição dos estilos
        styles = getSampleStyleSheet()
        if 'Title' not in styles:
            styles.add(ParagraphStyle(name='Title', fontSize=18, alignment=1))

        # Recuperar filtros do request ou sessão
        data_inicio = request.GET.get('data_inicio', '')
        data_fim = request.GET.get('data_fim', '')
        id_conta = request.GET.get('id_conta', '')
        id_categoria = request.GET.get('id_categoria', '')
        id_subcategoria = request.GET.get('id_subcategoria', '')
        id_forma_pagamento = request.GET.get('id_forma_pagamento', '')

        # Construir o queryset com os filtros
        filtros = Q()
        if data_inicio:
            filtros &= Q(data__gte=data_inicio)
        if data_fim:
            filtros &= Q(data__lte=data_fim)
        if id_conta:
            filtros &= Q(conta_id=id_conta)
        if id_categoria:
            filtros &= Q(categoria_id=id_categoria)
        if id_subcategoria:
            filtros &= Q(subcategoria_id=id_subcategoria)
        if id_forma_pagamento:
            filtros &= Q(forma_pagamento_id=id_forma_pagamento)

        despesas = Despesa.objects.filter(filtros)

        # Criar resposta PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'

        # Criar o documento PDF
        pdf = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        # Cabeçalho do relatório
        elements.append(Paragraph("Relatório de Despesas", styles['Title']))

        # Dados das despesas em tabela
        data = [['Data', 'Valor', 'Conta', 'Categoria', 'Subcategoria', 'Forma de Pagamento']]
        for despesa in despesas:
            # Formatar a data no formato 'd/m/aaaa'
            data.append([despesa.data.strftime('%d/%m/%Y'), despesa.valor, despesa.conta.nome, despesa.categoria.nome,
                         despesa.subcategoria.nome, despesa.forma_pagamento.nome])

        # Estilo da tabela
        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black)])

        # Criar a tabela
        table = Table(data)
        table.setStyle(style)
        elements.append(table)

        # Adicionar espaço entre a tabela e o rodapé
        elements.append(Spacer(1, 12))

        # Adicionar o rodapé
        elements.append(Paragraph(f"Relatório gerado pelo do site midas.dbsistemas.com.br, em {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}.", styles['Normal']))

        # Construir o PDF com todos os elementos
        pdf.build(elements)

        return response





class ExportExcel(View):
    def get(self, request, *args, **kwargs):
        data = {
            'Data': ['2021-01-01', '2021-01-02'],
            'Conta': ['Conta Corrente', 'Poupança'],
            'Valor': [200.00, 150.00],
            'Categoria': ['Alimentação', 'Transporte']
        }
        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return response


def subcategorias_por_categoria_relatorio(request):
    user = request.user  # Assume que o usuário está autenticado
    categoria_id = request.GET.get('categoria')
    subcategorias = SubCategoria.objects.filter(
        Q(padrao=True) | Q(usuario=user),  # Argumentos de filtro Q antes de qualquer argumento posicional
        categoria_id=categoria_id  # Argumentos posicionais ou outros filtros
    ).order_by('nome')
    options = '<option value="">---------</option>'
    for subcategoria in subcategorias:
        options += f'<option value="{subcategoria.id}">{subcategoria.nome}</option>'
    return HttpResponse(options)
