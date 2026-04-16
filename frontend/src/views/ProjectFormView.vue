<template>
  <div class="project-form-view">
    <!-- 顶部返回栏 -->
    <div class="page-header">
      <button class="btn-back" @click="$router.back()">
        <ArrowLeftOutlined /> 返回项目列表
      </button>
    </div>

    <!-- 表单主体 -->
    <div class="form-layout">
      <!-- 左侧主表单 -->
      <div class="form-main">

        <!-- 基本信息卡片 -->
        <div class="form-card">
          <div class="form-card__header">
            <div class="form-card__icon">
              <FileTextOutlined />
            </div>
            <div>
              <div class="form-card__title">基本信息</div>
              <div class="form-card__sub">填写项目的基础信息</div>
            </div>
          </div>
          <div class="form-card__body">
            <!-- 项目名称 -->
            <div class="field-group">
              <label class="field-label">
                项目名称 <span class="required">*</span>
              </label>
              <div class="field-control">
                <input
                  v-model="formData.name"
                  class="field-input"
                  :class="{ 'field-input--error': errors.name }"
                  placeholder="输入项目名称，2-32个字符"
                  maxlength="32"
                />
                <div v-if="errors.name" class="field-error">
                  <ExclamationCircleOutlined /> {{ errors.name }}
                </div>
              </div>
            </div>

            <!-- 项目描述 -->
            <div class="field-group">
              <label class="field-label">
                项目描述
                <span class="field-hint-tag">可选</span>
              </label>
              <div class="field-control">
                <textarea
                  v-model="formData.intro"
                  class="field-input field-textarea"
                  placeholder="简要描述项目目标、范围、背景等"
                  rows="3"
                  maxlength="200"
                ></textarea>
                <div class="field-count">{{ formData.intro.length }}/200</div>
              </div>
            </div>

            <!-- 项目地址 -->
            <div class="field-group">
              <label class="field-label">
                项目地址
                <span class="field-hint-tag">可选</span>
              </label>
              <div class="field-control">
                <div class="input-prefix-wrap">
                  <GlobalOutlined class="input-prefix-icon" />
                  <input
                    v-model="formData.url"
                    class="field-input field-input--prefix"
                    placeholder="https://example.com"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 时间周期卡片 -->
        <div class="form-card">
          <div class="form-card__header">
            <div class="form-card__icon">
              <CalendarOutlined />
            </div>
            <div>
              <div class="form-card__title">项目周期</div>
              <div class="form-card__sub">设置项目的开始和结束时间</div>
            </div>
          </div>
          <div class="form-card__body">
            <div class="date-range">
              <div class="field-group">
                <label class="field-label">开始日期</label>
                <div class="field-control">
                  <input v-model="formData.start_date" type="date" class="field-input" />
                </div>
              </div>
              <div class="date-separator">
                <MinusOutlined />
              </div>
              <div class="field-group">
                <label class="field-label">结束日期</label>
                <div class="field-control">
                  <input v-model="formData.end_date" type="date" class="field-input" :min="formData.start_date" />
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- 右侧配置 -->
      <div class="form-side">

        <!-- 状态与优先级 -->
        <div class="form-card">
          <div class="form-card__header">
            <div class="form-card__icon">
              <SettingOutlined />
            </div>
            <div>
              <div class="form-card__title">项目配置</div>
              <div class="form-card__sub">设置状态与优先级</div>
            </div>
          </div>
          <div class="form-card__body">

            <!-- 项目状态 -->
            <div class="field-group">
              <label class="field-label">项目状态</label>
              <div class="status-grid">
                <button
                  v-for="opt in statusOptions"
                  :key="opt.value"
                  type="button"
                  class="status-chip"
                  :class="{ 'status-chip--active': formData.status === opt.value }"
                  :style="formData.status === opt.value
                    ? { background: opt.bg, borderColor: opt.border, color: opt.color }
                    : {}"
                  @click="formData.status = opt.value"
                >
                  <span class="status-chip__dot" :style="{ background: opt.color }"></span>
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <!-- 优先级 -->
            <div class="field-group">
              <label class="field-label">优先级</label>
              <div class="priority-row">
                <button
                  v-for="opt in priorityOptions"
                  :key="opt.value"
                  type="button"
                  class="priority-btn"
                  :class="{ 'priority-btn--active': formData.priority === opt.value }"
                  :style="formData.priority === opt.value
                    ? { background: opt.bg, borderColor: opt.border, color: opt.color }
                    : {}"
                  @click="formData.priority = opt.value"
                >
                  <span class="priority-btn__bar" :style="{ background: opt.color }"></span>
                  {{ opt.label }}
                </button>
              </div>
            </div>

          </div>
        </div>

        <!-- 负责人 -->
        <div class="form-card form-card--no-clip">
          <div class="form-card__header">
            <div class="form-card__icon">
              <UserOutlined />
            </div>
            <div>
              <div class="form-card__title">负责人</div>
              <div class="form-card__sub">指定项目负责人</div>
            </div>
          </div>
          <div class="form-card__body">
            <div class="pm-selector">
              <div
                class="pm-trigger"
                :class="{ 'pm-trigger--open': pmDropdownOpen }"
                @click="togglePmDropdown"
              >
                <template v-if="formData.pm && selectedPmUser">
                  <span class="pm-avatar" :style="{ background: getPmColor }">
                    {{ selectedPmUser.username?.charAt(0).toUpperCase() }}
                  </span>
                  <span class="pm-name">{{ selectedPmUser.username }}</span>
                </template>
                <template v-else>
                  <span class="pm-avatar pm-avatar--empty">
                    <UserOutlined />
                  </span>
                  <span class="pm-placeholder">选择负责人</span>
                </template>
                <span class="pm-arrow" :class="{ 'pm-arrow--up': pmDropdownOpen }">
                  <DownOutlined />
                </span>
              </div>

              <Transition name="dropdown">
                <div
                  v-if="pmDropdownOpen"
                  class="pm-dropdown"
                >
                  <div
                    class="pm-option"
                    :class="{ 'pm-option--selected': !formData.pm }"
                    @click="selectPm(null)"
                  >
                    <span class="pm-dot" style="background:#9CA3AF"></span>
                    <span>未指定</span>
                    <CheckOutlined v-if="!formData.pm" class="pm-check" />
                  </div>
                  <div class="pm-dropdown__divider"></div>
                  <div
                    v-for="user in userList"
                    :key="user.id"
                    class="pm-option"
                    :class="{ 'pm-option--selected': formData.pm === user.id }"
                    @click="selectPm(user.id)"
                  >
                    <span class="pm-avatar pm-avatar--sm" :style="{ background: stringToColor(user.username) }">
                      {{ user.username?.charAt(0).toUpperCase() }}
                    </span>
                    <span>{{ user.username }}</span>
                    <CheckOutlined v-if="formData.pm === user.id" class="pm-check" />
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>

        <!-- 所属产品线 -->
        <div class="form-card form-card--muted">
          <div class="form-card__header">
            <div class="form-card__icon">
              <ShopOutlined />
            </div>
            <div>
              <div class="form-card__title">所属产品线</div>
              <div class="form-card__sub">系统自动关联</div>
            </div>
          </div>
          <div class="form-card__body">
            <div class="pl-badge">
              <span class="pl-badge__dot" :style="{ background: plColor }"></span>
              <span class="pl-badge__name">{{ currentProductLine?.name || '默认产品线' }}</span>
              <span class="pl-badge__tag">自动</span>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="action-bar">
      <div class="action-bar__inner">
        <button type="button" class="btn btn--ghost" @click="$router.back()">
          <CloseOutlined />
          取消
        </button>
        <button type="submit" class="btn btn--primary" :disabled="saving" @click="handleSubmit">
          <template v-if="saving">
            <LoadingOutlined />
            保存中...
          </template>
          <template v-else>
            <CheckOutlined />
            {{ isEdit ? '保存修改' : '创建项目' }}
          </template>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { createProject, updateProject, getProjectDetail } from '@/api/project'
