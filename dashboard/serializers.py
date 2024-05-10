from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import serializers

from despesas.models import Despesa
from despesas.models import Conta, Categoria, SubCategoria, FormaPagamento


class ContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conta
        fields = ['id', 'nome']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome']

class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategoria
        fields = ['id', 'nome']

class FormaPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormaPagamento
        fields = ['id', 'nome']


class DespesaSerializer(serializers.ModelSerializer):
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL')

    class Meta:
        model = Despesa
        fields = ['usuario', 'conta', 'valor', 'forma_pagamento', 'data', 'categoria', 'subcategoria', 'descricao']

