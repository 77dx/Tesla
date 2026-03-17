# Tesla 自动化测试平台 - 完整说明文档

## 📋 项目概述

Tesla 是一个基于 Django + DRF 的**企业级自动化测试管理平台**，支持 API 接口测试和 UI 自动化测试的全生命周期管理。

### 核心特性

- **用例管理**：数据库化管理 API/UI 测试用例，支持项目分组
- **测试套件**：灵活编排测试用例，支持单次执行、定时任务、WebHook 触发
- **依赖驱动执行（DAG）**：自动分析接口依赖关系，智能调度并行执行
- **分布式执行**：基于 Celery 的异步任务队列，支持多套件并发
- **数据隔离**：每次执行独立目录，互不干扰
- **可视化报告**：集成 Allure 生成精美测试报告

---

## 🛠 技术栈

| 类别 | 技术选型 |
|------|---------|
| **后端框架** | Django 4.2 + Django REST Framework |
| **异步任务** | Celery + Redis |
| **测试框架** | pytest + pytest-allure |
| **定时任务** | django-q |
| **数据库** | SQLite（可切换 MySQL/PostgreSQL）|
| **API 文档** | drf-spectacular (Swagger/ReDoc) |
| **其他** | PyYAML, jsonpath, openpyxl |

---

## 📁 项目结构

```
Tesla/
├── Tesla/                    # Django 项目配置
│   ├── settings.py           # 全局配置（数据库、Celery、测试框架）
│   ├── urls.py               # 主路由
│   ├── celery.py             # Celery 应用初始化
│   └── customPagination.py   # 自定义分页
│
├── account/                  # 用户账号模块
│   ├── models.py             # Avatar, Profile
│   └── views.py              # 用户注册、登录、头像上传
│
├── system/                   # 系统管理模块
│   ├── models.py             # Department, Position, Role, User_Role
│   └── views.py              # 部门、职位、角色管理
│
├── project/                  # 项目管理模块
│   ├── models.py             # Project, Config
│   └── views.py              # 项目 CRUD、成员管理
│
├── case_api/                 # API 用例模块
│   ├── models.py             # Endpoint（接口）, Case（用例）
│   ├── util.py               # GenerateCase（数据库转 YAML）
│   ├── serializers.py        # 序列化器
│   └── views.py              # 接口/用例 CRUD、单接口执行
│
├── case_ui/                  # UI 用例模块
│   ├── models.py             # Element（页面元素）, Case（UI 用例）
│   └── views.py              # UI 用例管理
│
├── suite/                    # 测试套件模块（核心）
│   ├── models.py             # Suite（套件）, RunResult（执行记录）
│   ├── tasks.py              # Celery DAG 任务（start_suite_dag, execute_endpoint_node）
│   ├── views.py              # 套件执行、WebHook、报告访问
│   └── serializers.py        # 套件序列化
│
├── apiframetest/             # API 测试执行引擎
│   ├── commons/              # 公共工具库
│   │   ├── main_util.py      # 用例执行主流程
│   │   ├── extract_util.py   # 变量提取与替换（支持 Redis/文件）
│   │   ├── requests_util.py  # HTTP 请求封装
│   │   ├── assert_util.py    # 断言工具
│   │   └── yaml_util.py      # YAML 读写
│   ├── hotload/debug_talk.py # 动态函数（${yaml_read()}）
│   └── conftest.py           # pytest 配置
│
├── tests/                    # 公共测试配置
│   ├── conftest.py           # YAML 文件收集器、YamlTest 执行逻辑
│   ├── pytest.ini            # pytest 配置
│   └── extract.yaml          # 默认变量存储文件
│
├── upload_yaml/              # 套件执行目录（动态生成）
│   └── result_{id}_{ts}/     # 每次执行的独立目录
│       ├── test_*.yaml       # 生成的测试用例
│       ├── results/          # Allure 原始结果
│       └── report/           # Allure HTML 报告
│
├── reports/                  # 历史报告存档
├── media/                    # 用户上传文件（头像等）
├── static/                   # 静态资源
├── docs/                     # 项目文档
└── db.sqlite3                # SQLite 数据库
```

---

## 🗄 数据模型关系

### 核心模型 ER 图

