from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case_ui', '0004_caserunhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='caserunhistory',
            name='execution_logs',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='执行日志'),
        ),
    ]
