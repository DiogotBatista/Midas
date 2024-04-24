from django import forms
from django.db import models

from .models import Despesa, Conta, Categoria, SubCategoria


class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = ['conta', 'valor', 'data', 'categoria', 'subcategoria', 'descricao']
        widgets = {
            'data': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'conta': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'subcategoria': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Digite uma descrição para a despesa'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        conta_id = kwargs.pop('conta_id', None)
        super(DespesaForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['conta'].queryset = Conta.objects.filter(usuario=user)
            if conta_id:
                self.fields['conta'].initial = Conta.objects.get(id=conta_id, usuario=user)
                self.fields['conta'].disabled = True  # Bloquear o campo se conta_id for fornecido


class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = ['nome', 'descricao']
        labels = {
            'nome': 'Nome da Conta',
            'descricao': 'Descrição',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome da conta'}),
            'descricao': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Digite uma descrição para a conta'}),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        labels = {
            'nome': 'Nome da Categoria',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome da categoria'}),
        }


class SubCategoriaForm(forms.ModelForm):
    class Meta:
        model = SubCategoria
        fields = ['nome', 'categoria']
        labels = {
            'nome': 'Nome da Subcategoria',
            'categoria': 'Categoria',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o nome da subcategoria'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
        }
