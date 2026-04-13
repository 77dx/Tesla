<template>
  <div v-if="alertVisible" class="alert-overlay" @click.self="hideAlert">
    <div class="alert-dialog">
      <div class="alert-icon-wrap" :class="`icon-${alertOptions.type}`">
        <span class="alert-icon">{{ icons[alertOptions.type] }}</span>
      </div>
      <div class="alert-body">
        <div class="alert-title">{{ alertOptions.title }}</div>
        <div class="alert-message">{{ alertOptions.message }}</div>
      </div>
      <div class="alert-footer">
        <button class="btn btn-primary" @click="hideAlert">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAlert } from '@/composables/useAlert'
const { alertVisible, alertOptions, hideAlert } = useAlert()
const icons = { info: 'ℹ️', success: '✅', error: '❌', warning: '⚠️' }
</script>

<style scoped>
.alert-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn .2s ease;
}
.alert-dialog {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0,0,0,.18);
  width: 90%;
  max-width: 420px;
  overflow: hidden;
  animation: slideUp .22s ease;
  display: flex;
  flex-direction: column;
}
.alert-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28px 24px 0;
}
.alert-icon { font-size: 40px; line-height: 1; }
.alert-body {
  padding: 16px 28px 20px;
  text-align: center;
}
.alert-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text, #1a1a1a);
  margin-bottom: 8px;
}
.alert-message {
  font-size: 14px;
  color: var(--text-light, #666);
  line-height: 1.65;
  word-break: break-word;
}
.alert-footer {
  padding: 0 24px 24px;
  display: flex;
  justify-content: center;
}
.alert-footer .btn { min-width: 100px; }
@keyframes fadeIn  { from { opacity:0 } to { opacity:1 } }
@keyframes slideUp { from { opacity:0; transform:translateY(20px) } to { opacity:1; transform:translateY(0) } }
</style>
