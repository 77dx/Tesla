from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("suite", "0005_add_environment_urls"),
    ]

    operations = [
        # 1. 先用 RunSQL 删除旧表重建（SQLite 不支持 DROP COLUMN，用重建方式）
        migrations.RunSQL(
            sql="""
                CREATE TABLE suite_globalvariable_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    environment_id INTEGER NOT NULL REFERENCES suite_environment(id) ON DELETE CASCADE,
                    key VARCHAR(64) NOT NULL,
                    value VARCHAR(1024) NOT NULL DEFAULT '',
                    description VARCHAR(250) NOT NULL DEFAULT '',
                    created_at DATETIME NULL,
                    UNIQUE(environment_id, key)
                );
                DROP TABLE IF EXISTS suite_globalvariable;
                ALTER TABLE suite_globalvariable_new RENAME TO suite_globalvariable;
            """,
            reverse_sql="""
                CREATE TABLE suite_globalvariable_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    key VARCHAR(64) NOT NULL,
                    value VARCHAR(1024) NOT NULL DEFAULT '',
                    description VARCHAR(250) NOT NULL DEFAULT '',
                    created_at DATETIME NULL,
                    UNIQUE(project_id, key)
                );
                DROP TABLE IF EXISTS suite_globalvariable;
                ALTER TABLE suite_globalvariable_new RENAME TO suite_globalvariable;
            """,
        ),
        # 2. 同步 Django state
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name="globalvariable",
                    name="project",
                ),
                migrations.AddField(
                    model_name="globalvariable",
                    name="environment",
                    field=models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="global_variables",
                        to="suite.environment",
                        verbose_name="所属环境",
                    ),
                    preserve_default=False,
                ),
                migrations.AlterUniqueTogether(
                    name="globalvariable",
                    unique_together={("environment", "key")},
                ),
            ],
        ),
    ]
