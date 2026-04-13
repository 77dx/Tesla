import api from './request'

// ── 迭代 ──────────────────────────────────────────
export const getSprints       = (params) => api.get('/project/sprint/',       { params })
export const getSprintDetail  = (id)     => api.get(`/project/sprint/${id}/`)
export const createSprint     = (data)   => api.post('/project/sprint/', data)
export const updateSprint     = (id, data) => api.put(`/project/sprint/${id}/`, data)
export const deleteSprint     = (id)     => api.delete(`/project/sprint/${id}/`)
export const getSprintRequirements = (id) => api.get(`/project/sprint/${id}/requirements/`)
export const runSprint = (id, data) => api.post(`/project/sprint/${id}/run/`, data)

// ── 需求 ──────────────────────────────────────────
export const getRequirements      = (params)   => api.get('/project/requirement/',       { params })
export const getRequirementDetail = (id)       => api.get(`/project/requirement/${id}/`)
export const createRequirement    = (data)     => api.post('/project/requirement/', data)
export const updateRequirement    = (id, data) => api.put(`/project/requirement/${id}/`, data)
export const deleteRequirement    = (id)       => api.delete(`/project/requirement/${id}/`)

// ── 迭代引用关系 ──────────────────────────────────
export const getSprintCaseRefs = (params) => api.get('/project/sprint-case-ref/', { params })
export const createSprintCaseRef = (data) => api.post('/project/sprint-case-ref/', data)
export const deleteSprintCaseRef = (id) => api.delete(`/project/sprint-case-ref/${id}/`)

export const getSprintSuiteRefs = (params) => api.get('/project/sprint-suite-ref/', { params })
export const createSprintSuiteRef = (data) => api.post('/project/sprint-suite-ref/', data)
export const deleteSprintSuiteRef = (id) => api.delete(`/project/sprint-suite-ref/${id}/`)
