import api from './request'

// 获取接口列表
export const getEndpoints = (params) => api.get('/case_api/endpoint/', { params })

// 获取单个接口详情
export const getEndpoint = (id) => api.get(`/case_api/endpoint/${id}/`)

// 创建接口
export const createEndpoint = (data) => api.post('/case_api/endpoint/', data)

// 更新接口
export const updateEndpoint = (id, data) => api.put(`/case_api/endpoint/${id}/`, data)

// 删除接口
export const deleteEndpoint = (id) => api.delete(`/case_api/endpoint/${id}/`)

// 获取用例列表
export const getCases = (params) => api.get('/case_api/case/', { params })

// 获取单个用例详情
export const getCase = (id) => api.get(`/case_api/case/${id}/`)

// 创建用例
export const createCase = (data) => api.post('/case_api/case/', data)

// 更新用例
export const updateCase = (id, data) => api.put(`/case_api/case/${id}/`, data)

// 删除用例
export const deleteCase = (id) => api.delete(`/case_api/case/${id}/`)

// 运行单条用例（新引擎）
export const runCaseById = (caseId) => api.post('/case_api/run_case/', { case_id: caseId })

// 运行用例（旧接口，保留兼容）
export const runCase = (endpointId) => api.post('/case_api/run/', { endpoint_id: endpointId })
