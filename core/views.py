# core/views.py
import uuid
from django.core.mail import send_mail
from django.conf import settings as django_settings


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import MesaForm, PlatoForm, MenuForm, MenuPlatoForm, UsuarioForm, PedidoForm
from .models import Mesa, Plato, Menu, MenuPlato, Estado, Usuario, Pedido, Rol# ─── MESAS ────────────────────────────────────────────────────────────────────

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
    
    
    # ─── USUARIOS ─────────────────────────────────────────────────────────────────

def usuarios_lista(request):
    usuarios = Usuario.objects.select_related('idRol').all()
    form = UsuarioForm()

    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Usuario agregado correctamente!')
            return redirect('usuarios_lista')
        else:
            messages.error(request, 'Error al agregar el usuario.')

    return render(request, 'core/usuarios.html', {'usuarios': usuarios, 'form': form})


def usuario_eliminar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, f'Usuario "{usuario.usuario}" eliminado.')
    return redirect('usuarios_lista')


def usuario_editar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario.usuario}" actualizado.')
            return redirect('usuarios_lista')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'core/usuario_editar.html', {'form': form, 'usuario': usuario})


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.method == 'POST':
        usuario_input = request.POST.get('usuario')
        contrasena_input = request.POST.get('contrasena')

        try:
            usuario = Usuario.objects.get(usuario=usuario_input, contrasena=contrasena_input)
            request.session['usuario_id'] = usuario.pk
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_rol'] = usuario.idRol.descripcion
            messages.success(request, f'¡Bienvenido, {usuario.nombre}!')
            return redirect('mesas_lista')
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'core/login.html')


def logout_view(request):
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


def recuperar_contrasena(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        try:
            usuario = Usuario.objects.get(correo=correo)
            token = str(uuid.uuid4())
            usuario.token_recuperacion = token
            usuario.save()

            enlace = request.build_absolute_uri(f'/reset-password/{token}/')
            send_mail(
                subject='Recuperación de contraseña - Restaurante',
                message=f'Hola {usuario.nombre},\n\nHaz clic en el siguiente enlace para restablecer tu contraseña:\n{enlace}\n\nSi no solicitaste esto, ignora este correo.',
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[correo],
            )
            messages.success(request, 'Te enviamos un correo con el enlace de recuperación.')
        except Usuario.DoesNotExist:
            messages.error(request, 'No existe una cuenta con ese correo.')

    return render(request, 'core/recuperar_contrasena.html')


def reset_password(request, token):
    try:
        usuario = Usuario.objects.get(token_recuperacion=token)
    except Usuario.DoesNotExist:
        messages.error(request, 'El enlace no es válido o ya fue usado.')
        return redirect('login')

    if request.method == 'POST':
        nueva = request.POST.get('contrasena')
        confirmar = request.POST.get('confirmar')
        if nueva == confirmar:
            usuario.contrasena = nueva
            usuario.token_recuperacion = None
            usuario.save()
            messages.success(request, '¡Contraseña actualizada! Ya puedes iniciar sesión.')
            return redirect('login')
        else:
            messages.error(request, 'Las contraseñas no coinciden.')

    return render(request, 'core/reset_password.html', {'token': token})