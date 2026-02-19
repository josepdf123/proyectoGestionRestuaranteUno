# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Mesas
    path('mesas/', views.mesas_lista, name='mesas_lista'),
    path('mesas/eliminar/<int:pk>/', views.mesa_eliminar, name='mesa_eliminar'),
    path('mesas/editar/<int:pk>/', views.mesa_editar, name='mesa_editar'),

    # Platos
    path('platos/', views.platos_lista, name='platos_lista'),
    path('platos/eliminar/<int:pk>/', views.plato_eliminar, name='plato_eliminar'),
    path('platos/editar/<int:pk>/', views.plato_editar, name='plato_editar'),

    # Menús
    path('menus/', views.menus_lista, name='menus_lista'),
    path('menus/eliminar/<int:pk>/', views.menu_eliminar, name='menu_eliminar'),
    path('menus/editar/<int:pk>/', views.menu_editar, name='menu_editar'),
]