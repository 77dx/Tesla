import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const clearAuthStorage = () => {
  localStorage.removeItem('access')
  localStorage.removeItem('refresh')
  localStorage.removeItem('permissions')
  localStorage.removeItem('currentProductLine')
  localStorage.removeItem('productLinePermissions')
}

let refreshPromise = null

const refreshAccessToken = async () => {
  const refresh = localStorage.getItem('refresh')
  if (!refresh) {
    throw new Error('No refresh token')
  }

  if (!refreshPromise) {
    refreshPromise = axios
      .post('/api/token/refresh/', { refresh }, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 30000,
      })
      .then((response) => {
        const data = response.data?.result ?? response.data
        const nextAccess = data?.access
        const nextRefresh = data?.refresh
        if (!nextAccess) {
          throw new Error('Refresh response missing access token')
        }
        localStorage.setItem('access', nextAccess)
        if (nextRefresh) {
          localStorage.setItem('refresh', nextRefresh)
        }
        return nextAccess
      })
      .finally(() => {
        refreshPromise = null
      })
  }

  return refreshPromise
}

api.interceptors.request.use(
  config => {
    const access = localStorage.getItem('access')
    if (access) {
      config.headers.Authorization = `Bearer ${access}`
    }
    return config
  },
  error => Promise.reject(error)
)

api.interceptors.response.use(
  response => {
    if (response.data?.code === 401 && response.data?.msg === '权限不足，无法执行此操作') {
      showToast(response.data.msg || '权限不足', 'error')
      return Promise.reject(response)
    }
    if (response.status === 404) {
      showToast('请求的资源不存在', 'error')
      return Promise.reject(response)
    }
    if (response.status === 500) {
      const msg = response.data?.message || response.data?.msg || '服务器错误'
      showToast(msg, 'error')
      return Promise.reject(response)
    }
    return response.data
  },
  async error => {
    const originalRequest = error.config || {}
    const status = error.response?.status

    if (status === 401 && !originalRequest._retry) {
      const refresh = localStorage.getItem('refresh')
      if (!refresh || originalRequest.url?.includes('/token/refresh/')) {
        clearAuthStorage()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      originalRequest._retry = true
      try {
        const nextAccess = await refreshAccessToken()
        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers.Authorization = `Bearer ${nextAccess}`
        return api(originalRequest)
      } catch (refreshError) {
        clearAuthStorage()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

function showToast(message, type = 'error') {
  const existing = document.getElementById('tesla-toast')
  if (existing) existing.remove()

  const colors = { error: '#e74c3c', warning: '#f39c12', success: '#27ae60', info: '#3498db' }
  const el = document.createElement('div')
  el.id = 'tesla-toast'
  el.textContent = message
  Object.assign(el.style, {
    position: 'fixed',
    top: '20px',
    right: '20px',
    padding: '12px 24px',
    borderRadius: '8px',
    fontSize: '14px',
    zIndex: 9999,
    maxWidth: '300px',
    backgroundColor: colors[type] || colors.error,
    color: '#fff',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
  })
  document.body.appendChild(el)
  setTimeout(() => el.remove(), 3000)
}

export default api
