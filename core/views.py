# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Mesa, Plato, Menu, MenuPlato, Estado
from .forms import MesaForm, PlatoForm, MenuForm, MenuPlatoForm


# ─── MESAS ────────────────────────────────────────────────────────────────────

def mesas_lista(request):
    mesas = Mesa.objects.select_related('estado').all()
    form = MesaForm()

    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Mesa agregada correctamente!')
            return redirect('mesas_lista')
        else:
            messages.error(request, 'Error al agregar la mesa. Revisa los datos.')

    return render(request, 'core/mesas.html', {'mesas': mesas, 'form': form})


def mesa_eliminar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        mesa.delete()
        messages.success(request, f'Mesa {mesa.numMesa} eliminada.')
    return redirect('mesas_lista')


def mesa_editar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        form = MesaForm(request.POST, instance=mesa)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mesa {mesa.numMesa} actualizada.')
            return redirect('mesas_lista')
    else:
        form = MesaForm(instance=mesa)
    return render(request, 'core/mesa_editar.html', {'form': form, 'mesa': mesa})


# ─── PLATOS ───────────────────────────────────────────────────────────────────

def platos_lista(request):
    platos = Plato.objects.all()
    form = PlatoForm()

    if request.method == 'POST':
        form = PlatoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Plato agregado correctamente!')
            return redirect('platos_lista')
        else:
            messages.error(request, 'Error al agregar el plato.')

    return render(request, 'core/platos.html', {'platos': platos, 'form': form})


def plato_eliminar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        plato.delete()
        messages.success(request, f'Plato "{plato.nombre}" eliminado.')
    return redirect('platos_lista')


def plato_editar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        form = PlatoForm(request.POST, instance=plato)
        if form.is_valid():
            form.save()
            messages.success(request, f'Plato "{plato.nombre}" actualizado.')
            return redirect('platos_lista')
    else:
        form = PlatoForm(instance=plato)
    return render(request, 'core/plato_editar.html', {'form': form, 'plato': plato})


# ─── MENÚS ────────────────────────────────────────────────────────────────────

def menus_lista(request):
    menus = Menu.objects.prefetch_related('menu_platos__idPlato').all()
    form = MenuForm()
    platos = Plato.objects.all()

    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save()
            # Guardar los platos seleccionados
            platos_ids = request.POST.getlist('platos')
            for plato_id in platos_ids:
                plato = Plato.objects.get(pk=plato_id)
                MenuPlato.objects.create(
                    idMenu=menu,
                    idPlato=plato,
                    nombre=plato.nombre,
                    descripcion=plato.descripcion,
                    precio=plato.precio,
                )
            messages.success(request, '¡Menú agregado correctamente!')
            return redirect('menus_lista')
        else:
            messages.error(request, 'Error al agregar el menú.')

    return render(request, 'core/menus.html', {
        'menus': menus,
        'form': form,
        'platos': platos,
    })


def menu_eliminar(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        menu.delete()
        messages.success(request, f'Menú "{menu.nombre}" eliminado.')
    return redirect('menus_lista')


def menu_editar(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    platos = Plato.objects.all()
    platos_actuales = menu.menu_platos.values_list('idPlato__pk', flat=True)

    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            # Eliminar platos anteriores y agregar los nuevos
            menu.menu_platos.all().delete()
            platos_ids = request.POST.getlist('platos')
            for plato_id in platos_ids:
                plato = Plato.objects.get(pk=plato_id)
                MenuPlato.objects.create(
                    idMenu=menu,
                    idPlato=plato,
                    nombre=plato.nombre,
                    descripcion=plato.descripcion,
                    precio=plato.precio,
                )
            messages.success(request, f'Menú "{menu.nombre}" actualizado.')
            return redirect('menus_lista')
    else:
        form = MenuForm(instance=menu)

    return render(request, 'core/menu_editar.html', {
        'form': form,
        'menu': menu,
        'platos': platos,
        'platos_actuales': list(platos_actuales),
    })