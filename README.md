# Tesla 测试平台
## 📖 项目简介

tar czf - -C /Users/cathy/python_project Tesla  | ssh Cathy@192.168.3.190 "cd /volume2/ssd_volume/projects && tar xzf -"

sudo tar czf - -C /Users/cathy/python_project/Tesla Dockerfile | ssh Cathy@192.168.3.190 "cd /volume2/ssd_volume/projects/Tesla && tar xzf -"

ssh Cathy@192.168.3.190

Tesla 是一个基于 Django + Vue3 的接口自动化测试管理平台，提供项目管理、接口管理、用例管理、测试套件管理和执行结果查看等功能。

### 核心特性

- 🚀 **异步执行**: 基于Celery的异步任务队列，不阻塞用户操作
- 🔄 **并发执行**: 支持多个测试套件同时执行，提高测试效率
- 🔒 **数据隔离**: 每次执行独立目录，完全隔离，互不干扰
- 📊 **实时跟踪**: 实时查看执行状态和进度
- 📈 **报告生成**: 自动生成Allure测试报告
- 🎯 **DAG调度**: 智能处理接口依赖关系

## 🎯 功能模块

| 模块 | 功能 | 状态 |
|------|------|------|
| 账户管理 | 用户登录、信息管理、密码修改 | ✅ |
| 系统管理 | 角色、部门、职位管理 | ✅ |
| 项目管理 | 项目CRUD、关联数据查看 | ✅ |
| 接口管理 | 接口CRUD、参数配置 | ✅ |
| 用例管理 | 用例CRUD、断言配置 | ✅ |
| 测试套件 | 套件CRUD、执行管理 | ✅ |
| 执行结果 | 结果查看、报告访问 | ✅ |
| 仪表盘 | 统计数据、快速操作 | ✅ |

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+
- Redis 6.0+
- Allure 2.0+

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd Tesla
```

#### 2. 安装后端依赖

```bash
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
```

#### 4. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. 创建超级用户

```bash
python manage.py createsuperuser
```

### 启动服务

#### 1. 启动Redis

```bash
redis-server
```

#### 2. 启动Django

```bash
python manage.py runserver
```

#### 3. 启动Celery Worker（重要！）

```bash
celery -A Tesla worker -l info
```

#### 4. 启动前端

```bash
cd frontend
npm run dev
```

#### 5. 访问系统

- 前端地址: http://localhost:5173
- 后端API: http://localhost:8000/api
- API文档: http://localhost:8000/api/schema/swagger/

### 默认账号

- 用户名: `keke`
- 密码: `123456`

## 📚 文档

### 用户文档
- [快速开始指南](docs/快速开始指南.md) - 新手入门
- [完整功能说明文档](docs/完整功能说明文档.md) - 详细功能说明

### 技术文档
- [Suite和Result模块详细说明](docs/Suite和Result模块详细说明.md) - 核心功能详解
- [前后端数据格式对接修复说明](docs/前后端数据格式对接修复说明.md) - 数据格式说明

### 测试文档
- [完整自测报告](docs/完整自测报告.md) - 全模块测试报告
- [测试报告](docs/测试报告.md) - 详细测试用例

### 交付文档
- [最终完整交付文档](docs/最终完整交付文档_v1.0.2.md) - 完整交付说明

## 🏗️ 技术架构

### 后端技术栈

- **框架**: Django 4.2
- **REST API**: Django REST Framework
- **认证**: Token Authentication
- **任务队列**: Celery
- **消息代理**: Redis
- **测试框架**: Pytest
- **报告工具**: Allure

### 前端技术栈

- **框架**: Vue 3 (Composition API)
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **HTTP客户端**: Axios
- **构建工具**: Vite

### 系统架构

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
┌──────▼──────┐
│  Vue 3 SPA  │
└──────┬──────┘
       │ REST API
┌──────▼──────┐
│   Django    │
└──────┬──────┘
       │
   ┌───┴───┬────────┬────────┐
   │       │        │        │
┌──▼──┐ ┌─▼──┐  ┌─▼──┐  ┌─▼────┐
│ DB  │ │Redis│ │Celery│ │Allure│
└─────┘ └────┘  └─────┘  └──────┘
```

## 🧪 测试

### 运行完整测试

```bash
python tests/test_full_automation.py
```

### 运行Suite和Result专项测试

```bash
python tests/test_suite_result.py
```

### 测试覆盖率

- 总测试项: 70+
- 成功率: 95%+
- 模块覆盖: 100%

## 📊 核心功能详解

### 异步执行

使用Celery任务队列实现异步执行，用户提交测试后立即返回，不阻塞操作。

```python
# 提交执行
result = suite.run()
# 立即返回result_id，后台异步执行
```

### 并发执行

支持多个测试套件同时执行，每个套件有独立的执行环境。

```
upload_yaml/
├── result_101_1234567890/  # 套件1
├── result_102_1234567891/  # 套件2（同时执行）
└── result_103_1234567892/  # 套件3（同时执行）
```

### 数据隔离

每次执行创建独立目录，包含：
- 独立的测试文件
- 独立的执行结果
- 独立的测试报告
- 独立的上下文变量

### DAG依赖调度

自动处理接口之间的依赖关系，按依赖顺序分波次执行。

```
Wave 1: [A, B]  # 无依赖，并行执行
  ↓
Wave 2: [C]     # 依赖A和B
  ↓
Wave 3: [D, E]  # 依赖C，并行执行
```

## 🔧 配置

### Django配置

```python
# settings.py

# 测试套件执行配置
SUITE_EXECUTION_BASE_DIR = BASE_DIR / 'upload_yaml'
MAX_CONCURRENT_SUITES = 6

# Celery配置
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
```

### 前端配置

```javascript
// vite.config.js

export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}
```

## 📈 性能指标

- API响应时间: < 200ms
- 页面加载时间: < 1s
- 并发执行能力: 6个套件
- 报告生成时间: < 30s

## 🐛 故障排查

### 问题1: 套件执行后无反应

**原因**: Celery Worker未启动  
**解决**: 
```bash
celery -A Tesla worker -l info
```

### 问题2: 报告未生成

**原因**: Allure未安装  
**解决**:
```bash
# macOS
brew install allure

# Ubuntu
apt-get install allure
```

### 问题3: Redis连接失败

**原因**: Redis未启动  
**解决**:
```bash
redis-server
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 联系方式

- 项目地址: /Users/cathy/python_project/Tesla
- 文档目录: docs/

## 🎉 更新日志

### v1.0.2 (2026-03-09)
- ✅ 完善Suite和Result模块核心功能
- ✅ 实现异步执行机制
- ✅ 实现并发执行支持
- ✅ 实现数据隔离机制
- ✅ 实现DAG依赖调度
- ✅ 创建专项测试脚本
- ✅ 生成详细技术文档

### v1.0.1 (2026-03-09)
- ✅ 修复登录跳转问题
- ✅ 完善接口管理模块
- ✅ 新增账户管理模块
- ✅ 新增系统管理模块
- ✅ 前后端数据格式完全对接
- ✅ 创建完整自测脚本

### v1.0.0 (2026-03-09)
- ✅ 完成所有核心模块开发
- ✅ 完成前端界面开发
- ✅ 完成API接口开发
- ✅ 完成基础测试

## ⭐ Star History

如果这个项目对你有帮助，请给一个Star！

---

**Made with ❤️ by Tesla Team**