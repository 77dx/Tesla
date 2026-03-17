# 测试套件执行使用示例

## 基本使用

### 1. 执行单个测试套件

```python
from suite.models import Suite

# 获取测试套件
suite = Suite.objects.get(id=1)

# 执行套件(异步,立即返回)
result = suite.run()

print(f"执行结果 ID: {result.id}")
print(f"执行路径: {result.path}")
print(f"初始状态: {result.get_status_display()}")

# 稍后查询执行状态
result.refresh_from_db()
print(f"当前状态: {result.get_status_display()}")
print(f"是否通过: {result.is_pass}")
```

### 2. 批量执行多个套件

```python
from suite.models import Suite

# 获取多个套件
suites = Suite.objects.filter(project_id=1)

# 并发执行所有套件
results = []
for suite in suites:
    result = suite.run()
    results.append(result)
    print(f"已提交套件: {suite.name}, 结果ID: {result.id}")

print(f"共提交 {len(results)} 个套件到执行队列")
```

### 3. 查询执行结果

```python
from suite.models import RunResult

# 查询最近的执行结果
recent_results = RunResult.objects.all().order_by('-id')[:10]

for result in recent_results:
    print(f"套件: {result.suite.name}")
    print(f"状态: {result.get_status_display()}")
    print(f"通过: {result.is_pass}")
    print(f"路径: {result.path}")
    print(f"报告: {result.path}/report/index.html")
    print("-" * 50)
```

### 4. 直接调用服务函数(高级用法)

```python
from README_CURSOR_LOG.services import run_suite_tests
from pathlib import Path

# 准备测试文件目录
test_dir = Path("my_tests")
test_dir.mkdir(exist_ok=True)

# 执行测试
result = run_suite_tests(
    result_id=123,
    yaml_files_dir=str(test_dir),
    report_base_dir=str(test_dir)
)

if result["success"]:
    print(f"测试通过: {result['is_pass']}")
    print(f"报告路径: {result['report_path']}")
else:
    print(f"执行失败: {result['error']}")
```

## 执行状态说明

| 状态码 | 状态名称 | 说明 |
|--------|----------|------|
| 0 | 初始化 | RunResult 刚创建 |
| 1 | 准备开始 | 测试用例已生成,准备执行 |
| 2 | 正在执行 | pytest 正在运行 |
| 3 | 正在生成报告 | pytest 完成,正在生成 Allure 报告 |
| 4 | 执行完毕 | 所有步骤完成 |
| -1 | 执行出错 | 执行过程中出现错误 |

## 目录结构

每次执行都会创建独立的目录:

```
upload_yaml/
└── result_{result_id}_{timestamp}/
    ├── test_*.yaml           # 生成的测试用例文件
    ├── results/              # pytest 执行结果
    │   ├── *.json
    │   └── *.xml
    └── report/               # Allure 报告
        ├── index.html
        └── ...
```

## 查看测试报告

### 方式1: 直接打开 HTML 文件

```bash
open upload_yaml/result_123_1234567890/report/index.html
```

### 方式2: 通过 Django 静态文件服务

如果配置了静态文件服务,可以通过浏览器访问:

```
http://localhost:8000/media/upload_yaml/result_123_1234567890/report/index.html
```

## 定时任务执行

### 创建定时执行的套件

```python
from suite.models import Suite

suite = Suite.objects.get(id=1)
suite.run_type = Suite.RunType.CRON
suite.cron = "0 2 * * *"  # 每天凌晨2点执行
suite.save()

print(f"已设置定时任务: {suite.schedule}")
```

### Webhook 触发

```python
from suite.models import Suite

suite = Suite.objects.get(id=1)
suite.run_type = Suite.RunType.WebHook
suite.save()

print(f"Webhook 密钥: {suite.hook_key}")
print(f"Webhook URL: http://your-domain/api/suite/webhook/{suite.hook_key}/")
```

## 监控执行进度

```python
import time
from suite.models import RunResult

result_id = 123
result = RunResult.objects.get(id=result_id)

# 轮询检查状态
while result.status not in [result.RunStatus.Done, result.RunStatus.Error]:
    time.sleep(2)
    result.refresh_from_db()
    print(f"当前状态: {result.get_status_display()}")

print(f"最终结果: {'通过' if result.is_pass else '失败'}")
```

## 错误处理

```python
from suite.models import Suite, RunResult

try:
    suite = Suite.objects.get(id=1)
    result = suite.run()
    
    # 等待执行完成
    import time
    time.sleep(10)
    
    result.refresh_from_db()
    
    if result.status == result.RunStatus.Error:
        print("执行出错,请检查日志")
    elif not result.is_pass:
        print("测试未通过,请查看报告")
    else:
        print("测试通过!")
        
except Suite.DoesNotExist:
    print("套件不存在")
except Exception as e:
    print(f"发生错误: {str(e)}")
```

## 清理旧报告

```python
from pathlib import Path
import shutil
from datetime import datetime, timedelta

# 清理7天前的报告
upload_dir = Path("../upload_yaml")
cutoff_time = datetime.now() - timedelta(days=7)

for result_dir in upload_dir.glob("result_*"):
    if result_dir.is_dir():
        # 从目录名提取时间戳
        try:
            timestamp = int(result_dir.name.split("_")[-1])
            dir_time = datetime.fromtimestamp(timestamp)

            if dir_time < cutoff_time:
                print(f"删除旧报告: {result_dir}")
                shutil.rmtree(result_dir)
        except:
            pass
```

## 常见问题

### Q1: 如何同时执行多个套件?

A: 直接调用多个 `suite.run()` 即可,系统会自动使用线程池并发执行。

### Q2: 如何确保数据不会互相干扰?

A: 每次执行都会创建带有唯一 ID 和时间戳的目录,保证数据隔离。

### Q3: 如何查看执行日志?

A: 查看 Django 日志文件,所有执行过程都有详细的日志记录。

### Q4: 可以同时执行多少个套件?

A: 默认线程池大小为 6,可以在 `suite/models.py` 中调整 `ThreadPoolExecutor(max_workers=6)`。

### Q5: 报告生成失败怎么办?

A: 检查:
1. allure 命令是否可用
2. results 目录是否有测试结果文件
3. 磁盘空间是否充足
4. 查看日志获取详细错误信息
