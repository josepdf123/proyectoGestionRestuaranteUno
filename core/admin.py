from django.contrib import admin
from .models import Estado, Mesa, Plato, Menu, MenuPlato

admin.site.register(Estado)
admin.site.register(Mesa)
admin.site.register(Plato)
admin.site.register(Menu)
admin.site.register(MenuPlato)