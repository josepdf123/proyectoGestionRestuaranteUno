from django.db import migrations


def add_estado_pagado(apps, schema_editor):
    Estado = apps.get_model('core', 'Estado')
    Estado.objects.get_or_create(descripcion='Pagado')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_cierrecaja_metodo_pago_pago'),
    ]

    operations = [
        migrations.RunPython(add_estado_pagado, migrations.RunPython.noop),
    ]
