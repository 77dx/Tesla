import api from './request'

// 获取项目列表
export const getProjects = (params) => api.get('/project/project/', { params })

// 创建项目
export const createProject = (data) => api.post('/project/project/', data)

// 更新项目
export const updateProject = (id, data) => api.put(`/project/project/${id}/`, data)

// 删除项目
export const deleteProject = (id) => api.delete(`/project/project/${id}/`)

// 批量删除项目
export const batchDeleteProjects = (ids) => api.post('/project/project/delete/', { ids })

// 获取项目详情
export const getProjectDetail = (id) => api.get(`/project/project/${id}/`)

// 项目执行
export const runProject = (id, data) => api.post(`/project/project/${id}/run/`, data)

// 项目引用关系
export const getProjectCaseRefs = (params) => api.get('/project/project-case-ref/', { params })
export const createProjectCaseRef = (data) => api.post('/project/project-case-ref/', data)
export const deleteProjectCaseRef = (id) => api.delete(`/project/project-case-ref/${id}/`)

export const getProjectSuiteRefs = (params) => api.get('/project/project-suite-ref/', { params })
export const createProjectSuiteRef = (data) => api.post('/project/project-suite-ref/', data)
export const deleteProjectSuiteRef = (id) => api.delete(`/project/project-suite-ref/${id}/`)
