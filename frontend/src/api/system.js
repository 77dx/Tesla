import api from './request'

// 获取部门列表
export const getDepartments = (params) => api.get('/system/department/', { params })

// 创建部门
export const createDepartment = (data) => api.post('/system/department/', data)

// 更新部门
export const updateDepartment = (id, data) => api.put(`/system/department/${id}/`, data)

// 删除部门
export const deleteDepartment = (data) => api.post('/system/department/delete/', data)

// 获取职位列表
export const getPositions = (params) => api.get('/system/position/', { params })

// 创建职位
export const createPosition = (data) => api.post('/system/position/', data)

// 更新职位
export const updatePosition = (id, data) => api.put(`/system/position/${id}/`, data)

// 删除职位
export const deletePosition = (id) => api.delete(`/system/position/${id}/`)

// 获取角色列表
export const getRoles = (params) => api.get('/system/role/', { params })

// 创建角色
export const createRole = (data) => api.post('/system/role/', data)

// 更新角色
export const updateRole = (id, data) => api.put(`/system/role/${id}/`, data)

// 删除角色
export const deleteRole = (id) => api.delete(`/system/role/${id}/`)

// 分配角色
export const assignRole = (data) => api.post('/system/role/assign_role/', data)

// 获取用户角色
export const getUserRoles = (data) => api.post('/system/role/get_user_roles/', data)

// 获取角色用户列表
export const getRoleUsers = (data) => api.post('/system/role/get_role_users/', data)

// 获取角色详情（含权限列表）
export const getRoleDetail = (id) => api.get(`/system/role/${id}/`)

// 给角色全量设置权限
export const setRolePermissions = (id, data) => api.post(`/system/role/${id}/set_permissions/`, data)

// 给角色全量设置用户
export const setRoleUsers = (id, data) => api.post(`/system/role/${id}/set_users/`, data)

// 获取所有权限码（按模块分组）
export const getPermissionsGrouped = () => api.get('/system/permission/grouped/')

// 获取所有权限码列表
export const getPermissions = () => api.get('/system/permission/')
