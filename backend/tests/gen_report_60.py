import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tesla.settings')
django.setup()

from pathlib import Path
from suite.models import RunResult
from suite.runner import SuiteRunner, SuiteRunResult

# 为已有的执行记录补生成 HTML 报告
result_id = 60
db = RunResult.objects.get(id=result_id)
log_file = Path(db.path) / 'log' / 'pytest.log'

# 从日志还原一个简单的 SuiteRunResult 用于生成报告
sr = SuiteRunResult(result_id)
sr.is_pass   = db.is_pass
sr.success   = True
sr.total     = 0
sr.passed    = 0
sr.failed    = 0
sr.duration  = 0.0
sr.case_results = []

runner = SuiteRunner(result_id=result_id, log_file=log_file)
runner._generate_html_report(sr)
print(f'报告已生成: {Path(db.path) / "report" / "index.html"}')
