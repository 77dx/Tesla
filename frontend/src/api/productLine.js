import api from './request'

// 我的产品线列表
export const getMyProductLines = () => api.get('/product-line/mine/')

// 所有产品线（管理员）
export const getProductLines = (params) => api.get('/product-line/', { params })

// 创建产品线
export const createProductLine = (data) => api.post('/product-line/', data)

// 更新产品线
export const updateProductLine = (id, data) => api.put(`/product-line/${id}/`, data)

// 删除产品线
export const deleteProductLine = (id) => api.delete(`/product-line/${id}/`)

// 获取产品线成员列表
export const getProductLineMembers = (id) => api.get(`/product-line/${id}/members/`)

// 添加产品线成员
export const addProductLineMember = (id, data) => api.post(`/product-line/${id}/members/`, data)

// 移除产品线成员
export const removeProductLineMember = (id, memberId) =>
  api.delete(`/product-line/${id}/members/${memberId}/`)

// 更新成员角色
export const updateMemberRole = (id, memberId, data) =>
  api.patch(`/product-line/${id}/members/${memberId}/role/`, data)

// 获取我在该产品线的权限码
export const getProductLinePermissions = (id) => api.get(`/product-line/${id}/permissions/`)
