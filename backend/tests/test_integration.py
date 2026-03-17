import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tesla.settings')
django.setup()

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

from pathlib import Path
import time
from suite.models import Suite, RunResult
from suite.runner import SuiteRunner

# 获取套件 #2
suite = Suite.objects.get(id=2)
print(f'套件: {suite.name}')

# 创建 RunResult
result = RunResult.objects.create(suite=suite, project=suite.project, path='todo')
base_dir = Path('upload_yaml') / f'test_integration_{result.id}_{int(time.time())}'
base_dir.mkdir(parents=True, exist_ok=True)
result.path = str(base_dir)
result.save()

log_file = base_dir / 'log' / 'pytest.log'

# 获取用例列表
case_ids = list(suite.get_case_api_items().order_by('order').values_list('case_api_id', flat=True))
print(f'用例列表: {case_ids}')

# 执行
runner = SuiteRunner(result_id=result.id, log_file=log_file)
suite_result = runner.run(case_api_ids=case_ids)

print(f'\n=== 执行结果 ===')
print(f'总计: {suite_result.total}  通过: {suite_result.passed}  失败: {suite_result.failed}')
print(f'整体通过: {suite_result.is_pass}')
print(f'耗时: {suite_result.duration:.2f}s')
print(f'\n=== 各用例详情 ===')
for cr in suite_result.case_results:
    status = '✓' if cr['success'] else '✗'
    print(f'  {status} #{cr["case_id"]} [{cr["case_name"]}] 状态码:{cr["status_code"]} 耗时:{cr["duration"]}s')
    if cr.get('extracted'):
        print(f'     提取变量: {cr["extracted"]}')
    if cr.get('error'):
        print(f'     错误: {cr["error"]}')

print(f'\n日志文件: {log_file}')
if log_file.exists():
    print(f'日志大小: {log_file.stat().st_size} bytes')
    print('\n=== 日志内容 ===')
    print(log_file.read_text(encoding='utf-8'))
