<template>
  <div v-if="visible" class="confirm-dialog-overlay" @click.self="handleCancel">
    <div class="confirm-dialog">
      <div class="confirm-dialog-header">
        <h3>{{ title }}</h3>
      </div>
      <div class="confirm-dialog-content">
        <div class="confirm-icon" :class="type === 'danger' ? 'icon-danger' : 'icon-warning'">
          {{ type === 'danger' ? '⚠️' : 'ℹ️' }}
        </div>
        <p>{{ message }}</p>
      </div>
      <div class="confirm-dialog-footer">
        <button @click="handleCancel" class="btn btn-secondary">{{ cancelText }}</button>
        <button @click="handleConfirm" class="btn btn-primary">{{ confirmText }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '确认操作'
  },
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'warning',
    validator: (value) => ['warning', 'danger'].includes(value)
  },
  confirmText: {
    type: String,
    default: '确定'
  },
  cancelText: {
    type: String,
    default: '取消'
  }
})

const emit = defineEmits(['confirm', 'cancel'])

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.confirm-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.confirm-dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 480px;
  animation: slideUp 0.3s ease;
  overflow: hidden;
}

.confirm-dialog-header {
  padding: 24px 24px 0;
  border-bottom: 1px solid var(--border, #e0e0e0);
}

.confirm-dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text, #333);
}

.confirm-dialog-content {
  padding: 32px 24px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.confirm-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.icon-warning {
  background: #fff3cd;
  color: #856404;
}

.icon-danger {
  background: #f8d7da;
  color: #721c24;
}

.confirm-dialog-content p {
  margin: 0;
  font-size: 15px;
  line-height: 1.5;
  color: var(--text, #333);
  flex: 1;
}

.confirm-dialog-footer {
  padding: 0 24px 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border: 1px solid var(--border, #e0e0e0);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: white;
  color: var(--text, #333);
}

.btn-secondary:hover {
  background: #f5f5f5;
}

.btn-primary {
  background: var(--primary, #1890ff);
  color: white;
  border-color: var(--primary, #1890ff);
}

.btn-primary:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>