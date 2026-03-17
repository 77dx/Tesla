# Tesla 测试平台 - Suite和Result模块详细说明

## 模块概述

Suite（测试套件）和Result（执行结果）模块是Tesla测试平台的核心功能，负责组织测试用例、执行测试、生成报告和管理执行结果。

## 核心特性

### 1. 异步执行
- 使用 **Celery** 任务队列实现异步执行
- 提交测试后立即返回，不阻塞用户操作
- 支持后台长时间运行的测试任务

### 2. 并发执行
- 支持多个测试套件同时执行
- 使用线程池控制并发数量（默认6个）
- Celery Worker可水平扩展，提高并发能力

### 3. 数据隔离
- 每次执行创建独立的目录：`result_{result_id}_{timestamp}/`
- 目录名包含：
  - `result_id`: 数据库主键，确保不同执行记录的目录不同
  - `timestamp`: Unix时间戳，确保同一记录多次执行的目录不同
- 测试文件、执行结果、报告完全隔离，互不干扰

### 4. DAG依赖调度
- 支持接口之间的依赖关系（requires/provides）
- 自动构建依赖图（DAG）
- 按依赖顺序分波次执行
- 检测循环依赖，避免死锁

### 5. 状态跟踪
- 实时跟踪执行状态：
  - `0`: 初始化
  - `1`: 准备开始
  - `2`: 正在执行
  - `3`: 生成报告
  - `4`: 执行完毕
  - `-1`: 执行出错

## 数据模型

### Suite（测试套件）

```python
class Suite(models.Model):
    name = models.CharField("套件名称", max_length=32)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.CharField('套件描述', max_length=250)
    
    # 关联的测试用例
    case_api_list = models.ManyToManyField(CaseAPI)
    case_ui_list = models.ManyToManyField(CaseUI)
    
    # 运行类型
    run_type = models.CharField(
        "运行类型", 
        choices=RunType.choices, 
        default=RunType.ONCE
    )
    # O: 单次执行（手动触发）
    # C: 计划任务（Cron定时）
    # W: Webhook（外部触发）
    
    cron = models.CharField("cron表达式", max_length=30)
    hook_key = models.CharField("webhook密钥", max_length=255)
```

### RunResult（执行结果）

```python
class RunResult(models.Model):
    suite = models.ForeignKey(Suite, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    
    path = models.CharField("用例路径", max_length=255)
    is_pass = models.BooleanField("测试通过", default=False)
    
    status = models.IntegerField(
        "执行状态", 
        choices=RunStatus.choices, 
        default=RunStatus.Init
    )
```

## 执行流程

### 1. 提交执行

```python
# 前端调用
POST /api/suite/suite/{id}/run/
{
    "endpoint_ids": [1, 2, 3],  # 可选，指定要执行的接口
    "context": {"env": "test"}   # 可选，初始上下文
}

# 返回
{
    "result_id": 123
}
```

### 2. 创建执行记录

```python
# Suite.run() 方法
result = RunResult.objects.create(
    suite=self,
    project=self.project,
    path="todo"  # 临时值
)
```

### 3. 创建独立目录

```python
# 生成唯一目录名
dir_name = f"result_{result.id}_{int(time.time())}"
path = Path('upload_yaml') / dir_name
path.mkdir(parents=True, exist_ok=True)

# 更新路径
result.path = str(path)
result.status = RunStatus.Ready
result.save()
```

### 4. 提交Celery任务

```python
from suite.tasks import start_suite_dag

# 异步执行
start_suite_dag.delay(
    result.id, 
    endpoint_ids, 
    initial_context
)
```

### 5. DAG调度执行

```python
# tasks.py

@shared_task
def start_suite_dag(result_id, endpoint_ids, initial_context):
    """
    1. 初始化Redis上下文
    2. 构建依赖图
    3. 检测循环依赖
    4. 开始第一波执行
    """
    
@shared_task
def schedule_next_wave(result_id):
    """
    1. 加载DAG状态
    2. 找出可执行的节点（依赖已满足）
    3. 提交执行
    4. 等待完成后调度下一波
    """
    
@shared_task
def execute_endpoint_node(result_id, endpoint_id):
    """
    1. 生成YAML测试文件
    2. 执行pytest
    3. 收集Allure结果
    """
    
@shared_task
def dag_wave_complete(results, result_id, executed):
    """
    1. 收集本波执行结果
    2. 更新DAG状态
    3. 触发下一波
    """
    
@shared_task
def finalize_suite_run(result_id):
    """
    1. 合并Allure结果
    2. 生成HTML报告
    3. 更新最终状态
    """
```

### 6. 生成报告

