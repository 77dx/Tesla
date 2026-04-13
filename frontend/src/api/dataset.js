import api from './request'

// 获取参数集列表
export const getDataSets = (params) => api.get('/suite/dataset/', { params })

// 获取单个参数集
export const getDataSet = (id) => api.get(`/suite/dataset/${id}/`)

// 创建参数集
export const createDataSet = (data) => api.post('/suite/dataset/', data)

// 删除参数集
export const deleteDataSet = (id) => api.delete(`/suite/dataset/${id}/`)

// 上传 CSV/Excel 文件解析为参数集
export const uploadDataSet = (formData) => api.post('/suite/dataset/upload/', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
