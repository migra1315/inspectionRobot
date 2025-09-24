/**
 * 数据差异比较工具
 */

/**
 * 深度比较两个对象，返回差异信息
 * @param {Object} oldData - 旧数据
 * @param {Object} newData - 新数据
 * @param {string} prefix - 属性前缀（用于递归）
 * @returns {Object} 差异信息
 */
export function deepCompare(oldData, newData, prefix = '') {
  const changes = {
    added: [],
    removed: [],
    modified: [],
    unchanged: []
  }

  if (!oldData && !newData) {
    return changes
  }

  if (!oldData) {
    changes.added.push({
      path: prefix,
      value: newData,
      type: 'added'
    })
    return changes
  }

  if (!newData) {
    changes.removed.push({
      path: prefix,
      value: oldData,
      type: 'removed'
    })
    return changes
  }

  // 获取所有属性
  const allKeys = new Set([...Object.keys(oldData), ...Object.keys(newData)])

  for (const key of allKeys) {
    const currentPath = prefix ? `${prefix}.${key}` : key
    const oldValue = oldData[key]
    const newValue = newData[key]

    // 检查属性是否被移除
    if (!(key in newData)) {
      changes.removed.push({
        path: currentPath,
        value: oldValue,
        type: 'removed'
      })
      continue
    }

    // 检查属性是否被添加
    if (!(key in oldData)) {
      changes.added.push({
        path: currentPath,
        value: newValue,
        type: 'added'
      })
      continue
    }

    // 比较值
    if (isObject(oldValue) && isObject(newValue)) {
      // 递归比较对象
      const nestedChanges = deepCompare(oldValue, newValue, currentPath)
      changes.added.push(...nestedChanges.added)
      changes.removed.push(...nestedChanges.removed)
      changes.modified.push(...nestedChanges.modified)
      changes.unchanged.push(...nestedChanges.unchanged)
    } else if (oldValue !== newValue) {
      // 值发生变化
      changes.modified.push({
        path: currentPath,
        oldValue,
        newValue,
        type: 'modified'
      })
    } else {
      // 值未变化
      changes.unchanged.push({
        path: currentPath,
        value: newValue,
        type: 'unchanged'
      })
    }
  }

  return changes
}

/**
 * 检查是否为对象
 * @param {any} value - 要检查的值
 * @returns {boolean}
 */
function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

/**
 * 比较设备状态数据
 * @param {Array} oldDevices - 旧设备数据
 * @param {Array} newDevices - 新设备数据
 * @returns {Object} 设备状态差异
 */
export function compareDeviceStatus(oldDevices, newDevices) {
  const result = {
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
  }

  // 创建设备ID映射
  const oldDeviceMap = new Map(oldDevices.map(device => [device.device_id, device]))
  const newDeviceMap = new Map(newDevices.map(device => [device.device_id, device]))

  // 检查新增的设备
  for (const [deviceId, newDevice] of newDeviceMap) {
    if (!oldDeviceMap.has(deviceId)) {
      result.added.push({
        deviceId,
        device: newDevice,
        type: 'device_added'
      })
    }
  }

  // 检查移除的设备
  for (const [deviceId, oldDevice] of oldDeviceMap) {
    if (!newDeviceMap.has(deviceId)) {
      result.removed.push({
        deviceId,
        device: oldDevice,
        type: 'device_removed'
      })
    }
  }

  // 检查修改的设备
  for (const [deviceId, newDevice] of newDeviceMap) {
    if (oldDeviceMap.has(deviceId)) {
      const oldDevice = oldDeviceMap.get(deviceId)
      const changes = deepCompare(oldDevice, newDevice, deviceId)
      
      if (changes.modified.length > 0 || changes.added.length > 0 || changes.removed.length > 0) {
        result.modified.push({
          deviceId,
          oldDevice,
          newDevice,
          changes,
          type: 'device_modified'
        })
      } else {
        result.unchanged.push({
          deviceId,
          device: newDevice,
          type: 'device_unchanged'
        })
      }
    }
  }

  // 计算摘要
  result.summary.addedCount = result.added.length
  result.summary.removedCount = result.removed.length
  result.summary.modifiedCount = result.modified.length
  result.summary.totalChanges = result.added.length + result.removed.length + result.modified.length

  return result
}

/**
 * 获取设备状态变化的关键信息
 * @param {Object} deviceDiff - 设备差异信息
 * @returns {Array} 关键变化信息
 */
export function getKeyChanges(deviceDiff) {
  const keyChanges = []

  // 检查状态变化
  if (deviceDiff.changes) {
    for (const change of deviceDiff.changes.modified) {
      if (change.path.includes('status')) {
        keyChanges.push({
          type: 'status_change',
          deviceId: deviceDiff.deviceId,
          oldValue: change.oldValue,
          newValue: change.newValue,
          message: `设备状态从"${change.oldValue}"变更为"${change.newValue}"`
        })
      }
      
      if (change.path.includes('actual_value')) {
        keyChanges.push({
          type: 'value_change',
          deviceId: deviceDiff.deviceId,
          oldValue: change.oldValue,
          newValue: change.newValue,
          message: `设备数值从"${change.oldValue}"变更为"${change.newValue}"`
        })
      }
      
      if (change.path.includes('connection_status')) {
        keyChanges.push({
          type: 'connection_change',
          deviceId: deviceDiff.deviceId,
          oldValue: change.oldValue,
          newValue: change.newValue,
          message: `连接状态从"${change.oldValue}"变更为"${change.newValue}"`
        })
      }
    }
  }

  return keyChanges
}

/**
 * 生成差异更新摘要
 * @param {Object} diffResult - 差异比较结果
 * @returns {string} 摘要信息
 */
export function generateDiffSummary(diffResult) {
  const { summary } = diffResult
  
  if (summary.totalChanges === 0) {
    return '设备状态无变化'
  }

  const parts = []
  
  if (summary.addedCount > 0) {
    parts.push(`新增 ${summary.addedCount} 个设备`)
  }
  
  if (summary.removedCount > 0) {
    parts.push(`移除 ${summary.removedCount} 个设备`)
  }
  
  if (summary.modifiedCount > 0) {
    parts.push(`更新 ${summary.modifiedCount} 个设备`)
  }

  return parts.join('，')
}

/**
 * 检查是否为重要变化
 * @param {Object} change - 变化信息
 * @returns {boolean} 是否为重要变化
 */
export function isImportantChange(change) {
  const importantFields = [
    'status',
    'actual_value',
    'connection_status',
    'ai_analysis_result',
    'battery_level'
  ]
  
  return importantFields.some(field => change.path.includes(field))
}

/**
 * 获取变化优先级
 * @param {Object} change - 变化信息
 * @returns {number} 优先级（数字越小优先级越高）
 */
export function getChangePriority(change) {
  if (change.path.includes('status')) return 1
  if (change.path.includes('connection_status')) return 2
  if (change.path.includes('actual_value')) return 3
  if (change.path.includes('ai_analysis_result')) return 4
  if (change.path.includes('battery_level')) return 5
  return 10
}
