from django.db import migrations


def ensure_suite_schedule_column(apps, schema_editor):
    connection = schema_editor.connection
    table_name = 'suite_suite'

    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table_name)
        existing_columns = {col.name for col in description}

        if 'schedule_id' in existing_columns:
            return

        if connection.vendor == 'sqlite':
            cursor.execute('ALTER TABLE "suite_suite" ADD COLUMN "schedule_id" bigint NULL')
        else:
            cursor.execute('ALTER TABLE "suite_suite" ADD COLUMN "schedule_id" bigint NULL')


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('suite', '0014_add_mock_rules'),
    ]

    operations = [
        migrations.RunPython(ensure_suite_schedule_column, noop_reverse),
    ]
