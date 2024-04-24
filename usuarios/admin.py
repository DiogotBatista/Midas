from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Aviso
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms

# Formulários personalizados para adicionar e alterar instâncias de usuário
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = '__all__'

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

# Customizando a exibição do usuário no admin
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'last_access')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'data_cadastro', 'last_access')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # edit mode
            return self.readonly_fields + ('data_cadastro',)
        return self.readonly_fields


admin.site.register(CustomUser, CustomUserAdmin)

# Configurando o Admin para o modelo Aviso
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ordenacao', 'data_criacao')
    list_editable = ('ordenacao',)
    search_fields = ('titulo',)
    list_per_page = 25

admin.site.register(Aviso, AvisoAdmin)
