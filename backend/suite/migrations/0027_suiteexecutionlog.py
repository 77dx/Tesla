from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('suite', '0026_assign_default_user_product_line'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuiteExecutionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy_type', models.CharField(choices=[('manual', '手动执行'), ('cron', '定时执行'), ('webhook', 'Webhook')], max_length=16)),
                ('strategy_key', models.CharField(max_length=255)),
                ('strategy_label', models.CharField(blank=True, default='', max_length=255)),
                ('strategy_payload', models.JSONField(blank=True, default=dict)),
                ('execution_count', models.PositiveIntegerField(default=0)),
                ('recent_result_ids', models.JSONField(blank=True, default=list)),
                ('first_triggered_at', models.DateTimeField(blank=True, null=True)),
                ('last_triggered_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('latest_result', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='suite.runresult')),
                ('suite', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='execution_logs', to='suite.suite')),
            ],
            options={
                'ordering': ['-last_triggered_at', '-id'],
                'unique_together': {('suite', 'strategy_type', 'strategy_key')},
            },
        ),
    ]
