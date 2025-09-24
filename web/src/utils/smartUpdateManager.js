/**
 * 智能更新管理器
 * 负责管理设备状态的智能更新，避免不必要的全量刷新
 */

import { ref, reactive } from 'vue'
import frontendLogger from './logger.js'

class SmartUpdateManager {
  constructor() {
    // 设备级更新状态
    this.deviceUpdateStates = reactive(new Map())
    
    // 更新配置
    this.config = {
      enableSilentUpdates: true,      // 启用静默更新
      showDeviceHighlights: true,     // 显示设备高亮
      enableValueAnimations: true,    // 启用数值变化动画
      autoRefreshInterval: 30000,     // 自动刷新间隔（30秒）
      maxSilentUpdates: 5,           // 最大静默更新次数
      highlightDuration: 2000,       // 高亮持续时间
      animationDuration: 500         // 动画持续时间
    }
    
    // 更新统计
    this.updateStats = reactive({
      totalUpdates: 0,
      silentUpdates: 0,
      highlightedUpdates: 0,
      lastUpdateTime: null
    })
    
    // 设备数据缓存
    this.deviceDataCache = new Map()
    
    // 更新队列
    this.updateQueue = []
    this.isProcessingQueue = false
  }

  /**
   * 分析更新类型
   * @param {Object} data - 更新数据
   * @returns {string} 更新类型
   */
  analyzeUpdateType(data) {
    const oldData = this.deviceDataCache.get(data.device_id)
    
    if (!oldData) {
      return 'full' // 首次加载
    }
    
    // 检查图片变化
    if (data.image_url !== oldData.image_url) {
      return 'image'
    }
    
    // 检查状态变化
    if (data.status !== oldData.status) {
      return 'status'
    }
    
    // 检查数值变化
    if (data.actual_value !== oldData.actual_value) {
      return 'value'
    }
    
    // 检查连接状态变化
    if (data.connection_status !== oldData.connection_status) {
      return 'connection'
    }
    
    // 检查AI分析结果变化
    if (data.ai_analysis_result !== oldData.ai_analysis_result) {
      return 'analysis'
    }
    
    return 'silent' // 无重要变化
  }

  /**
   * 智能更新设备数据
   * @param {string} deviceId - 设备ID
   * @param {Object} newData - 新数据
   * @param {string} updateType - 更新类型
   * @returns {Object} 更新结果
   */
  smartUpdateDevice(deviceId, newData, updateType = null) {
    try {
      // 分析更新类型
      const detectedType = updateType || this.analyzeUpdateType(newData)
      
      // 更新缓存
      this.deviceDataCache.set(deviceId, { ...newData })
      
      // 设置设备更新状态
      this.setDeviceUpdateState(deviceId, {
        type: detectedType,
        timestamp: Date.now(),
        data: newData
      })
      
      // 更新统计
      this.updateStats.totalUpdates++
      this.updateStats.lastUpdateTime = new Date()
      
      if (detectedType === 'silent') {
        this.updateStats.silentUpdates++
      } else {
        this.updateStats.highlightedUpdates++
      }
      
      // 记录日志
      frontendLogger.info('SmartUpdateManager', 'smartUpdateDevice', {
        deviceId,
        updateType: detectedType,
        hasImageChange: detectedType === 'image',
        hasStatusChange: detectedType === 'status',
        hasValueChange: detectedType === 'value'
      }, `设备 ${deviceId} 智能更新完成`)
      
      return {
        success: true,
        updateType: detectedType,
        deviceId,
        data: newData,
        shouldHighlight: this.shouldHighlight(detectedType),
        shouldAnimate: this.shouldAnimate(detectedType)
      }
      
    } catch (error) {
      frontendLogger.error('SmartUpdateManager', 'smartUpdateDevice', {
        deviceId,
        error: error.message
      }, '设备智能更新失败')
      
      return {
        success: false,
        error: error.message,
        deviceId
      }
    }
  }

  /**
   * 设置设备更新状态
   * @param {string} deviceId - 设备ID
   * @param {Object} state - 更新状态
   */
  setDeviceUpdateState(deviceId, state) {
    this.deviceUpdateStates.set(deviceId, state)
    
    // 自动清理过期的更新状态
    setTimeout(() => {
      this.deviceUpdateStates.delete(deviceId)
    }, this.config.highlightDuration)
  }

  /**
   * 获取设备更新状态
   * @param {string} deviceId - 设备ID
   * @returns {Object|null} 更新状态
   */
  getDeviceUpdateState(deviceId) {
    return this.deviceUpdateStates.get(deviceId) || null
  }

