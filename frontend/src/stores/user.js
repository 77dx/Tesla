import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, logout as logoutApi, getProfile, getMyPermissions } from '@/api/account'
import { getMyProductLines, getProductLinePermissions } from '@/api/productLine'

export const useUserStore = defineStore('user', () => {
  const access = ref(localStorage.getItem('access') || '')
  const refresh = ref(localStorage.getItem('refresh') || '')
  const userInfo = ref(null)
  const permissions = ref(JSON.parse(localStorage.getItem('permissions') || '[]'))

  const productLines = ref([])
  const currentProductLine = ref(
    JSON.parse(localStorage.getItem('currentProductLine') || 'null')
  )

  const productLinePermissions = ref(
    JSON.parse(localStorage.getItem('productLinePermissions') || '[]')
  )

  const effectivePermissions = computed(() => {
    if (permissions.value.includes('*')) return permissions.value
    if (productLinePermissions.value.length > 0) return productLinePermissions.value
    return permissions.value
  })

  const hasPermission = (code) => {
    const perms = effectivePermissions.value
    if (perms.includes('*')) return true
    return perms.includes(code)
  }

  async function fetchUserInfo() {
    try {
      const res = await getProfile()
      if (res.result) userInfo.value = res.result
      else if (res) userInfo.value = res
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  async function fetchPermissions() {
    try {
      const res = await getMyPermissions()
      const codes = res.result ?? res
      if (Array.isArray(codes)) {
        permissions.value = codes
        localStorage.setItem('permissions', JSON.stringify(codes))
      }
    } catch (error) {
      console.error('获取权限失败:', error)
    }
  }

  async function fetchProductLines() {
    try {
      const res = await getMyProductLines()
      const list = res.result ?? res
      if (Array.isArray(list)) {
        productLines.value = list
        const saved = currentProductLine.value
        const found = saved ? list.find(p => p.id === saved.id) : null
        if (!found && list.length > 0) {
        await switchProductLine(list[0])
      } else if (found) {
        await fetchProductLinePermissions(found.id)
      }
    }
    } catch (error) {
      console.error('获取产品线失败:', error)
    }
  }

  async function switchProductLine(pl) {
    currentProductLine.value = pl
    localStorage.setItem('currentProductLine', JSON.stringify(pl))
    if (pl) await fetchProductLinePermissions(pl.id)
  }

  async function fetchProductLinePermissions(plId) {
    try {
      const res = await getProductLinePermissions(plId)
      const codes = res.result ?? res
      if (Array.isArray(codes)) {
        productLinePermissions.value = codes
        localStorage.setItem('productLinePermissions', JSON.stringify(codes))
      }
    } catch (error) {
      console.error('获取产品线权限失败:', error)
    }
  }

  async function loginUser(username, password) {
    try {
      const res = await login({ username, password })
      const data = res.result ?? res
      setAuth(data)
      if (data) {
        userInfo.value = data
      }
      await fetchPermissions()
      await fetchProductLines()
      return true
    } catch (error) {
      console.error('登录失败:', error)
      clearAuth()
      return false
    }
  }

  async function logout() {
    const refreshToken = refresh.value || localStorage.getItem('refresh')
    try {
      if (refreshToken) {
        await logoutApi({ refresh: refreshToken })
      }
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      clearAuth()
      permissions.value = []
      productLines.value = []
      currentProductLine.value = null
      productLinePermissions.value = []
      localStorage.removeItem('permissions')
      localStorage.removeItem('currentProductLine')
      localStorage.removeItem('productLinePermissions')
    }
  }

  function setAuth(data) {
    if (data.access) {
      access.value = data.access
      localStorage.setItem('access', data.access)
    }
    if (data.refresh) {
      refresh.value = data.refresh
      localStorage.setItem('refresh', data.refresh)
    }
    if (data.userInfo) {
      userInfo.value = data.userInfo
    }
  }

  function clearAuth() {
    access.value = ''
    refresh.value = ''
    userInfo.value = null
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
  }

  return {
    access,
    refresh,
    userInfo,
    permissions,
    productLines,
    currentProductLine,
    productLinePermissions,
    effectivePermissions,
    hasPermission,
    login: loginUser,
    logout,
    fetchUserInfo,
    fetchPermissions,
    fetchProductLines,
    switchProductLine,
    fetchProductLinePermissions,
    setAuth,
    clearAuth,
  }
})
