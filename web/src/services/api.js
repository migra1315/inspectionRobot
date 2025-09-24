/**
 * API服务
 */
import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 15000, // 增加超时时间到15秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加请求日志
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
    // 添加响应日志
    console.log(`[API响应] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.status, response.data)
    return response.data
  },
  error => {
    // 添加错误日志
    console.error(`[API错误] ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.status, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// 机器人控制API
export const robotApi = {
  // 获取机器人状态
  getStatus: () => api.get('/robot/status'),
  
  // 连接机器人
  connect: () => api.post('/robot/connect'),
  
  // 启动巡检
  startInspection: () => api.post('/robot/start-inspection'),
  
  // 回到基站
  goHome: () => api.post('/robot/go-home'),
  
  // 获取巡检进度
  getProgress: () => api.get('/robot/progress'),
  
  // 获取巡检历史记录
  getHistory: (limit = 10) => api.get(`/robot/history?limit=${limit}`),
  
  // 获取硬件连接状态
  getHardwareStatus: () => api.get('/robot/hardware-status'),
  
  // 重新连接硬件
  reconnectHardware: () => api.post('/robot/reconnect-hardware'),
  
  // 清空巡检历史记录
  clearHistory: () => api.post('/robot/clear-history'),
  
  // 获取设备位置信息（用于巡检路径显示）
  getDevicePositions: () => api.get('/device/status?inspection_order=true')
}

// 环境参数API
export const environmentApi = {
  // 获取环境参数
  getParameters: () => api.get('/environment/parameters'),
  
  // 接收环境数据
  receiveData: (data) => api.post('/environment/data', data),
  
  // 更新环境参数
  updateParameters: (data) => api.post('/environment/parameters', data),
  
  // 获取阈值
  getThresholds: () => api.get('/environment/thresholds'),
  
  // 更新阈值
  updateThresholds: (data) => api.put('/environment/thresholds', data),
  
  // 获取环境状态
  getStatus: () => api.get('/environment/status')
}

// 设备状态API
export const deviceApi = {
  // 获取所有设备状态
  getAllStatus: () => api.get('/device/status'),
  
  // 获取指定设备状态
  getStatus: (deviceId) => api.get(`/device/status/${deviceId}`),
  
  // 上传设备图片
  uploadImage: (formData) => api.post('/device/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  
  // 分析设备
  analyzeDevice: (data) => api.post('/device/analyze', data),
  
  // 获取设备历史
  getHistory: (deviceId) => api.get(`/device/history/${deviceId}`)
}

// Mock测试API
export const mockTestApi = {
  // 启动Mock测试
  start: (scenario) => api.post('/mock-test/start', { scenario }),
  
  // 停止Mock测试
  stop: () => api.post('/mock-test/stop'),
  
  // 切换测试场景
  switchScenario: (scenario) => api.post('/mock-test/scenario', { scenario }),
  
  // 获取测试状态
  getStatus: () => api.get('/mock-test/status'),
  
  // 获取可用场景
  getScenarios: () => api.get('/mock-test/scenarios')
}

// 日志API
export const logsApi = {
  // 获取最近日志
  getRecent: (limit = 100, type = null) => {
    const params = new URLSearchParams()
    if (limit) params.append('limit', limit)
    if (type) params.append('type', type)
    return api.get(`/logs/recent?${params.toString()}`)
  },
  
  // 获取日志统计
  getStatistics: () => api.get('/logs/statistics'),
  
  // 清空日志
  clear: () => api.post('/logs/clear'),
  
  // 导出日志
  export: (type = null) => api.post('/logs/export', { type })
}

// 安防监控API
export const securityApi = {
  // 获取视频流信息
  getStreams: () => api.get('/security/streams'),
  
  // 获取指定视频流
  getStream: (streamId) => api.get(`/security/streams/${streamId}`),
  
  // 获取视频流状态
  getStreamStatus: (streamId) => api.get(`/security/streams/${streamId}/status`),
  
  // 控制视频流
  controlStream: (streamId, action) => api.post(`/security/streams/${streamId}/control`, { action }),
  
  // 获取告警信息
  getAlerts: () => api.get('/security/alerts'),
  
  // 确认告警
  acknowledgeAlert: (alertId) => api.post(`/security/alerts/${alertId}/acknowledge`)
}

// 导出默认的api实例
export default api

// 导出apiService别名，保持向后兼容
export const apiService = api