import { getAllUsers } from '@/api/account'
import { useUserStore } from '@/stores/user'
import {
  ArrowLeftOutlined,
  FileTextOutlined,
  CalendarOutlined,
  GlobalOutlined,
  SettingOutlined,
  UserOutlined,
  ShopOutlined,
  CheckOutlined,
  DownOutlined,
  MinusOutlined,
  ExclamationCircleOutlined,
  CloseOutlined,
  LoadingOutlined,
} from '@ant-design/icons-vue'
import {
  PROJECT_STATUS_LIST,
  PROJECT_PRIORITY_LIST,
  getProductLineColor,
  stringToColor,
} from '@/components/UI'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isEdit = computed(() => !!route.params.id)
const currentProductLine = computed(() => userStore.currentProductLine)

const plColor = computed(() => {
  if (!currentProductLine.value) return '#9CA3AF'
  return getProductLineColor(currentProductLine.value.id)
})

// 复用常量
const statusOptions = PROJECT_STATUS_LIST
const priorityOptions = PROJECT_PRIORITY_LIST

const formData = reactive({
  name: '',
  intro: '',
  url: '',
  status: 'active',
  pm: null,
  priority: 0,
  start_date: '',
  end_date: '',
})

const errors = reactive({ name: '' })
const saving = ref(false)
const userList = ref([])
const pmDropdownOpen = ref(false)

