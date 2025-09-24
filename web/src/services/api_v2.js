/**
 * API服务 v2.0 - 匹配简化后端接口
 */
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://192.168.8.18:5000/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log(`[API请求] ${config.method?.toUpperCase()} ${config.url}`, config.data || config.params)
    return config
  },
  error => {
    console.error('[API请求错误]', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log(`[API响应] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.status, response.data)
    return response.data
  },
  error => {
    console.error(`[API错误] ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.status, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// 巡检任务API
export const taskApi = {
  // 开始巡检任务
  startInspection: (taskName) => api.post('/task/start', { task_name: taskName }),
  
  // 获取任务进度
  getProgress: () => api.get('/task/progress')
}

// 设备状态API
export const deviceApi = {
  // 获取设备状态
  getStatus: () => api.get('/devices/status')
}

// 系统信息API
export const systemApi = {
  // 获取系统信息
  getInfo: () => api.get('/system/info')
}

// 报警信息API
export const alertApi = {
  // 获取最新报警
  getLatest: (limit = 10) => api.get(`/alerts/latest?limit=${limit}`)
}

// 图片服务API
export const imageApi = {
  // 获取机器人图片
  getRobotImage: (filename) => `http://192.168.8.18:5000/api/images/robot/${filename}`,
  
  // 获取报警图片
  getAlertImage: (filename) => `http://192.168.8.18:5000/api/images/alerts/${filename}`
}

// 导出默认的api实例
export default api

// 导出apiService别名，保持向后兼容
export const apiService = api
