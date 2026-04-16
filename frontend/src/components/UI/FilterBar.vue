<template>
  <div class="filter-bar">
    <div class="filter-bar__search">
      <span class="filter-bar__icon">🔍</span>
      <input
        v-model="searchText"
        type="text"
        class="filter-bar__input"
        :placeholder="placeholder"
        @keyup.enter="handleSearch"
      />
    </div>

    <div class="filter-bar__filters">
      <slot name="filters" />
    </div>

    <div class="filter-bar__actions">
      <button class="filter-btn filter-btn--primary" @click="handleSearch">
        搜索
      </button>
      <button v-if="showReset" class="filter-btn filter-btn--ghost" @click="handleReset">
        重置
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '搜索...'
  },
  showReset: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const searchText = ref(props.modelValue)

watch(() => props.modelValue, (val) => {
  searchText.value = val
})

watch(searchText, (val) => {
  emit('update:modelValue', val)
})

const handleSearch = () => {
  emit('search', searchText.value)
}

const handleReset = () => {
  searchText.value = ''
  emit('reset')
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  flex-wrap: wrap;
}

.filter-bar__search {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-page);
  min-width: 240px;
  transition: border-color var(--transition-fast);
}

.filter-bar__search:focus-within {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-focus);
}

.filter-bar__icon {
  font-size: 14px;
  opacity: 0.5;
}

.filter-bar__input {
  flex: 1;
  border: none;
  outline: none;
  padding: 9px 0;
  font-size: var(--text-sm);
  background: transparent;
  color: var(--color-text-primary);
}

.filter-bar__input::placeholder {
  color: var(--color-text-tertiary);
}

.filter-bar__filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-bar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.filter-btn--primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  color: white;
}

.filter-btn--primary:hover {
  background: linear-gradient(135deg, var(--color-primary-hover), var(--color-primary-active));
}

.filter-btn--ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.filter-btn--ghost:hover {
  color: var(--color-primary);
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}
</style>
