/**
 * 工具函数
 */

/**
 * 格式化时间
 */
export function formatTime(timestamp) {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

/**
 * 格式化相对时间
 */
export function formatRelativeTime(timestamp) {
  if (!timestamp) return ''
  
  const now = Date.now()
  const diff = now - timestamp
  
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (days > 0) return `${days}天前`
  if (hours > 0) return `${hours}小时前`
  if (minutes > 0) return `${minutes}分钟前`
  return `${seconds}秒前`
}

/**
 * 格式化数值
 */
export function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined) return '-'
  return Number(value).toFixed(decimals)
}

/**
 * 格式化百分比
 */
export function formatPercentage(value, decimals = 1) {
  if (value === null || value === undefined) return '-'
  return `${Number(value).toFixed(decimals)}%`
}

/**
 * 格式化温度
 */
export function formatTemperature(value, unit = '℃') {
  if (value === null || value === undefined) return '-'
  return `${Number(value).toFixed(1)}${unit}`
}

/**
 * 获取状态颜色
 */
export function getStatusColor(status) {
  const statusColors = {
    '正常': '#67C23A',
    '异常': '#F56C6C',
    '警告': '#E6A23C',
    '信息': '#409EFF',
    '成功': '#67C23A',
    '错误': '#F56C6C',
    'idle': '#909399',
    'running': '#409EFF',
    'completed': '#67C23A',
    'error': '#F56C6C',
    'stopped': '#E6A23C'
  }
  
  return statusColors[status] || '#909399'
}

/**
 * 获取状态文本
 */
export function getStatusText(status) {
  const statusTexts = {
    'idle': '空闲',
    'running': '运行中',
    'completed': '已完成',
    'error': '错误',
    'stopped': '已停止'
  }
  
  return statusTexts[status] || status
}

/**
 * 计算进度百分比
 */
export function calculateProgress(current, total) {
  if (!total || total === 0) return 0
  return Math.round((current / total) * 100)
}

/**
 * 防抖函数
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * 节流函数
 */
export function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 深拷贝
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (typeof obj === 'object') {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}

/**
 * 生成唯一ID
 */
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * 验证邮箱
 */
export function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

/**
 * 验证手机号
 */
export function validatePhone(phone) {
  const re = /^1[3-9]\d{9}$/
  return re.test(phone)
}

/**
 * 格式化文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 获取文件扩展名
 */
export function getFileExtension(filename) {
  return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2)
}

/**
 * 检查是否为图片文件
 */
export function isImageFile(filename) {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
  const extension = getFileExtension(filename).toLowerCase()
  return imageExtensions.includes(extension)
}

/**
 * 获取随机颜色
 */
export function getRandomColor() {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

/**
 * 数组去重
 */
export function uniqueArray(arr, key) {
  if (!key) {
    return [...new Set(arr)]
  }
  
  const seen = new Set()
  return arr.filter(item => {
    const value = item[key]
    if (seen.has(value)) {
      return false
    }
    seen.add(value)
    return true
  })
}

/**
 * 对象数组排序
 */
export function sortArray(arr, key, order = 'asc') {
  return arr.sort((a, b) => {
    const aVal = a[key]
    const bVal = b[key]
    
    if (order === 'desc') {
      return bVal > aVal ? 1 : -1
    }
    return aVal > bVal ? 1 : -1
  })
}
