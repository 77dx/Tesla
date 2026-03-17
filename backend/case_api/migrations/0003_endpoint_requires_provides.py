from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("case_api", "0002_alter_case_project"),
    ]

    operations = [
        migrations.AddField(
            model_name="endpoint",
            name="requires",
            field=models.JSONField(blank=True, null=True, verbose_name="依赖变量"),
        ),
        migrations.AddField(
            model_name="endpoint",
            name="provides",
            field=models.JSONField(blank=True, null=True, verbose_name="产出变量"),
        ),
    ]