```
User (Django 内置)
  ├── Profile (1:1) - 用户资料
  ├── User_Role (M2M) - 用户角色关系
  └── Project.members (M2M) - 项目成员

Project (项目)
  ├── Config (1:1) - pytest 配置
  ├── Endpoint (1:N) - 接口定义
  ├── Case (API) (1:N) - API 用例
  ├── Case (UI) (1:N) - UI 用例
  └── Suite (1:N) - 测试套件

Endpoint (接口)
  ├── Case (1:N) - 一个接口可有多个用例
  ├── requires (JSON) - 依赖的变量列表
  └── provides (JSON) - 产出的变量列表

Suite (测试套件)
  ├── case_api_list (M2M → Case API)
  ├── case_ui_list (M2M → Case UI)
  ├── run_type (单次/定时/WebHook)
  └── RunResult (1:N) - 执行记录

RunResult (执行记录)
  ├── suite (FK)
  ├── project (FK)
  ├── path (执行目录)
  ├── status (Init/Running/Done/Error)
  └── is_pass (是否通过)
```

### 关键字段说明

#### Endpoint（接口定义）
```python
name = CharField("接口名称")
method = CharField("GET/POST/PUT/DELETE")
url = CharField("接口地址")
params = JSONField("查询参数")
data = JSONField("表单参数")
json = JSONField("JSON 参数")
headers = JSONField("请求头")
requires = JSONField("依赖变量", example=["token", "userId"])
provides = JSONField("产出变量", example=["orderId"])
```

#### Case（API 用例）
```python
name = CharField("用例名称")
endpoint = ForeignKey(Endpoint)
api_args = JSONField("实际传参", example={"json": {"username": "test"}})
extract = JSONField("数据提取", example={"token": ["json", "$.data.token", 0]})
validate = JSONField("断言", example={"equals": {"状态码": [200, "status_code"]}})
```

#### Suite（测试套件）
```python
name = CharField("套件名称")
run_type = CharField(choices=["O"单次, "C"定时, "W"WebHook])
cron = CharField("cron 表达式")
hook_key = CharField("WebHook 密钥")
```

---

## 🔄 核心业务流程

