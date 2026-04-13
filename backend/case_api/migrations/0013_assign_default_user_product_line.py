from django.db import migrations


def assign_default_user_product_line(apps, schema_editor):
    ProductLine = apps.get_model('product_line', 'ProductLine')
    Endpoint = apps.get_model('case_api', 'Endpoint')
    Case = apps.get_model('case_api', 'Case')

    default_pl = ProductLine.objects.filter(name='用户产品线').first()
    if not default_pl:
        return

    Endpoint.objects.filter(product_line__isnull=True).update(product_line=default_pl)
    Case.objects.filter(product_line__isnull=True).update(product_line=default_pl)


class Migration(migrations.Migration):

    dependencies = [
        ('product_line', '0001_initial'),
        ('case_api', '0012_casenode'),
    ]

    operations = [
        migrations.RunPython(assign_default_user_product_line, migrations.RunPython.noop),
    ]
