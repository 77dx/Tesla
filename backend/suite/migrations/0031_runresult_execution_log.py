from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('suite', '0030_backfill_execution_log_stats'),
    ]

    operations = [
        migrations.AddField(
            model_name='runresult',
            name='execution_log',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='run_results', to='suite.suiteexecutionlog'),
        ),
    ]
