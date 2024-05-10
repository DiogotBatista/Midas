import pandas as pd
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from django.views.generic.list import ListView
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from django.db.models import Sum

from despesas.models import Conta, Categoria, SubCategoria, FormaPagamento, Despesa


class RelatorioListView(ListView):
    model = Despesa
    template_name = 'relatorios/relatorios.html'
    context_object_name = 'despesas'
    paginate_by = 25

    def get_queryset(self):
        queryset = Despesa.objects.filter(usuario=self.request.user)
        self.filtros_aplicados = False
        id_conta = self.request.GET.get('id_conta')
        id_categoria = self.request.GET.get('id_categoria')
        id_subcategoria = self.request.GET.get('id_subcategoria')
        id_forma_pagamento = self.request.GET.get('id_forma_pagamento')
        id_descricao = self.request.GET.get('id_descricao')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')

        for field in ['id_conta', 'id_categoria', 'id_subcategoria', 'id_forma_pagamento', 'id_descricao', 'data_inicio', 'data_fim']:
            value = self.request.GET.get(field)
            if value:
                self.filtros_aplicados = True
                break

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
        context['filtros_aplicados'] = self.filtros_aplicados
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
        context['filtro_descricao'] = self.request.GET.get('id_descricao', '')
        total = self.get_queryset().aggregate(total=Sum('valor'))['total'] or 0
        context['total_despesas'] = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        return context


class GeneratePDFReport(View):
    def get(self, request, *args, **kwargs):
        user = request.user  # Assume que o usuário está autenticado
        styles = getSampleStyleSheet()
        if 'Title' not in styles:
            styles.add(ParagraphStyle(name='Title', fontSize=22, alignment=TA_CENTER, spaceAfter=20, textColor=colors.darkblue))
        if 'Footer' not in styles:
            styles.add(ParagraphStyle(name='Footer', fontSize=10, alignment=TA_LEFT, spaceBefore=5, textColor=colors.gray))
        if 'TotalStyle' not in styles:
            styles.add(ParagraphStyle(name='TotalStyle', fontSize=13, alignment=TA_LEFT, spaceBefore=10, textColor=colors.black, spaceAfter=20, fontName='Helvetica-Bold'))

        # Construir o queryset com os filtros
        filtros = Q(usuario=user)
        for key in ['data_inicio', 'data_fim', 'id_conta', 'id_categoria', 'id_subcategoria', 'id_forma_pagamento', 'id_descricao']:
            value = request.GET.get(key, '')
            if value:
                if 'data' in key:
                    filtros &= Q(**{f"data__{'gte' if 'inicio' in key else 'lte'}": parse_date(value)})
                else:
                    field_map = {
                        'id_conta': 'conta_id',
                        'id_categoria': 'categoria_id',
                        'id_subcategoria': 'subcategoria_id',
                        'id_forma_pagamento': 'forma_pagamento_id',
                        'id_descricao': 'descricao__icontains'
                    }
                    filtros &= Q(**{field_map[key]: value})

        despesas = Despesa.objects.filter(filtros)
        total = despesas.aggregate(Sum('valor'))['valor__sum'] or 0

        # Criar resposta PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Relatório de Despesas.pdf"'

        # Criar o documento PDF
        pdf = SimpleDocTemplate(response, pagesize=landscape(letter))
        elements = [Paragraph("Relatório de Despesas", styles['Title'])]

        # Dados das despesas em tabela
        data = [['Data', 'Valor', 'Conta', 'Categoria', 'Subcategoria', 'Forma de Pagamento', 'Descrição']]
        styleN = styles["BodyText"]
        styleN.alignment = TA_CENTER
        styleN.wordWrap = 'CJK'



        for despesa in despesas:
            row = [
                Paragraph(despesa.data.strftime('%d/%m/%Y') if despesa.data else 'N/A', styleN),
                despesa.valor if despesa.valor else 'N/A',
                Paragraph(despesa.conta.nome if despesa.conta else 'N/A', styleN),
                Paragraph(despesa.categoria.nome if despesa.categoria else 'N/A', styleN),
                Paragraph(despesa.subcategoria.nome if despesa.subcategoria else 'N/A', styleN),
                Paragraph(despesa.forma_pagamento.nome if despesa.forma_pagamento else 'Não informado', styleN),
                Paragraph(despesa.descricao if despesa.descricao else ' ', styleN)
            ]
            data.append(row)

        # Adicionar linha com o total
        total_str = f"Total: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        total_row = [Paragraph(total_str, styles['TotalStyle'])]
        data.append(total_row)


        table = Table(data, colWidths=[80, 80, 100, 100, 120, 120, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Estilos adicionais para a linha do total
            ('SPAN', (0, -1), (-1, -1)),  # Mescla todas as células da última linha
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),  # Fundo da linha do total
        ]))
        elements.append(table)

        # Footer
        # elements.append(Spacer(1, 20))
        footer_text = f"Relatório gerado por midas.dbsistemas.com.br em {timezone.localtime().strftime('%d/%m/%Y %H:%M:%S')}."
        elements.append(Paragraph(footer_text, styles['Footer']))

        # # Adicionar total como parágrafo
        # total_str = f"Total: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        # total_paragraph = Paragraph(total_str, styles['TotalStyle'])
        # elements.append(total_paragraph)

        # Construir o PDF com todos os elementos
        pdf.build(elements)

        return response


