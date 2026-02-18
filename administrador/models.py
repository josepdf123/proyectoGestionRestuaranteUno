from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
#contraseña es contraseña

class Menu(models.Model):
    nombre = models.CharField(max_length=150, default="NN")
    tipo = models.CharField(max_length=100, default="normal")

class Usuario(AbstractUser):
    rolOpcion = [
        ('admin', 'Administrador'),
        ('cajero', 'Cajero'),
        ('mesero', 'Mesero'),
        ('cocina', 'Personal de Cocina'),
    ]

    rol = models.CharField(max_length=20, choices=rolOpcion, default='mesero')

    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name()} - {self.get_rol_display()}"
    

    @property
    def es_admin(self):
        return self.rol == 'admin'

    @property
    def es_mesero(self):
        return self.rol == 'mesero'

    @property
    def es_cajero(self):
        return self.rol == 'cajero'

    @property
    def es_cocina(self):
        return self.rol == 'cocina'

class Plato(models.Model):
    nombre = models.CharField(max_length=150, default='vacio')
    descripcion = models.TextField()
    precio = models.FloatField(default=0.0)
    creador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null = True, blank = True, related_name='creadorPlato')

class Mesa(models.Model):
    estadosOpcion = [
        ('ocupado', 'Ocupado'), 
        ('disponible', 'Disponible'), 
        ('reservada', 'Reservada'),
        ('sinServicio', 'Fuera de servicio')
    ]
    estado = models.CharField(max_length=20, choices=estadosOpcion, default='disponible')
    creador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null = True, blank = True, related_name='creadorMesa')
    numero_mesa = models.IntegerField(unique=True)
    capacidad = models.IntegerField(default=4)

    def __str__(self):
        return f"Mesa {self.numero_mesa} - Capacidad: {self.capacidad} - {self.get_estado_display()}"


class Pedido(models.Model):
    estadoOpcion = [
        ('pendiente', 'Pendiente'),
        ('preparando' , 'Preparando'),
        ('finalizado' , 'Finalizado'),
        ('cancelado', 'Cancelado')
    ]
    estado = models.CharField(max_length=30, choices=estadoOpcion, default="pendiente")
    mesero = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null = True, blank = True, related_name='pedidoAtendido')
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, related_name='pedidos')
    fechaCreacion = models.DateTimeField(auto_now_add=True)

class MenuPlato(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='platos')
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name='menus')

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    plato = models.ForeignKey(Plato, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField(default=1)
    precioUnitario = models.FloatField() 
    notaCliente = models.TextField()
