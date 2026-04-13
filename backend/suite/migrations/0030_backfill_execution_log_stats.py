from django.db import migrations


def backfill_execution_log_stats(apps, schema_editor):
    RunResult = apps.get_model('suite', 'RunResult')
    SuiteExecutionLog = apps.get_model('suite', 'SuiteExecutionLog')

    done_status = 4

    for log in SuiteExecutionLog.objects.all().iterator():
        ids = log.recent_result_ids or []
        result_ids = list(RunResult.objects.filter(suite_id=log.suite_id).filter(id__in=ids).values_list('id', flat=True))
        if log.strategy_type == 'manual' and log.latest_result_id:
            qs = RunResult.objects.filter(id=log.latest_result_id)
        elif log.strategy_type == 'cron':
            qs = RunResult.objects.filter(suite_id=log.suite_id, trigger_source='cron')
        elif log.strategy_type == 'webhook':
            qs = RunResult.objects.filter(suite_id=log.suite_id, trigger_source='webhook')
        else:
            qs = RunResult.objects.filter(id__in=result_ids)

        ordered = list(qs.order_by('created_at', 'id'))
        pass_count = sum(1 for r in ordered if r.status == done_status and r.is_pass)
        fail_count = max(len(ordered) - pass_count, 0)
        latest_failed = None
        for r in reversed(ordered):
            if not (r.status == done_status and r.is_pass):
                latest_failed = r
                break

        log.execution_count = len(ordered)
        log.pass_count = pass_count
        log.fail_count = fail_count
        log.latest_failed_result_id = latest_failed.id if latest_failed else None
        log.save(update_fields=['execution_count', 'pass_count', 'fail_count', 'latest_failed_result'])


class Migration(migrations.Migration):

    dependencies = [
        ('suite', '0029_suiteexecutionlog_stats'),
    ]

    operations = [
        migrations.RunPython(backfill_execution_log_stats, migrations.RunPython.noop),
    ]