  /**
   * 判断是否应该高亮显示
   * @param {string} updateType - 更新类型
   * @returns {boolean}
   */
  shouldHighlight(updateType) {
    const highlightTypes = ['status', 'connection', 'analysis']
    return this.config.showDeviceHighlights && highlightTypes.includes(updateType)
  }

  /**
   * 判断是否应该显示动画
   * @param {string} updateType - 更新类型
   * @returns {boolean}
   */
  shouldAnimate(updateType) {
    const animateTypes = ['value', 'image']
    return this.config.enableValueAnimations && animateTypes.includes(updateType)
  }

  /**
   * 批量更新设备数据
   * @param {Array} devicesData - 设备数据数组
   * @returns {Object} 批量更新结果
   */
  batchUpdateDevices(devicesData) {
    const results = []
    const highlights = []
    const animations = []
    
    for (const deviceData of devicesData) {
      const result = this.smartUpdateDevice(deviceData.device_id, deviceData)
      results.push(result)
      
      if (result.shouldHighlight) {
        highlights.push({
          deviceId: result.deviceId,
          type: result.updateType,
          timestamp: Date.now()
        })
      }
      
      if (result.shouldAnimate) {
        animations.push({
          deviceId: result.deviceId,
          type: result.updateType,
          timestamp: Date.now()
        })
      }
    }
    
    return {
      results,
      highlights,
      animations,
      summary: this.generateBatchSummary(results)
    }
  }

  /**
   * 生成批量更新摘要
   * @param {Array} results - 更新结果数组
   * @returns {string} 摘要信息
   */
  generateBatchSummary(results) {
    const typeCounts = results.reduce((acc, result) => {
      acc[result.updateType] = (acc[result.updateType] || 0) + 1
      return acc
    }, {})
    
    const parts = []
    if (typeCounts.status) parts.push(`${typeCounts.status}个设备状态更新`)
    if (typeCounts.value) parts.push(`${typeCounts.value}个设备数值更新`)
    if (typeCounts.image) parts.push(`${typeCounts.image}个设备图片更新`)
    if (typeCounts.connection) parts.push(`${typeCounts.connection}个设备连接更新`)
    if (typeCounts.silent) parts.push(`${typeCounts.silent}个设备静默更新`)
    
    return parts.length > 0 ? parts.join('，') : '设备状态无变化'
  }

  /**
   * 获取设备高亮类名
   * @param {string} deviceId - 设备ID
   * @returns {string} CSS类名
   */
  getDeviceHighlightClass(deviceId) {
    const state = this.getDeviceUpdateState(deviceId)
    if (!state) return ''
    
    const elapsed = Date.now() - state.timestamp
    if (elapsed > this.config.highlightDuration) return ''
    
    return `highlight-${state.type}`
  }

  /**
   * 获取设备动画类名
   * @param {string} deviceId - 设备ID
   * @returns {string} CSS类名
   */
  getDeviceAnimationClass(deviceId) {
    const state = this.getDeviceUpdateState(deviceId)
    if (!state) return ''
    
    const elapsed = Date.now() - state.timestamp
    if (elapsed > this.config.animationDuration) return ''
    
    return `animate-${state.type}`
  }

  /**
   * 更新配置
   * @param {Object} newConfig - 新配置
   */
  updateConfig(newConfig) {
    Object.assign(this.config, newConfig)
    frontendLogger.info('SmartUpdateManager', 'updateConfig', newConfig, '配置已更新')
  }

  /**
   * 获取更新统计
   * @returns {Object} 统计信息
   */
  getUpdateStats() {
    return {
      ...this.updateStats,
      deviceCount: this.deviceDataCache.size,
      activeHighlights: this.deviceUpdateStates.size
    }
  }

  /**
   * 清除所有状态
   */
  clearAllStates() {
    this.deviceUpdateStates.clear()
    this.deviceDataCache.clear()
    this.updateQueue = []
    
    frontendLogger.info('SmartUpdateManager', 'clearAllStates', null, '所有状态已清除')
  }

  /**
   * 重置统计信息
   */
  resetStats() {
    this.updateStats.totalUpdates = 0
    this.updateStats.silentUpdates = 0
    this.updateStats.highlightedUpdates = 0
    this.updateStats.lastUpdateTime = null
    
    frontendLogger.info('SmartUpdateManager', 'resetStats', null, '统计信息已重置')
  }
}

// 创建全局实例
const smartUpdateManager = new SmartUpdateManager()

export default smartUpdateManager
