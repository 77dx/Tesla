<template>
  <div class="base-input" :class="{ 'has-error': error, 'is-disabled': disabled }">
    <label v-if="label" class="input-label">
      {{ label }}
      <span v-if="required" class="required-mark">*</span>
    </label>
    
    <div class="input-wrapper">
      <div v-if="$slots.prefix" class="input-prefix">
        <slot name="prefix"></slot>
      </div>
      
      <input
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
        ref="inputRef"
      />
      
      <div v-if="$slots.suffix" class="input-suffix">
        <slot name="suffix"></slot>
      </div>
      
      <button
        v-if="clearable && modelValue"
        type="button"
        class="clear-button"
        @click="handleClear"
        aria-label="清除内容"
      >
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <div v-if="error" class="error-message">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      {{ error }}
    </div>
    
    <div v-if="description" class="input-description">
      {{ description }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  label: String,
  placeholder: String,
  error: String,
  description: String,
  disabled: Boolean,
  readonly: Boolean,
  required: Boolean,
  clearable: Boolean,
  size: {
    type: String,
    default: 'middle',
    validator: (value) => ['small', 'middle', 'large'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'input', 'blur', 'focus', 'clear'])

const inputRef = ref(null)

const inputClasses = computed(() => {
  const classes = []
  if (props.size) classes.push(`size-${props.size}`)
  if (props.error) classes.push('has-error')
  if (props.disabled) classes.push('is-disabled')
  return classes
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
  emit('input', event)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
  inputRef.value?.focus()
}

defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur(),
  select: () => inputRef.value?.select()
})
</script>

<style scoped>
.base-input {
  margin-bottom: var(--space-md, 16px);
}

.input-label {
  display: block;
  margin-bottom: var(--space-xs, 8px);
  font-size: var(--font-size-caption, 14px);
  font-weight: 500;
  color: var(--color-text-primary, #4d4c48);
}

.required-mark {
  color: var(--color-error-crimson, #b53333);
  margin-left: 2px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid var(--color-border-cream, #f0eee6);
  border-radius: var(--radius-generous, 10px);
  background-color: var(--color-ivory, #faf9f5);
  transition: all 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: var(--color-terracotta-brand, #c96442);
  box-shadow: 0 0 0 2px rgba(201, 100, 66, 0.1);
}

.input-wrapper.has-error {
  border-color: var(--color-error-crimson, #b53333);
}

.input-wrapper.is-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-prefix,
.input-suffix {
  display: flex;
  align-items: center;
  padding: 0 var(--space-sm, 12px);
  color: var(--color-text-tertiary, #87867f);
}

.input-prefix {
  border-right: 1px solid var(--color-border-cream, #f0eee6);
}

.input-suffix {
  border-left: 1px solid var(--color-border-cream, #f0eee6);
}

.base-input input {
  flex: 1;
  width: 100%;
  padding: var(--space-sm, 12px) var(--space-md, 16px);
  border: none;
  background: transparent;
  font-size: var(--font-size-body, 17px);
  color: var(--color-text-primary, #4d4c48);
  outline: none;
  font-family: inherit;
}

.base-input input::placeholder {
  color: var(--color-text-tertiary, #87867f);
}

.base-input input:disabled {
  cursor: not-allowed;
}

/* 尺寸变体 */
.base-input input.size-small {
  padding: var(--space-xs, 8px) var(--space-sm, 12px);
  font-size: var(--font-size-caption, 14px);
}

.base-input input.size-middle {
  padding: var(--space-sm, 12px) var(--space-md, 16px);
  font-size: var(--font-size-body, 17px);
}

.base-input input.size-large {
  padding: var(--space-md, 16px) var(--space-lg, 20px);
  font-size: var(--font-size-body-lg, 19px);
}

.clear-button {
  position: absolute;
  right: var(--space-sm, 12px);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary, #87867f);
  cursor: pointer;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.clear-button:hover {
  opacity: 1;
}

.clear-button svg {
  width: 16px;
  height: 16px;
}

.error-message {
  display: flex;
  align-items: center;
  gap: var(--space-xs, 8px);
  margin-top: var(--space-xs, 8px);
  font-size: var(--font-size-label, 13px);
  color: var(--color-error-crimson, #b53333);
}

.error-message svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.input-description {
  margin-top: var(--space-xs, 8px);
  font-size: var(--font-size-label, 13px);
  color: var(--color-text-tertiary, #87867f);
}
</style>