/**
 * 项目管理模块通用常量与工具函数
 * 所有状态、优先级、颜色等配置统一在此管理
 */

// ─── 项目状态配置 ───
export const PROJECT_STATUS = {
  PLANNING: { value: 'planning', label: '规划中', color: '#3B82F6', bg: '#EFF6FF', border: '#BFDBFE' },
  ACTIVE:   { value: 'active',   label: '进行中', color: '#10B981', bg: '#ECFDF5', border: '#A7F3D0' },
  TESTING:  { value: 'testing',  label: '测试中', color: '#F59E0B', bg: '#FFFBEB', border: '#FDE68A' },
  DONE:     { value: 'done',     label: '已完成', color: '#06B6D4', bg: '#ECFEFF', border: '#A5F3FC' },
  ARCHIVED: { value: 'archived', label: '已归档', color: '#9CA3AF', bg: '#F9FAFB', border: '#E5E7EB' },
}

export const PROJECT_STATUS_LIST = Object.values(PROJECT_STATUS)

// ─── 项目优先级配置 ───
export const PROJECT_PRIORITY = {
  LOW:    { value: 0, label: '普通', color: '#6B7280', bg: '#F3F4F6', border: '#D1D5DB' },
  MEDIUM: { value: 1, label: '重要', color: '#D97706', bg: '#FEF3C7', border: '#FCD34D' },
  HIGH:   { value: 2, label: '紧急', color: '#DC2626', bg: '#FEF2F2', border: '#FECACA' },
}

export const PROJECT_PRIORITY_LIST = Object.values(PROJECT_PRIORITY)

// ─── 工具函数 ───

/**
 * 根据状态值获取配置
 */
export const getProjectStatusConfig = (value) => {
  return PROJECT_STATUS_LIST.find(s => s.value === value) || PROJECT_STATUS.PLANNING
}

/**
 * 根据优先级值获取配置
 */
export const getProjectPriorityConfig = (value) => {
  return PROJECT_PRIORITY_LIST.find(p => p.value === value) || PROJECT_PRIORITY.LOW
}

/**
 * 获取状态文字
 */
export const getProjectStatusText = (value) => {
  const config = getProjectStatusConfig(value)
  return config.label
}

/**
 * 获取优先级文字
 */
export const getProjectPriorityText = (value) => {
  const config = getProjectPriorityConfig(value)
  return config.label
}

/**
 * 获取优先级样式类名
 */
export const getProjectPriorityClass = (value) => {
  const classMap = { 0: 'priority-low', 1: 'priority-medium', 2: 'priority-high' }
  return classMap[value] ?? 'priority-low'
}

/**
 * 用户名转颜色
 */
export const stringToColor = (str) => {
  if (!str) return '#3B82F6'
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']
  return colors[Math.abs(hash) % colors.length]
}

/**
 * 格式化日期显示
 */
export const formatDate = (d) => {
  if (!d) return '—'
  const date = new Date(d)
  const pad = (n) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

/**
 * 格式化周期显示
 */
export const formatPeriod = (start, end) => {
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

/**
 * 产品线颜色
 */
export const getProductLineColor = (id) => {
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
  return colors[(id || 0) % colors.length]
}