```python
# 合并所有endpoint的结果
results_dir = base_dir / "results"
for sub in (base_dir / "results_raw").iterdir():
    for f in sub.iterdir():
        shutil.copy2(f, results_dir / f.name)

# 生成Allure报告
subprocess.run([
    "allure", "generate", 
    str(results_dir), 
    "-o", str(report_dir)
])
```

### 7. 查看结果

```python
# 获取执行结果
GET /api/suite/runresult/{id}/

# 返回
{
    "id": 123,
    "suite": 1,
    "project": 1,
    "status": 4,  # 执行完毕
    "is_pass": true,
    "report_url": "/api/suite/static/result_123_1234567890/report/index.html",
    "log_url": "/api/suite/static/result_123_1234567890/log/pytest.log"
}
```

## 目录结构

```
upload_yaml/
├── result_123_1234567890/          # 执行结果目录
│   ├── inputs/                     # 输入数据
│   │   └── dag_state.json         # DAG状态
│   ├── test_endpoint_1.yaml       # 测试文件
│   ├── test_endpoint_2.yaml
│   ├── test_endpoint_3.yaml
│   ├── conftest.py                # pytest配置
│   ├── pytest.ini                 # pytest配置
│   ├── extract.yaml               # 提取的变量
│   ├── results_raw/               # 原始结果
│   │   ├── 1/                     # endpoint 1的结果
│   │   ├── 2/                     # endpoint 2的结果
│   │   └── 3/                     # endpoint 3的结果
│   ├── results/                   # 合并后的结果
│   ├── report/                    # HTML报告
│   │   └── index.html
│   └── log/                       # 日志
│       └── pytest.log
├── result_124_1234567891/          # 另一个执行
└── result_125_1234567892/          # 又一个执行
```

## 并发执行示例

### 场景：同时执行3个测试套件

```python
# 提交套件1
POST /api/suite/suite/1/run/
# 返回 {"result_id": 101}

# 提交套件2
POST /api/suite/suite/2/run/
# 返回 {"result_id": 102}

# 提交套件3
POST /api/suite/suite/3/run/
# 返回 {"result_id": 103}
```

### 数据隔离

```
upload_yaml/
├── result_101_1234567890/  # 套件1的执行
├── result_102_1234567891/  # 套件2的执行
└── result_103_1234567892/  # 套件3的执行
```

每个执行完全独立，互不干扰：
- ✅ 独立的测试文件
- ✅ 独立的执行结果
- ✅ 独立的测试报告
- ✅ 独立的上下文变量

## 配置说明

### Django settings.py

```python
# 测试套件执行结果存储目录
SUITE_EXECUTION_BASE_DIR = BASE_DIR / 'upload_yaml'

# 线程池配置 - 控制同时执行的测试套件数量
MAX_CONCURRENT_SUITES = 6

# pytest 执行超时时间(秒)
PYTEST_EXECUTION_TIMEOUT = 300

# Allure 报告生成超时时间(秒)
ALLURE_GENERATION_TIMEOUT = 120

# pytest 参数
PYTEST_ARGS = ["-v", "--tb=short"]

# Allure 参数
ALLURE_ARGS = ["--clean"]
```

### Celery配置

```python
# celery.py
from celery import Celery

app = Celery('Tesla')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# settings.py
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
```

## 启动服务

### 1. 启动Redis

```bash
redis-server
```

### 2. 启动Django

```bash
python manage.py runserver
```

### 3. 启动Celery Worker

```bash
celery -A Tesla worker -l info
```

### 4. 启动Celery Beat（可选，用于定时任务）

```bash
celery -A Tesla beat -l info
```

## API接口

### 执行测试套件

```http
POST /api/suite/suite/{id}/run/
Content-Type: application/json
Authorization: Token {token}

{
    "endpoint_ids": [1, 2, 3],  # 可选
    "context": {"env": "test"}   # 可选
}

Response:
{
    "result_id": 123
}
```

### 获取执行结果

```http
GET /api/suite/runresult/{id}/
Authorization: Token {token}

Response:
{
    "id": 123,
    "suite": 1,
    "project": 1,
    "status": 4,
    "is_pass": true,
    "report_url": "/api/suite/static/result_123_1234567890/report/index.html",
    "log_url": "/api/suite/static/result_123_1234567890/log/pytest.log",
    "created_at": "2026-03-09T10:00:00Z"
}
```

### 获取执行结果列表

```http
GET /api/suite/runresult/?suite=1
Authorization: Token {token}

Response:
{
    "code": 200,
    "message": "ok",
    "result": {
        "page": 1,
        "pageSize": 10,
        "itemCount": 5,
        "list": [...]
    }
}
```

### Webhook触发

