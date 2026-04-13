import api from './request'

// ── 旧接口（兼容保留）────────────────────────────────
export const getPerformanceTests   = (params) => api.get('/suite/performance/', { params })
export const createPerformanceTest = (data)   => api.post('/suite/performance/', data)
export const runPerformanceTest    = (id)     => api.post(`/suite/performance/${id}/run/`)
export const stopPerformanceTest   = (id)     => api.post(`/suite/performance/${id}/stop/`)
export const deletePerformanceTest = (id)     => api.delete(`/suite/performance/${id}/`)
export const getPerformanceStats   = (id)     => api.get(`/suite/performance/${id}/stats/`)
export const getPerformanceReport  = (id)     => api.get(`/suite/performance/${id}/report/`)
export const getPerformanceLog     = (id, n = 200) => api.get(`/suite/performance/${id}/log/`, { params: { n } })

// ── 压测配置 ──────────────────────────────────────────
export const getPerfConfigs    = (params) => api.get('/suite/perf-config/', { params })
export const getPerfConfig     = (id)     => api.get(`/suite/perf-config/${id}/`)
export const createPerfConfig  = (data)   => api.post('/suite/perf-config/', data)
export const updatePerfConfig  = (id, data) => api.put(`/suite/perf-config/${id}/`, data)
export const deletePerfConfig  = (id)     => api.delete(`/suite/perf-config/${id}/`)
export const runPerfConfig     = (id)     => api.post(`/suite/perf-config/${id}/run/`)

// ── 压测结果 ──────────────────────────────────────────
export const getPerfResults    = (params) => api.get('/suite/perf-result/', { params })
export const getPerfResult     = (id)     => api.get(`/suite/perf-result/${id}/`)
export const deletePerfResult  = (id)     => api.delete(`/suite/perf-result/${id}/`)
export const stopPerfResult    = (id)     => api.post(`/suite/perf-result/${id}/stop/`)
export const getPerfResultStats = (id)    => api.get(`/suite/perf-result/${id}/stats/`)
export const getPerfResultLog  = (id, n = 200) => api.get(`/suite/perf-result/${id}/log/`, { params: { n } })
export const getPerfResultReport = (id)  => api.get(`/suite/perf-result/${id}/report/`)
