<template>
  <div class="page-header">
    <button class="page-back-btn" @click="handleBack">
      <ArrowLeftOutlined />
      {{ text }}
    </button>
  </div>
</template>

<script setup>
import { ArrowLeftOutlined } from '@ant-design/icons-vue'

const props = defineProps({
  text: {
    type: String,
    default: '返回'
  }
})

const emit = defineEmits(['back'])

const handleBack = () => {
  emit('back')
}
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
}

.page-back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.page-back-btn:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}
</style>
