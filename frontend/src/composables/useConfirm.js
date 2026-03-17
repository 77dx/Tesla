import { ref } from 'vue'

const confirmVisible = ref(false)
const confirmOptions = ref({
  title: '确认操作',
  message: '',
  type: 'warning',
  confirmText: '确定',
  cancelText: '取消',
  onConfirm: null,
  onCancel: null
})

export function useConfirm() {
  const showConfirm = (options) => {
    confirmOptions.value = {
      title: '确认操作',
      message: '',
      type: 'warning',
      confirmText: '确定',
      cancelText: '取消',
      onConfirm: null,
      onCancel: null,
      ...options
    }
    confirmVisible.value = true
  }

  const hideConfirm = () => {
    confirmVisible.value = false
    // 重置回调函数
    confirmOptions.value.onConfirm = null
    confirmOptions.value.onCancel = null
  }

  const handleConfirm = () => {
    if (typeof confirmOptions.value.onConfirm === 'function') {
      confirmOptions.value.onConfirm()
    }
    hideConfirm()
  }

  const handleCancel = () => {
    if (typeof confirmOptions.value.onCancel === 'function') {
      confirmOptions.value.onCancel()
    }
    hideConfirm()
  }

  return {
    confirmVisible,
    confirmOptions,
    showConfirm,
    hideConfirm,
    handleConfirm,
    handleCancel
  }
}

// 导出全局方法
export const confirm = (message, options = {}) => {
  return new Promise((resolve) => {
    const {
      showConfirm
    } = useConfirm()

    showConfirm({
      message,
      ...options,
      onConfirm: () => resolve(true),
      onCancel: () => resolve(false)
    })
  })
}