const selectedPmUser = computed(() =>
  userList.value.find(u => u.id === formData.pm) || null
)

const getPmColor = computed(() => {
  if (!selectedPmUser.value) return '#9CA3AF'
  return stringToColor(selectedPmUser.value.username)
})

const selectPm = (userId) => {
  formData.pm = userId
  pmDropdownOpen.value = false
}

const validate = () => {
  errors.name = ''
  if (!formData.name.trim()) {
    errors.name = '项目名称不能为空'
    return false
  }
  if (formData.name.trim().length < 2) {
    errors.name = '项目名称至少2个字符'
    return false
  }
  if (formData.name.trim().length > 32) {
    errors.name = '项目名称最多32个字符'
    return false
  }
  return true
}

const handleSubmit = async () => {
  if (!validate()) return
  saving.value = true
  try {
    const payload = { ...formData }
    if (!isEdit.value) {
      payload.product_line = currentProductLine.value?.id || null
    }
    if (!payload.start_date) payload.start_date = null
    if (!payload.end_date) payload.end_date = null

    if (isEdit.value) {
      await updateProject(route.params.id, payload)
      message.success('项目更新成功')
    } else {
      await createProject(payload)
      message.success('项目创建成功')
    }
    router.push('/projects')
  } catch (e) {
    const detail = e.response?.data?.detail || e.response?.data?.name?.[0] || ''
    message.error('保存失败' + (detail ? '：' + detail : ''))
  } finally {
    saving.value = false
  }
}

const togglePmDropdown = (e) => {
  e.stopPropagation()
  pmDropdownOpen.value = !pmDropdownOpen.value
}

const handleOutsideClick = (e) => {
  if (pmDropdownOpen.value && pmSelectorRef.value && !pmSelectorRef.value.contains(e.target)) {
    pmDropdownOpen.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', handleOutsideClick)
  await loadUsers()
  if (isEdit.value) {
    await loadProject()
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
})

const loadUsers = async () => {
  try {
    const res = await getAllUsers()
    userList.value = res.result || res || []
  } catch (e) {
    console.error('加载用户失败', e)
  }
}

const loadProject = async () => {
  try {
    const res = await getProjectDetail(route.params.id)
    const p = res.result || res
    formData.name = p.name || ''
    formData.intro = p.intro || ''
    formData.url = p.url || ''
    formData.status = p.status || 'active'
    formData.pm = p.pm || null
    formData.priority = p.priority ?? 0
    formData.start_date = p.start_date || ''
    formData.end_date = p.end_date || ''
  } catch (e) {
    message.error('加载项目信息失败')
    router.push('/projects')
  }
}
</script>

<style scoped>
/* ─── 页面整体 ─── */
.project-form-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

/* ─── 顶部返回栏 ─── */
.page-header {
  display: flex;
  align-items: center;
  padding: 0 4px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  color: var(--color-text-primary);
  border-color: var(--color-primary);
  background: #f0f7ff;
}

/* ─── 表单布局 ─── */
.form-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 20px;
  align-items: start;
}

.form-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-side {
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: sticky;
  top: 84px;
  z-index: 10;
}

/* ─── 表单卡片 ─── */
.form-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  transition: box-shadow 0.2s;
}

.form-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.form-card--muted {
  background: #fafbfc;
}

.form-card--no-clip {
  overflow: visible;
}

.form-card__header {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 22px 16px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(to bottom, #fafbfc, white);
}

.form-card__icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover, #2563EB));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  flex-shrink: 0;
}

.form-card__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.3;
}

.form-card__sub {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 2px;
}

