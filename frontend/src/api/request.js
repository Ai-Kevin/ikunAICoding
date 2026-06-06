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
    const detail = error.response?.data?.detail || '请求失败，请稍后重试'
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    ElMessage.error(detail)
    return Promise.reject(error)
  }
)

export default request
