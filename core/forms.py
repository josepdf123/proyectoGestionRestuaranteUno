# core/forms.py

from django import forms
from .models import Mesa, Plato, Menu, MenuPlato, Estado


class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['numMesa', 'capacidad', 'estado']
        labels = {
            'numMesa': 'Número de Mesa',
            'capacidad': 'Capacidad',
            'estado': 'Estado',
        }
        widgets = {
            'numMesa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 4'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = ['nombre', 'descripcion', 'precio']
        labels = {
            'nombre': 'Nombre del Plato',
            'descripcion': 'Descripción',
            'precio': 'Precio',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bandeja Paisa'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe el plato...'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 25000', 'step': '0.01'}),
        }


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['nombre', 'tipo']
        labels = {
            'nombre': 'Nombre del Menú',
            'tipo': 'Tipo',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Menú del día'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }


class MenuPlatoForm(forms.ModelForm):
    class Meta:
        model = MenuPlato
        fields = ['idMenu', 'idPlato', 'nombre', 'descripcion', 'precio']
        labels = {
            'idMenu': 'Menú',
            'idPlato': 'Plato',
            'nombre': 'Nombre en Menú',
            'descripcion': 'Descripción',
            'precio': 'Precio',
        }
        widgets = {
            'idMenu': forms.Select(attrs={'class': 'form-select'}),
            'idPlato': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        
class MenuPlatoInlineForm(forms.Form):
    platos = forms.ModelMultipleChoiceField(
        queryset=Plato.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Platos del Menú"
    )