from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import DespesaForm
from .models import Despesa, PagamentoParcelado, SubCategoria, Conta


def marcar_parcela_como_paga(request, parcela_id):
    parcela = get_object_or_404(PagamentoParcelado, id=parcela_id, usuario=request.user)
    parcela.pago = True
    parcela.save()
    return redirect('alguma-url-para-listar-parcelas')


class DespesaListView(LoginRequiredMixin, ListView):
    model = Despesa
    template_name = 'despesas/despesa_list.html'
    context_object_name = 'despesas'
    paginate_by = 10  # Define o número de despesas por página

    def get_queryset(self):
        queryset = super().get_queryset().filter(usuario=self.request.user)
        search_query = self.request.GET.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(valor__icontains=search_query) |
                Q(descricao__icontains=search_query) |
                Q(categoria__nome__icontains=search_query) |
                Q(subcategoria__nome__icontains=search_query) |
                Q(conta__nome__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super(DespesaListView, self).get_context_data(**kwargs)
        context['conta_id'] = self.request.GET.get('conta_id', '')
        return context


class DespesaDetailView(LoginRequiredMixin, DetailView):
    model = Despesa
    template_name = 'despesas/despesa_detail.html'

    def get_queryset(self):
        return Despesa.objects.filter(usuario=self.request.user)


class DespesaCreateView(LoginRequiredMixin, CreateView):
    model = Despesa
    form_class = DespesaForm
    template_name = 'despesas/despesa_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        conta_id = self.request.GET.get('conta_id')
        if conta_id:
            kwargs['initial'] = {'conta': conta_id}
            kwargs['conta_id'] = conta_id  # Passando conta_id para o form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conta_id'] = self.request.GET.get('conta_id')  # Adicionar conta_id ao contexto para uso no template
        return context

    def get_form(self, form_class=None):
        form = super(DespesaCreateView, self).get_form(form_class)
        # Se a conta foi passada pela URL, bloqueia a edição deste campo
        if 'conta_locked' in self.request.session:
            form.fields['conta'].widget.attrs['disabled'] = True
        return form

    def form_valid(self, form):
        # Garante que a conta não seja alterada maliciosamente se estiver bloqueada
        if 'conta_locked' in self.request.session:
            conta_id = self.request.session.pop('conta_locked')
            form.instance.conta = get_object_or_404(Conta, pk=conta_id)
            messages.info(self.request, 'Conta bloqueada. Não é possível alterar a conta.')
        messages.success(self.request, 'Despesa criada com sucesso!')
        form.instance.usuario = self.request.user
        return super(DespesaCreateView, self).form_valid(form)

    def get_success_url(self):
        # Retorna ao local apropriado com base na origem do usuário
        return self.request.GET.get('next', reverse('despesa-list'))


class DespesaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Despesa
    form_class = DespesaForm
    template_name = 'despesas/despesa_form.html'
    success_url = reverse_lazy('despesa-list')

    def get_form_kwargs(self):
        kwargs = super(DespesaUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user  # Adiciona o usuário atual aos kwargs do formulário
        return kwargs

    # Verifica se o usuário logado é o dono da despesa
    def test_func(self):
        despesa = self.get_object()
        return despesa.usuario == self.request.user

    def get_queryset(self):
        return Despesa.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Despesa atualizada com sucesso!')
        return response


class DespesaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Despesa
    template_name = 'despesas/despesa_confirm_delete.html'
    success_url = reverse_lazy('despesa-list')

    # Verifica se o usuário logado é o dono da despesa
    def test_func(self):
        despesa = self.get_object()
        return despesa.usuario == self.request.user

    def get_queryset(self):
        """
        Assegura que apenas as despesas pertencentes ao usuário logado possam ser acessadas.
        """
        qs = super().get_queryset()  # Obtem a queryset original
        return qs.filter(usuario=self.request.user)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  # Isso chama delete()
        messages.success(request, 'Despesa deletada com sucesso!')
        return response


def subcategorias_por_categoria(request):
    categoria_id = request.GET.get('categoria')
    subcategorias = SubCategoria.objects.filter(categoria_id=categoria_id).order_by('nome')
    options = '<option value="">---------</option>'
    for subcategoria in subcategorias:
        options += f'<option value="{subcategoria.id}">{subcategoria.nome}</option>'
    return HttpResponse(options)


class DespesasPorContaView(ListView):
    model = Despesa
    template_name = 'despesas/despesa_list.html'  # Reutilize o template de listagem de despesas ou crie um novo se necessário
    paginate_by = 10

    def get_queryset(self):
        conta_id = self.kwargs.get('conta_id')
        despesas = Despesa.objects.filter(conta__id=conta_id, usuario=self.request.user)
        # print("Despesas encontradas:", despesas)  # Apenas para depuração
        return despesas
