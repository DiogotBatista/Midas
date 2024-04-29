from django.contrib import admin

from .models import Conta, Categoria, SubCategoria, Despesa, CartaoCredito, PagamentoParcelado, Cheque, FormaPagamento

class FormasPagamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'padrao')
    search_fields = ('nome', 'usuario__username')
    list_filter = ('padrao',)

class ContaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'descricao')
    search_fields = ('nome', 'usuario__username')


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'padrao')
    search_fields = ('nome', 'usuario__username')
    list_filter = ('padrao',)


class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'usuario', 'padrao')
    search_fields = ('nome', 'categoria__nome', 'usuario__username')
    list_filter = ('categoria', 'padrao')


class DespesaAdmin(admin.ModelAdmin):
    list_display = ('valor', 'data', 'categoria', 'subcategoria', 'usuario')
    search_fields = ('descricao', 'categoria__nome', 'subcategoria__nome', 'usuario__username')
    list_filter = ('categoria', 'subcategoria', 'data')


class CartaoCreditoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'banco', 'usuario', 'final_cartao')
    search_fields = ('nome', 'banco', 'usuario__username', 'final_cartao')


class PagamentoParceladoAdmin(admin.ModelAdmin):
    list_display = ('cartao_credito', 'valor_total', 'numero_parcelas', 'pago', 'usuario')
    search_fields = ('cartao_credito__nome', 'usuario__username')
    list_filter = ('pago',)


class ChequeAdmin(admin.ModelAdmin):
    list_display = ('numero', 'valor', 'data_emissao', 'pre_datado', 'usuario')
    search_fields = ('numero', 'usuario__username')
    list_filter = ('data_emissao', 'pre_datado')


admin.site.register(Conta, ContaAdmin)
admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(SubCategoria, SubCategoriaAdmin)
admin.site.register(Despesa, DespesaAdmin)
admin.site.register(CartaoCredito, CartaoCreditoAdmin)
admin.site.register(PagamentoParcelado, PagamentoParceladoAdmin)
admin.site.register(Cheque, ChequeAdmin)
admin.site.register(FormaPagamento, FormasPagamentoAdmin)

admin.site.site_header = "MIDAS - Administração"
admin.site.site_title = "MIDAS - Administração"
admin.site.index_title = "MIDAS - ADM"
