from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect


from .forms import CategoriaForm, SubCategoriaForm
from .models import Categoria, SubCategoria


class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'despesas/categoria_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(usuario=self.request.user) | Categoria.objects.filter(padrao=True)
        search_query = self.request.GET.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoriaListView, self).get_context_data(**kwargs)
        return context


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'despesas/categoria_form.html'
    success_url = reverse_lazy('categoria-list')

    def form_valid(self, form):
        if not form.instance.padrao:
            form.instance.usuario = self.request.user
            messages.success(self.request, 'Categoria criada com sucesso!')
        return super().form_valid(form)


class CategoriaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'despesas/categoria_form.html'
    success_url = reverse_lazy('categoria-list')

    def test_func(self):
        categoria = self.get_object()
        return categoria.usuario == self.request.user or categoria.padrao == False

    def form_valid(self, form):
        if not form.instance.padrao:
            messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)


class CategoriaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Categoria
    template_name = 'despesas/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria-list')

    def test_func(self):
        categoria = self.get_object()
        return categoria.usuario == self.request.user and not categoria.padrao

    def get_queryset(self):
        """
        Assegura que apenas as despesas pertencentes ao usuário logado possam ser acessadas.
        """
        qs = super().get_queryset()  # Obtem a queryset original
        return qs.filter(usuario=self.request.user)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  # Isso chama delete()
        messages.success(request, 'Categoria deletada com sucesso!')
        return response


# Similar views for SubCategoria
class SubCategoriaListView(LoginRequiredMixin, ListView):
    model = SubCategoria
    template_name = 'despesas/subcategoria_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(usuario=self.request.user) | SubCategoria.objects.filter(padrao=True)

        search_query = self.request.GET.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(nome__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SubCategoriaListView, self).get_context_data(**kwargs)
        return context


class SubCategoriaCreateView(LoginRequiredMixin, CreateView):
    model = SubCategoria
    form_class = SubCategoriaForm
    template_name = 'despesas/subcategoria_form.html'


    def get_success_url(self):
        return self.request.GET.get('next', reverse('subcategoria-list'))

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Subcategoria criada com sucesso!')
        return HttpResponseRedirect(self.get_success_url())


class SubCategoriaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SubCategoria
    form_class = SubCategoriaForm
    template_name = 'despesas/subcategoria_form.html'
    success_url = reverse_lazy('subcategoria-list')

    def test_func(self):
        subcategoria = self.get_object()
        return subcategoria.usuario == self.request.user

    def form_valid(self, form):
        if not form.instance.padrao:
            messages.success(self.request, 'Subcategoria atualizada com sucesso!')
        return super().form_valid(form)


class SubCategoriaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = SubCategoria
    template_name = 'despesas/subcategoria_confirm_delete.html'
    success_url = reverse_lazy('subcategoria-list')

    def test_func(self):
        subcategoria = self.get_object()
        return subcategoria.usuario == self.request.user and subcategoria.padrao == False

    def get_queryset(self):
        """
        Assegura que apenas as despesas pertencentes ao usuário logado possam ser acessadas.
        """
        qs = super().get_queryset()  # Obtem a queryset original
        return qs.filter(usuario=self.request.user)

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)  # Isso chama delete()
        messages.success(request, 'Subategoria deletada com sucesso!')
        return response


class CongiguracaoView(LoginRequiredMixin, ListView):
    template_name = 'despesas/configuracao.html'
    model = Categoria



class SubcategoriaPorCategoriaView(ListView):
    model = SubCategoria
    template_name = 'despesas/subcategoria_list.html'  # Reutilize o template de listagem de despesas ou crie um novo se necessário
    paginate_by = 10

    def get_queryset(self):
        categoria_id = self.kwargs.get('categoria_id')
        subcategoria = SubCategoria.objects.filter(categoria__id=categoria_id, usuario=self.request.user)
        # print("Subvategorias encontradas:", categoria)  # Apenas para depuração
        return subcategoria
