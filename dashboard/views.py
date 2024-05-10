from django.db.models import Sum, Value, CharField, Q, Func, IntegerField
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.dateparse import parse_date
from django.views import View
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime

from despesas.models import Despesa, Conta, Categoria, SubCategoria, FormaPagamento
from .serializers import ContaSerializer, CategoriaSerializer, SubcategoriaSerializer, FormaPagamentoSerializer, \
    DespesaSerializer


class ContaListAPIView(generics.ListAPIView):
    serializer_class = ContaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retorna apenas as contas do usuário logado e contas padrão
        return Conta.objects.filter(Q(usuario=self.request.user))

class CategoriaListAPIView(generics.ListAPIView):
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retorna as categorias do usuário logado e categorias padrão
        return Categoria.objects.filter(Q(usuario=self.request.user) | Q(padrao=True))

class SubcategoriaListAPIView(generics.ListAPIView):
    serializer_class = SubcategoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retorna as subcategorias do usuário logado e subcategorias padrão
        return SubCategoria.objects.filter(Q(usuario=self.request.user) | Q(padrao=True))

class FormaPagamentoListAPIView(generics.ListAPIView):
    serializer_class = FormaPagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Retorna as formas de pagamento do usuário logado e formas de pagamento padrão
        return FormaPagamento.objects.filter(Q(usuario=self.request.user) | Q(padrao=True))

class DespesasAPIView(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        account = request.GET.get('account')
        category = request.GET.get('category')
        subcategory = request.GET.get('subcategory')
        forma_pagamento = request.GET.get('forma_pagamento')
        year = request.GET.get('year')
        month = request.GET.get('month')



        # Inicializa a query base para despesas do usuário
        despesas_query = Despesa.objects.filter(usuario=user)

        if account:
            despesas_query = despesas_query.filter(conta_id=account)
        if category:
            despesas_query = despesas_query.filter(categoria_id=category)
        if subcategory:
            despesas_query = despesas_query.filter(subcategoria_id=subcategory)
        if forma_pagamento:
            despesas_query = despesas_query.filter(forma_pagamento_id=forma_pagamento)
        if year:
            despesas_query = despesas_query.filter(data__year=year)
        if month:
            despesas_query = despesas_query.filter(data__month=month)

        # Aplica filtro de datas somente se ambas as datas forem fornecidas
        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)

            # Checa a validade das datas
            if not start_date or not end_date:
                return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
            if start_date > end_date:
                return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)

            # Filtra despesas dentro do intervalo de datas
            despesas_query = despesas_query.filter(data__gte=start_date, data__lte=end_date)

        # Serializa e retorna os resultados
        serializer = DespesaSerializer(despesas_query, many=True)
        return Response(serializer.data)


class DespesasPorAnoAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        account = request.GET.get('account')
        category = request.GET.get('category')
        subcategory = request.GET.get('subcategory')
        forma_pagamento = request.GET.get('forma_pagamento')
        year = request.GET.get('year')
        month = request.GET.get('month')

        # Inicializa a query base para despesas do usuário
        despesas_query = Despesa.objects.filter(usuario=user)

        if account:
            despesas_query = despesas_query.filter(conta_id=account)
        if category:
            despesas_query = despesas_query.filter(categoria_id=category)
        if subcategory:
            despesas_query = despesas_query.filter(subcategoria_id=subcategory)
        if forma_pagamento:
            despesas_query = despesas_query.filter(forma_pagamento_id=forma_pagamento)
        if year:
            despesas_query = despesas_query.filter(data__year=year)
        if month:
            despesas_query = despesas_query.filter(data__month=month)

        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if not start_date or not end_date:
                return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
            if start_date > end_date:
                return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)
            despesas_query = despesas_query.filter(data__gte=start_date, data__lte=end_date)

        despesas_por_ano = despesas_query.annotate(ano=Year('data')).values('ano').annotate(total=Sum('valor')).order_by('ano')
        data = [{'ano': result['ano'], 'total': result['total']} for result in despesas_por_ano]
        return Response(data)


class DespesasPorMesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        account = request.GET.get('account')
        category = request.GET.get('category')
        subcategory = request.GET.get('subcategory')
        forma_pagamento = request.GET.get('forma_pagamento')
        year = request.GET.get('year')
        month = request.GET.get('month')

        # Inicializa a query base para despesas do usuário
        despesas_query = Despesa.objects.filter(usuario=user)

        if account:
            despesas_query = despesas_query.filter(conta_id=account)
        if category:
            despesas_query = despesas_query.filter(categoria_id=category)
        if subcategory:
            despesas_query = despesas_query.filter(subcategoria_id=subcategory)
        if forma_pagamento:
            despesas_query = despesas_query.filter(forma_pagamento_id=forma_pagamento)
        if year:
            despesas_query = despesas_query.filter(data__year=year)
        if month:
            despesas_query = despesas_query.filter(data__month=month)

        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if not start_date or not end_date:
                return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
            if start_date > end_date:
                return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)
            despesas_query = despesas_query.filter(data__gte=start_date, data__lte=end_date)

        despesas_por_mes = despesas_query.annotate(mes=Func('data', function='EXTRACT', template='%(function)s(MONTH from %(expressions)s)')).values('mes').annotate(total=Sum('valor')).order_by('mes')
        data = [{'mes': result['mes'], 'total': result['total']} for result in despesas_por_mes]
        return Response(data)

class DespesasPorContaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        account = request.GET.get('account')
        category = request.GET.get('category')
        subcategory = request.GET.get('subcategory')
        forma_pagamento = request.GET.get('forma_pagamento')
        year = request.GET.get('year')
        month = request.GET.get('month')

        # Inicializa a query base para despesas do usuário
        despesas_query = Despesa.objects.filter(usuario=user)

        if account:
            despesas_query = despesas_query.filter(conta_id=account)
        if category:
            despesas_query = despesas_query.filter(categoria_id=category)
        if subcategory:
            despesas_query = despesas_query.filter(subcategoria_id=subcategory)
        if forma_pagamento:
            despesas_query = despesas_query.filter(forma_pagamento_id=forma_pagamento)
        if year:
            despesas_query = despesas_query.filter(data__year=year)
        if month:
            despesas_query = despesas_query.filter(data__month=month)

        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if not start_date or not end_date:
                return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
            if start_date > end_date:
                return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)
            despesas_query = despesas_query.filter(data__gte=start_date, data__lte=end_date)

        despesas_por_conta = despesas_query.values('conta__nome').annotate(total=Sum('valor')).order_by('-total')
        data = [
            {'conta': result['conta__nome'], 'total': result['total']}
            for result in despesas_por_conta
        ]
        return Response(data)

class DespesasPorCategoriaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        account = request.GET.get('account')
        category = request.GET.get('category')
        subcategory = request.GET.get('subcategory')
        forma_pagamento = request.GET.get('forma_pagamento')
        year = request.GET.get('year')
        month = request.GET.get('month')

        # Inicializa a query base para despesas do usuário
        despesas_query = Despesa.objects.filter(usuario=user)

        if account:
            despesas_query = despesas_query.filter(conta_id=account)
        if category:
            despesas_query = despesas_query.filter(categoria_id=category)
        if subcategory:
            despesas_query = despesas_query.filter(subcategoria_id=subcategory)
        if forma_pagamento:
            despesas_query = despesas_query.filter(forma_pagamento_id=forma_pagamento)
        if year:
            despesas_query = despesas_query.filter(data__year=year)
        if month:
            despesas_query = despesas_query.filter(data__month=month)


        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if not start_date or not end_date:
                return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
            if start_date > end_date:
                return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)
            despesas_query = despesas_query.filter(data__gte=start_date, data__lte=end_date)

        despesas_por_categoria = despesas_query.values('categoria__nome').annotate(total=Sum('valor')).order_by(
            '-total')
        data = [{'categoria': result['categoria__nome'], 'total': result['total']}
                for result in despesas_por_categoria]
        return Response(data)

class DespesasPorSubcategoriaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        account = request.GET.get('account')
        category = request.GET.get('category')
        subcategory = request.GET.get('subcategory')
        forma_pagamento = request.GET.get('forma_pagamento')
        year = request.GET.get('year')
        month = request.GET.get('month')

        # Inicializa a query base para despesas do usuário
        despesas_query = Despesa.objects.filter(usuario=user)

        if account:
            despesas_query = despesas_query.filter(conta_id=account)
        if category:
            despesas_query = despesas_query.filter(categoria_id=category)
        if subcategory:
            despesas_query = despesas_query.filter(subcategoria_id=subcategory)
        if forma_pagamento:
            despesas_query = despesas_query.filter(forma_pagamento_id=forma_pagamento)
        if year:
            despesas_query = despesas_query.filter(data__year=year)
        if month:
            despesas_query = despesas_query.filter(data__month=month)

        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if not start_date or not end_date:
                return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
            if start_date > end_date:
                return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)
            despesas_query = despesas_query.filter(data__gte=start_date, data__lte=end_date)

        despesas_por_subcategoria = despesas_query.values('subcategoria__nome').annotate(total=Sum('valor')).order_by('-total')
        data = [{'subcategoria': result['subcategoria__nome'], 'total': result['total']} for result in despesas_por_subcategoria]
        return Response(data)


class DespesasPorFormaPagamentoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        account = request.GET.get('account')
        category = request.GET.get('category')
        subcategory = request.GET.get('subcategory')
        forma_pagamento = request.GET.get('forma_pagamento')
        year = request.GET.get('year')
        month = request.GET.get('month')


        # Inicializa a query base para despesas do usuário
        despesas_query = Despesa.objects.filter(usuario=user)

        if account:
            despesas_query = despesas_query.filter(conta_id=account)
        if category:
            despesas_query = despesas_query.filter(categoria_id=category)
        if subcategory:
            despesas_query = despesas_query.filter(subcategoria_id=subcategory)
        if forma_pagamento:
            despesas_query = despesas_query.filter(forma_pagamento_id=forma_pagamento)
        if year:
            despesas_query = despesas_query.filter(data__year=year)
        if month:
            despesas_query = despesas_query.filter(data__month=month)

        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if not start_date or not end_date:
                return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
            if start_date > end_date:
                return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)
            despesas_query = despesas_query.filter(data__gte=start_date, data__lte=end_date)

        despesas_por_forma_pagamento = despesas_query.annotate(
            forma_pagamento_nome=Coalesce('forma_pagamento__nome', Value('Não informada', output_field=CharField()))
        ).values('forma_pagamento_nome').annotate(total=Sum('valor')).order_by('-total')

        data = [{'forma_pagamento': result['forma_pagamento_nome'], 'total': result['total']}
                for result in despesas_por_forma_pagamento]
        return Response(data)


class Atualiza_total(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Extrai os parâmetros de filtro da URL
        user = request.user
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        account = request.GET.get('account')
        category = request.GET.get('category')
        subcategory = request.GET.get('subcategory')
        forma_pagamento = request.GET.get('forma_pagamento')
        year = request.GET.get('year')
        month = request.GET.get('month')

        # Constrói o queryset com base nos filtros
        queryset = Despesa.objects.filter(usuario=user)
        if account:
            queryset = queryset.filter(conta_id=account)
        if category:
            queryset = queryset.filter(categoria_id=category)
        if subcategory:
            queryset = queryset.filter(subcategoria_id=subcategory)
        if forma_pagamento:
            queryset = queryset.filter(forma_pagamento_id=forma_pagamento)
        if year:
            queryset = queryset.filter(data__year=year)
        if month:
            queryset = queryset.filter(data__month=month)

        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
            if not start_date or not end_date:
                return Response({"error": "Invalid date format."}, status=status.HTTP_400_BAD_REQUEST)
            if start_date > end_date:
                return Response({"error": "Start date must be before end date."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(data__gte=start_date, data__lte=end_date)


        # Calcula o total
        total = queryset.aggregate(total=Sum('valor'))['total'] or 0
        total_formatado = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # Retorna o total formatado como resposta JSON
        return JsonResponse({'total_despesas': total_formatado})

''' usar essa função quando o banco de dados for postgresql ou mysql '''
class Year(Func):
    function = 'EXTRACT'
    template = '%(function)s(YEAR from %(expressions)s)'
    output_field = IntegerField()

''' usar essa função quando o banco de dados for sqlite '''
# class Year(Func):
#     function = 'strftime'
#     # Note que estamos usando '%%%%Y' para garantir que o Django e o SQLite interpretem corretamente
#     template = "%(function)s('%%%%Y', %(expressions)s)"
#     output_field = IntegerField()

class Month(Func):
    function = 'strftime'
    # Note que estamos usando '%%%%m' para garantir que o Django e o SQLite interpretem corretamente
    template = "%(function)s('%%%%m', %(expressions)s)"
    output_field = IntegerField()

class DespesaDashboardView(View):
    def get(self, request):
        total = self.get_queryset().aggregate(total=Sum('valor'))['total'] or 0
        current_year = datetime.now().year
        years = Despesa.objects.filter(usuario=request.user) \
            .annotate(year=Year('data')) \
            .values_list('year', flat=True) \
            .distinct() \
            .order_by('-year')


        context = {
            'total_despesas': f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            'years': list(years),
            'current_year': current_year,
        }
        return render(request, 'dashboard/despesa_dashboard.html', context)

    def get_queryset(self):
        return Despesa.objects.all()
