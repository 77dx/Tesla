<template>
  <div class="forbidden">
    <div class="content">
      <div class="code">403</div>
      <h2>无访问权限</h2>
      <p>您没有权限访问此页面，请联系管理员分配相应权限。</p>
      <div class="actions">
        <button @click="router.back()" class="btn btn-outline">返回上一页</button>
        <button @click="router.push('/dashboard')" class="btn btn-primary">回到首页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<style scoped>
.forbidden {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg, #f5f7fa);
}

.content {
  text-align: center;
  padding: 48px;
}

.code {
  font-size: 120px;
  font-weight: 800;
  color: var(--primary, #2c3e50);
  line-height: 1;
  opacity: 0.15;
  margin-bottom: 16px;
}

h2 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text, #2c3e50);
  margin-bottom: 12px;
}

p {
  color: var(--text-light, #7f8c8d);
  font-size: 15px;
  margin-bottom: 32px;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary, #2c3e50);
  color: white;
}

.btn-primary:hover {
  opacity: 0.85;
}

.btn-outline {
  background: transparent;
  color: var(--text, #2c3e50);
  border: 1px solid var(--border, #ddd);
}

.btn-outline:hover {
  background: var(--bg, #f5f7fa);
}
</style>
