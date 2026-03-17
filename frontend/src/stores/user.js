import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getProfile, getMyPermissions } from '@/api/account'
import { getMyProductLines, getProductLinePermissions } from '@/api/productLine'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const permissions = ref(JSON.parse(localStorage.getItem('permissions') || '[]'))

  // 产品线状态
  const productLines = ref([])
  const currentProductLine = ref(
    JSON.parse(localStorage.getItem('currentProductLine') || 'null')
  )
  // 产品线级权限（切换产品线后动态加载）
  const productLinePermissions = ref(
    JSON.parse(localStorage.getItem('productLinePermissions') || '[]')
  )

  // 最终有效权限：超管用全局权限，否则用产品线级权限（若已加载），兜底用全局权限
  const effectivePermissions = computed(() => {
    if (permissions.value.includes('*')) return permissions.value
    if (productLinePermissions.value.length > 0) return productLinePermissions.value
    return permissions.value
  })

  // 判断是否有某个权限码
  const hasPermission = (code) => {
    const perms = effectivePermissions.value
    if (perms.includes('*')) return true
    return perms.includes(code)
  }

  // 判断是否是管理员
  const isAdmin = () => permissions.value.includes('*')

  const login = async (username, password) => {
    try {
      const res = await loginApi({ username, password })
      if (res && res.result && res.result.token) {
        token.value = res.result.token
        localStorage.setItem('token', res.result.token)
        userInfo.value = res.result
        await fetchPermissions()
        await fetchProductLines()
        return true
      }
      return false
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  const logout = () => {
    token.value = ''
    userInfo.value = null
    permissions.value = []
    productLines.value = []
    currentProductLine.value = null
    productLinePermissions.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('permissions')
    localStorage.removeItem('currentProductLine')
    localStorage.removeItem('productLinePermissions')
  }

  const fetchUserInfo = async () => {
    try {
      const res = await getProfile()
      if (res.result) userInfo.value = res.result
      else if (res) userInfo.value = res
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  const fetchPermissions = async () => {
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

  // 拉取我的产品线列表，并自动选中上次的或第一个
  const fetchProductLines = async () => {
    try {
      const res = await getMyProductLines()
      const list = res.result ?? res
      if (Array.isArray(list)) {
        productLines.value = list
        // 如果没有当前产品线，或当前产品线已不在列表中，自动选第一个
        const saved = currentProductLine.value
        const found = saved ? list.find(p => p.id === saved.id) : null
        if (!found && list.length > 0) {
          await switchProductLine(list[0])
        } else if (found) {
          // 刷新权限
          await fetchProductLinePermissions(found.id)
        }
      }
    } catch (error) {
      console.error('获取产品线失败:', error)
    }
  }

  // 切换产品线
  const switchProductLine = async (pl) => {
    currentProductLine.value = pl
    localStorage.setItem('currentProductLine', JSON.stringify(pl))
    if (pl) await fetchProductLinePermissions(pl.id)
  }

  // 拉取指定产品线的权限码
  const fetchProductLinePermissions = async (plId) => {
    try {
      // 超管不需要产品线级权限
      if (permissions.value.includes('*')) return
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

  return {
    token,
    userInfo,
    permissions,
    productLines,
    currentProductLine,
    productLinePermissions,
    effectivePermissions,
    hasPermission,
    isAdmin,
    login,
    logout,
    fetchUserInfo,
    fetchPermissions,
    fetchProductLines,
    switchProductLine,
    fetchProductLinePermissions,
  }
})
