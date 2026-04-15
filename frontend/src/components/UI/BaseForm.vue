<template>
  <form :class="formClasses" @submit.prevent="handleSubmit">
    <slot></slot>
    
    <div v-if="showActions" class="form-actions">
      <slot name="actions">
        <BaseButton
          type="submit"
          :loading="submitting"
          :disabled="disabled"
          :block="layout === 'vertical'"
          size="large"
          variant="primary"
        >
          {{ submitText }}
        </BaseButton>
        
        <BaseButton
          v-if="showCancel"
          type="button"
          :disabled="submitting"
          :block="layout === 'vertical'"
          size="large"
          variant="ghost"
          @click="handleCancel"
        >
          {{ cancelText }}
        </BaseButton>
      </slot>
    </div>
  </form>
</template>

<script setup>
import { computed } from 'vue'
import BaseButton from './BaseButton.vue'

const props = defineProps({
  layout: {
    type: String,
    default: 'vertical',
    validator: (value) => ['vertical', 'horizontal', 'inline'].includes(value)
  },
  submitting: Boolean,
  disabled: Boolean,
  showActions: {
    type: Boolean,
    default: true
  },
  showCancel: {
    type: Boolean,
    default: false
  },
  submitText: {
    type: String,
    default: '提交'
  },
  cancelText: {
    type: String,
    default: '取消'
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formClasses = computed(() => {
  const classes = ['base-form']
  classes.push(`layout-${props.layout}`)
  return classes
})

const handleSubmit = () => {
  if (!props.disabled && !props.submitting) {
    emit('submit')
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.base-form {
  width: 100%;
}

/* 垂直布局 */
.base-form.layout-vertical .form-actions {
  margin-top: var(--space-xl, 32px);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm, 12px);
}

/* 水平布局 */
.base-form.layout-horizontal {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: var(--space-md, 16px);
}

.base-form.layout-horizontal .form-actions {
  flex: 0 0 auto;
  display: flex;
  gap: var(--space-sm, 12px);
  align-items: center;
}

/* 行内布局 */
.base-form.layout-inline {
  display: flex;
  align-items: flex-end;
  gap: var(--space-sm, 12px);
}

.base-form.layout-inline .form-actions {
  flex: 0 0 auto;
  display: flex;
  gap: var(--space-sm, 12px);
  align-items: center;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .base-form.layout-horizontal,
  .base-form.layout-inline {
    flex-direction: column;
    align-items: stretch;
  }
  
  .base-form.layout-horizontal .form-actions,
  .base-form.layout-inline .form-actions {
    width: 100%;
    justify-content: stretch;
  }
  
  .base-form.layout-horizontal .form-actions > *,
  .base-form.layout-inline .form-actions > * {
    flex: 1;
  }
}
</style>