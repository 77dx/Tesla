# Tesla 测试平台

## 📖 项目简介
<<<<<<< HEAD

Tesla 是一个基于 Django + Vue3 的自动化测试平台，覆盖接口用例管理、测试套件编排、异步执行、结果追踪与报告查看。

> 当前版本已支持 **产品线级资产共享**、**项目/迭代引用执行**、**执行结果按范围隔离**、**执行快照追溯**、**异步导入任务**。

---

## ✨ 核心能力（最新）
=======
Tesla 是一个基于 Django + Vue3 的接口自动化测试管理平台，提供项目管理、接口管理、用例管理、测试套件管理和执行结果查看等功能。
>>>>>>> d2b52625c2f7c2c0df12fa295420ab6a0dd118e4

- 🚀 **异步执行**：基于 Celery + Redis，提交后立即返回 `result_id`
- 🔁 **并发执行**：多套件可并行执行
- 🧩 **产品线资产池**：`Case/Endpoint/Suite` 支持产品线维度归属与复用
- 🔗 **引用关系执行**：
  - 项目可引用用例/套件（`ProjectCaseRef` / `ProjectSuiteRef`）
  - 迭代可引用用例/套件（`SprintCaseRef` / `SprintSuiteRef`）
- 🎯 **范围隔离执行**：执行结果支持 `scope_type` + `scope_id`（project/sprint）
- 🧾 **执行快照**：执行时固化 case 内容与版本，支持回溯
- 📥 **异步导入**：支持 CSV/Excel 导入用例并后台处理（`ImportJob`）
- 📊 **报告与日志**：执行日志实时刷新，支持 Allure 报告

---

## 🧱 功能模块

| 模块 | 功能 | 状态 |
|------|------|------|
| 账户管理 | 用户登录、信息管理 | ✅ |
| 产品线管理 | 产品线与成员权限控制 | ✅ |
| 项目管理 | 项目 CRUD、引用关系、项目级执行 | ✅ |
| 迭代管理 | Sprint CRUD、需求管理、迭代级执行 | ✅ |
| 接口管理 | Endpoint CRUD、接口归属产品线 | ✅ |
| 用例管理 | Case CRUD、版本号、引用关系 | ✅ |
| 套件管理 | Suite CRUD、运行配置、手动/定时/Webhook | ✅ |
| 执行结果 | 按 scope 隔离查询、状态追踪、报告查看 | ✅ |
| 执行快照 | 记录当次执行 case 内容/version | ✅ |
| 导入任务 | 异步导入用例任务管理 | ✅ |

---

## 🏗️ 技术栈

### 后端

- Django 4.2
- Django REST Framework
- Celery
- Redis
- django-q（定时任务）
- Allure（报告）

### 前端

- Vue 3（Composition API）
- Vue Router 4
- Pinia
- Axios
- Vite

---

## 🚀 快速开始

## 环境要求

- Python 3.8+
- Node.js 18+
- Redis 6+
- MySQL（或项目配置中的数据库）

## 安装

```bash
git clone <repository-url>
cd Tesla
```

### 后端依赖

```bash
pip install -r requirements.txt
```

### 前端依赖

```bash
cd frontend
npm install
cd ..
```

### 数据库迁移

```bash
cd backend
python manage.py migrate
```

### 创建管理员

```bash
python manage.py createsuperuser
```

---

## ▶️ 启动服务

在不同终端分别执行：

### 1) 启动 Redis

```bash
redis-server
```

### 2) 启动 Django

```bash
cd backend
python manage.py runserver
```

### 3) 启动 Celery Worker

```bash
cd backend
celery -A Tesla worker -l info
```

### 4) 启动 定时调度任务
```bash
cd backend
python manage.py run_suite_scheduler


### 5) 启动前端
```bash
cd frontend
npm run dev
```

访问地址：

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000/api
- Swagger：http://localhost:8000/api/schema/swagger/

---

## 🧭 新能力使用说明

## 1. 产品线资产共享

- `Endpoint`、`Case`、`Suite` 均支持 `product_line`
- 同产品线下可跨项目复用资产

## 2. 项目/迭代引用关系

- 项目：
  - `project-case-ref`
  - `project-suite-ref`
- 迭代：
  - `sprint-case-ref`
  - `sprint-suite-ref`

前端页面已支持“引用用例/引用套件”的基础弹窗操作。

## 3. 执行范围隔离

`RunResult` 新增：

- `scope_type`：`project` / `sprint`
- `scope_id`
- `product_line`
- `trigger_source`

结果页可按 `scope_type/scope_id/product_line` 过滤。

## 4. 执行快照追溯

执行时会生成：

- `ExecutionSnapshot`
- `ExecutionCaseSnapshot`

结果详情页可查看当次执行固化的 case 快照数据（含 version）。

## 5. 异步导入用例

- 上传 CSV/Excel -> 创建 `ImportJob`
- 调用 `start` 触发异步任务
- 导入结果写入任务统计字段（total/success/failed/detail）

---

## 📡 关键接口（新增/更新）

> 以下仅列核心新增能力，完整接口以 Swagger 为准。

### 项目相关

- `POST /api/project/project/{id}/run/` 项目级执行
- `GET/POST /api/project/project-case-ref/`
- `GET/POST /api/project/project-suite-ref/`

### 迭代相关

- `POST /api/project/sprint/{id}/run/` 迭代级执行
- `GET/POST /api/project/sprint-case-ref/`
- `GET/POST /api/project/sprint-suite-ref/`

### 执行结果与快照

- `GET /api/suite/runresult/`（支持 scope/product_line 过滤）
- `GET /api/suite/execution-snapshot/`

### 导入任务

- `GET/POST /api/suite/import-job/`
- `POST /api/suite/import-job/upload_case_file/`
- `POST /api/suite/import-job/{id}/start/`

---

## 🧪 检查与验证

### Django 检查

```bash
cd backend
python manage.py check
```

### 迁移（模型变更后）

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

---

## 🛠️ 常见问题

### 1) 提交执行后无结果更新

通常是 Celery Worker 未启动：

```bash
cd backend
celery -A Tesla worker -l info
```

### 2) 导入任务一直 pending

检查：

- Redis 是否正常
- Worker 是否连接同一 broker
- 上传文件路径是否可写

### 3) 权限返回 403

请确认当前用户已加入对应产品线（`ProductLineMember`）。

---

## 📚 相关文档

- `docs/快速开始指南.md`
- `docs/完整功能说明文档.md`
- `docs/Suite和Result模块详细说明.md`

---

## 📄 License
