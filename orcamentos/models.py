# from django.db import models
# from despesas.models import Categoria, Conta
# from django.core.exceptions import ValidationError
# from djmoney.models.fields import MoneyField
#
# def validar_data_orcamento(data_inicio, data_fim):
#     if data_fim < data_inicio:
#         raise ValidationError(('A data final não pode ser anterior à data inicial.'))
#
# class Orcamento(models.Model):
#     categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_index=True)
#     conta = models.ForeignKey(Conta, on_delete=models.CASCADE, db_index=True)
#     valor = MoneyField(max_digits=14, decimal_places=2, default_currency='BRL')
#     data_inicio = models.DateField(db_index=True)
#     data_fim = models.DateField(db_index=True)
#
#     class Meta:
#         verbose_name_plural = 'Orçamentos'
#
#     def clean(self):
#         super().clean()
#         validar_data_orcamento(self.data_inicio, self.data_fim)
#
#     def __str__(self):
#         return f"{self.categoria.nome} - {self.valor}"
