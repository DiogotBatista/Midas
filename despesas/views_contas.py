from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.http import HttpResponseRedirect
from django.urls import reverse


from .forms import ContaForm
from .models import Conta


class ContaCreateView(LoginRequiredMixin, CreateView):
    model = Conta
    form_class = ContaForm
    template_name = 'despesas/conta_form.html'
    success_url = reverse_lazy('conta-list')

    '''O método form_valid é chamado quando o formulário é válido.'''

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Conta adicionada com sucesso!')
        if 'save_and_add_another' in self.request.POST:
            return HttpResponseRedirect(reverse('conta-create'))

        return response


class ContaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Conta
    form_class = ContaForm
    template_name = 'despesas/conta_form.html'
    success_url = reverse_lazy('conta-list')

    # Verifica se o usuário logado é o dono da conta
    def test_func(self):
        conta = self.get_object()
        return conta.usuario == self.request.user

    def get_queryset(self):
        return Conta.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Conta atualizada com sucesso!')
        return response


class ContaListView(LoginRequiredMixin, ListView):
    model = Conta
    template_name = 'despesas/conta_list.html'
    context_object_name = 'contas'
    paginate_by = 10  # Número de contas por página

    def get_queryset(self):
        qs = super().get_queryset().filter(usuario=self.request.user)
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(Q(nome__icontains=search) | Q(descricao__icontains=search))
        return qs


class ContaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Conta
    template_name = 'despesas/conta_confirm_delete.html'
    success_url = reverse_lazy('conta-list')

    # Verifica se o usuário logado é o dono da conta
    def test_func(self):
        conta = self.get_object()
        return conta.usuario == self.request.user

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(usuario=self.request.user)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(self.request, 'Conta excluída com sucesso!')
        return response
