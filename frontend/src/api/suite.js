import api from './request'

// 获取测试套件列表
export const getSuites = (params) => api.get('/suite/suite/', { params })

// 获取单个测试套件
export const getSuiteDetail = (id) => api.get(`/suite/suite/${id}/`)

// 创建测试套件
export const createSuite = (data) => api.post('/suite/suite/', data)

// 更新测试套件
export const updateSuite = (id, data) => api.put(`/suite/suite/${id}/`, data)

// 删除测试套件
export const deleteSuite = (id) => api.delete(`/suite/suite/${id}/`)

// 执行测试套件
export const runSuite = (id, data) => api.post(`/suite/suite/${id}/run/`, data)

// 停止定时任务
export const stopCron = (id) => api.post(`/suite/suite/${id}/stop_cron/`)

// 获取执行结果

export const getRunResult = (id) => api.get(`/suite/runresult/${id}/`)

// 获取执行结果列表

export const getRunResults = (params) => api.get('/suite/runresult/', { params })

// 删除执行结果

export const deleteRunResult = (id) => api.delete(`/suite/runresult/${id}/`)

// ---- 套件用例项 ----
// 获取套件内用例项列表
export const getSuiteCaseItems = (suiteId) =>
  api.get('/suite/suite-case-item/', { params: { suite: suiteId } })

// 批量添加用例到套件
export const batchAddCaseItems = (data) =>
  api.post('/suite/suite-case-item/batch_add/', data)

// 删除套件用例项
export const deleteCaseItem = (id) => api.delete(`/suite/suite-case-item/${id}/`)

// 更新套件用例项（enabled / env_override）
export const updateCaseItem = (id, data) => api.patch(`/suite/suite-case-item/${id}/`, data)

// 批量更新排序
export const reorderCaseItems = (items) =>
  api.post('/suite/suite-case-item/reorder/', { items })

// ---- 服务注册表 ----
export const getServices = (params) => api.get('/suite/service/', { params })
export const createService = (data) => api.post('/suite/service/', data)
export const updateService = (id, data) => api.put(`/suite/service/${id}/`, data)
export const deleteService = (id) => api.delete(`/suite/service/${id}/`)

// ---- 运行环境 ----
export const getEnvironments = (params) => api.get('/suite/environment/', { params })
export const getEnvironment = (id) => api.get(`/suite/environment/${id}/`)
export const createEnvironment = (data) => api.post('/suite/environment/', data)
export const updateEnvironment = (id, data) => api.put(`/suite/environment/${id}/`, data)
export const deleteEnvironment = (id) => api.delete(`/suite/environment/${id}/`)

// ---- 全局变量 ----
export const getGlobalVariables = (params) => api.get('/suite/global-variable/', { params })
export const createGlobalVariable = (data) => api.post('/suite/global-variable/', data)
export const updateGlobalVariable = (id, data) => api.put(`/suite/global-variable/${id}/`, data)
export const deleteGlobalVariable = (id) => api.delete(`/suite/global-variable/${id}/`)
