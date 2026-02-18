from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Plato, Mesa, Pedido, Menu, MenuPlato, DetallePedido

# Register your models here.

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'get_full_name', 'rol', 'activo')
    list_filter = ('rol', 'activo')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('rol', 'activo')}),
    )

# Los demás modelos son más simples
@admin.register(Plato)
class PlatoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'creador')

@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ('numero_mesa', 'capacidad', 'estado')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa', 'mesero', 'estado', 'fechaCreacion')

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo')

@admin.register(MenuPlato)
class MenuPlatoAdmin(admin.ModelAdmin):
    list_display = ('menu', 'plato')
