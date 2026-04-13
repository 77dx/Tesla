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

// 获取用例树（加时间戳避免缓存导致树不刷新）
export const getCaseTree = (params = {}) => api.get('/case_api/case-node/', { params: { _t: Date.now(), ...params } })

// 新建用例文件夹
export const createCaseFolder = (data) => api.post('/case_api/case-node/create_folder/', data)

// 挂载/移动用例到目录
export const attachCaseToFolder = (data) => api.post('/case_api/case-node/attach_case/', data)

// 移动目录/节点
export const moveCaseNode = (data) => api.post('/case_api/case-node/move/', data)

// 重命名节点
export const renameCaseNode = (data) => api.post('/case_api/case-node/rename/', data)

// 删除目录/节点
export const deleteCaseNode = (id) => api.delete(`/case_api/case-node/${id}/`)

// 运行单条用例（新引擎）
export const runCaseById = (caseId, data = {}) => api.post('/case_api/run_case/', { case_id: caseId, ...data })

// 运行用例（旧接口，保留兼容）
export const runCase = (endpointId) => api.post('/case_api/run/', { endpoint_id: endpointId })
