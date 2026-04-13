from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('suite', '0024_suite_cron_next_run_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='suite',
            name='schedule',
        ),
    ]
