import api from './request'

// 获取接口列表
export const getEndpoints = (params) => api.get('/case_api/endpoint/', { params })

// 创建接口
export const createEndpoint = (data) => api.post('/case_api/endpoint/', data)

// 更新接口
export const updateEndpoint = (id, data) => api.put(`/case_api/endpoint/${id}/`, data)

// 删除接口
export const deleteEndpoint = (id) => api.delete(`/case_api/endpoint/${id}/`)

// 获取接口详情
export const getEndpointDetail = (id) => api.get(`/case_api/endpoint/${id}/`)
