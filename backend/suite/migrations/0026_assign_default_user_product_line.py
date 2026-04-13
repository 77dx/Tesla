from django.db import migrations


def assign_default_user_product_line(apps, schema_editor):
    ProductLine = apps.get_model('product_line', 'ProductLine')
    Suite = apps.get_model('suite', 'Suite')
    RunResult = apps.get_model('suite', 'RunResult')

    default_pl = ProductLine.objects.filter(name='用户产品线').first()
    if not default_pl:
        return

    Suite.objects.filter(product_line__isnull=True).update(product_line=default_pl)
    RunResult.objects.filter(product_line__isnull=True).update(product_line=default_pl)


class Migration(migrations.Migration):

    dependencies = [
        ('product_line', '0001_initial'),
        ('suite', '0025_remove_suite_schedule'),
    ]

    operations = [
        migrations.RunPython(assign_default_user_product_line, migrations.RunPython.noop),
    ]
