import api from './request'

export const getAutomationProjects = (params) => api.get('/automation/project/', { params })
export const createAutomationProject = (data) => api.post('/automation/project/', data)
export const updateAutomationProject = (id, data) => api.put(`/automation/project/${id}/`, data)
export const deleteAutomationProject = (id) => api.delete(`/automation/project/${id}/`)

export const getAutomationSuites = (params) => api.get('/automation/suite/', { params })
export const createAutomationSuite = (data) => api.post('/automation/suite/', data)
export const updateAutomationSuite = (id, data) => api.put(`/automation/suite/${id}/`, data)
export const deleteAutomationSuite = (id) => api.delete(`/automation/suite/${id}/`)
export const runAutomationSuite = (id, data) => api.post(`/automation/suite/${id}/run/`, data)

export const getAutomationRuns = (params) => api.get('/automation/run/', { params })
export const getAutomationRun = (id) => api.get(`/automation/run/${id}/`)
export const getAutomationRunLogPreview = (id) => api.get(`/automation/run/${id}/log_preview/`)
export const getAutomationRunReportMeta = (id) => api.get(`/automation/run/${id}/report_meta/`)
