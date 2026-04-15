<template>
  <div class="login-container">
    <!-- 左侧装饰区域 -->
    <div class="login-decoration">
      <div class="decoration-content">
        <div class="logo-section">
          <div class="logo-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94 0 .31.04.64.09.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
            </svg>
          </div>
          <h1 class="platform-title">Tesla测试平台</h1>
          <p class="platform-subtitle">企业级自动化测试管理系统</p>
        </div>
        <div class="features-section">
          <div class="feature-item">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>自动化测试执行</h3>
              <p>支持API和UI自动化测试，提高测试效率</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>智能报告分析</h3>
              <p>可视化测试报告，智能分析测试结果</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 15c1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3 1.34 3 3 3zm0-12c5.52 0 10 4.48 10 10s-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2zm0 18c4.42 0 8-3.58 8-8s-3.58-8-8-8-8 3.58-8 8 3.58 8 8 8z"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>团队协作管理</h3>
              <p>多项目管理，支持团队协作与权限控制</p>
            </div>
          </div>
        </div>
        <div class="quote-section">
          <p class="quote-text">"高质量代码从高效测试开始"</p>
          <p class="quote-author">—— Tesla自动化测试平台</p>
        </div>
      </div>
    </div>

    <!-- 右侧登录区域 -->
    <div class="login-content">
      <div class="login-card">
        <div class="login-header">
          <h2>欢迎回来</h2>
          <p>请登录您的账号以继续使用Tesla平台</p>
        </div>

        <a-form
          ref="formRef"
          :model="formState"
          :rules="formRules"
          layout="vertical"
          class="login-form"
          @finish="handleLogin"
        >
          <a-form-item label="用户名" name="username" required>
            <a-input
              v-model:value="formState.username"
              placeholder="请输入用户名"
              size="large"
              allow-clear
            >
              <template #prefix>
                <UserOutlined style="color: rgba(0, 0, 0, 0.25)" />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item label="密码" name="password" required>
            <a-input-password
              v-model:value="formState.password"
              placeholder="请输入密码"
              size="large"
              allow-clear
            >
              <template #prefix>
                <LockOutlined style="color: rgba(0, 0, 0, 0.25)" />
              </template>
            </a-input-password>
          </a-form-item>

          <a-form-item>
            <a-checkbox v-model:checked="formState.remember">记住密码</a-checkbox>
            <a-button type="link" style="float: right; padding: 0;">忘记密码？</a-button>
          </a-form-item>

          <a-form-item>
            <a-button
              type="primary"
              html-type="submit"
              size="large"
              :loading="loading"
              block
              class="login-btn"
            >
              {{ loading ? '登录中...' : '登录' }}
            </a-button>
          </a-form-item>

          <div v-if="error" class="error-message">
            <AlertOutlined style="margin-right: 8px;" />
            {{ error }}
          </div>
        </a-form>

        <div class="login-footer">
          <p>还没有账号？<a-button type="link" style="padding: 0;">联系管理员开通</a-button></p>
          <p class="version-info">Tesla测试平台 v1.0.0</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  UserOutlined,
  LockOutlined,
  AlertOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const error = ref('')

const formState = reactive({
  username: '',
  password: '',
  remember: false
})

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6到20个字符之间', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const success = await userStore.login(formState.username, formState.password)
    if (success) {
      router.push('/')
    } else {
      error.value = '用户名或密码错误'
    }
  } catch (err) {
    console.error('登录失败:', err)
    error.value = '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

/* 左侧装饰区域 */
.login-decoration {
  flex: 1;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  position: relative;
  overflow: hidden;
}

.login-decoration::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 30px 30px;
  animation: float 20s linear infinite;
  opacity: 0.3;
}

@keyframes float {
  0% {
    transform: translate(0, 0) rotate(0deg);
  }
  100% {
    transform: translate(30px, 30px) rotate(360deg);
  }
}

.decoration-content {
  max-width: 500px;
  width: 100%;
  z-index: 1;
}

.logo-section {
  text-align: center;
  margin-bottom: 60px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
  padding: 16px;
}

.logo-icon svg {
  width: 48px;
  height: 48px;
  fill: white;
}

.platform-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px;
  letter-spacing: 1px;
}

