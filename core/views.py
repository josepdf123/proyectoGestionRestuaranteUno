# core/views.py
import uuid
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import MesaForm, PlatoForm, MenuForm, MenuPlatoForm, UsuarioForm, PedidoForm
from .models import Mesa, Plato, Menu, MenuPlato, Estado, Usuario, Pedido, Rol, DetallePedido
from datetime import date, timedelta

# ─── DECORADORES DE SEGURIDAD ─────────────────────────────────────────────────

def login_requerido(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            messages.error(request, 'Debes iniciar sesión para acceder.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def rol_requerido(*roles_permitidos):
    def decorador(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.session.get('usuario_id'):
                messages.error(request, 'Debes iniciar sesión para acceder.')
                return redirect('login')
            rol_actual = request.session.get('usuario_rol', '')
            if rol_actual not in roles_permitidos:
                messages.error(request, 'No tienes permiso para acceder a esta sección.')
                return redirect('acceso_denegado')
            return view_func(request, *args, **kwargs)
        wrapper.__name__ = view_func.__name__
        return wrapper
    return decorador


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.session.get('usuario_id'):
        rol = request.session.get('usuario_rol', '')
        if rol == 'Mesero':
            return redirect('panel_mesero')
        elif rol == 'Cocinero':
            return redirect('panel_cocina')
        return redirect('mesas_lista')

    if request.method == 'POST':
        usuario_input = request.POST.get('usuario')
        contrasena_input = request.POST.get('contrasena')
        try:
            usuario = Usuario.objects.get(usuario=usuario_input, contrasena=contrasena_input)
            request.session['usuario_id'] = usuario.pk
            request.session['usuario_nombre'] = usuario.nombre
            request.session['usuario_rol'] = usuario.idRol.descripcion
            messages.success(request, f'¡Bienvenido, {usuario.nombre}!')
            rol = usuario.idRol.descripcion
            if rol == 'Administrador':
                return redirect('mesas_lista')
            elif rol == 'Mesero':
                return redirect('panel_mesero')
            elif rol == 'Cocinero':
                return redirect('panel_cocina')
            else:
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


def acceso_denegado(request):
    return render(request, 'core/acceso_denegado.html')


# ─── MESAS ────────────────────────────────────────────────────────────────────

@rol_requerido('Administrador')
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


@rol_requerido('Administrador')
def mesa_eliminar(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        mesa.delete()
        messages.success(request, f'Mesa {mesa.numMesa} eliminada.')
    return redirect('mesas_lista')


@rol_requerido('Administrador')
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

@rol_requerido('Administrador')
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


@rol_requerido('Administrador')
def plato_eliminar(request, pk):
    plato = get_object_or_404(Plato, pk=pk)
    if request.method == 'POST':
        plato.delete()
        messages.success(request, f'Plato "{plato.nombre}" eliminado.')
    return redirect('platos_lista')


@rol_requerido('Administrador')
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

@rol_requerido('Administrador')
def menus_lista(request):
    menus = Menu.objects.prefetch_related('menu_platos__idPlato').all()
    form = MenuForm()
    platos = Plato.objects.all()
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            menu = form.save()
            platos_ids = request.POST.getlist('platos')
            for plato_id in platos_ids:
                plato = Plato.objects.get(pk=plato_id)
                MenuPlato.objects.create(
                    idMenu=menu, idPlato=plato,
                    nombre=plato.nombre, descripcion=plato.descripcion, precio=plato.precio,
                )
            messages.success(request, '¡Menú agregado correctamente!')
            return redirect('menus_lista')
        else:
            messages.error(request, 'Error al agregar el menú.')
    return render(request, 'core/menus.html', {'menus': menus, 'form': form, 'platos': platos})


@rol_requerido('Administrador')
def menu_eliminar(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        menu.delete()
        messages.success(request, f'Menú "{menu.nombre}" eliminado.')
    return redirect('menus_lista')


@rol_requerido('Administrador')
def menu_editar(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    platos = Plato.objects.all()
    platos_actuales = menu.menu_platos.values_list('idPlato__pk', flat=True)
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            menu.menu_platos.all().delete()
            platos_ids = request.POST.getlist('platos')
            for plato_id in platos_ids:
                plato = Plato.objects.get(pk=plato_id)
                MenuPlato.objects.create(
                    idMenu=menu, idPlato=plato,
                    nombre=plato.nombre, descripcion=plato.descripcion, precio=plato.precio,
                )
            messages.success(request, f'Menú "{menu.nombre}" actualizado.')
            return redirect('menus_lista')
    else:
        form = MenuForm(instance=menu)
    return render(request, 'core/menu_editar.html', {
        'form': form, 'menu': menu, 'platos': platos, 'platos_actuales': list(platos_actuales),
    })


# ─── USUARIOS ─────────────────────────────────────────────────────────────────

@rol_requerido('Administrador')
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


@rol_requerido('Administrador')
def usuario_eliminar(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, f'Usuario "{usuario.usuario}" eliminado.')
    return redirect('usuarios_lista')


@rol_requerido('Administrador')
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


# ─── PANEL MESERO ─────────────────────────────────────────────────────────────

@rol_requerido('Administrador', 'Mesero')
def panel_mesero(request):
    mesas = Mesa.objects.select_related('estado').all()
    estado_listo = Estado.objects.filter(descripcion__iexact='listo').first()
    pedidos_listos = Pedido.objects.filter(idEstado=estado_listo).select_related('idMesa') if estado_listo else []
    return render(request, 'core/mesero/panel.html', {
        'mesas': mesas,
        'pedidos_listos': pedidos_listos,
    })


@rol_requerido('Administrador', 'Mesero')
def mesa_pedido(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    platos = Plato.objects.all()
    estados = Estado.objects.all()

    pedido_activo = mesa.pedidos.filter(
        idEstado__descripcion__iexact='pendiente'
    ).first() or mesa.pedidos.filter(
        idEstado__descripcion__iexact='en cocina'
    ).first() or mesa.pedidos.filter(
        idEstado__descripcion__iexact='listo'
    ).first()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'cambiar_estado':
            nuevo_estado_desc = request.POST.get('estado_mesa')
            estado_obj = Estado.objects.filter(descripcion__iexact=nuevo_estado_desc).first()
            if estado_obj:
                mesa.estado = estado_obj
                mesa.save()
                messages.success(request, f'Estado de Mesa {mesa.numMesa} actualizado.')
            return redirect('mesa_pedido', pk=pk)

        elif action == 'agregar_plato':
            plato_id = request.POST.get('plato_id')
            cantidad = int(request.POST.get('cantidad', 1))
            notas = request.POST.get('notas', '')
            plato = get_object_or_404(Plato, pk=plato_id)

            if not pedido_activo:
                estado_ocupada = Estado.objects.filter(descripcion__iexact='ocupada').first()
                if estado_ocupada:
                    mesa.estado = estado_ocupada
                    mesa.save()
                usuario = Usuario.objects.get(pk=request.session['usuario_id'])
                estado_pendiente = Estado.objects.filter(descripcion__iexact='pendiente').first()
                pedido_activo = Pedido.objects.create(
                    idMesa=mesa,
                    idUsuario=usuario,
                    idEstado=estado_pendiente,
                )

            DetallePedido.objects.create(
                pedido=pedido_activo,
                plato=plato,
                cantidad=cantidad,
                notas=notas,
                precio_unitario=plato.precio,
            )
            pedido_activo.calcular_total()
            messages.success(request, f'"{plato.nombre}" agregado al pedido.')
            return redirect('mesa_pedido', pk=pk)

        elif action == 'eliminar_detalle':
            detalle_id = request.POST.get('detalle_id')
            detalle = get_object_or_404(DetallePedido, pk=detalle_id)
            detalle.delete()
            if pedido_activo:
                pedido_activo.calcular_total()
            messages.success(request, 'Platillo eliminado del pedido.')
            return redirect('mesa_pedido', pk=pk)

        elif action == 'enviar_cocina':
            if pedido_activo:
                estado_cocina = Estado.objects.filter(descripcion__iexact='en cocina').first()
                if estado_cocina:
                    pedido_activo.idEstado = estado_cocina
                    pedido_activo.save()
                messages.success(request, f'¡Pedido de Mesa {mesa.numMesa} enviado a cocina!')
            return redirect('panel_mesero')

        elif action == 'entregar_pedido':
            if pedido_activo:
                estado_entregado = Estado.objects.filter(descripcion__iexact='entregado').first()
                if estado_entregado:
                    pedido_activo.idEstado = estado_entregado
                    pedido_activo.save()
                estado_disponible = Estado.objects.filter(descripcion__iexact='disponible').first()
                if estado_disponible:
                    mesa.estado = estado_disponible
                    mesa.save()
                messages.success(request, f'¡Pedido de Mesa {mesa.numMesa} entregado! Mesa liberada.')
            return redirect('panel_mesero')

    return render(request, 'core/mesero/mesa_pedido.html', {
        'mesa': mesa,
        'platos': platos,
        'pedido': pedido_activo,
        'estados': estados,
    })


# ─── PANEL COCINA ─────────────────────────────────────────────────────────────

@rol_requerido('Administrador', 'Mesero', 'Cocinero')
def panel_cocina(request):
    estado_cocina = Estado.objects.filter(descripcion__iexact='en cocina').first()
    pedidos = Pedido.objects.filter(idEstado=estado_cocina).prefetch_related('detalles__plato').select_related('idMesa') if estado_cocina else []

    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        pedido = get_object_or_404(Pedido, pk=pedido_id)
        estado_listo = Estado.objects.filter(descripcion__iexact='listo').first()
        if estado_listo:
            pedido.idEstado = estado_listo
            pedido.save()
        messages.success(request, f'Pedido de Mesa {pedido.idMesa.numMesa} marcado como listo.')
        return redirect('panel_cocina')

    return render(request, 'core/cocina/panel.html', {'pedidos': pedidos})

#-------REPORTES-------
@rol_requerido('Administrador')
def reportes(request):
    hoy = date.today()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    pedidos_entregados = Pedido.objects.filter(
        idEstado__descripcion__iexact='entregado'
    ).select_related('idMesa', 'idUsuario').prefetch_related('detalles__plato')

    # Diario
    pedidos_hoy = pedidos_entregados.filter(fecha__date=hoy)
    total_hoy = sum(p.total for p in pedidos_hoy)

    # Semanal
    pedidos_semana = pedidos_entregados.filter(fecha__date__gte=inicio_semana)
    total_semana = sum(p.total for p in pedidos_semana)

    # Mensual
    pedidos_mes = pedidos_entregados.filter(fecha__date__gte=inicio_mes)
    total_mes = sum(p.total for p in pedidos_mes)

    # Por camarero (hoy)
    meseros = Usuario.objects.filter(idRol__descripcion__iexact='mesero')
    reporte_camareros = []
    for mesero in meseros:
        pedidos_mesero = pedidos_entregados.filter(idUsuario=mesero, fecha__date=hoy)
        mesas = pedidos_mesero.values('idMesa').distinct().count()
        total = sum(p.total for p in pedidos_mesero)
        reporte_camareros.append({
            'nombre': f"{mesero.nombre} {mesero.apellido}",
            'mesas': mesas,
            'pedidos': pedidos_mesero.count(),
            'total': total,
        })

    return render(request, 'core/reportes.html', {
        'hoy': hoy,
        'pedidos_hoy': pedidos_hoy,
        'total_hoy': total_hoy,
        'pedidos_semana': pedidos_semana,
        'total_semana': total_semana,
        'pedidos_mes': pedidos_mes,
        'total_mes': total_mes,
        'reporte_camareros': reporte_camareros,
        'inicio_semana': inicio_semana,
        'inicio_mes': inicio_mes,
    })