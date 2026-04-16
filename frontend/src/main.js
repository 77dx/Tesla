import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import * as Icons from '@ant-design/icons-vue'
import App from './App.vue'
import router from './router'
import './assets/tesla-design-system.css' // Tesla 全新设计系统
import './assets/tesla-common.css' // 通用组件样式
import './assets/tesla-list-design.css' // 列表设计规范
import './assets/tesla-form-design.css' // 表单设计规范
import './assets/antd-theme.css' // Ant Design 主题覆盖
import 'ant-design-vue/dist/reset.css' // Ant Design 基础样式重置

const app = createApp(App)

// 注册所有Ant Design图标
for (const [key, component] of Object.entries(Icons)) {
  if (key.includes('Icon')) {
    app.component(key, component)
  }
}

app.use(createPinia())
app.use(router)
app.use(Antd)

app.mount('#app')