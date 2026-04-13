from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suite', '0023_suitenode'),
    ]

    operations = [
        migrations.AddField(
            model_name='suite',
            name='cron_next_run_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='下次执行时间'),
        ),
    ]
