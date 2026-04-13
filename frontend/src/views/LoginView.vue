<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>鱼小七测试平台</h1>
        <p>接口自动化测试管理系统</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="请输入用户名"
            required
          />
        </div>
        
        <div class="form-group">
          <label>密码</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="请输入密码"
            required
          />
        </div>
        
        <button type="submit" class="btn btn-brand-terracotta btn-block" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
        
        <div v-if="error" class="error-message">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const success = await userStore.login(username.value, password.value)
    if (success) {
      router.push('/')
    } else {
      error.value = '用户名或密码错误'
    }
  } catch (err) {
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
  align-items: center;
  justify-content: center;
  background-color: var(--color-parchment);
  padding: var(--space-xl);
  position: relative;
  overflow: hidden;
}

/* 背景装饰元素 */
.login-container::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -30%;
  width: 80%;
  height: 150%;
  background: linear-gradient(135deg,
    rgba(201, 100, 66, 0.05) 0%,
    rgba(217, 119, 87, 0.03) 50%,
    transparent 100%);
  border-radius: 50%;
  z-index: 0;
}

.login-container::after {
  content: '';
  position: absolute;
  bottom: -40%;
  left: -20%;
  width: 70%;
  height: 120%;
  background: linear-gradient(135deg,
    transparent 0%,
    rgba(232, 230, 220, 0.08) 50%,
    rgba(245, 244, 237, 0.1) 100%);
  border-radius: 50%;
  z-index: 0;
}

.login-card {
  background-color: var(--color-ivory);
  border: 1px solid var(--color-border-cream);
  border-radius: var(--radius-maximum);
  padding: var(--space-5xl);
  width: 100%;
  max-width: 440px;
  box-shadow: var(--shadow-level-3);
  animation: card-appear 0.6s ease-out;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg,
    var(--color-terracotta-brand),
    var(--color-coral-accent));
  border-radius: var(--radius-maximum) var(--radius-maximum) 0 0;
}

@keyframes card-appear {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.login-header {
  text-align: center;
  margin-bottom: var(--space-4xl);
  padding-bottom: var(--space-xl);
  border-bottom: 1px solid var(--color-border-cream);
}

.login-header h1 {
  font-family: var(--font-family-heading);
  font-size: var(--font-size-subheading);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-md);  /* 从sm增加到md */
  line-height: var(--line-height-normal);  /* 从tight增加到normal */
}

.login-header p {
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: var(--line-height-body-relaxed);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-2xl);  /* 从xl增加到2xl */
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);  /* 从xs增加到sm */
}

.form-group label {
  font-family: var(--font-family-ui);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  letter-spacing: var(--letter-spacing-wide);
}

.form-group input {
  padding: var(--space-md) var(--space-lg);
  border: 1px solid var(--color-border-cream);
  border-radius: var(--radius-generous);
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body);
  color: var(--color-text-primary);
  background-color: var(--color-pure-white);
  transition: all 0.2s ease;
  outline: none;
}

.form-group input:focus {
  border-color: var(--color-focus-blue);
  box-shadow: 0 0 0 3px rgba(56, 152, 236, 0.15);
}

.form-group input::placeholder {
  color: var(--color-text-tertiary);
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body-sm);
}

.btn-block {
  width: 100%;
  padding: var(--space-md) var(--space-xl);
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-generous);
  margin-top: var(--space-xs);
  background-color: var(--color-terracotta-brand);
  color: var(--color-ivory);
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.btn-block:hover:not(:disabled) {
  background-color: var(--color-coral-accent);
  transform: translateY(-2px);
  box-shadow: var(--shadow-level-2);
}

.btn-block:active:not(:disabled) {
  transform: translateY(0);
}

.btn-block:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-block::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%, -50%);
  transform-origin: 50% 50%;
}

.btn-block:focus:not(:active)::after {
  animation: ripple 1s ease-out;
}

@keyframes ripple {
  0% {
    transform: scale(0, 0);
    opacity: 0.5;
  }
  100% {
    transform: scale(40, 40);
    opacity: 0;
  }
}

.error-message {
  font-family: var(--font-family-ui);
  font-size: var(--font-size-caption);
  color: var(--color-error-crimson);
  text-align: center;
  padding: var(--space-md);
  background-color: rgba(181, 51, 51, 0.08);
  border: 1px solid rgba(181, 51, 51, 0.2);
  border-radius: var(--radius-comfortable);
  margin-top: var(--space-sm);
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* 响应式设计 */
@media (max-width: 767px) {
  .login-container {
    padding: var(--space-md);
  }

  .login-card {
    padding: var(--space-3xl);
    border-radius: var(--radius-very-rounded);
    max-width: 100%;
  }

  .login-header h1 {
    font-size: var(--font-size-subheading-sm);
  }

  .login-header p {
    font-size: var(--font-size-body-sm);
  }

  .form-group input {
    padding: var(--space-sm) var(--space-md);
  }

  .btn-block {
    padding: var(--space-sm) var(--space-lg);
  }
}

@media (max-width: 479px) {
  .login-card {
    padding: var(--space-2xl);
    border-radius: var(--radius-generous);
  }

  .login-header {
    margin-bottom: var(--space-2xl);
    padding-bottom: var(--space-lg);
  }

  .login-form {
    gap: var(--space-lg);
  }
}
</style>
