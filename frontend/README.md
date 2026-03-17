# Tesla 测试平台 - 前端项目

基于 Vue 3 + Vite 构建的接口自动化测试管理系统前端。

## 技术栈

- Vue 3 - 渐进式 JavaScript 框架
- Vue Router - 官方路由管理器
- Pinia - 状态管理
- Axios - HTTP 客户端
- Vite - 下一代前端构建工具

## 项目结构

```
frontend/
├── src/
│   ├── api/           # API 接口封装
│   ├── assets/        # 静态资源
│   ├── components/    # 公共组件
│   ├── router/        # 路由配置
│   ├── stores/        # 状态管理
│   ├── views/         # 页面组件
│   ├── App.vue        # 根组件
│   └── main.js        # 入口文件
├── index.html         # HTML 模板
├── package.json       # 项目配置
└── vite.config.js     # Vite 配置
```

## 功能模块

- 🔐 用户登录认证
- 📊 仪表盘统计
- 📁 项目管理
- 🔗 接口管理
- 📝 用例管理
- 📦 测试套件管理
- 📈 执行结果查看

## 安装依赖

```bash
cd frontend
npm install
```

## 开发运行

```bash
npm run dev
```

访问 http://localhost:5173

## 构建生产版本

```bash
npm run build
```

## 后端配置

前端通过 Vite 代理与后端通信，确保后端服务运行在 `http://127.0.0.1:8000`

代理配置见 `vite.config.js`:
- `/api` - 后端 API 接口
- `/media` - 媒体文件
- `/reports` - 测试报告

## 默认账号

请使用后端已创建的用户账号登录。

## 注意事项

1. 确保后端服务已启动
2. 后端需要配置 CORS 允许跨域（已在 settings.py 中配置）
3. Token 认证方式使用 Django REST Framework 的 TokenAuthentication
