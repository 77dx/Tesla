<template>
  <div class="form-card" :class="{ 'form-card--muted': muted }">
    <div class="form-card__header">
      <div class="form-card__icon" :style="iconStyle">
        <slot name="icon">
          <FileTextOutlined v-if="icon" />
        </slot>
      </div>
      <div class="form-card__content">
        <div class="form-card__title">{{ title }}</div>
        <div v-if="subtitle" class="form-card__subtitle">{{ subtitle }}</div>
      </div>
    </div>
    <div class="form-card__body">
      <slot />
    </div>
  </div>
</template>

<script setup>
import { FileTextOutlined } from '@ant-design/icons-vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: String,
  icon: {
    type: Boolean,
    default: true
  },
  muted: Boolean,
  iconColor: {
    type: String,
    default: ''
  }
})

const iconStyle = props.iconColor ? {
  background: `linear-gradient(135deg, ${props.iconColor}, ${props.iconColor}dd)`
} : {}
</script>

<style scoped>
.form-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-base);
}

.form-card:hover {
  box-shadow: var(--shadow-md);
}

.form-card--muted {
  background: var(--color-gray-50);
}

.form-card__header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 22px 16px;
  border-bottom: 1px solid var(--color-gray-100);
  background: linear-gradient(to bottom, var(--color-gray-50), var(--color-bg-card));
}

.form-card__icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  flex-shrink: 0;
}

.form-card__content {
  flex: 1;
  min-width: 0;
}

.form-card__title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.3;
}

.form-card__subtitle {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: 2px;
}

.form-card__body {
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
</style>