def GenerateExcelReport(request):
    user = request.user  # Assume que o usuário está autenticado

    # Obter os filtros do request
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    id_conta = request.GET.get('id_conta', '')
    id_categoria = request.GET.get('id_categoria', '')
    id_subcategoria = request.GET.get('id_subcategoria', '')
    id_forma_pagamento = request.GET.get('id_forma_pagamento', '')
    id_descricao = request.GET.get('id_descricao', '')

    # Construir os filtros garantindo que apenas despesas do usuário logado sejam consideradas
    filtros = Q(usuario=user)
    for key in ['data_inicio', 'data_fim', 'id_conta', 'id_categoria', 'id_subcategoria', 'id_forma_pagamento',
                'id_descricao']:
        value = request.GET.get(key, '')
        if value:
            if 'data' in key:
                filtros &= Q(**{f"data__{'gte' if 'inicio' in key else 'lte'}": parse_date(value)})
            else:
                field_map = {
                    'id_conta': 'conta_id',
                    'id_categoria': 'categoria_id',
                    'id_subcategoria': 'subcategoria_id',
                    'id_forma_pagamento': 'forma_pagamento_id',
                    'id_descricao': 'descricao__icontains'
                }
                filtros &= Q(**{field_map[key]: value})

    despesas = Despesa.objects.filter(filtros)
    total = despesas.aggregate(Sum('valor'))['valor__sum'] or 0
    total_str = f"Total: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Criar um DataFrame do pandas
    data = {
        'Data': [despesa.data.strftime('%d/%m/%Y') if despesa.data else 'N/A' for despesa in despesas],
        'Conta': [despesa.conta.nome if despesa.conta else 'N/A' for despesa in despesas],
        'Valor': [despesa.valor if despesa.valor else 0 for despesa in despesas],  # Assumindo 0 se o valor for nulo
        'Categoria': [despesa.categoria.nome if despesa.categoria else 'N/A' for despesa in despesas],
        'Subcategoria': [despesa.subcategoria.nome if despesa.subcategoria else 'N/A' for despesa in despesas],
        'Forma de Pagamento': [despesa.forma_pagamento.nome if despesa.forma_pagamento else 'Não informado' for despesa in
                               despesas],
        'Descrição': [despesa.descricao if despesa.descricao else ' ' for despesa in despesas],
    }

    df = pd.DataFrame(data)

    # Adicionar uma linha de total ao DataFrame
    total_row = pd.DataFrame({'Data': [total_str], 'Conta': [''], 'Valor': [''], 'Categoria': [''], 'Subcategoria': [''],
                              'Forma de Pagamento': [''], 'Descrição': ['']})

    df = pd.concat([df, total_row], ignore_index=True)

    # Converter o DataFrame para um arquivo Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="Relatório de Despesas.xlsx"'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return response




def subcategorias_por_categoria_relatorio(request):
    user = request.user  # Assume que o usuário está autenticado
    categoria_id = request.GET.get('categoria')
    if not categoria_id:
        return HttpResponse('<option value="">Selecione uma categoria primeiro</option>')
    subcategorias = SubCategoria.objects.filter(
        Q(padrao=True) | Q(usuario=user),  # Argumentos de filtro Q antes de qualquer argumento posicional
        categoria_id=categoria_id  # Argumentos posicionais ou outros filtros
    ).order_by('nome')
    options = '<option value="">---------</option>'
    for subcategoria in subcategorias:
        options += f'<option value="{subcategoria.id}">{subcategoria.nome}</option>'
    return HttpResponse(options)
