import { ref } from 'vue'

const alertVisible = ref(false)
const alertOptions = ref({
  title: '提示',
  message: '',
  type: 'info', // 'info' | 'success' | 'error' | 'warning'
})
let _resolve = null

export function useAlert() {
  const showAlert = (message, options = {}) => {
    alertOptions.value = {
      title: options.title || '提示',
      message,
      type: options.type || 'info',
    }
    alertVisible.value = true
    return new Promise((resolve) => { _resolve = resolve })
  }

  const hideAlert = () => {
    alertVisible.value = false
    if (_resolve) { _resolve(); _resolve = null }
  }

  return { alertVisible, alertOptions, showAlert, hideAlert }
}

// 全局 alert 方法，供各页面直接 import 使用
export async function alert(message, options = {}) {
  const { showAlert } = useAlert()
  return showAlert(message, options)
}
