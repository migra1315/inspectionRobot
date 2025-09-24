/**
 * 状态更新管理器
 * 负责管理设备状态的差异更新和UI反馈
 */

import { ref, reactive } from 'vue'
import { compareDeviceStatus, getKeyChanges, generateDiffSummary, isImportantChange, getChangePriority } from './dataDiff.js'
import frontendLogger from './logger.js'

class StatusUpdateManager {
  constructor() {
    // 状态数据
    this.oldDevices = []
    this.newDevices = []
    this.updateHistory = []
    
    // 更新状态
    this.isUpdating = ref(false)
    this.lastUpdateTime = ref(null)
    this.updateCount = ref(0)
    
    // 差异信息
    this.lastDiff = reactive({
      added: [],
      removed: [],
      modified: [],
      unchanged: [],
      summary: {
        totalChanges: 0,
        addedCount: 0,
        removedCount: 0,
        modifiedCount: 0
      }
    })
    
    // 更新配置
    this.config = {
      enableVisualFeedback: true,
      enableSoundFeedback: false,
      enableLogging: true,
      animationDuration: 300,
      highlightDuration: 2000
    }
  }

  /**
   * 更新设备状态数据
   * @param {Array} newDevices - 新的设备数据
   * @param {Object} options - 更新选项
   * @returns {Object} 更新结果
   */
  async updateDeviceStatus(newDevices, options = {}) {
    const startTime = Date.now()
    this.isUpdating.value = true
    
    try {
      // 保存旧数据
      this.oldDevices = [...this.newDevices]
      this.newDevices = [...newDevices]
      
      // 比较数据差异
      const diffResult = compareDeviceStatus(this.oldDevices, this.newDevices)
      
      // 更新差异信息
      Object.assign(this.lastDiff, diffResult)
      
      // 记录更新历史
      this.recordUpdateHistory(diffResult, startTime)
      
      // 生成更新摘要
      const summary = generateDiffSummary(diffResult)
      
      // 记录日志
      if (this.config.enableLogging) {
        this.logUpdate(diffResult, summary)
      }
      
      // 更新统计信息
      this.updateCount.value++
      this.lastUpdateTime.value = new Date()
      
      // 返回更新结果
      return {
        success: true,
        diff: diffResult,
        summary,
        updateTime: this.lastUpdateTime.value,
        duration: Date.now() - startTime,
        keyChanges: this.getKeyChanges(diffResult)
      }
      
    } catch (error) {
      frontendLogger.error('StatusUpdateManager', 'updateDeviceStatus', { error: error.message }, '设备状态更新失败')
      return {
        success: false,
        error: error.message,
        updateTime: new Date()
      }
    } finally {
      this.isUpdating.value = false
    }
  }

  /**
   * 获取关键变化信息
   * @param {Object} diffResult - 差异结果
   * @returns {Array} 关键变化列表
   */
  getKeyChanges(diffResult) {
    const keyChanges = []
    
    // 处理修改的设备
    for (const modified of diffResult.modified) {
      const changes = getKeyChanges(modified)
      keyChanges.push(...changes)
    }
    
    // 处理新增的设备
    for (const added of diffResult.added) {
      keyChanges.push({
        type: 'device_added',
        deviceId: added.deviceId,
        message: `新增设备: ${added.device.device_name}`,
        priority: 1
      })
    }
    
    // 处理移除的设备
    for (const removed of diffResult.removed) {
      keyChanges.push({
        type: 'device_removed',
        deviceId: removed.deviceId,
        message: `移除设备: ${removed.device.device_name}`,
        priority: 1
      })
    }
    
    // 按优先级排序
    return keyChanges.sort((a, b) => (a.priority || 10) - (b.priority || 10))
  }

  /**
   * 记录更新历史
   * @param {Object} diffResult - 差异结果
   * @param {number} startTime - 开始时间
   */
  recordUpdateHistory(diffResult, startTime) {
    const historyEntry = {
      timestamp: new Date(),
      duration: Date.now() - startTime,
      summary: generateDiffSummary(diffResult),
      changes: {
        added: diffResult.added.length,
        removed: diffResult.removed.length,
        modified: diffResult.modified.length
      },
      keyChanges: this.getKeyChanges(diffResult)
    }
    
    this.updateHistory.unshift(historyEntry)
    
    // 限制历史记录数量
    if (this.updateHistory.length > 50) {
      this.updateHistory = this.updateHistory.slice(0, 50)
    }
  }

  /**
   * 记录更新日志
   * @param {Object} diffResult - 差异结果
   * @param {string} summary - 更新摘要
   */
  logUpdate(diffResult, summary) {
    const logData = {
      summary,
      changes: {
        added: diffResult.added.length,
        removed: diffResult.removed.length,
        modified: diffResult.modified.length
      },
      keyChanges: this.getKeyChanges(diffResult)
    }
    
    if (diffResult.summary.totalChanges > 0) {
      frontendLogger.info('StatusUpdateManager', 'updateDeviceStatus', logData, '设备状态更新完成')
    } else {
      frontendLogger.info('StatusUpdateManager', 'updateDeviceStatus', logData, '设备状态无变化')
    }
  }

  /**
   * 获取更新统计信息
   * @returns {Object} 统计信息
   */
  getUpdateStats() {
    return {
      totalUpdates: this.updateCount.value,
      lastUpdateTime: this.lastUpdateTime.value,
      isUpdating: this.isUpdating.value,
      historyCount: this.updateHistory.length,
      lastDiff: this.lastDiff
    }
  }

  /**
   * 获取最近的变化
   * @param {number} count - 获取数量
   * @returns {Array} 最近的变化
   */
  getRecentChanges(count = 10) {
    return this.updateHistory.slice(0, count)
  }

  /**
   * 清除更新历史
   */
  clearHistory() {
    this.updateHistory = []
    frontendLogger.info('StatusUpdateManager', 'clearHistory', null, '更新历史已清除')
  }

  /**
   * 更新配置
   * @param {Object} newConfig - 新配置
   */
  updateConfig(newConfig) {
    Object.assign(this.config, newConfig)
    frontendLogger.info('StatusUpdateManager', 'updateConfig', newConfig, '配置已更新')
  }

  /**
   * 检查是否有重要变化
   * @param {Object} diffResult - 差异结果
   * @returns {boolean} 是否有重要变化
   */
  hasImportantChanges(diffResult) {
    for (const modified of diffResult.modified) {
      for (const change of modified.changes?.modified || []) {
        if (isImportantChange(change)) {
          return true
        }
      }
    }
    return false
  }

  /**
   * 获取设备变化详情
   * @param {string} deviceId - 设备ID
   * @returns {Object|null} 设备变化详情
   */
  getDeviceChanges(deviceId) {
    for (const modified of this.lastDiff.modified) {
      if (modified.deviceId === deviceId) {
        return modified
      }
    }
    return null
  }

  /**
   * 重置状态
   */
  reset() {
    this.oldDevices = []
    this.newDevices = []
    this.updateHistory = []
    this.updateCount.value = 0
    this.lastUpdateTime.value = null
    this.isUpdating.value = false
    
    // 重置差异信息
    Object.assign(this.lastDiff, {
      added: [],
      removed: [],
      modified: [],
      unchanged: [],
      summary: {
        totalChanges: 0,
        addedCount: 0,
        removedCount: 0,
        modifiedCount: 0
      }
    })
    
    frontendLogger.info('StatusUpdateManager', 'reset', null, '状态管理器已重置')
  }
}

// 创建全局实例
const statusUpdateManager = new StatusUpdateManager()

export default statusUpdateManager
