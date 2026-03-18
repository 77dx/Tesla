import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ── 简易 toast（无需第三方库，用原生 DOM）────────────────────
function showToast(message, type = 'error') {
  // 防重复
  const existing = document.getElementById('tesla-toast')
  if (existing) existing.remove()

  const colors = { error: '#e74c3c', warning: '#f39c12', success: '#27ae60', info: '#3498db' }
  const el = document.createElement('div')
  el.id = 'tesla-toast'
  el.textContent = message
  Object.assign(el.style, {
    position: 'fixed',
    top: '20px',
    left: '50%',
    transform: 'translateX(-50%)',
    background: colors[type] || colors.error,
    color: '#fff',
    padding: '10px 24px',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
    zIndex: '99999',
    boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
    transition: 'opacity 0.3s ease',
    opacity: '1',
  })
  document.body.appendChild(el)
  setTimeout(() => {
    el.style.opacity = '0'
    setTimeout(() => el.remove(), 300)
  }, 3000)
}

// ── 请求拦截器 ────────────────────────────────────────────────
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Token ${token}`
    return config
  },
  error => Promise.reject(error)
)

// ── 响应拦截器 ────────────────────────────────────────────────
api.interceptors.response.use(
  response => response.data,
  error => {
    const status = error.response?.status
    const data = error.response?.data

    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('permissions')
      showToast('登录已过期，请重新登录')
      setTimeout(() => { window.location.href = '/login' }, 1500)
      return Promise.reject(error)
    }

    if (status === 403) {
      showToast('权限不足，无法执行此操作')
      return Promise.reject(error)
    }

    if (status === 404) {
      showToast('请求的资源不存在')
      return Promise.reject(error)
    }

    // 业务错误：提取后端返回的 message
    const msg =
      data?.message ||
      data?.msg ||
      data?.detail ||
      (typeof data === 'string' ? data : null) ||
      `请求失败（${status || '网络错误'}）`

    showToast(msg)
    return Promise.reject(error)
  }
)

export default api
export { showToast }

