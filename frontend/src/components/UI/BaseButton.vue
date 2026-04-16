<template>
  <button
    class="ui-btn"
    :class="[
      `ui-btn--${type}`,
      `ui-btn--${size}`,
      { 'ui-btn--loading': loading }
    ]"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <LoadingOutlined v-if="loading" class="ui-btn__icon" />
    <slot v-else name="icon" />
    <span class="ui-btn__text"><slot /></span>
  </button>
</template>

<script setup>
import { LoadingOutlined } from '@ant-design/icons-vue'

defineProps({
  type: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'ghost', 'danger', 'text'].includes(v)
  },
  size: {
    type: String,
    default: 'medium',
    validator: (v) => ['small', 'medium', 'large'].includes(v)
  },
  disabled: Boolean,
  loading: Boolean
})

defineEmits(['click'])
</script>

<style scoped>
.ui-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
  outline: none;
}

.ui-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ─── 类型 ─── */
.ui-btn--primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  color: white;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.ui-btn--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-primary-hover), var(--color-primary-active));
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}

.ui-btn--ghost {
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  border: 1.5px solid var(--color-border);
}

.ui-btn--ghost:hover:not(:disabled) {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.ui-btn--danger {
  background: var(--color-error);
  color: white;
  border: 1.5px solid var(--color-error);
}

.ui-btn--danger:hover:not(:disabled) {
  background: var(--color-error-hover);
  border-color: var(--color-error-hover);
}

.ui-btn--text {
  background: transparent;
  color: var(--color-primary);
  padding: 4px 8px;
}

.ui-btn--text:hover:not(:disabled) {
  background: var(--color-primary-bg);
}

/* ─── 尺寸 ─── */
.ui-btn--small {
  padding: 6px 12px;
  font-size: var(--text-xs);
}

.ui-btn--medium {
  padding: 10px 18px;
  font-size: var(--text-sm);
}

.ui-btn--large {
  padding: 12px 24px;
  font-size: var(--text-base);
}

/* ─── 图标 ─── */
.ui-btn__icon {
  font-size: 14px;
}

.ui-btn__icon--spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
