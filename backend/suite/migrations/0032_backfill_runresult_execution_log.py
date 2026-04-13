from django.db import migrations


def backfill_runresult_execution_log(apps, schema_editor):
    RunResult = apps.get_model('suite', 'RunResult')
    SuiteExecutionLog = apps.get_model('suite', 'SuiteExecutionLog')

    for log in SuiteExecutionLog.objects.all().iterator():
        if log.strategy_type == 'manual' and log.latest_result_id:
            RunResult.objects.filter(id=log.latest_result_id).update(execution_log_id=log.id)
        elif log.strategy_type == 'cron':
            RunResult.objects.filter(suite_id=log.suite_id, trigger_source='cron').update(execution_log_id=log.id)
        elif log.strategy_type == 'webhook':
            RunResult.objects.filter(suite_id=log.suite_id, trigger_source='webhook').update(execution_log_id=log.id)


class Migration(migrations.Migration):

    dependencies = [
        ('suite', '0031_runresult_execution_log'),
    ]

    operations = [
        migrations.RunPython(backfill_runresult_execution_log, migrations.RunPython.noop),
    ]
