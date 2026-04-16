<template>
  <span
    class="status-badge"
    :class="[`status-badge--${type}`, { 'status-badge--clickable': clickable }]"
    :style="customStyle"
    @click="handleClick"
  >
    <span v-if="dot" class="status-badge__dot" :style="{ background: color }"></span>
    <slot>{{ text }}</slot>
    <slot name="suffix" />
  </span>
</template>

<script setup>
const props = defineProps({
  type: {
    type: String,
    default: 'default'
  },
  color: {
    type: String,
    default: ''
  },
  text: {
    type: String,
    default: ''
  },
  clickable: Boolean,
  customStyle: Object
})

const emit = defineEmits(['click'])

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: 600;
  white-space: nowrap;
}

.status-badge--clickable {
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.status-badge--clickable:hover {
  opacity: 0.8;
}

.status-badge__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* 默认 */
.status-badge--default {
  background: var(--color-gray-100);
  color: var(--color-gray-600);
}

/* 蓝色系 */
.status-badge--blue {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}

/* 绿色系 */
.status-badge--green,
.status-badge--success {
  background: var(--color-success-bg);
  color: var(--color-success);
}

/* 橙色系 */
.status-badge--orange,
.status-badge--warning {
  background: var(--color-warning-bg);
  color: var(--color-warning);
}

/* 红色系 */
.status-badge--red,
.status-badge--error,
.status-badge--danger {
  background: var(--color-error-bg);
  color: var(--color-error);
}

/* 青色系 */
.status-badge--cyan,
.status-badge--info {
  background: #ecfeff;
  color: #0891b2;
}

/* 灰色系 */
.status-badge--gray,
.status-badge--muted {
  background: var(--color-gray-100);
  color: var(--color-gray-500);
}
</style>
