import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tesla.settings')
django.setup()

import logging, time
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

from pathlib import Path
from suite.models import Suite, RunResult
from suite.runner import SuiteRunner

suite = Suite.objects.get(id=2)
result = RunResult.objects.create(suite=suite, project=suite.project, path='todo')
base_dir = Path('upload_yaml') / f'test_allure_{result.id}_{int(time.time())}'
base_dir.mkdir(parents=True, exist_ok=True)
result.path = str(base_dir)
result.save()

log_file = base_dir / 'log' / 'pytest.log'
case_ids = list(suite.get_case_api_items().order_by('order').values_list('case_api_id', flat=True))
print(f'套件: {suite.name}, 用例: {case_ids}')

runner = SuiteRunner(result_id=result.id, log_file=log_file)
suite_result = runner.run(case_api_ids=case_ids)

report_path = base_dir / 'report' / 'index.html'
print(f'\n报告路径: {report_path}')
print(f'报告存在: {report_path.exists()}')
if report_path.exists():
    url = f'/api/suite/static/{base_dir.name}/report/index.html'
    print(f'访问地址: http://localhost:8000{url}')
