from django.db import migrations


def backfill_suite_execution_logs(apps, schema_editor):
    Suite = apps.get_model('suite', 'Suite')
    RunResult = apps.get_model('suite', 'RunResult')
    SuiteExecutionLog = apps.get_model('suite', 'SuiteExecutionLog')

    for suite in Suite.objects.all().iterator():
        suite_results = RunResult.objects.filter(suite_id=suite.id).order_by('created_at', 'id')
        if not suite_results.exists():
            continue

        cron_results = []
        webhook_results = []
        manual_results = []
        for result in suite_results:
            source = (result.trigger_source or 'manual').lower()
            if source == 'cron':
                cron_results.append(result)
            elif source == 'webhook':
                webhook_results.append(result)
            else:
                manual_results.append(result)

        cron_key = suite.cron or 'cron:legacy'
        if cron_results:
            SuiteExecutionLog.objects.update_or_create(
                suite_id=suite.id,
                strategy_type='cron',
                strategy_key=cron_key,
                defaults={
                    'strategy_label': f'定时策略：{suite.cron or "历史定时策略"}',
                    'strategy_payload': {'cron': suite.cron or ''},
                    'execution_count': len(cron_results),
                    'latest_result_id': cron_results[-1].id,
                    'recent_result_ids': [r.id for r in reversed(cron_results[-20:])],
                    'first_triggered_at': cron_results[0].created_at,
                    'last_triggered_at': cron_results[-1].created_at,
                }
            )

        webhook_key = suite.hook_key or f'webhook:{suite.id}'
        if webhook_results:
            SuiteExecutionLog.objects.update_or_create(
                suite_id=suite.id,
                strategy_type='webhook',
                strategy_key=webhook_key,
                defaults={
                    'strategy_label': 'Webhook 触发',
                    'strategy_payload': {'hook_key': suite.hook_key or ''},
                    'execution_count': len(webhook_results),
                    'latest_result_id': webhook_results[-1].id,
                    'recent_result_ids': [r.id for r in reversed(webhook_results[-20:])],
                    'first_triggered_at': webhook_results[0].created_at,
                    'last_triggered_at': webhook_results[-1].created_at,
                }
            )

        for result in manual_results:
            SuiteExecutionLog.objects.update_or_create(
                suite_id=suite.id,
                strategy_type='manual',
                strategy_key=f'manual:{result.id}',
                defaults={
                    'strategy_label': '手动立即执行',
                    'strategy_payload': {},
                    'execution_count': 1,
                    'latest_result_id': result.id,
                    'recent_result_ids': [result.id],
                    'first_triggered_at': result.created_at,
                    'last_triggered_at': result.created_at,
                }
            )


class Migration(migrations.Migration):

    dependencies = [
        ('suite', '0027_suiteexecutionlog'),
    ]

    operations = [
        migrations.RunPython(backfill_suite_execution_logs, migrations.RunPython.noop),
    ]
