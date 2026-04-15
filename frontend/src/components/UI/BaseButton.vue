<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
    ref="buttonRef"
  >
    <span v-if="loading" class="button-loading">
      <svg class="loading-spinner" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
        <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
      </svg>
    </span>
    
    <span v-if="$slots.icon && !loading" class="button-icon">
      <slot name="icon"></slot>
    </span>
    
    <span class="button-content">
      <slot>{{ label }}</slot>
    </span>
    
    <span v-if="$slots.suffix" class="button-suffix">
      <slot name="suffix"></slot>
    </span>
  </button>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'button',
    validator: (value) => ['button', 'submit', 'reset'].includes(value)
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'outline', 'ghost', 'danger', 'link'].includes(value)
  },
  size: {
    type: String,
    default: 'middle',
    validator: (value) => ['small', 'middle', 'large'].includes(value)
  },
  disabled: Boolean,
  loading: Boolean,
  block: Boolean,
  label: String,
  rounded: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

const buttonRef = ref(null)

const buttonClasses = computed(() => {
  const classes = ['base-button']
  classes.push(`variant-${props.variant}`)
  classes.push(`size-${props.size}`)
  if (props.block) classes.push('block')
  if (props.rounded) classes.push('rounded')
  if (props.disabled) classes.push('disabled')
  if (props.loading) classes.push('loading')
  return classes
})

const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}

defineExpose({
  focus: () => buttonRef.value?.focus(),
  blur: () => buttonRef.value?.blur()
})
</script>

<style scoped>
.base-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs, 8px);
  border: 1px solid transparent;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  white-space: nowrap;
  outline: none;
}

.base-button:focus-visible {
  outline: 2px solid var(--color-focus-blue, #3898ec);
  outline-offset: 2px;
}

.base-button.disabled,
.base-button.loading {
  cursor: not-allowed;
  opacity: 0.6;
}

/* 尺寸变体 */
.base-button.size-small {
  padding: var(--space-xs, 8px) var(--space-sm, 12px);
  font-size: var(--font-size-caption, 14px);
  min-height: 32px;
}

.base-button.size-middle {
  padding: var(--space-sm, 12px) var(--space-md, 16px);
  font-size: var(--font-size-body, 17px);
  min-height: 40px;
}

.base-button.size-large {
  padding: var(--space-md, 16px) var(--space-lg, 20px);
  font-size: var(--font-size-body-lg, 19px);
  min-height: 48px;
}

/* 圆角 */
.base-button.rounded {
  border-radius: var(--radius-generous, 10px);
}

/* 块级按钮 */
.base-button.block {
  display: flex;
  width: 100%;
}

/* 变体样式 */
.base-button.variant-primary {
  background: linear-gradient(135deg, var(--color-terracotta-brand, #c96442), var(--color-coral-accent, #d97757));
  color: var(--color-ivory, #faf9f5);
  border: none;
}

.base-button.variant-primary:hover:not(.disabled):not(.loading) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(201, 100, 66, 0.3);
}

.base-button.variant-primary:active:not(.disabled):not(.loading) {
  transform: translateY(0);
}

.base-button.variant-secondary {
  background-color: var(--color-warm-sand, #e8e6dc);
  color: var(--color-text-primary, #4d4c48);
  border-color: var(--color-border-warm, #e8e6dc);
}

.base-button.variant-secondary:hover:not(.disabled):not(.loading) {
  background-color: var(--color-border-cream, #f0eee6);
}

.base-button.variant-outline {
  background-color: transparent;
  color: var(--color-terracotta-brand, #c96442);
  border-color: var(--color-terracotta-brand, #c96442);
}

.base-button.variant-outline:hover:not(.disabled):not(.loading) {
  background-color: rgba(201, 100, 66, 0.05);
}

.base-button.variant-ghost {
  background-color: transparent;
  color: var(--color-text-primary, #4d4c48);
  border-color: transparent;
}

.base-button.variant-ghost:hover:not(.disabled):not(.loading) {
  background-color: var(--color-warm-sand, #e8e6dc);
}

.base-button.variant-danger {
  background-color: var(--color-error-crimson, #b53333);
  color: var(--color-ivory, #faf9f5);
  border: none;
}

.base-button.variant-danger:hover:not(.disabled):not(.loading) {
  background-color: #9c2b2b;
}

.base-button.variant-link {
  background-color: transparent;
  color: var(--color-terracotta-brand, #c96442);
  border-color: transparent;
  text-decoration: underline;
  padding: 0;
  min-height: auto;
}

.base-button.variant-link:hover:not(.disabled):not(.loading) {
  color: var(--color-coral-accent, #d97757);
  text-decoration: none;
}

/* 图标 */
.button-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-icon svg {
  width: 16px;
  height: 16px;
}

.base-button.size-small .button-icon svg {
  width: 14px;
  height: 14px;
}

.base-button.size-large .button-icon svg {
  width: 18px;
  height: 18px;
}

/* 加载状态 */
.button-loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.base-button.size-small .loading-spinner {
  width: 14px;
  height: 14px;
}

.base-button.size-large .loading-spinner {
  width: 18px;
  height: 18px;
}

/* 内容区域 */
.button-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

.button-suffix {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>