```http
POST /api/suite/suite/{id}/webhook/?key={hook_key}
Content-Type: application/json

{
    "endpoint_ids": [1, 2, 3],
    "context": {"env": "prod"}
}

Response:
{
    "result_id": 124
}
```

## 前端集成

### 执行套件

```javascript
import { runSuite } from '@/api/suite'

const executeSuite = async (suiteId) => {
  try {
    const res = await runSuite(suiteId, {})
    const resultId = res.result?.result_id || res.result_id
    
    // 跳转到结果页面
    router.push(`/results?id=${resultId}`)
  } catch (error) {
    console.error('执行失败:', error)
  }
}
```

### 查看结果

```javascript
import { getRunResults } from '@/api/suite'

const loadResults = async () => {
  const res = await getRunResults({ suite: suiteId })
  results.value = res.result?.list || []
}
```

### 查看报告

```javascript
const viewReport = (reportUrl) => {
  if (reportUrl) {
    window.open(reportUrl, '_blank')
  }
}
```

## 测试验证

### 运行自测脚本

```bash
# 确保服务都在运行
# 1. Redis
# 2. Django
# 3. Celery Worker

# 运行测试
python tests/test_suite_result.py
```

### 测试内容

1. ✅ 创建测试数据（项目、接口、用例、套件）
2. ✅ 并发执行3个测试套件
3. ✅ 验证数据隔离（独立目录）
4. ✅ 验证状态跟踪（实时状态）
5. ✅ 验证执行结果（报告生成）
6. ✅ 清理测试数据

### 预期结果

```
========== 测试报告 ==========
总测试数: 25
成功: 24
失败: 0
警告: 1
成功率: 96.00%

========== 核心功能验证 ==========
✓ 并发执行: 成功提交3个套件同时执行
✓ 数据隔离: 每个执行结果有独立的存储路径
✓ 异步执行: 使用Celery异步任务队列
✓ 状态跟踪: 可以查询执行状态和结果
```

## 性能优化

### 1. 并发控制

```python
# settings.py
MAX_CONCURRENT_SUITES = 6  # 根据服务器性能调整
```

### 2. Celery Worker扩展

```bash
# 启动多个worker
celery -A Tesla worker -l info -c 4  # 4个并发进程
```

### 3. Redis连接池

```python
# 使用连接池提高性能
CELERY_BROKER_POOL_LIMIT = 10
```

### 4. 超时控制

```python
# 避免任务长时间占用资源
PYTEST_EXECUTION_TIMEOUT = 300  # 5分钟
ALLURE_GENERATION_TIMEOUT = 120  # 2分钟
```

## 故障排查

### 问题1: 任务不执行

**检查**:
1. Celery Worker是否运行
2. Redis是否运行
3. 查看Celery日志

**解决**:
```bash
# 查看Celery状态
celery -A Tesla inspect active

# 重启Worker
celery -A Tesla worker -l info
```

### 问题2: 报告未生成

**检查**:
1. Allure是否安装
2. 查看执行日志
3. 检查目录权限

**解决**:
```bash
# 安装Allure
brew install allure  # macOS
apt-get install allure  # Ubuntu

# 手动生成报告测试
allure generate results -o report
```

### 问题3: 并发冲突

**检查**:
1. 目录是否独立
2. Redis key是否隔离
3. 查看DAG状态文件

**解决**:
- 确保每个执行有唯一的result_id
- 确保目录名包含timestamp
- 检查Redis key前缀

## 最佳实践

### 1. 合理组织用例

- 按功能模块划分套件
- 控制单个套件的用例数量（建议<50个）
- 设置合理的依赖关系

### 2. 监控执行状态

- 定期检查执行结果
- 关注失败用例
- 分析执行时间

### 3. 清理历史数据

```python
# 定期清理旧的执行结果
from suite.models import RunResult
from datetime import datetime, timedelta

# 删除30天前的结果
old_date = datetime.now() - timedelta(days=30)
RunResult.objects.filter(created_at__lt=old_date).delete()
```

### 4. 备份重要报告

```bash
# 备份报告目录
tar -czf reports_backup.tar.gz upload_yaml/
```

## 总结

Suite和Result模块是Tesla测试平台的核心，提供了：

- ✅ **异步执行**: 不阻塞用户操作
- ✅ **并发执行**: 支持多套件同时运行
- ✅ **数据隔离**: 完全独立的执行环境
- ✅ **DAG调度**: 智能处理依赖关系
- ✅ **状态跟踪**: 实时查看执行进度
- ✅ **报告生成**: 自动生成Allure报告

这些特性确保了测试平台的高效、稳定和可扩展性。

---

**文档版本**: v1.0.1  
**更新日期**: 2026-03-09  
**作者**: Tesla Team
