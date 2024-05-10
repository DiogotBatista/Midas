# from despesas.forms import DespesaForm
# from despesas.models import Despesa
# from django.shortcuts import render, redirect, get_object_or_404
# from django.utils import timezone
#
#
# def criar_gasto_futuro(request):
#     if request.method == 'POST':
#         form = DespesaForm(request.POST)
#         if form.is_valid():
#             gasto_futuro = form.save(commit=False)
#             gasto_futuro.usuario = request.user
#             gasto_futuro.save()
#             return redirect('lista_de_gastos_futuros')
#     else:
#         form = DespesaForm()
#
#     return render(request, 'orcamentos/criar_gasto_futuro.html', {'form': form})
#
#
# def atualizar_gasto_futuro(request, id):
#     gasto_futuro = get_object_or_404(Despesa, id=id, usuario=request.user)
#     if request.method == 'POST':
#         form = DespesaForm(request.POST, instance=gasto_futuro)
#         if form.is_valid():
#             form.save()
#             return redirect('lista_de_gastos_futuros')
#     else:
#         form = DespesaForm(instance=gasto_futuro)
#
#     return render(request, 'despesas/atualizar_gasto_futuro.html', {'form': form, 'gasto_futuro': gasto_futuro})
#
# def transicao_gastos_para_despesas():
#     hoje = timezone.now().date()
#     gastos_futuros = Despesa.objects.filter(data_vencimento__lte=hoje, tipo_despesa='parcelada', pago=True)
#     for gasto in gastos_futuros:
#         gasto.tipo_despesa = 'regular'
#         gasto.data_vencimento = None  # Limpa a data de vencimento após a transição
#         gasto.save()
