import logging

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from djmoney.models.fields import MoneyField

from usuarios.models import CustomUser

logger = logging.getLogger(__name__)


class Conta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, db_index=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Contas'

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categorias',
                                null=True, blank=True)
    nome = models.CharField(max_length=100, db_index=True)
    padrao = models.BooleanField(default=False)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


class SubCategoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subcategorias',
                                null=True, blank=True)
    nome = models.CharField(max_length=100, db_index=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    padrao = models.BooleanField(default=False)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Subcategorias'

    def __str__(self):
        return self.nome


class Despesa(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL')
    data = models.DateField(db_index=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True)
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.CASCADE, null=True)
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-data']
        verbose_name_plural = 'Despesas'

    def __str__(self):
        return f"{self.valor} - {self.data}"


class CartaoCredito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    final_cartao = models.CharField(max_length=4, db_index=True, unique=True, help_text='Últimos 4 dígitos do cartão')
    bandeira = models.CharField(max_length=100)
    nome = models.CharField(max_length=100)
    banco = models.CharField(max_length=100)
    observacao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome


class PagamentoParcelado(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    cartao_credito = models.ForeignKey(CartaoCredito, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    valor_total = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL')
    numero_parcelas = models.IntegerField()
    parcela_atual = models.IntegerField()
    valor_parcela = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL')
    data_pagamento = models.DateField()
    pago = models.BooleanField(default=False)

    @classmethod
    def criar_pagamentos_parcelados(cls, usuario, cartao_credito, categoria, valor_total, numero_parcelas, data_inicio):
        # Validação do número de parcelas
        if numero_parcelas <= 0:
            raise ValidationError("O número de parcelas deve ser maior que zero.")

        # Validação do valor total
        if valor_total <= 0:
            raise ValidationError("O valor total deve ser positivo.")

        # Validação da data de início (não deve ser no passado)
        if data_inicio < timezone.now().date():
            raise ValidationError("A data de início não pode estar no passado.")

        valor_parcela = valor_total / numero_parcelas
        parcelas = []

        for parcela in range(1, numero_parcelas + 1):
            data_pagamento = data_inicio + relativedelta(months=+parcela - 1)
            pagamento = cls(
                usuario=usuario,
                conta=cartao_credito.conta,  # Supondo que CartaoCredito tenha uma FK para Conta
                cartao_credito=cartao_credito,
                categoria=categoria,
                valor_total=valor_total,
                numero_parcelas=numero_parcelas,
                parcela_atual=parcela,
                valor_parcela=valor_parcela,
                data_pagamento=data_pagamento,
                pago=False
            )
            parcelas.append(pagamento)

        try:
            cls.objects.bulk_create(parcelas)
        except Exception as e:
            logger.error(f"Erro ao criar pagamentos parcelados: {str(e)}")
            raise ValidationError(f"Erro ao criar pagamentos parcelados: {str(e)}")

    def __str__(self):
        return f"{self.cartao_credito.nome} - Parcela {self.parcela_atual}/{self.numero_parcelas} - {self.valor_parcela}"


def validar_data_cheque(data_emissao, pre_datado):
    if pre_datado < data_emissao:
        raise ValidationError(('A data pré-datada não pode ser anterior à data de emissão.'))


class Cheque(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE)
    numero = models.CharField(max_length=100)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL')
    data_emissao = models.DateField()
    pre_datado = models.DateField(db_index=True)
    observacao = models.TextField(null=True, blank=True)

    def clean(self):
        super().clean()
        validar_data_cheque(self.data_emissao, self.pre_datado)

    def __str__(self):
        return f"{self.numero} - {self.valor} - para: {self.pre_datado}"


def soma_despesas_usuario(usuario):
    return Despesa.objects.filter(conta__usuario=usuario).aggregate(Sum('valor'))