### 1. 套件执行流程（DAG 模式）

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 用户触发                                                  │
│    POST /api/suite/{id}/run/                                │
│    Body: {"endpoint_ids": [1,2,3], "context": {"token":""}} │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Suite.run() - 创建执行记录                                │
│    - 创建 RunResult 记录                                     │
│    - 生成独立目录: upload_yaml/result_{id}_{timestamp}/     │
│    - 复制 conftest.py, pytest.ini                           │
│    - 投递 Celery 任务: start_suite_dag.delay()              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. start_suite_dag - 初始化 DAG                              │
│    - 初始化 Redis 上下文: suite:{result_id}:context          │
│    - 读取 Endpoint.requires/provides 构建依赖图              │
│    - 检测循环依赖                                            │
│    - 保存 DAG 状态到 dag_state.json                          │
│    - 触发第一波执行: schedule_next_wave.delay()              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. schedule_next_wave - 调度下一波                           │
│    - 读取 dag_state.json                                     │
│    - 找出依赖已满足的 endpoint（ready）                      │
│    - 并行执行: chord(execute_endpoint_node × N)              │
│    - 回调: dag_wave_complete                                 │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. execute_endpoint_node - 执行单个接口                      │
│    - 设置环境变量: APIFRAME_CONTEXT_BACKEND=redis            │
│    - GenerateCase(endpoint_id).to_yaml() 生成 YAML           │
│    - pytest.main([yaml_path, --alluredir=results_raw/{eid}]) │
│    - 返回执行结果: {endpoint_id, success, returncode}        │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. dag_wave_complete - 收集结果                              │
│    - 更新 dag_state: succeeded/failed 列表                   │
│    - 如有失败，标记 is_pass=False                            │
│    - 递归调用: schedule_next_wave.delay()                    │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. finalize_suite_run - 生成报告                             │
│    - 合并 results_raw/* → results/                           │
│    - allure generate results -o report --clean               │
│    - 更新 RunResult.status = Done                            │
│    - 报告地址: /api/suite/static/result_xx/report/index.html│
└─────────────────────────────────────────────────────────────┘
```

### 2. 单用例执行流程（apiframetest）

```
YAML 用例文件
  ↓
pytest 收集 (tests/conftest.py)
  ↓
YamlTest.runtest()
  ├─ 1. ExtractUtil.change(request)
  │     - 替换 ${yaml_read(token)} 为实际值
  │     - 支持 ${func()} 动态函数
  │
  ├─ 2. RequestsUtil.send_all_requests()
  │     - 发送 HTTP 请求
  │     - 返回 Response 对象
  │
  ├─ 3. ExtractUtil.extract_key()
  │     - 从响应提取变量（jsonpath/正则）
  │     - 写入 extract.yaml 或 Redis
  │
  └─ 4. AssertUtil.assert_all_case()
        - 执行断言（equals/contains/startswith 等）
        - 失败抛出 AssertionError
```

### 3. 变量提取与共享机制

#### 提取配置（extract）
```yaml
extract:
  token: [json, $.data.token, 0]
  userId: [json, $.data.user.id, 0]
  orderId: [regex, "orderId=(\\d+)", 0]
```

格式：`变量名: [attr_name, expression, index]`
- `attr_name`: json/text/headers/cookies/regex
- `expression`: jsonpath 表达式或正则
- `index`: 提取结果的索引（通常为 0）

#### 变量引用
```yaml
request:
  headers:
    Authorization: Bearer ${yaml_read(token)}
  json:
    userId: ${yaml_read(userId)}
```

#### 存储后端

| 模式 | 配置 | 适用场景 |
|------|------|---------|
| **文件模式** | `APIFRAME_CONTEXT_BACKEND=file` | 单机顺序执行 |
| **Redis 模式** | `APIFRAME_CONTEXT_BACKEND=redis` | 分布式并发执行 |

套件执行时自动使用 Redis，按 `suite:{result_id}:context` 隔离。

---

## 🚀 部署与运行

### 环境要求
- Python 3.8+
- Redis 5.0+
- Allure 2.x（可选，用于报告生成）

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository_url>
cd Tesla

# 2. 安装依赖
pip install -r requirements.txt

# 3. 数据库迁移
python manage.py migrate

# 4. 创建超级用户
python manage.py createsuperuser

# 5. 启动 Redis
brew services start redis  # macOS
# 或 sudo systemctl start redis  # Linux

# 6. 启动 Django
python manage.py runserver

# 7. 启动 Celery Worker（新终端）
celery -A Tesla worker -l info

# 8. 启动 django-q（可选，用于定时任务）
python manage.py qcluster
```

### 访问地址
- **管理后台**: http://127.0.0.1:8000/admin/
- **API 文档**: http://127.0.0.1:8000/api/schema/swagger/
- **ReDoc**: http://127.0.0.1:8000/api/schema/redoc/

---

## 📡 API 接口文档

### 套件管理

#### 执行套件
```http
POST /api/suite/{id}/run/
Content-Type: application/json

{
  "endpoint_ids": [1, 2, 3],  // 可选，不传则用套件默认配置
  "context": {                 // 可选，初始上下文
    "token": "预置 token",
    "baseUrl": "https://api.example.com"
  }
}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 123,
    "suite": 1,
    "path": "upload_yaml/result_123_1234567890",
    "status": 1,  // 0:Init, 1:Ready, 2:Running, 3:Reporting, 4:Done, -1:Error
    "is_pass": false
  }
}
```

#### 查询执行结果
```http
GET /api/suite/result/{result_id}/

Response:
{
  "code": 200,
  "data": {
    "id": 123,
    "status": 4,
    "is_pass": true,
    "report_url": "/api/suite/static/result_123_1234567890/report/index.html"
  }
}
```

#### WebHook 触发
```http
POST /api/suite/{id}/webhook/?key={hook_key}
Content-Type: application/json

{
  "endpoint_ids": [1, 2],
  "context": {}
}
```

### 接口用例

#### 单接口执行
```http
POST /api/case_api/run/
Content-Type: application/json

{
  "endpoint_id": 1
}

Response:
{
  "code": 200,
  "message": "测试执行完成",
  "data": {
    "return_code": 0,  // pytest 返回码
    "report_path": "reports/2_1234567890/report/index.html"
  }
}
```

---

## ⚙️ 配置说明

### settings.py 关键配置

```python
# 测试框架配置
TEST_YAML_PATH = BASE_DIR / 'tests/test_case_yaml'
EXTRACT_PATH = BASE_DIR / 'tests/extract.yaml'
REPORT_DIR = BASE_DIR / 'reports'
SUITE_EXECUTION_BASE_DIR = BASE_DIR / 'upload_yaml'

# 并发控制
MAX_CONCURRENT_SUITES = 6  # 同时执行的套件数

# 超时设置
PYTEST_EXECUTION_TIMEOUT = 300  # 单个套件超时（秒）
ALLURE_GENERATION_TIMEOUT = 120  # 报告生成超时（秒）

# pytest 参数
PYTEST_ARGS = ['-v', '--tb=short']

# Celery 配置
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
```

### 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `APIFRAME_EXTRACT_PATH` | 覆盖 extract 文件路径 | `/tmp/extract.yaml` |
| `APIFRAME_CONTEXT_BACKEND` | 上下文后端 | `file` / `redis` |
| `APIFRAME_CONTEXT_PREFIX` | Redis key 前缀 | `suite:123` |
| `APIFRAME_REDIS_URL` | Redis 连接 | `redis://localhost:6379/1` |
| `CELERY_BROKER_URL` | Celery broker | `redis://localhost:6379/0` |

---

## 🎯 使用示例

### 示例 1：创建并执行 API 测试

```python
# 1. 创建项目
project = Project.objects.create(name="电商系统", url="https://api.shop.com")

# 2. 创建登录接口
login_endpoint = Endpoint.objects.create(
    name="用户登录",
    project=project,
    method="POST",
    url="https://api.shop.com/login",
    headers={"Content-Type": "application/json"},
    provides=["token", "userId"]  # 声明产出变量
)

# 3. 创建登录用例
login_case = Case.objects.create(
    name="正常登录",
    project=project,
    endpoint=login_endpoint,
    api_args={
        "json": {"username": "test", "password": "123456"}
    },
    extract={
        "token": ["json", "$.data.token", 0],
        "userId": ["json", "$.data.userId", 0]
    },
    validate={
        "equals": {
            "状态码200": [200, "status_code"],
            "登录成功": ["success", "json.message"]
        }
    }
)

# 4. 创建订单接口（依赖登录）
order_endpoint = Endpoint.objects.create(
    name="订单列表",
    project=project,
    method="GET",
    url="https://api.shop.com/orders",
    requires=["token", "userId"],  # 声明依赖
    headers={"Authorization": "Bearer ${yaml_read(token)}"}
)

# 5. 创建测试套件
suite = Suite.objects.create(
    name="用户流程测试",
    project=project,
    run_type="O"  # 单次执行
)
suite.case_api_list.add(login_case)

# 6. 执行套件
result = suite.run(endpoint_ids=[login_endpoint.id, order_endpoint.id])
print(f"执行ID: {result.id}, 状态: {result.get_status_display()}")
```

### 示例 2：配置定时任务

```python
suite = Suite.objects.create(
    name="每日回归测试",
    project=project,
    run_type="C",  # 定时任务
    cron="0 2 * * *"  # 每天凌晨 2 点
)
# 保存时自动创建 django-q Schedule
```

### 示例 3：WebHook 集成

```python
suite = Suite.objects.create(
    name="CI/CD 触发测试",
    project=project,
    run_type="W"  # WebHook
)
# 保存时自动生成 hook_key

# 在 CI/CD 中调用
# curl -X POST "http://your-domain/api/suite/{suite.id}/webhook/?key={suite.hook_key}"
```

---

## 🔍 故障排查

### 常见问题

#### 1. Celery 任务不执行
```bash
# 检查 Redis 连接
redis-cli ping

# 检查 Celery worker 是否运行
ps aux | grep celery

# 查看 Celery 日志
celery -A Tesla worker -l debug
```

#### 2. 报告生成失败
```bash
# 检查 Allure 是否安装
allure --version

# 手动生成报告测试
allure generate upload_yaml/result_xx/results -o test_report
```

#### 3. 变量提取失败
- 检查 jsonpath 表达式是否正确
- 确认响应格式（JSON/Text）
- 查看 extract.yaml 或 Redis 中是否有值

#### 4. DAG 依赖错误
- 检查 requires/provides 配置
- 确保没有循环依赖
- 查看 dag_state.json 中的依赖图

---

## 📚 附录

### YAML 用例完整格式

```yaml
feature: 项目名称
story: 接口名称
title: 用例标题

allure:
  title: Allure 显示标题
  feature: 功能模块
  story: 用户故事
  severity: critical  # blocker/critical/normal/minor/trivial
  description: 用例描述

request:
  url: https://api.example.com/login
  method: POST
  headers:
    Content-Type: application/json
    Authorization: Bearer ${yaml_read(token)}
  json:
    username: test
    password: "123456"

extract:
  token: [json, $.data.token, 0]
  userId: [json, $.data.user.id, 0]
  orderId: [regex, "order_id=(\\d+)", 0]

validate:
  equals:
    状态码200: [200, status_code]
    返回成功: ["success", json.code]
  contains:
    包含token: ["token", json.data]
  startswith:
    消息前缀: ["登录", json.message]
```

### 数据驱动测试（DDT）

```yaml
feature: 登录测试
story: 参数化登录

parametrize:
  - [username, password, expected]  # 参数名
  - ["admin", "123456", "success"]  # 数据组1
  - ["test", "wrong", "failed"]     # 数据组2

request:
  url: https://api.example.com/login
  method: POST
  json:
    username: $ddt{username}
    password: $ddt{password}

validate:
  equals:
    预期结果: [$ddt{expected}, json.status]
```

---

## 📞 联系与支持

- **项目地址**: [GitHub Repository]
- **问题反馈**: [Issues]
- **文档更新**: 2026-03-07

---

**Tesla 测试平台 - 让自动化测试更简单、更高效！** 🚀