.form-card__body {
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* ─── 字段 ─── */
.field-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.required {
  color: var(--color-primary);
}

.field-hint-tag {
  font-size: 11px;
  font-weight: 400;
  color: #9CA3AF;
  background: #f3f4f6;
  padding: 1px 6px;
  border-radius: 4px;
}

.field-control {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-input {
  width: 100%;
  box-sizing: border-box;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: white;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}

.field-input::placeholder {
  color: #c4c9d4;
}

.field-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.field-input--error {
  border-color: var(--color-primary) !important;
}

.field-input--prefix {
  padding-left: 38px;
}

.field-textarea {
  resize: vertical;
  min-height: 88px;
  line-height: 1.6;
}

.field-count {
  font-size: 12px;
  color: var(--color-text-tertiary);
  text-align: right;
}

.field-error {
  font-size: 12px;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.input-prefix-wrap {
  position: relative;
}

.input-prefix-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  font-size: 14px;
}

/* ─── 日期范围 ─── */
.date-range {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
}

.date-separator {
  color: #d1d5db;
  font-size: 14px;
  padding-top: 24px;
}

/* ─── 状态选择 ─── */
.status-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.status-chip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 6px;
  border-radius: 8px;
  border: 1.5px solid #e5e7eb;
  background: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
  transition: all 0.15s;
  user-select: none;
}

.status-chip:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.status-chip__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ─── 优先级选择 ─── */
.priority-row {
  display: flex;
  gap: 8px;
}

.priority-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 6px;
  border-radius: 8px;
  border: 1.5px solid #e5e7eb;
  background: white;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  transition: all 0.15s;
  user-select: none;
}

.priority-btn:hover {
  border-color: #d1d5db;
  background: #f9fafb;
}

.priority-btn__bar {
  width: 4px;
  height: 14px;
  border-radius: 2px;
  flex-shrink: 0;
}

/* ─── 负责人选择器 ─── */
.pm-selector {
  position: relative;
  z-index: 100;
}

.pm-trigger {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 14px;
  cursor: pointer;
  background: white;
  transition: border-color 0.2s, box-shadow 0.2s;
  user-select: none;
}

.pm-trigger:hover,
.pm-trigger--open {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
}

.pm-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
  background: linear-gradient(135deg, #3B82F6, #60A5FA);
}

.pm-avatar--empty {
  background: #f3f4f6;
  color: #9CA3AF;
  font-size: 14px;
}

.pm-avatar--sm {
  width: 26px;
  height: 26px;
  font-size: 11px;
}

.pm-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  flex: 1;
}

.pm-placeholder {
  font-size: 14px;
  color: #c4c9d4;
  flex: 1;
}

.pm-arrow {
  color: #9CA3AF;
  font-size: 10px;
  transition: transform 0.2s;
}

.pm-arrow--up {
  transform: rotate(180deg);
}

.pm-dropdown {
  position: absolute;
  left: 0;
  top: calc(100% + 6px);
  width: 100%;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  max-height: 280px;
  overflow-y: auto;
  z-index: 9999;
}

.pm-dropdown__divider {
  height: 1px;
  background: #f0f0f0;
  margin: 4px 0;
}

.pm-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 14px;
  color: var(--color-text-primary);
  transition: background 0.15s;
}

.pm-option:hover {
  background: #f9fafb;
}

.pm-option--selected {
  background: rgba(59, 130, 246, 0.04);
  color: var(--color-primary);
}

.pm-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.pm-check {
  margin-left: auto;
  color: var(--color-primary);
  font-size: 12px;
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
  transform-origin: top;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: scaleY(0.9) translateY(-4px);
}

/* ─── 产品线徽章 ─── */
.pl-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
}

.pl-badge__dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}

.pl-badge__name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  flex: 1;
}

.pl-badge__tag {
  font-size: 11px;
  color: #9CA3AF;
  background: #f3f4f6;
  padding: 2px 7px;
  border-radius: 4px;
}

/* ─── 底部操作栏 ─── */
.action-bar {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 16px 24px;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.04);
}

.action-bar__inner {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

/* ─── 按钮 ─── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 24px;
  border: 1.5px solid transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover, #2563EB));
  color: white;
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-primary-hover, #2563EB), #1d4ed8);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}

.btn--primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn--ghost {
  background: white;
  color: var(--color-text-secondary);
  border-color: #e5e7eb;
}

.btn--ghost:hover:not(:disabled) {
  color: var(--color-text-primary);
  border-color: #d1d5db;
  background: #f9fafb;
}

/* ─── 响应式 ─── */
@media (max-width: 1024px) {
  .form-layout {
    grid-template-columns: 1fr;
  }

  .form-side {
    position: static;
  }

  .status-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 768px) {
  .form-card__body {
    padding: 16px;
  }

  .action-bar__inner {
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
  }
}
</style>
