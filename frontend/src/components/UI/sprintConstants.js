/**
 * 迭代管理模块通用常量与工具函数
 */

// ─── 迭代状态配置 ───
export const SPRINT_STATUS = {
  PLANNING:  { value: 'planning',  label: '规划中', color: '#3B82F6', bg: '#EFF6FF', border: '#BFDBFE' },
  ACTIVE:    { value: 'active',    label: '进行中', color: '#10B981', bg: '#ECFDF5', border: '#A7F3D0' },
  REVIEWING: { value: 'reviewing', label: '评审中', color: '#F59E0B', bg: '#FFFBEB', border: '#FDE68A' },
  DONE:      { value: 'done',      label: '已完成', color: '#06B6D4', bg: '#ECFEFF', border: '#A5F3FC' },
}

export const SPRINT_STATUS_LIST = Object.values(SPRINT_STATUS)

// ─── 需求状态配置 ───
export const REQUIREMENT_STATUS = {
  TODO:     { value: 'todo',      label: '待开发', color: '#6B7280', bg: '#F3F4F6' },
  IN_DEV:   { value: 'in_dev',    label: '开发中', color: '#3B82F6', bg: '#EFF6FF' },
  IN_TEST:  { value: 'in_test',   label: '测试中', color: '#8B5CF6', bg: '#F5F3FF' },
  IN_REVIEW:{ value: 'in_review', label: '评审中', color: '#F59E0B', bg: '#FFFBEB' },
  DONE:     { value: 'done',      label: '已完成', color: '#10B981', bg: '#ECFDF5' },
  REJECTED: { value: 'rejected',  label: '已驳回', color: '#EF4444', bg: '#FEF2F2' },
}

export const REQUIREMENT_STATUS_LIST = Object.values(REQUIREMENT_STATUS)

// ─── 需求优先级配置 ───
export const REQUIREMENT_PRIORITY = {
  LOW:    { value: 0, label: '低', color: '#6B7280', bg: '#F3F4F6' },
  MEDIUM: { value: 1, label: '中', color: '#F59E0B', bg: '#FFFBEB' },
  HIGH:   { value: 2, label: '高', color: '#EF4444', bg: '#FEF2F2' },
}

export const REQUIREMENT_PRIORITY_LIST = Object.values(REQUIREMENT_PRIORITY)

// ─── 工具函数 ───

/**
 * 根据迭代状态值获取配置
 */
export const getSprintStatusConfig = (value) => {
  return SPRINT_STATUS_LIST.find(s => s.value === value) || SPRINT_STATUS.PLANNING
}

/**
 * 根据需求状态值获取配置
 */
export const getRequirementStatusConfig = (value) => {
  return REQUIREMENT_STATUS_LIST.find(s => s.value === value) || REQUIREMENT_STATUS.TODO
}

/**
 * 根据需求优先级值获取配置
 */
export const getRequirementPriorityConfig = (value) => {
  return REQUIREMENT_PRIORITY_LIST.find(p => p.value === value) || REQUIREMENT_PRIORITY.MEDIUM
}

/**
 * 获取迭代状态文字
 */
export const getSprintStatusText = (value) => {
  return getSprintStatusConfig(value)?.label || '未知'
}

/**
 * 获取需求状态文字
 */
export const getRequirementStatusText = (value) => {
  return getRequirementStatusConfig(value)?.label || '未知'
}

/**
 * 获取需求优先级文字
 */
export const getRequirementPriorityText = (value) => {
  return getRequirementPriorityConfig(value)?.label || '中'
}

/**
 * 获取需求优先级样式类名
 */
export const getRequirementPriorityClass = (value) => {
  const classMap = { 0: 'priority-low', 1: 'priority-medium', 2: 'priority-high' }
  return classMap[value] ?? 'priority-medium'
}

/**
 * 格式化周期显示
 */
export const formatSprintPeriod = (start, end) => {
  if (!start && !end) return '—'
  const fmt = (d) => {
    if (!d) return '—'
    const date = new Date(d)
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`
  }
  if (start && end) return `${fmt(start)} ~ ${fmt(end)}`
  if (start) return `${fmt(start)} ~`
  return `~ ${fmt(end)}`
}

