import api from './request'

// 获取项目列表
export const getProjects = (params) => api.get('/project/project/', { params })

// 创建项目
export const createProject = (data) => api.post('/project/project/', data)

// 更新项目
export const updateProject = (id, data) => api.put(`/project/project/${id}/`, data)

// 删除项目
export const deleteProject = (id) => api.delete(`/project/project/${id}/`)

// 获取项目详情
export const getProjectDetail = (id) => api.get(`/project/project/${id}/`)
