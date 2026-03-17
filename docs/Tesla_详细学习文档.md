# Tesla 自动化测试平台 — 完整学习文档

> 本文档面向已完成项目开发但需要重新梳理的开发者，力求每个模块都讲清楚「是什么、为什么、怎么用」。

---

## 目录

1. [项目整体架构](#1-项目整体架构)
2. [目录结构详解](#2-目录结构详解)
3. [数据库模型全解析](#3-数据库模型全解析)
4. [后端模块详解](#4-后端模块详解)
5. [前端架构详解](#5-前端架构详解)
6. [核心业务流程](#6-核心业务流程)
7. [权限系统详解](#7-权限系统详解)
8. [产品线多租户机制](#8-产品线多租户机制)
9. [环境与服务注册表](#9-环境与服务注册表)
10. [测试执行引擎](#10-测试执行引擎)
11. [API 接口规范](#11-api-接口规范)
12. [前端页面与组件](#12-前端页面与组件)

---

## 1. 项目整体架构

### 1.1 架构全貌

```
┌─────────────────────────────────────────────────────┐
│                  浏览器 (Vue3 SPA)                   │
│  路由守卫 → Pinia Store → Axios → API Layer          │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP REST API (/api/...)
┌─────────────────────▼───────────────────────────────┐
│              Django 4.2 + DRF                        │
│  URL Router → ViewSet → Serializer → Model           │
│  Middleware: CORS, Token Auth                        │
└──────┬──────────────┬──────────────┬────────────────┘
       │              │              │
┌──────▼──────┐ ┌─────▼─────┐ ┌────▼──────────────────┐
│  SQLite DB  │ │   Redis   │ │  Celery Worker        │
│  (模型存储)  │ │ (任务队列) │ │  (异步执行套件)        │
│             │ │ (上下文   │ │  → pytest 执行引擎     │
│             │ │  变量存储)│ │  → Allure 报告生成     │
└─────────────┘ └───────────┘ └───────────────────────┘
                      │
               ┌──────▼──────┐
               │  django-q   │
               │  (定时任务)  │
               └─────────────┘
```

### 1.2 请求生命周期

以「查看用例列表」为例，完整链路：

```
1. 用户打开 /cases 页面
2. Vue Router 检查 meta.permission='case:list'
3. router.beforeEach 读取 localStorage['permissions'] 验证
4. CaseView.vue onMounted() 调用 getCases(params)
5. Axios 发送 GET /api/case_api/?page=1&product_line=1
6. Django URL Router 匹配到 CaseViewSet
7. TokenAuthentication 验证请求头 Authorization: Token xxx
8. ViewSet.get_queryset() 按 product_line 过滤
9. CaseSerializer 序列化数据（包含 endpoint 嵌套、project_name 等）
10. 返回 JSON → Axios → CaseView.vue 渲染表格
```

---

## 2. 目录结构详解

```
Tesla/
├── backend/                    # 所有后端代码
│   ├── Tesla/                  # Django 项目配置目录
│   │   ├── settings.py         # 全局配置（数据库/Celery/静态文件等）
│   │   ├── urls.py             # 主路由：include 各 app 的 urls
│   │   ├── celery.py           # Celery 应用初始化
│   │   └── customPagination.py # 统一分页格式
│   │
│   ├── account/                # 用户账号模块
│   │   ├── models.py           # Profile（扩展用户信息）
│   │   ├── views.py            # 登录/注册/头像上传/用户管理
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   ├── system/                 # 系统管理模块
│   │   ├── models.py           # Department/Position/Role/Permission
│   │   ├── views.py            # CRUD + 权限配置 + 用户角色分配
│   │   ├── serializers.py
│   │   └── management/
│   │       └── commands/
│   │           └── init_permissions.py  # 初始化权限码命令
│   │
│   ├── product_line/           # 产品线模块
│   │   ├── models.py           # ProductLine / ProductLineMember
│   │   ├── views.py            # 产品线 CRUD / 成员管理 / 我的产品线
│   │   └── serializers.py
│   │
│   ├── project/                # 项目管理模块
│   │   ├── models.py           # Project（关联 ProductLine）/ Config
│   │   ├── views.py            # 项目 CRUD
│   │   └── serializers.py      # 包含 pm_name / product_line_name
│   │
│   ├── case_api/               # API 用例模块
│   │   ├── models.py           # Endpoint / Case
│   │   ├── views.py            # 接口/用例 CRUD
│   │   ├── serializers.py      # CaseSerializer（含 endpoint 嵌套）
│   │   ├── engine.py           # SuiteRunner（执行引擎核心）
│   │   └── util.py             # GenerateCase（数据库→YAML，已废弃）
│   │
│   ├── suite/                  # 测试套件模块
│   │   ├── models.py           # Service/Environment/Suite/SuiteCaseItem/RunResult
│   │   ├── views.py            # 套件 CRUD / 执行 / WebHook / 结果查询
│   │   ├── serializers.py
│   │   └── tasks.py            # Celery 任务：run_suite_task
│   │
│   ├── snippet/                # 公共工具
│   │   └── permissions.py      # RolePermission / make_permission
│   │
│   ├── upload_yaml/            # 套件执行目录（运行时动态生成）
│   │   └── result_{id}_{ts}/   # 每次执行的独立目录
│   │       ├── results/        # Allure 原始结果
│   │       └── report/         # Allure HTML 报告
│   │
│   └── media/                  # 用户上传文件（头像）
│       └── avatar/user_{id}/
│
└── frontend/                   # 所有前端代码
    ├── src/
    │   ├── api/                # Axios 请求封装
    │   │   ├── request.js      # Axios 实例（拦截器/Token/401处理）
    │   │   ├── account.js      # 用户相关 API
    │   │   ├── project.js      # 项目相关 API
    │   │   ├── endpoint.js     # 接口相关 API
    │   │   ├── case.js         # 用例相关 API
    │   │   ├── suite.js        # 套件/环境/服务 API
    │   │   ├── system.js       # 系统管理 API
    │   │   └── productLine.js  # 产品线 API
    │   │
    │   ├── stores/
    │   │   └── user.js         # Pinia Store：用户信息/产品线/权限
    │   │
    │   ├── router/
    │   │   └── index.js        # 路由配置 + beforeEach 权限守卫
    │   │
    │   ├── composables/
    │   │   └── useConfirm.js   # 全局确认弹框 composable
    │   │
    │   ├── components/
    │   │   └── ConfirmDialog.vue
    │   │
    │   └── views/              # 所有页面组件
    │       ├── LayoutView.vue  # 主布局（侧边栏+Header）
    │       ├── LoginView.vue
    │       ├── DashboardView.vue
    │       ├── ProjectView.vue / ProjectDetailView.vue
    │       ├── EndpointView.vue / EndpointDetailView.vue / EndpointFormView.vue
    │       ├── CaseView.vue / CaseDetailView.vue
    │       ├── SuiteView.vue / SuiteDetailView.vue / SuiteFormView.vue
    │       ├── EnvironmentView.vue
    │       ├── ResultView.vue / ResultDetailView.vue
    │       ├── SystemView.vue
    │       ├── ProductLineView.vue
    │       └── AccountView.vue
    │
    ├── index.html
    ├── vite.config.js
    └── package.json
```

---

## 3. 数据库模型全解析

### 3.1 模型关系总图

```
User (Django 内置)
  │
  ├──(1:1)── Profile          昵称/头像/联系方式
  ├──(M2M)── Role             通过 User_Role 中间表
  └──(M2M)── ProductLine      通过 ProductLineMember 中间表

ProductLine（产品线）
  ├──(1:N)── ProductLineMember  成员（含产品线级角色）
  └──(1:N)── Project（间接，通过 Project.product_line FK）

Project（项目）
  ├── product_line FK → ProductLine
  ├── pm FK → User（项目负责人）
  ├──(1:1)── Config           pytest 配置脚本
  ├──(1:N)── Endpoint         接口
  ├──(1:N)── Case (API)       API 用例
  ├──(1:N)── Environment      运行环境
  ├──(1:N)── Service          服务注册表
  └──(1:N)── Suite            测试套件

Endpoint（接口）
  └──(1:N)── Case             一个接口可有多个用例

Suite（测试套件）
  ├── environment FK → Environment（可选）
  ├──(1:N)── SuiteCaseItem    套件用例项（中间表）
  │           ├── case_api FK → Case (API)
  │           ├── case_ui FK → Case (UI)
  │           ├── role: setup/main/teardown
  │           ├── order: 执行顺序
  │           └── enabled: 是否启用
  └──(1:N)── RunResult        执行记录

Environment（运行环境）
  ├──(1:N)── GlobalVariable   环境级全局变量
  └──(1:N)── Suite            引用此环境的套件

Role（角色）
  └──(M2M)── Permission       权限码（通过 role.permissions）

Permission（权限码）
  ├── code: 'project:list'
  ├── name: '查看项目列表'
  └── module: 'project'
```

### 3.2 关键模型字段详解

#### Endpoint（接口定义）

```python
class Endpoint(models.Model):
    name        # 接口名称，如「用户登录」
    project     # FK → Project
    method      # GET/POST/PUT/DELETE/PATCH
    url         # 接口路径，如 /api/users（不含域名）
    service_key # 服务标识，如 user-service
                # 完整地址 = {service_key 对应的域名} + url
    params      # JSON：查询字符串 ?key=value
    data        # JSON：表单参数（form-data）
    json        # JSON：JSON Body
    headers     # JSON：请求头
    cookies     # JSON：Cookies
    requires    # JSON：依赖变量列表，如 ["token", "userId"]
                # 表示执行前上下文中必须有这些变量
    provides    # JSON：产出变量列表，如 ["orderId"]
                # 表示执行后会往上下文写入这些变量
    created_by  # FK → User
    updated_by  # FK → User
```

#### Case（API 用例）

```python
class Case(models.Model):
    name        # 用例名称
    project     # FK → Project
    endpoint    # FK → Endpoint（关联的接口）
    alluer      # JSON：Allure 标注（title/feature/story/severity）
    api_args    # JSON：实际传参，覆盖 Endpoint 默认参数
                # 格式：{"json": {"username": "test"}, "params": {"page": 1}}
    extract     # JSON：数据提取规则
                # 格式：{"token": ["json", "$.data.token", 0]}
                # [attr_name, expression, index]
                # attr_name: json/text/headers/cookies/regex
    validate    # JSON：断言规则
                # 格式：{"equals": {"状态码200": [200, "status_code"]}}
```

#### Suite（测试套件）

```python
class Suite(models.Model):
    name            # 套件名称
    project         # FK → Project
    description     # 描述
    environment     # FK → Environment（可选，执行时注入环境配置）
    suite_variables # JSON：套件级变量，优先级高于全局变量
    suite_headers   # JSON：套件级请求头，注入所有请求
    timeout_seconds # 单条用例超时秒数，0=不限制
    fail_strategy   # 'continue' 继续 / 'stop' 立即停止
    retry_count     # 失败重试次数
    retry_delay     # 重试间隔秒数
    run_type        # 'O' 单次 / 'C' 定时 / 'W' WebHook
    cron            # cron 表达式，如 "0 2 * * *"
    hook_key        # WebHook 密钥，run_type=W 时自动生成
    schedule        # FK → django_q.Schedule（定时任务对象）
```

#### SuiteCaseItem（套件用例项，核心中间表）

```python
class SuiteCaseItem(models.Model):
    suite       # FK → Suite
    case_type   # 'API' 或 'UI'
    case_api    # FK → Case（API），case_type=API 时有值
    case_ui     # FK → Case（UI），case_type=UI 时有值
    role        # 'setup'前置 / 'main'正式 / 'teardown'后置
    order       # 执行顺序（数字越小越先执行）
    enabled     # 是否启用
    env_override # JSON：运行时覆盖参数
```

#### RunResult（执行记录）

```python
class RunResult(models.Model):
    suite       # FK → Suite
    project     # FK → Project
    path        # 执行目录路径，如 upload_yaml/result_5_1750000000
    is_pass     # 是否通过（所有用例全过才为 True）
    status      # 0=初始化 1=准备开始 2=执行中 3=生成报告 4=完毕 -1=出错
    created_at  # 创建时间
```

---

## 4. 后端模块详解

### 4.1 account 模块（用户账号）

**models.py 关键模型：**
```python
class Profile(models.Model):
    user      # OneToOne → User
    nickname  # 昵称（显示名称）
    phone     # 手机号
    email     # 邮箱
    avatar_url # 头像 URL（相对路径，如 /api/media/avatar/user_1/xxx.png）
```

**主要 API：**
- `POST /api/account/profile/login/` → 登录，返回 Token
- `GET /api/account/profile/profile/` → 获取当前用户信息
- `POST /api/account/profile/modify/` → 修改个人信息
- `POST /api/account/profile/img_upload/` → 上传头像
- `GET /api/account/profile/get_all_users/` → 获取所有用户（用于下拉选择）
- `GET /api/account/admin/users/list/` → 管理员获取用户详情列表（含部门/角色）
- `POST /api/account/admin/users/update/` → 管理员修改用户部门/角色

**登录机制：**

Django 内置 Token Authentication。登录成功后返回 `token` 字符串，前端存入 `localStorage['token']`。
后续每个请求在 Header 加 `Authorization: Token {token}`，Django 自动验证。

### 4.2 system 模块（系统管理）

**模型：**
```python
Department  # 部门：name, intro, leader FK→User, default_role FK→Role
Position    # 职位：name, is_leader
Role        # 角色：name, permissions(M2M→Permission)
Permission  # 权限码：code, name, module
```

**权限码初始化：**
```bash
# 执行管理命令，同步预置权限码到数据库
python manage.py init_permissions
```

所有权限码在 `system/management/commands/init_permissions.py` 中定义，格式：
```python
('project:list', '查看项目列表', 'project'),
('case:create', '新建用例', 'case'),
# ...
```

**角色权限配置 API：**
- `POST /api/system/role/{id}/set_permissions/` → 全量设置角色权限
- `POST /api/system/role/{id}/set_users/` → 全量设置角色成员

### 4.3 project 模块

**序列化器额外字段：**
```python
pm_name          # 项目负责人昵称（从 pm.profile.nickname 取）
product_line_name # 产品线名称
```

**ViewSet 过滤逻辑：**
```python
def get_queryset(self):
    qs = Project.objects.all()
    product_line_id = self.request.query_params.get('product_line')
    if product_line_id:
        qs = qs.filter(product_line_id=product_line_id)  # 产品线过滤
    search = self.request.query_params.get('search')
    if search:
        qs = qs.filter(name__icontains=search)  # 模糊搜索
    return qs
```

### 4.4 case_api 模块

**Endpoint 序列化器特殊处理：**
```python
class CaseSerializer(serializers.ModelSerializer):
    # endpoint 写入时接收 ID，输出时返回嵌套对象
    endpoint = PrimaryKeyRelatedField(write_only=True)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 输出时替换为完整 endpoint 数据
        data['endpoint'] = EndpointDetailSerializer(instance.endpoint).data
        # 附加 project_name
        data['project_name'] = instance.project.name if instance.project else ''
        # 附加 project_product_line（用于前端跨产品线过滤）
        data['project_product_line'] = instance.project.product_line_id if instance.project else None
        return data
```

**执行引擎（engine.py）：**
`SuiteRunner` 是套件执行的核心类，由 Celery 任务调用：
```python
class SuiteRunner:
    def run(self, result_id, case_ids, initial_context, ...):
        # 1. 读取套件配置（环境变量、套件变量、套件请求头）
        # 2. 初始化上下文（ContextStore，Redis 后端）
        # 3. 按 role 顺序执行：setup → main → teardown
        # 4. 每条用例执行前替换变量，执行后提取变量
        # 5. 按 fail_strategy 决定是否继续
        # 6. 支持 retry_count 次重试
        # 7. 执行完毕生成 Allure 报告
```

### 4.5 suite 模块

**Service（服务注册表）：**
```python
class Service(models.Model):
    key         # 全局唯一标识，如 user-service
    name        # 显示名称，如「用户服务」
    project     # FK → Project
```

**Environment（运行环境）：**
```python
class Environment(models.Model):
    name        # 环境名，如「测试环境」
    project     # FK → Project
    urls        # JSON：多服务 URL 列表
                # [{"var": "user-service", "url": "https://user.test.example.com", "name": "用户服务"}]
    headers     # JSON：全局请求头，注入所有请求
    variables   # JSON：环境变量键值对
    mock_rules  # JSON：Mock 拦截规则
```

**Suite.run() 执行流程：**
```python
def run(self, case_ids=None, ui_case_ids=None, initial_context=None):
    # 1. 创建 RunResult 记录（status=Init）
    # 2. 创建独立目录 upload_yaml/result_{id}_{timestamp}/
    # 3. 更新 RunResult.path，status=Ready
    # 4. 确定要执行的用例 ID 列表
    # 5. 提交 Celery 任务 run_suite_task.delay()
    # 6. 立即返回 RunResult 对象
    return result
```

**tasks.py（Celery 任务）：**
```python
@app.task
def run_suite_task(result_id, case_ids, initial_context, max_retries, retry_delay, timeout_seconds, fail_strategy):
    # Worker 进程异步执行
    runner = SuiteRunner()
    runner.run(result_id, case_ids, initial_context, ...)
```

### 4.6 snippet/permissions.py（权限工具）

```python
class RolePermission(BasePermission):
    def __init__(self, code: str):  # 用法：RolePermission('case:list')
    
    def has_permission(self, request, view):
        user = request.user
        if user.is_staff or user.is_superuser:
            return True  # 管理员自动放行
        # 检查用户的所有角色是否包含该权限码
        return Permission.objects.filter(
            roles__users=user, code=self.code
        ).exists()
```

---

## 5. 前端架构详解

### 5.1 Pinia Store（user.js）

这是前端最核心的状态管理，存储：
```javascript
const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token'),     // 登录 Token
    userInfo: null,                           // 用户信息（含 profile）
    permissions: [],                          // 权限码列表，如 ['project:list', 'case:create']
    productLines: [],                         // 我的产品线列表
    currentProductLine: null,                 // 当前选中的产品线
  }),
  
  actions: {
    async fetchUserInfo()     // 拉取用户信息
    async fetchProductLines() // 拉取我的产品线列表
    async switchProductLine(pl)  // 切换产品线（存入 localStorage，刷新页面重新拉取数据）
    hasPermission(code)     // 检查是否有某个权限码
    logout()                // 清除 token 和所有状态
  }
})
```

**hasPermission 逻辑：**
```javascript
hasPermission(code) {
  // '*' 表示超级管理员，拥有所有权限
  return this.permissions.includes('*') || this.permissions.includes(code)
}
```

### 5.2 路由配置（router/index.js）

每个路由可配置 `meta.permission`：
```javascript
{
  path: 'cases',
  name: 'cases',
  meta: { permission: 'case:list' },  // 访问此页需要的权限码
  component: () => import('@/views/CaseView.vue')
}
```

**路由守卫（beforeEach）：**
```javascript
router.beforeEach((to, from, next) => {
  // 1. 未登录 → 跳登录页
  // 2. 已登录访问登录页 → 跳首页
  // 3. 检查 meta.permission
  const permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
  const hasPermission = permissions.includes('*') || permissions.includes(requiredPermission)
  if (!hasPermission) return next('/403')
  next()
})
```

### 5.3 Axios 请求封装（api/request.js）

```javascript
// 请求拦截器：自动加 Token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Token ${token}`
  return config
})

// 响应拦截器：统一处理错误
api.interceptors.response.use(
  response => response.data,  // 直接返回 data，省去 response.data
  error => {
    if (error.response?.status === 401) {
      // Token 过期，清除登录状态跳登录页
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

### 5.4 产品线切换器（LayoutView.vue Header）

```html
<!-- Header 右侧的产品线切换下拉 -->
<div v-if="userStore.productLines.length" class="product-line-switcher">
  <div class="pl-dropdown">
    <button class="pl-current">
      <span class="pl-dot"></span>  <!-- 绿色圆点 -->
      <span class="pl-name">{{ userStore.currentProductLine?.name }}</span>
      <span class="pl-arrow">▾</span>
    </button>
    <ul class="pl-menu">  <!-- hover 时显示 -->
      <li v-for="pl in userStore.productLines" @click="handleSwitchProductLine(pl)">
        {{ pl.name }}
        <span v-if="currentProductLine?.id === pl.id">✓</span>
      </li>
    </ul>
  </div>
</div>
```

切换时：
```javascript
const handleSwitchProductLine = async (pl) => {
  await userStore.switchProductLine(pl)  // 更新 store 和 localStorage
  router.go(0)  // 强制刷新页面，重新拉取当前产品线的数据
}
```

---

## 6. 核心业务流程

### 6.1 套件执行完整流程

```
前端：用户点击「运行套件」
  ↓
SuiteDetailView.vue → runSuite() → POST /api/suite/{id}/run/
  ↓
后端：SuiteViewSet.run() action
  ↓
Suite.run() 方法（suite/models.py）
  ├── 创建 RunResult（status=0 Init）
  ├── 创建独立目录 upload_yaml/result_{id}_{ts}/
  ├── 更新 RunResult（status=1 Ready，path=目录路径）
  ├── 确定用例 ID 列表（传参 or 套件默认）
  └── 提交 Celery 任务：run_suite_task.delay(result_id, case_ids, ...)
  ↓
立即返回 {result_id, status=1, path=...} 给前端

=== 异步：Celery Worker 进程 ===
run_suite_task（suite/tasks.py）
  ↓
SuiteRunner.run()（case_api/engine.py）
  ├── 更新 RunResult（status=2 Running）
  ├── 读取 Suite 配置（environment, suite_variables, suite_headers）
  ├── 初始化 ContextStore（Redis key: suite:{result_id}:context）
  │   写入：initial_context + environment.variables + suite_variables
  ├── 按 role 分三阶段执行：
  │   for phase in [setup, main, teardown]:
  │     for case in phase_cases（按 order 排序）:
  │       if not enabled: skip
  │       执行用例（execute_case）
  │         ├── 变量替换：把 ${var} 替换为 ContextStore 中的值
  │         ├── 合并 headers（环境 < 套件 < 用例）
  │         ├── 发送 HTTP 请求
  │         ├── 断言验证
  │         ├── 提取变量写入 ContextStore
  │         └── 失败时按 retry_count 重试
  │       if fail and fail_strategy=="stop": break
  ├── 更新 RunResult（status=3 Reporting）
  ├── 生成 Allure 报告：allure generate results -o report
  └── 更新 RunResult（status=4 Done，is_pass=all_passed）

=== 前端轮询 ===
SuiteDetailView.vue 每 2 秒查询 GET /api/suite/result/{result_id}/
当 status==4 时停止轮询，显示「查看报告」按钮
```

### 6.2 变量提取与注入机制

**场景：登录接口 → 获取用户信息接口**

```
步骤1：配置登录用例的 extract
Case（登录用例）.extract = {
  "token": ["json", "$.data.token", 0],
  "userId": ["json", "$.data.user.id", 0]
}

步骤2：执行登录用例
发送 POST /api/login → 收到响应 {"data": {"token": "abc123", "user": {"id": 5}}}

步骤3：引擎提取变量写入 ContextStore
ContextStore.set("token", "abc123")
ContextStore.set("userId", 5)
Redis key: suite:42:context → {"token": "abc123", "userId": 5}

步骤4：配置获取用户信息用例
Case（用户信息用例）.api_args = {
  "headers": {"Authorization": "Bearer ${token}"},
  "params": {"id": "${userId}"}
}

步骤5：执行前变量替换
"Bearer ${token}" → "Bearer abc123"
"${userId}" → "5"

步骤6：发送 GET /api/users?id=5，Header: Authorization: Bearer abc123
```

### 6.3 服务注册表工作原理

```
问题：同一套接口需要在测试环境、预发环境分别运行
  测试环境用户服务：https://user.test.example.com
  预发环境用户服务：https://user.staging.example.com

解决方案：

1. 在服务注册表创建服务
   Service(key="user-svc", name="用户服务", project=xxx)

2. 接口 URL 只写路径，service_key 填 user-svc
   Endpoint(url="/api/users", service_key="user-svc")
   → 前端展示：{user-svc}/api/users

3. 在测试环境配置
   Environment(name="测试环境").urls = [
     {"var": "user-svc", "url": "https://user.test.example.com", "name": "用户服务"}
   ]

4. 在预发环境配置
   Environment(name="预发环境").urls = [
     {"var": "user-svc", "url": "https://user.staging.example.com", "name": "用户服务"}
   ]

5. 套件选择不同环境运行，用例零修改
   套件执行时引擎查找 environment.urls 中 var=="user-svc" 的条目
   拼接完整 URL：https://user.test.example.com/api/users
```

### 6.4 断言机制

```python
# validate 字段支持的断言类型
validate = {
  "equals": {
    "状态码200": [200, "status_code"],       # 响应状态码 == 200
    "返回成功": ["success", "json.code"],    # json响应中 code 字段 == "success"
    "数据非空": [True, "json.data"],         # json.data == True（非空）
  },
  "contains": {
    "包含token": ["token", "json.data"],    # json.data 中包含字符串 "token"
  },
  "startswith": {
    "消息前缀": ["登录", "json.message"],    # json.message 以 "登录" 开头
  }
}

# 响应属性路径写法
# status_code    → response.status_code（HTTP 状态码）
# json.xxx       → response.json()["xxx"]
# json.data.id   → response.json()["data"]["id"]
# headers.xxx    → response.headers["xxx"]
# text           → response.text
```

---

## 7. 权限系统详解

### 7.1 权限码体系

所有权限码格式：`模块:操作`

| 模块 | 权限码 | 说明 |
|------|--------|------|
| project | project:list | 查看项目列表 |
| project | project:create | 新建项目 |
| project | project:update | 修改项目 |
| project | project:delete | 删除项目 |
| endpoint | endpoint:list | 查看接口列表 |
| case | case:list | 查看用例列表 |
| case | case:create | 新建用例 |
| suite | suite:run | 执行套件 |
| environment | environment:list | 查看环境 |
| system | system:manage | 系统管理 |
| product_line | product_line:list | 查看产品线 |
| product_line | product_line:create | 新建产品线 |
| product_line | product_line:manage_members | 管理成员 |

### 7.2 权限检查路径

```
请求到达 → DRF 认证（TokenAuthentication）→ 权限检查（RolePermission）

管理员（is_staff=True）→ 直接放行
普通用户 → SQL查询：
  SELECT 1 FROM system_permission sp
  JOIN system_role_permissions srp ON srp.permission_id = sp.id
  JOIN system_user_role sur ON sur.role_id = srp.role_id
  WHERE sur.user_id = {user.id} AND sp.code = '{required_code}'
  LIMIT 1
```

### 7.3 前端双重鉴权

```
层1：路由守卫
  router.beforeEach → 检查 localStorage['permissions'] → 无权限跳 /403
  层2：菜单显示
  v-if="hasPermission('xxx:list')" → 无权限菜单不显示

注意：permissions 存储在 localStorage 中，格式为 JSON 数组：
["project:list", "endpoint:list", "case:list", "case:create", ...]
管理员的 permissions = ["*"]（通配符，hasPermission 永远返回 true）

---

## 8. 产品线多租户机制

### 8.1 模型设计

```
ProductLine（产品线）
  ↓ 1:N
ProductLineMember（成员关系）
  ├── user FK → User
  ├── product_line FK → ProductLine
  └── role FK → Role（该用户在本产品线的角色，可与全局角色不同）

Project.product_line FK → ProductLine
（所有接口/用例/套件/环境 通过 Project 间接关联产品线）
```

### 8.2 数据过滤机制

前端切换产品线时，所有列表请求都会带上 `product_line` 参数：
```javascript
// 示例：加载接口列表
const params = { page: 1, page_size: 10 }
if (userStore.currentProductLine) {
  params.product_line = userStore.currentProductLine.id
}
getEndpoints(params)
```

后端 ViewSet 的 `get_queryset` 方法统一处理：
```python
# 接口 ViewSet
def get_queryset(self):
    qs = Endpoint.objects.all()
    product_line_id = self.request.query_params.get('product_line')
    if product_line_id:
        qs = qs.filter(project__product_line_id=product_line_id)
    return qs

# 套件 ViewSet
def get_queryset(self):
    qs = Suite.objects.all()
    product_line_id = self.request.query_params.get('product_line')
    if product_line_id:
        qs = qs.filter(project__product_line_id=product_line_id)
    return qs
```

### 8.3 服务注册表特殊处理

服务注册表不按产品线过滤（全局可见），但展示时带产品线标签：
- 后端 `ServiceSerializer.get_product_line_name` 返回 `project.product_line.name`
- 前端表格显示「产品线」列，用绿色标签展示
- 新增/编辑环境时 URL 下拉可以看到所有服务

### 8.4 产品线级权限

`ProductLineMember.role` 可以与用户的全局角色不同：
- 用户 A 全局角色是「测试人员」
- 但在产品线 B 中，角色是「测试负责人」（有更高权限）

前端切换产品线时重新拉取该产品线的权限码：
```javascript
async switchProductLine(pl) {
  this.currentProductLine = pl
  localStorage.setItem('currentProductLine', JSON.stringify(pl))
  // 重新拉取该产品线的权限（调用产品线权限 API）
  await this.fetchProductLinePermissions(pl.id)
}
```

---

## 9. 环境与服务注册表

### 9.1 环境配置结构

```json
// Environment.urls 字段示例
[
  {
    "var": "user-svc",
    "url": "https://user.test.example.com",
    "name": "用户服务"
  },
  {
    "var": "order-svc",
    "url": "https://order.test.example.com",
    "name": "订单服务"
  }
]

// Environment.variables 字段示例
{
  "timeout": "30",
  "max_retry": "3",
  "test_user": "test@example.com"
}

// Environment.headers 字段示例
{
  "X-App-Version": "1.0.0",
  "X-Platform": "test"
}

// Environment.mock_rules 字段示例
[
  {
    "url": "https://pay.example.com/pay",
    "method": "POST",
    "status": 200,
    "body": {"code": 0, "msg": "支付成功"},
    "delay": 500
  }
]
```

### 9.2 变量优先级（从低到高）

```
优先级1（最低）：Environment.variables（环境变量）
优先级2：Environment GlobalVariable（全局变量表）
优先级3：Suite.suite_variables（套件变量）
优先级4：用例 extract 提取的变量（覆盖所有上游）
优先级5（最高）：initial_context（执行时手动传入）
```

### 9.3 请求头优先级（从低到高）

```
优先级1：Environment.headers（环境全局请求头）
优先级2：Suite.suite_headers（套件请求头）
优先级3：Endpoint.headers（接口默认请求头）
优先级4（最高）：Case.api_args.headers（用例级请求头）
```

---

## 10. 测试执行引擎

### 10.1 用例执行单元（execute_case）

```python
def execute_case(case, context_store, suite_headers, env_headers):
    # 1. 合并参数：api_args 覆盖 endpoint 默认参数
    merged_args = merge(endpoint.params, case.api_args)
    
    # 2. 变量替换：把 ${var} 替换为 context 中的实际值
    replaced_args = replace_variables(merged_args, context_store)
    
    # 3. 合并请求头（优先级：用例 > 套件 > 环境）
    final_headers = merge(env_headers, suite_headers, replaced_args.get('headers'))
    
    # 4. 解析服务URL：service_key → 实际域名
    base_url = resolve_service_url(endpoint.service_key, environment)
    full_url = base_url + endpoint.url
    
    # 5. 发送 HTTP 请求
    response = requests.request(
        method=endpoint.method,
        url=full_url,
        headers=final_headers,
        params=replaced_args.get('params'),
        json=replaced_args.get('json'),
        data=replaced_args.get('data'),
        timeout=timeout_seconds or None
    )
    
    # 6. 提取变量写入 ContextStore
    for var_name, rule in case.extract.items():
        value = extract_value(response, rule)  # jsonpath/regex
        context_store.set(var_name, value)
    
    # 7. 执行断言
    for assert_type, assert_rules in case.validate.items():
        for desc, (expected, attr_path) in assert_rules.items():
            actual = get_response_attr(response, attr_path)
            assert_func[assert_type](actual, expected, desc)
    
    # 8. 记录 Allure 报告数据
    allure.attach(response.text, name='响应体')
    allure.attach(str(final_headers), name='请求头')
```

### 10.2 三阶段执行（setup/main/teardown）

```python
api_items = suite.get_case_api_items()  # 已按 role_weight + order 排序

# 分组
setup_cases    = [i for i in api_items if i.role == 'setup']
main_cases     = [i for i in api_items if i.role == 'main']
teardown_cases = [i for i in api_items if i.role == 'teardown']

# 执行
for phase_name, phase_cases in [('setup', setup_cases), ('main', main_cases), ('teardown', teardown_cases)]:
    for item in phase_cases:
        try:
            execute_case(item.case_api, ...)
        except AssertionError:
            is_pass = False
            if fail_strategy == 'stop' and phase_name == 'main':
                break
```

### 10.3 重试机制

```python
for attempt in range(max_retries + 1):  # 0次重试 = 只执行1次
    try:
        execute_case(case, ...)
        break  # 成功则跳出重试循环
    except AssertionError as e:
        if attempt < max_retries:
            time.sleep(retry_delay)
            continue  # 继续重试
        raise  # 重试耗尽，抛出异常
```

### 10.4 Allure 报告生成

```python
# 执行时收集 Allure 原始数据到 results/ 目录
pytest.main(['--alluredir', str(results_dir), ...])

# 执行完毕生成 HTML 报告
subprocess.run([
    'allure', 'generate',
    str(results_dir),
    '-o', str(report_dir),
    '--clean'
])

# 报告访问地址（通过 Django 静态文件服务）
# /api/suite/static/result_42_1750000000/report/index.html
```

---

## 11. API 接口规范

### 11.1 统一响应格式

所有接口返回 `customPagination.py` 定义的统一格式：

```json
// 列表响应
{
  "code": 200,
  "message": "success",
  "result": {
    "list": [...],
    "page": 1,
    "pageCount": 5,
    "itemCount": 48
  }
}

// 单对象响应
{
  "code": 200,
  "message": "success",
  "result": { "id": 1, "name": "xxx", ... }
}

// 错误响应
{
  "code": 400,
  "message": "项目名称不能为空"
}
```

### 11.2 主要 API 路由

```
# 账号
POST   /api/account/profile/login/          登录
GET    /api/account/profile/profile/         我的信息
POST   /api/account/profile/modify/          修改信息
POST   /api/account/profile/img_upload/      上传头像

# 产品线
GET    /api/product_line/                    产品线列表
POST   /api/product_line/                    新建产品线
GET    /api/product_line/my_product_lines/   我的产品线
GET    /api/product_line/{id}/permissions/   产品线权限码

# 项目
GET    /api/project/?product_line=1          项目列表（产品线过滤）
POST   /api/project/                         新建项目
GET    /api/project/{id}/                    项目详情
PUT    /api/project/{id}/                    修改项目
DELETE /api/project/{id}/                   删除项目

# 接口
GET    /api/case_api/endpoint/               接口列表
POST   /api/case_api/endpoint/               新建接口
GET    /api/case_api/endpoint/{id}/          接口详情

# 用例
GET    /api/case_api/case/                   用例列表
POST   /api/case_api/case/                   新建用例

# 套件
GET    /api/suite/suite/                     套件列表
POST   /api/suite/suite/                     新建套件
POST   /api/suite/suite/{id}/run/            执行套件
GET    /api/suite/result/                    执行结果列表
GET    /api/suite/result/{id}/              执行结果详情
DELETE /api/suite/result/{id}/              删除执行结果
POST   /api/suite/suite/{id}/webhook/?key=  WebHook 触发

# 环境管理
GET    /api/suite/environment/               环境列表
POST   /api/suite/environment/               新建环境
GET    /api/suite/service/                   服务注册表
POST   /api/suite/service/                   新建服务

# 系统管理
GET    /api/system/role/                     角色列表
POST   /api/system/role/{id}/set_permissions/ 配置角色权限
GET    /api/system/permission/grouped/       权限码（按模块分组）
```

---

## 12. 前端页面与组件

### 12.1 主布局（LayoutView.vue）

```
整体布局：
┌──────────┬──────────────────────────────────────┐
│ Sidebar  │ Header（标题 + 产品线切换器 + 用户头像）│
│ (240px)  ├──────────────────────────────────────┤
│ 导航菜单  │ <router-view />（页面内容区域）          │
│          │                                      │
└──────────┴──────────────────────────────────────┘

导航菜单项（均有 v-if 权限控制）：
- 首页 (dashboard) — 无需权限
- 项目管理 (project:list)
- 接口管理 (endpoint:list)
- 用例管理 (case:list)
- 套件管理 (suite:list)
- 环境管理 (environment:list)
- 执行结果 (result:list)
- 个人信息 (user:list)
- 系统管理 (system:manage)
- 产品线管理 (product_line:list)
```

### 12.2 典型页面结构（以 CaseView.vue 为例）

```javascript
// 页面结构模式（所有列表页基本一致）

// 1. toolbar：新建按钮 + 刷新 + 批量删除
// 2. filter-bar：搜索框 + 筛选条件
// 3. table-container：数据表格 + 分页
// 4. modal：新建/编辑弹窗（v-if 控制显示）

// script setup 模式（所有页面统一用 Composition API）
const items = ref([])          // 列表数据
const showDialog = ref(false)  // 弹窗开关
const editingItem = ref(null)  // 当前编辑项（null=新建）
const formData = ref({})       // 表单数据
const errors = ref({})         // 字段级错误
const pagination = ref({ page:1, pageCount:1, itemCount:0 })

// 生命周期
onMounted(() => { loadItems() })

// 加载数据（带产品线过滤）
const loadItems = async (page=1) => {
  const params = { page, page_size: 10 }
  if (userStore.currentProductLine) params.product_line = userStore.currentProductLine.id
  const res = await getItems(params)
  items.value = res.result?.list || []
  pagination.value = { page: res.result?.page, ... }
}
```

### 12.3 全局确认弹框（useConfirm）

```javascript
// composables/useConfirm.js 提供全局确认弹框
import { confirm } from '@/composables/useConfirm'

// 使用方式（在任何组件中）
const deleteItem = async (id) => {
  const confirmed = await confirm('确定要删除吗？', { type: 'danger' })
  if (!confirmed) return
  await deleteApi(id)
}
// confirm() 返回 Promise<boolean>
// type: 'danger'（红色）/ 'warning'（黄色）/ 'info'（蓝色）
```

`ConfirmDialog.vue` 在 `LayoutView.vue` 中全局挂载一个，通过 `useConfirm` composable 的响应式状态驱动。

### 12.4 SuiteDetailView.vue（最复杂的页面）

```
页面分区：
1. 套件基本信息卡片（名称/描述/环境/运行类型）
2. 套件配置卡片（变量/请求头/超时/失败策略/重试）
3. 用例列表（SuiteCaseItem）
   - 支持 setup/main/teardown 分组显示
   - 支持拖拽排序（order 字段）
   - 支持启用/禁用单条用例
4. 执行面板
   - 「运行套件」按钮
   - 执行状态实时显示（轮询）
   - 「查看报告」按钮（iframe 嵌入 Allure 报告）
```

---

## 附录：常见开发操作

### 新增一个权限码

1. 在 `system/management/commands/init_permissions.py` 的 `PERMISSIONS` 列表中添加
2. 运行 `python manage.py init_permissions` 同步到数据库
3. 在系统管理页面给对应角色配置该权限
4. 在前端需要的菜单/路由/按钮加上 `v-if="hasPermission('xxx:yyy')"`

### 新增一个后端 ViewSet

```python
# 1. 定义 Serializer
class FooSerializer(serializers.ModelSerializer):
    class Meta:
        model = Foo
        fields = '__all__'

# 2. 定义 ViewSet
class FooViewSet(viewsets.ModelViewSet):
    serializer_class = FooSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [RolePermission('foo:list')()]
        elif self.action == 'create':
            return [RolePermission('foo:create')()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        qs = Foo.objects.all()
        # 加产品线过滤
        pl = self.request.query_params.get('product_line')
        if pl:
            qs = qs.filter(project__product_line_id=pl)
        return qs

# 3. 注册路由
router.register('foo', FooViewSet)
```

### 新增一个前端列表页

```javascript
// 1. 在 api/foo.js 定义 API
export const getFoos = (params) => api.get('/foo/', { params })
export const createFoo = (data) => api.post('/foo/', data)

// 2. 在 router/index.js 加路由
{
  path: 'foos',
  name: 'foos',
  meta: { permission: 'foo:list' },
  component: () => import('@/views/FooView.vue')
}

// 3. 在 LayoutView.vue 加菜单项
<router-link v-if="hasPermission('foo:list')" to="/foos" class="nav-item">
  <span class="icon">🔧</span>
  <span>Foo管理</span>
</router-link>
```

---

**文档版本**：基于 Tesla v1.0.2，最后更新 2026-03-17
