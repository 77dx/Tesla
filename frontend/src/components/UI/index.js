// UI组件库入口文件
export { default as BaseInput } from './BaseInput.vue'
export { default as BaseButton } from './BaseButton.vue'
export { default as BaseForm } from './BaseForm.vue'
export { default as BaseCard } from './BaseCard.vue'

// 图标组件（如果需要）
export { default as UserIcon } from './icons/UserIcon.vue'
export { default as LockIcon } from './icons/LockIcon.vue'
export { default as AlertIcon } from './icons/AlertIcon.vue'

// 工具函数
export const useFormValidation = () => {
  const validateRequired = (value, fieldName = '此字段') => {
    if (!value || value.toString().trim() === '') {
      return `${fieldName}不能为空`
    }
    return null
  }

  const validateEmail = (value) => {
    if (!value) return null
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(value)) {
      return '请输入有效的邮箱地址'
    }
    return null
  }

  const validatePassword = (value) => {
    if (!value) return null
    // 可以根据需要添加密码复杂度验证
    return null
  }

  return {
    validateRequired,
    validateEmail,
    validatePassword
  }
}