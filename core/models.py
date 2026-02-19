# core/models.py

from django.db import models


class Estado(models.Model):
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return self.descripcion

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"


class Mesa(models.Model):
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='mesas')
    numMesa = models.IntegerField(unique=True, verbose_name="Número de Mesa")
    capacidad = models.IntegerField()

    def __str__(self):
        return f"Mesa {self.numMesa}"

    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"
        ordering = ['numMesa']


class Plato(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Plato"
        verbose_name_plural = "Platos"


class Menu(models.Model):
    TIPO_CHOICES = [
        ('desayuno', 'Desayuno'),
        ('almuerzo', 'Almuerzo'),
        ('cena', 'Cena'),
        ('especial', 'Especial'),
    ]
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Menú"
        verbose_name_plural = "Menús"


class MenuPlato(models.Model):
    idMenu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_platos')
    idPlato = models.ForeignKey(Plato, on_delete=models.CASCADE, related_name='menu_platos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} - {self.idMenu}"

    class Meta:
        verbose_name = "Menú Plato"
        verbose_name_plural = "Menú Platos"