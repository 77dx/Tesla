from django.core.management.base import BaseCommand

from suite.models import Suite


class Command(BaseCommand):
    help = '轮询触发套件 cron 计划任务'

    def add_arguments(self, parser):
        parser.add_argument('--once', action='store_true', help='仅执行一次调度扫描')
        parser.add_argument('--sleep', type=int, default=30, help='轮询间隔秒数，默认 30 秒')

    def handle(self, *args, **options):
        run_once = options['once']
        sleep_seconds = max(int(options['sleep'] or 30), 5)

        self.stdout.write(self.style.SUCCESS(f'套件调度器已启动，轮询间隔 {sleep_seconds} 秒'))
        while True:
            triggered = Suite.dispatch_due_cron_suites()
            if triggered:
                self.stdout.write(self.style.SUCCESS(f'已触发 {triggered} 个到期套件'))
            if run_once:
                break
            import time
            time.sleep(sleep_seconds)
