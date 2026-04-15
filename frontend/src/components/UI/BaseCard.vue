<template>
  <div :class="cardClasses">
    <div v-if="title || $slots.extra" class="card-header">
      <div class="card-title">
        <slot name="title">
          <h3 v-if="title" class="title-text">{{ title }}</h3>
        </slot>
      </div>
      
      <div v-if="$slots.extra" class="card-extra">
        <slot name="extra"></slot>
      </div>
    </div>
    
    <div class="card-body">
      <slot></slot>
    </div>
    
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: String,
  bordered: {
    type: Boolean,
    default: true
  },
  hoverable: Boolean,
  shadow: {
    type: String,
    default: 'normal',
    validator: (value) => ['none', 'subtle', 'normal', 'elevated'].includes(value)
  },
  padding: {
    type: String,
    default: 'normal',
    validator: (value) => ['none', 'compact', 'normal', 'comfortable'].includes(value)
  }
})

const cardClasses = computed(() => {
  const classes = ['base-card']
  if (props.bordered) classes.push('bordered')
  if (props.hoverable) classes.push('hoverable')
  classes.push(`shadow-${props.shadow}`)
  classes.push(`padding-${props.padding}`)
  return classes
})
</script>

<style scoped>
.base-card {
  background-color: var(--color-ivory, #faf9f5);
  border-radius: var(--radius-generous, 12px);
  transition: all 0.2s ease;
}

/* 边框 */
.base-card.bordered {
  border: 1px solid var(--color-border-cream, #f0eee6);
}

/* 悬停效果 */
.base-card.hoverable:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

/* 阴影变体 */
.base-card.shadow-none {
  box-shadow: none;
}

.base-card.shadow-subtle {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.base-card.shadow-normal {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.base-card.shadow-elevated {
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

/* 内边距变体 */
.base-card.padding-none .card-body {
  padding: 0;
}

.base-card.padding-compact .card-body {
  padding: var(--space-md, 16px);
}

.base-card.padding-normal .card-body {
  padding: var(--space-lg, 24px);
}

.base-card.padding-comfortable .card-body {
  padding: var(--space-xl, 32px);
}

/* 头部 */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-lg, 24px) var(--space-lg, 24px) 0;
  border-bottom: 1px solid var(--color-border-cream, #f0eee6);
  margin-bottom: var(--space-lg, 24px);
}

.base-card.padding-none .card-header,
.base-card.padding-compact .card-header {
  padding: var(--space-md, 16px) var(--space-md, 16px) 0;
  margin-bottom: var(--space-md, 16px);
}

.card-title {
  flex: 1;
}

.title-text {
  margin: 0;
  font-size: var(--font-size-feature-title, 22px);
  font-weight: 600;
  color: var(--color-text-primary, #4d4c48);
}

.card-extra {
  flex: 0 0 auto;
}

/* 主体 */
.card-body {
  color: var(--color-text-primary, #4d4c48);
}

/* 底部 */
.card-footer {
  padding: 0 var(--space-lg, 24px) var(--space-lg, 24px);
  border-top: 1px solid var(--color-border-cream, #f0eee6);
  margin-top: var(--space-lg, 24px);
}

.base-card.padding-none .card-footer,
.base-card.padding-compact .card-footer {
  padding: 0 var(--space-md, 16px) var(--space-md, 16px);
  margin-top: var(--space-md, 16px);
}
</style>