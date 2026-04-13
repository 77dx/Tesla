import api from './request'

export const getUICases = (params) => api.get('/case_ui/case/', { params })
export const getUICase = (id) => api.get(`/case_ui/case/${id}/`)
export const createUICase = (data) => api.post('/case_ui/case/', data)
export const updateUICase = (id, data) => api.put(`/case_ui/case/${id}/`, data)
export const runUICase = (id, data = {}) => api.post(`/case_ui/case/${id}/run/`, data, { timeout: 300000 })
export const getUICaseHistory = (id) => api.get(`/case_ui/case/${id}/history/`)
export const getUICaseHistoryScreenshot = (id, historyId, index) => api.get(`/case_ui/case/${id}/history/${historyId}/screenshot/`, { params: { index }, responseType: 'blob', timeout: 120000 })
export const deleteUICase = (id) => api.delete(`/case_ui/case/${id}/`)
export const getUIElements = (params) => api.get('/case_ui/element/', { params })
