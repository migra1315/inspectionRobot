/**
 * 前端日志记录工具
 */
class FrontendLogger {
  constructor() {
    this.logs = []
    this.maxLogs = 1000
    this.isEnabled = true
    this.logLevel = 'INFO' // DEBUG, INFO, WARN, ERROR
    
    // 绑定到全局，方便调试
    window.frontendLogger = this
  }

  /**
   * 记录日志
   * @param {string} level - 日志级别
   * @param {string} component - 组件名称
   * @param {string} action - 操作名称
   * @param {any} data - 数据
   * @param {string} message - 消息
   */
  log(level, component, action, data = null, message = '') {
    if (!this.isEnabled) return

    const logEntry = {
      timestamp: new Date().toISOString(),
      level,
      component,
      action,
      data,
      message,
      url: window.location.href,
      userAgent: navigator.userAgent
    }

    // 添加到日志数组
    this.logs.push(logEntry)
    
    // 限制日志数量
    if (this.logs.length > this.maxLogs) {
      this.logs.shift()
    }

    // 控制台输出
    const consoleMessage = `[${level}] ${component}: ${action} ${message}`
    const logData = data ? { data } : {}
    
    switch (level) {
      case 'DEBUG':
        console.debug(consoleMessage, logData)
        break
      case 'INFO':
        console.info(consoleMessage, logData)
        break
      case 'WARN':
        console.warn(consoleMessage, logData)
        break
      case 'ERROR':
        console.error(consoleMessage, logData)
        break
      default:
        console.log(consoleMessage, logData)
    }

    // 前端日志仅本地记录，不发送到后端
  }

  /**
   * 记录调试信息
   */
  debug(component, action, data = null, message = '') {
    this.log('DEBUG', component, action, data, message)
  }

  /**
   * 记录信息
   */
  info(component, action, data = null, message = '') {
    this.log('INFO', component, action, data, message)
  }

  /**
   * 记录警告
   */
  warn(component, action, data = null, message = '') {
    this.log('WARN', component, action, data, message)
  }

  /**
   * 记录错误
   */
  error(component, action, data = null, message = '') {
    this.log('ERROR', component, action, data, message)
  }

  /**
   * 记录API请求
   */
  logApiRequest(method, url, status, responseTime, data = null) {
    this.info('API', `${method} ${url}`, {
      method,
      url,
      status,
      responseTime,
      requestData: data
    }, `API请求完成 - 状态码: ${status}, 响应时间: ${responseTime}ms`)
  }

  /**
   * 记录API错误
   */
  logApiError(method, url, error, data = null) {
    this.error('API', `${method} ${url}`, {
      method,
      url,
      error: error.message || error,
      requestData: data
    }, `API请求失败: ${error.message || error}`)
  }

  // WebSocket事件记录方法已移除

  /**
   * 记录用户操作
   */
  logUserAction(component, action, data = null) {
    this.info('UserAction', `${component}.${action}`, data, `用户操作: ${component} - ${action}`)
  }

  /**
   * 记录组件生命周期
   */
  logComponentLifecycle(component, lifecycle, data = null) {
    this.info('Component', `${component}.${lifecycle}`, data, `组件生命周期: ${component} - ${lifecycle}`)
  }

  /**
   * 记录错误边界
   */
  logErrorBoundary(component, error, errorInfo = null) {
    this.error('ErrorBoundary', component, {
      error: error.message || error,
      stack: error.stack,
      errorInfo
    }, `组件错误: ${component}`)
  }


  /**
   * 获取日志
   */
  getLogs(level = null, component = null, limit = 100) {
    let filteredLogs = this.logs

    if (level) {
      filteredLogs = filteredLogs.filter(log => log.level === level)
    }

    if (component) {
      filteredLogs = filteredLogs.filter(log => log.component === component)
    }

    return filteredLogs.slice(-limit)
  }

  /**
   * 清空日志
   */
  clearLogs() {
    this.logs = []
    console.clear()
  }

  /**
   * 导出日志
   */
  exportLogs() {
    const logs = this.getLogs()
    const dataStr = JSON.stringify(logs, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    
    const link = document.createElement('a')
    link.href = URL.createObjectURL(dataBlob)
    link.download = `frontend_logs_${new Date().toISOString().split('T')[0]}.json`
    link.click()
  }

  /**
   * 设置日志级别
   */
  setLogLevel(level) {
    this.logLevel = level
  }

  /**
   * 启用/禁用日志
   */
  setEnabled(enabled) {
    this.isEnabled = enabled
  }

  /**
   * 获取日志统计
   */
  getStatistics() {
    const stats = {
      total: this.logs.length,
      byLevel: {},
      byComponent: {},
      recentErrors: 0,
      recentWarnings: 0
    }

    this.logs.forEach(log => {
      // 按级别统计
      stats.byLevel[log.level] = (stats.byLevel[log.level] || 0) + 1
      
      // 按组件统计
      stats.byComponent[log.component] = (stats.byComponent[log.component] || 0) + 1
      
      // 最近错误和警告
      if (log.level === 'ERROR') stats.recentErrors++
      if (log.level === 'WARN') stats.recentWarnings++
    })

    return stats
  }
}

// 创建全局实例
const frontendLogger = new FrontendLogger()

// 导出
export default frontendLogger

// 全局错误处理
window.addEventListener('error', (event) => {
  frontendLogger.error('Global', 'JavaScriptError', {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    stack: event.error?.stack
  }, `全局JavaScript错误: ${event.message}`)
})

// 未处理的Promise拒绝
window.addEventListener('unhandledrejection', (event) => {
  frontendLogger.error('Global', 'UnhandledPromiseRejection', {
    reason: event.reason,
    promise: event.promise
  }, `未处理的Promise拒绝: ${event.reason}`)
})