.platform-subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.features-section {
  margin-bottom: 60px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.feature-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon svg {
  width: 20px;
  height: 20px;
  fill: white;
}

.feature-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px;
}

.feature-content p {
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
  line-height: 1.5;
}

.quote-section {
  text-align: center;
}

.quote-text {
  font-size: 18px;
  font-weight: 500;
  font-style: italic;
  margin: 0 0 12px;
  position: relative;
}

.quote-text::before,
.quote-text::after {
  content: '"';
  font-size: 24px;
  font-weight: bold;
  opacity: 0.5;
}

.quote-author {
  font-size: 14px;
  opacity: 0.7;
  margin: 0;
}

/* 右侧登录区域 */
.login-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-card {
  width: 100%;
  max-width: 440px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  padding: 48px;
  animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1f1f1f;
  margin: 0 0 12px;
}

.login-header p {
  font-size: 14px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

.login-form {
  margin-bottom: 32px;
}

.login-form :deep(.ant-form-item-label) {
  font-weight: 500;
  margin-bottom: 8px;
}

.login-form :deep(.ant-input),
.login-form :deep(.ant-input-password) {
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 16px;
}

.login-form :deep(.ant-input-affix-wrapper) {
  border-radius: 10px;
  padding: 12px 16px;
}

.login-form :deep(.ant-input-affix-wrapper-focused) {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.login-form :deep(.ant-checkbox-wrapper) {
  font-size: 14px;
  color: #666;
}

.login-form :deep(.ant-btn-link) {
  font-size: 14px;
  color: #666;
}

.login-btn {
  border-radius: 10px;
  padding: 14px;
  font-size: 16px;
  font-weight: 600;
  height: auto;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.login-btn:active {
  transform: translateY(0);
}

.error-message {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  color: #ff4d4f;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
  margin-top: 16px;
  display: flex;
  align-items: center;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-footer {
  text-align: center;
  border-top: 1px solid #f0f0f0;
  padding-top: 24px;
}

.login-footer p {
  font-size: 14px;
  color: #666;
  margin: 0 0 12px;
}

.login-footer p:last-child {
  margin-bottom: 0;
}

.login-footer .ant-btn-link {
  padding: 0;
  font-size: 14px;
}

.version-info {
  font-size: 12px;
  color: #999;
  margin-top: 16px;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .login-container {
    flex-direction: column;
  }
  
  .login-decoration {
    padding: 40px;
    min-height: 300px;
  }
  
  .login-content {
    padding: 40px 20px;
  }
  
  .login-card {
    padding: 32px;
    margin-top: -60px;
    position: relative;
    z-index: 2;
  }
}

@media (max-width: 576px) {
  .login-decoration {
    padding: 30px 20px;
  }
  
  .decoration-content {
    max-width: 100%;
  }
  
  .logo-section {
    margin-bottom: 40px;
  }
  
  .logo-icon {
    width: 60px;
    height: 60px;
    padding: 12px;
  }
  
  .logo-icon svg {
    width: 36px;
    height: 36px;
  }
  
  .platform-title {
    font-size: 24px;
  }
  
  .platform-subtitle {
    font-size: 14px;
  }
  
  .features-section {
    margin-bottom: 40px;
  }
  
  .feature-item {
    padding: 16px;
  }
  
  .feature-content h3 {
    font-size: 14px;
  }
  
  .feature-content p {
    font-size: 12px;
  }
  
  .quote-text {
    font-size: 16px;
  }
  
  .quote-author {
    font-size: 12px;
  }
  
  .login-card {
    padding: 24px;
  }
  
  .login-header h2 {
    font-size: 24px;
  }
  
  .login-header p {
    font-size: 13px;
  }
  
  .login-form :deep(.ant-input),
  .login-form :deep(.ant-input-password),
  .login-form :deep(.ant-input-affix-wrapper) {
    padding: 10px 14px;
    font-size: 14px;
  }
  
  .login-btn {
    padding: 12px;
    font-size: 14px;
  }
}

@media (max-width: 360px) {
  .login-decoration {
    min-height: 250px;
  }
  
  .login-card {
    padding: 20px;
  }
  
  .login-header h2 {
    font-size: 20px;
  }
  
  .login-form {
    margin-bottom: 24px;
  }
  
  .error-message {
    font-size: 12px;
    padding: 10px 14px;
  }
}
</style>