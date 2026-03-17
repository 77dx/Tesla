import api from './request'
import axios from 'axios'

// 创建文件上传专用的axios实例
const uploadApi = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

// 添加请求拦截器（复制原有的token逻辑）
uploadApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 添加响应拦截器（复制原有的逻辑）
uploadApi.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 用户登录
export const login = (data) => api.post('/account/profile/login/', data)

// 获取用户信息
export const getProfile = () => api.get('/account/profile/profile/')

// 获取所有用户
export const getAllUsers = () => api.get('/account/profile/get_all_users/')

// 重置密码
export const resetPassword = (data) => api.post('/account/profile/reset_password/', data)

// 修改用户信息
export const modify = (data) => api.post('/account/profile/modify/', data)

// 上传头像
export const imgUpload = (formData) => uploadApi.post('/account/profile/img_upload/', formData)

// 获取当前用户权限码列表
export const getMyPermissions = () => api.get('/account/profile/my_permissions/')

// ── 管理员用户管理 ──
// 获取所有用户详情（含部门/职位/角色）
export const getAdminUserList = () => api.get('/account/admin/users/list/')

// 修改用户部门/职位/角色
export const updateAdminUser = (data) => api.post('/account/admin/users/update/', data)
