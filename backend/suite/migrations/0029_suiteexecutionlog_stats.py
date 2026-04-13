from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('suite', '0028_backfill_suite_execution_logs'),
    ]

    operations = [
        migrations.AddField(
            model_name='suiteexecutionlog',
            name='fail_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='suiteexecutionlog',
            name='latest_failed_result',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='suite.runresult'),
        ),
        migrations.AddField(
            model_name='suiteexecutionlog',
            name='pass_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
