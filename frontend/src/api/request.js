import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const rawDetail = error.response?.data?.detail
    let detail = '请求失败，请稍后重试'
    if (typeof rawDetail === 'string') {
      detail = rawDetail
    } else if (Array.isArray(rawDetail)) {
      detail = rawDetail.map((item) => item.msg || item.message || JSON.stringify(item)).join('；')
    } else if (rawDetail && typeof rawDetail === 'object') {
      detail = rawDetail.message || JSON.stringify(rawDetail)
    }
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('session_id')
      router.push('/login')
    }
    ElMessage.error(detail)
    return Promise.reject(error)
  }
)

export default request
