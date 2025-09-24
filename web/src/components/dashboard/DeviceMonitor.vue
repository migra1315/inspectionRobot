<template>
  <div class="device-monitor">
    <div class="monitor-header">
      <h3 class="monitor-title">设备状态监控</h3>
    </div>
    
    <!-- 设备监控内容区域 - 始终显示 -->
    <div class="device-content">
      <!-- 移除全局加载状态覆盖层，改为智能更新 -->
      
      <!-- 四组件并排显示 -->
      <div class="device-grid-four">
        <div class="device-card" 
             v-for="(device, index) in getDisplayCards()" 
             :key="device.id || `placeholder-${index}`"
             :class="{ 
               'alert': device.status === 'error', 
               'warning': device.status === 'warning',
               'placeholder': !device.id,
               [smartUpdateManager.getDeviceHighlightClass(device.id)]: device.id,
               [smartUpdateManager.getDeviceAnimationClass(device.id)]: device.id
             }"
        >
        <!-- 机器人回传图片区域 -->
        <div class="robot-image-section">
          <div class="image-placeholder">
            <div class="image-label">来自机器人回传的{{ getImageLabel(index) }}照片</div>
            <div class="image-container" v-if="device.imageLoaded && device.imageUrl && device.id">
              <img 
                :src="device.imageUrl" 
                :alt="device.name" 
                @error="handleImageError"
                @click="openPreview(device.imageUrl, device.name)"
                class="clickable-image"
              >
              <div class="image-status" v-if="device.imageTimestamp">
                <span class="timestamp">{{ formatImageTimestamp(device.imageTimestamp) }}</span>
              </div>
              <div class="image-overlay">
                <div class="preview-hint">
                  <i class="icon-zoom">🔍</i>
                  <span>点击放大</span>
                </div>
              </div>
            </div>
            <div class="no-image" v-else-if="device.id">
              <i class="icon-camera"></i>
              <span>{{ device.imageLoaded ? '图片加载中...' : '等待机器人回传' }}</span>
            </div>
            <div class="no-image" v-else>
              <i class="icon-camera"></i>
              <span>等待数据</span>
            </div>
          </div>
        </div>
        
        <!-- 指标信息区域 -->
        <div class="indicators-section">
          <!-- 低温冰箱显示温度参数 -->
          <template v-if="device.type === '低温冰箱'">
            <div class="indicator-item">
              <span class="indicator-label">当前温度:</span>
              <span class="indicator-value">{{ device.currentTemp || '--' }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">设定温度:</span>
              <span class="indicator-value">{{ device.setTemp || '--' }}</span>
            </div>
          </template>
          
          <!-- 液氮罐显示容量参数 -->
          <template v-if="device.type === '液氮罐'">
            <div class="indicator-item">
              <span class="indicator-label">当前余量:</span>
              <span class="indicator-value">{{ device.currentVolume || '--' }}</span>
            </div>
            <div class="indicator-item">
              <span class="indicator-label">安全余量:</span>
              <span class="indicator-value">{{ device.safeVolume || '--' }}</span>
            </div>
          </template>
          
          <div class="indicator-item">
            <span class="indicator-label">状态:</span>
            <span class="indicator-value status" :class="getDataStatusClass(device)">
              {{ device.id ? getStatusText(device.status) : '--' }}
            </span>
          </div>
        </div>
        
        </div>
      </div>
    </div>
    
    <!-- 更新通知 -->
    <div v-if="showUpdateNotification" class="update-notification">
      <div class="notification-content">
        <i class="icon-update">🔄</i>
        <span class="notification-message">{{ updateNotificationMessage }}</span>
        <button class="notification-close" @click="showUpdateNotification = false">×</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
// WebSocket服务已移除，使用HTTP轮询
import frontendLogger from '../../utils/logger.js'
import { deviceApi } from '../../services/api_v2.js'
import imagePreviewService from '../../services/imagePreviewService.js'
import smartUpdateManager from '../../utils/smartUpdateManager.js'
import statusUpdateManager from '../../utils/statusUpdateManager.js'

// Props - 移除测试模式相关props

// 响应式数据
const refreshTimer = ref(null)
const hasError = ref(false)
const errorMessage = ref('')
const isAnalyzing = ref(false)
const isLoading = ref(false)

// 设备数据
const devices = ref([])

// 移除图片预览相关状态，使用全局服务

// 差异更新相关状态
const updateStats = ref(statusUpdateManager.getUpdateStats())
const lastUpdateResult = ref(null)
const showUpdateNotification = ref(false)
const updateNotificationMessage = ref('')
const deviceChangeHighlights = ref(new Map()) // 设备变化高亮状态

// 计算属性：显示前4个设备用于四组件并排显示
const displayDevices = computed(() => {
  return devices.value.slice(0, 4)
})

// 方法
const getDisplayCards = () => {
  // 始终返回4个卡片，不足的用占位符填充
  const cards = [...displayDevices.value]
  while (cards.length < 4) {
    cards.push({
      id: null,
      name: `设备${cards.length + 1}`,
      coreParameter: null,
      referenceValue: null,
      actualValue: null,
      status: null,
      imageUrl: null
    })
  }
  return cards
}

const getImageLabel = (index) => {
  const labels = ['A', 'B', 'C', 'D']
  return labels[index] || 'A'
}

const getStatusText = (status) => {
  const statusMap = {
    '正常': '正常',
    '异常': '异常',
    '液位不足': '液位不足',
    '转速异常': '转速异常',
    '温度异常': '温度异常',
    '光源不足': '光源不足',
    '等待数据': '等待数据',
    '分析中...': '分析中...',
    '分析失败': '分析失败'
  }
  return statusMap[status] || status || '未知'
}

// 新增：根据数据状态获取显示值
const getDisplayValue = (device) => {
  if (!device.id) return '--'
  if (device.dataStatus === 'waiting') return '等待数据'
  if (device.dataStatus === 'analyzing') return '分析中...'
  if (device.dataStatus === 'error') return '分析失败'
  return device.actualValue || '--'
}

// 新增：根据数据状态获取CSS类
const getDataStatusClass = (device) => {
  if (!device.id) return 'placeholder'
  if (device.dataStatus === 'waiting') return 'waiting'
  if (device.dataStatus === 'analyzing') return 'analyzing'
  if (device.dataStatus === 'error') return 'error'
  return 'ready'
}

// 根据设备名称确定设备类型
const getDeviceTypeFromName = (deviceName) => {
  if (deviceName.includes('低温冰箱')) return '低温冰箱'
  if (deviceName.includes('液氮罐')) return '液氮罐'
  return '低温冰箱' // 默认类型
}

// 根据步骤顺序确定设备类型（第4个是液氮罐）
const getDeviceTypeByStep = (stepOrder) => {
  if (stepOrder === 4) return '液氮罐'
  return '低温冰箱'
}

// 根据设备类型和步骤生成设备参数
const getDeviceParams = (deviceType, stepOrder) => {
  if (deviceType === '低温冰箱') {
    // 根据图片数据生成参数
    const tempData = [
      { current: '-79.8°C', set: '-80°C', status: '正常' },
      { current: '-75°C', set: '-80°C', status: '异常' },
      { current: '-80.2°C', set: '-80°C', status: '正常' }
    ]
    const data = tempData[stepOrder - 1] || tempData[0]
    
    return {
      currentTemp: data.current,
      setTemp: data.set,
      normalStatus: '正常',
      abnormalStatus: '异常',
      doorOpenStatus: '门开'
    }
  } else if (deviceType === '液氮罐') {
    // 第4个设备是液氮罐
    return {
      currentVolume: '40L',
      safeVolume: '60L',
      normalStatus: '正常',
      abnormalStatus: '异常',
      doorOpenStatus: '门开'
    }
  }
  
  return {
    currentTemp: '--',
    setTemp: '--',
    normalStatus: '正常',
    abnormalStatus: '异常',
    doorOpenStatus: '门开'
  }
}

const getStatusClass = (status) => {
  if (status === '正常') return 'normal'
  if (status === '异常' || status === '液位不足' || status === '转速异常' || status === '温度异常' || status === '光源不足') return 'error'
  return 'normal'
}

const getDeviceIcon = (deviceType) => {
  const iconMap = {
    '低温冰箱': 'icon-refrigerator',
    '液氮罐': 'icon-tank',
    '离心机': 'icon-centrifuge',
    '培养箱': 'icon-incubator',
    '显微镜': 'icon-microscope'
  }
  return iconMap[deviceType] || 'icon-device'
}

const refreshDevices = async () => {
  frontendLogger.info('DeviceMonitor', 'refreshDevices', null, '开始刷新设备数据')
  
  isLoading.value = true
  hasError.value = false
  errorMessage.value = ''
  
  try {
    // 按巡检顺序获取设备状态
    const response = await deviceApi.getStatus()
    frontendLogger.info('DeviceMonitor', 'refreshDevices', { 
      responseStatus: response.status,
      responseData: response.data 
    }, 'API响应数据')
    
    if (response && response.success) {
      frontendLogger.info('DeviceMonitor', 'refreshDevices', { 
        deviceCount: response.data.length,
        devices: response.data.map(d => ({ id: d.device_id, name: d.device_name, status: d.status }))
      }, '设备数据获取成功')
      
      devices.value = response.data.map(device => {
        // 根据步骤顺序确定设备类型（第4个是液氮罐）
        const deviceType = getDeviceTypeByStep(device.step_order)
        const deviceParams = getDeviceParams(deviceType, device.step_order)
        
        // 解析LLM结果
        let llmData = null
        if (device.llm_result) {
          try {
            llmData = typeof device.llm_result === 'string' 
              ? JSON.parse(device.llm_result) 
              : device.llm_result
          } catch (e) {
            console.warn('解析LLM分析结果失败:', e)
          }
        }
        
        // 根据LLM结果更新参数
        let currentTemp = deviceParams.currentTemp
        let setTemp = deviceParams.setTemp
        let currentVolume = deviceParams.currentVolume
        let safeVolume = deviceParams.safeVolume
        let status = device.status
        
        if (llmData) {
          if (llmData['当前温度'] && llmData['设定温度']) {
            currentTemp = llmData['当前温度']
            setTemp = llmData['设定温度']
          }
          if (llmData['当前余量'] && llmData['安全余量']) {
            currentVolume = llmData['当前余量']
            safeVolume = llmData['安全余量']
          }
          if (llmData['系统状态']) {
            status = llmData['系统状态']
          }
        }
        
        return {
          id: device.id,
          name: device.name,
          location: `巡检点${device.step_order}`,
          status: status,
          icon: getDeviceIcon(deviceType),
          type: deviceType,
          // 温度相关参数（低温冰箱）
          currentTemp: currentTemp,
          setTemp: setTemp,
          // 液氮罐相关参数
          currentVolume: currentVolume,
          safeVolume: safeVolume,
          // 状态参数
          normalStatus: deviceParams.normalStatus,
          abnormalStatus: deviceParams.abnormalStatus,
          doorOpenStatus: deviceParams.doorOpenStatus,
          batteryLevel: 100,
          connectionStatus: 'connected',
          lastUpdate: new Date(device.inspected_at || device.created_at).toLocaleString('zh-CN'),
          dataStatus: device.status === 'completed' ? 'ready' : 'waiting',
          imageUrl: device.image_url || null,
          imageLoaded: !!device.image_url,
          imageTimestamp: device.inspected_at || null,
          aiAnalysis: llmData ? {
            status: llmData['系统状态'] === '正常' ? 'normal' : 'warning',
            text: llmData['系统状态'] || '分析中',
            confidence: 95,
            timestamp: new Date(device.inspected_at || device.created_at).toLocaleString('zh-CN'),
            details: `设备${device.name}状态分析完成`,
            recommendations: ['定期维护', '检查设备状态']
          } : null,
          // 添加巡检顺序
          inspectionOrder: device.step_order || 0
        }
      })
      
      frontendLogger.info('DeviceMonitor', 'refreshDevices', { 
        processedDevices: devices.value.length,
        deviceIds: devices.value.map(d => d.id)
      }, '设备数据处理完成')
    } else {
      frontendLogger.warn('DeviceMonitor', 'refreshDevices', { 
        response: response 
      }, 'API返回失败或无数据')
      
      // 如果API返回失败但没有数据，不显示错误，而是显示空状态
      if (response && response.data && response.data.length === 0) {
        hasError.value = false
        devices.value = []
        frontendLogger.info('DeviceMonitor', 'refreshDevices', null, '设备数据为空，显示空状态')
      } else {
        hasError.value = true
        errorMessage.value = response?.message || '获取设备数据失败'
        frontendLogger.error('DeviceMonitor', 'refreshDevices', { 
          error: response?.message || '获取设备数据失败' 
        }, '设备数据获取失败')
      }
    }
  } catch (error) {
    frontendLogger.error('DeviceMonitor', 'refreshDevices', { 
      error: error.message,
      stack: error.stack,
      url: '/device/status?inspection_order=true'
    }, '获取设备状态失败')
    hasError.value = true
    errorMessage.value = '获取设备数据失败，请检查网络连接'
  } finally {
    isLoading.value = false
    frontendLogger.info('DeviceMonitor', 'refreshDevices', { 
      finalDeviceCount: devices.value.length,
      hasError: hasError.value
    }, '设备数据刷新完成')
  }
}



// 移除模拟数据函数，改为从数据库获取真实数据


// 自动刷新功能
const startAutoRefresh = () => {
  refreshTimer.value = setInterval(refreshDevices, 2000) // 每2秒刷新
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

const handleImageError = (event) => {
  // 处理图片加载错误
  event.target.style.display = 'none'
}

// 图片预览相关方法
const openPreview = (imageUrl, alt) => {
  frontendLogger.info('DeviceMonitor', 'openPreview', { imageUrl, alt }, '打开图片预览')
  imagePreviewService.openPreview(imageUrl, alt)
}

// 差异更新处理方法
const handleDeviceStatusUpdate = async (updateResult) => {
  try {
    const { diff, summary, keyChanges } = updateResult
    
    // 显示更新通知
    if (diff.summary.totalChanges > 0) {
      showUpdateNotification.value = true
      updateNotificationMessage.value = summary
      
      // 3秒后隐藏通知
      setTimeout(() => {
        showUpdateNotification.value = false
      }, 3000)
    }
    
    // 处理设备变化高亮
    if (diff.modified.length > 0) {
      for (const modified of diff.modified) {
        const deviceId = modified.deviceId
        deviceChangeHighlights.value.set(deviceId, {
          type: 'modified',
          timestamp: Date.now(),
          changes: modified.changes
        })
        
        // 2秒后移除高亮
        setTimeout(() => {
          deviceChangeHighlights.value.delete(deviceId)
        }, 2000)
      }
    }
    
    // 处理新增设备高亮
    if (diff.added.length > 0) {
      for (const added of diff.added) {
        const deviceId = added.deviceId
        deviceChangeHighlights.value.set(deviceId, {
          type: 'added',
          timestamp: Date.now()
        })
        
        // 3秒后移除高亮
        setTimeout(() => {
          deviceChangeHighlights.value.delete(deviceId)
        }, 3000)
      }
    }
    
    // 记录关键变化
    if (keyChanges.length > 0) {
      frontendLogger.info('DeviceMonitor', 'handleDeviceStatusUpdate', {
        keyChanges: keyChanges.map(change => ({
          type: change.type,
          deviceId: change.deviceId,
          message: change.message
        }))
      }, '检测到关键变化')
    }
    
  } catch (error) {
    frontendLogger.error('DeviceMonitor', 'handleDeviceStatusUpdate', { 
      error: error.message 
    }, '处理设备状态更新失败')
  }
}

// 获取设备变化高亮类名
const getDeviceHighlightClass = (deviceId) => {
  const highlight = deviceChangeHighlights.value.get(deviceId)
  if (!highlight) return ''
  
  const elapsed = Date.now() - highlight.timestamp
  if (elapsed > 2000) return ''
  
  return `highlight-${highlight.type}`
}

const formatImageTimestamp = (timestamp) => {
  if (!timestamp) return ''
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    return '刚刚'
  }
}

// WebSocket事件处理函数已移除
const handleWebSocketDeviceStatusUpdate = (data) => {
  console.log('收到设备状态更新:', data)
  refreshDevices()
}

const handleDeviceStatus = (data) => {
  console.log('收到设备状态:', data)
  refreshDevices()
}

// 新增：处理设备数据更新事件
const handleDeviceDataUpdate = (data) => {
  console.log('收到设备数据更新:', data)
  
  // 更新对应设备的数据
  const deviceIndex = devices.value.findIndex(d => d.id === data.device_id)
  if (deviceIndex !== -1) {
    // 映射后端数据到前端格式
    const updatedDevice = {
      id: data.device_id,
      name: data.device_name,
      location: data.location,
      status: data.status,
      icon: getDeviceIcon(data.device_type),
      type: data.device_type,
      coreParameter: data.core_parameter,
      actualValue: data.actual_value,
      referenceValue: data.reference_value,
      batteryLevel: data.battery_level,
      connectionStatus: data.connection_status,
      lastUpdate: new Date(data.updated_at).toLocaleString('zh-CN'),
      dataStatus: data.actual_value ? 'ready' : 'waiting',
      imageUrl: data.image_url || null,
      aiAnalysis: data.ai_analysis_result ? {
        status: data.ai_analysis_result.status === '正常' ? 'normal' : 'warning',
        text: data.ai_analysis_result.status,
        confidence: data.ai_analysis_result.confidence || 95,
        timestamp: new Date(data.updated_at).toLocaleString('zh-CN'),
        details: `设备${data.device_name}状态分析完成`,
        recommendations: ['定期维护', '检查设备状态']
      } : null
    }
    
    devices.value[deviceIndex] = updatedDevice
    console.log(`设备 ${data.device_id} 数据已实时更新`)
  }
}

// 加载初始数据
const loadInitialData = async () => {
  await refreshDevices()
}

onMounted(() => {
  // 加载初始数据
  loadInitialData()
  
  // 启动自动刷新
  startAutoRefresh()
})

onUnmounted(() => {
  // 清理定时器
  stopAutoRefresh()
})
</script>

<style scoped>
.device-monitor {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 8px;
  padding: 20px;
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.monitor-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0;
  color: #4fc3f7;
}

.monitor-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}


/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(79, 195, 247, 0.2);
  border-top: 4px solid #4fc3f7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.loading-text {
  color: #4fc3f7;
  font-size: 1.1rem;
  font-weight: 500;
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 60px 20px;
  text-align: center;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.8;
}

.error-text {
  color: #f44336;
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.error-detail {
  color: #b3d9ff;
  font-size: 0.9rem;
  margin-bottom: 25px;
  max-width: 400px;
  line-height: 1.5;
}

.retry-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: linear-gradient(135deg, #d32f2f, #b71c1c);
  transform: translateY(-1px);
}

/* 空数据状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.6;
}

.empty-text {
  color: #4fc3f7;
  font-size: 1.3rem;
  font-weight: bold;
  margin-bottom: 10px;
}

.empty-detail {
  color: #b3d9ff;
  font-size: 0.9rem;
  margin-bottom: 25px;
  max-width: 400px;
  line-height: 1.5;
}

/* 设备内容区域 */
.device-content {
  position: relative;
  flex: 1;
  overflow-y: auto;
}

/* 覆盖层样式 */
.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 12px;
}

/* 四组件并排显示 */
.device-grid-four {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
  height: 100%;
}

.device-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 10px;
  border: 2px solid rgba(79, 195, 247, 0.3);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 300px;
  max-height: 800px;
}

.device-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}

.device-card.alert {
  border-color: #f44336;
  background: rgba(244, 67, 54, 0.1);
}

.device-card.warning {
  border-color: #ff9800;
  background: rgba(255, 152, 0, 0.1);
}

.device-card.placeholder {
  border-color: #666;
  background: rgba(255, 255, 255, 0.02);
  opacity: 0.6;
}

.device-card.placeholder .indicator-value {
  color: #888;
  height: calc(100% - 10px);
  min-height: 4vh;
}

/* 数据状态样式 */
.indicator-value.waiting {
  color: #ffa726;
  font-style: italic;
}

.indicator-value.analyzing {
  color: #42a5f5;
  animation: pulse 1.5s ease-in-out infinite;
}

.indicator-value.error {
  color: #f44336;
  font-weight: bold;
}

.indicator-value.ready {
  color: #4caf50;
}

.indicator-value.placeholder {
  color: #888;
}

/* 机器人回传图片区域 */
.robot-image-section {
  margin-bottom: 10px;
}

.image-placeholder {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  border: 1px dashed rgba(79, 195, 247, 0.3);
}

.image-label {
  font-size: 0.9rem;
  color: #4fc3f7;
  margin-bottom: 10px;
  font-weight: 500;
}

.image-container {
  height: 60%;
  min-height: 160px;
  max-height: 400px;
  border-radius: 6px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.2);
  position: relative;
  cursor: pointer;
  flex-shrink: 0;
  flex-grow: 1;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.clickable-image {
  cursor: pointer;
}

.clickable-image:hover {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.image-container:hover .image-overlay {
  opacity: 1;
}

.preview-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
  font-size: 12px;
  text-align: center;
}

.preview-hint i {
  font-size: 20px;
  margin-bottom: 4px;
}

.preview-hint span {
  font-weight: 500;
}

/* 差异更新相关样式 */
.update-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #409eff;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  z-index: 1000;
  animation: slideInRight 0.3s ease;
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.notification-message {
  font-size: 14px;
  font-weight: 500;
}

.notification-close {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.3s ease;
}

.notification-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 设备变化高亮效果 */
.highlight-modified {
  animation: highlightModified 2s ease;
  border: 2px solid #e6a23c !important;
  box-shadow: 0 0 10px rgba(230, 162, 60, 0.5) !important;
}

.highlight-added {
  animation: highlightAdded 3s ease;
  border: 2px solid #67c23a !important;
  box-shadow: 0 0 10px rgba(103, 194, 58, 0.5) !important;
}

.highlight-removed {
  animation: highlightRemoved 2s ease;
  border: 2px solid #f56c6c !important;
  box-shadow: 0 0 10px rgba(245, 108, 108, 0.5) !important;
}

/* 高亮动画 */
@keyframes highlightModified {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(230, 162, 60, 0.5);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(230, 162, 60, 0.8);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 10px rgba(230, 162, 60, 0.5);
  }
}

@keyframes highlightAdded {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(103, 194, 58, 0.5);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(103, 194, 58, 0.8);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 10px rgba(103, 194, 58, 0.5);
  }
}

@keyframes highlightRemoved {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(245, 108, 108, 0.5);
  }
  50% {
    transform: scale(0.98);
    box-shadow: 0 0 20px rgba(245, 108, 108, 0.8);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 10px rgba(245, 108, 108, 0.5);
  }
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.no-image {
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #b3d9ff;
  font-size: 0.8rem;
}

.no-image i {
  font-size: 2rem;
  margin-bottom: 8px;
  opacity: 0.5;
}

/* 指标信息区域 */
.indicators-section {
  margin-bottom: 20px;
}

.indicator-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 3px;
  padding: 2px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.indicator-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.indicator-label {
  color: #b3d9ff;
  font-size: 0.9rem;
  font-weight: 500;
}

.indicator-value {
  color: #ffffff;
  font-weight: 600;
  font-size: 0.9rem;
}

.indicator-value.alert {
  color: #f44336;
}

.indicator-value.status.normal {
  color: #4caf50;
}

.indicator-value.status.error {
  color: #f44336;
}

.indicator-value.status.warning {
  color: #ff9800;
}

/* 设备信息区域 */
.device-info-section {
  margin-bottom: 20px;
  text-align: center;
}

.device-info-section .device-name {
  font-size: 1.1rem;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 5px;
}

.device-info-section .device-location {
  font-size: 0.8rem;
  color: #b3d9ff;
}

.device-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.device-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(79, 195, 247, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  font-size: 1.5rem;
  color: #4fc3f7;
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 1rem;
  font-weight: bold;
  margin: 0 0 4px 0;
  color: #ffffff;
}

.device-location {
  font-size: 0.8rem;
  color: #b3d9ff;
  margin: 0;
}

.device-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.device-status.normal .status-dot {
  background: #4caf50;
  box-shadow: 0 0 10px #4caf50;
}

.device-status.warning .status-dot {
  background: #ff9800;
  box-shadow: 0 0 10px #ff9800;
}

.device-status.error .status-dot {
  background: #f44336;
  box-shadow: 0 0 10px #f44336;
}

.device-image {
  position: relative;
  height: 120px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  margin-bottom: 15px;
  overflow: hidden;
}

.device-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 8px;
  right: 8px;
}

.analysis-result {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 500;
}

.analysis-result.normal {
  background: rgba(76, 175, 80, 0.9);
  color: white;
}

.analysis-result.warning {
  background: rgba(255, 152, 0, 0.9);
  color: white;
}

.analysis-result.error {
  background: rgba(244, 67, 54, 0.9);
  color: white;
}

.device-params {
  margin-bottom: 15px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 0.8rem;
}

.param-label {
  color: #b3d9ff;
}

.param-value {
  color: #ffffff;
  font-weight: 500;
}

.param-value.alert {
  color: #f44336;
}

.device-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #4fc3f7, #29b6f6);
  color: white;
}

.action-btn.primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #29b6f6, #0288d1);
}

.action-btn.primary:disabled {
  background: rgba(79, 195, 247, 0.3);
  cursor: not-allowed;
  opacity: 0.6;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: #b3d9ff;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.device-timestamp {
  font-size: 0.7rem;
  color: #b3d9ff;
  text-align: center;
  margin-top: auto;
}



@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 1600px) {
  .device-grid-four {
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
  }
}

@media (max-width: 1200px) {
  .device-grid-four {
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }
}

@media (max-width: 900px) {
  .device-grid-four {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}

@media (max-width: 768px) {
  .device-grid-four {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .device-card {
    padding: 15px;
    min-height: 500px;
    height: 100%;
  }
  
  .image-container {
    height: 50%;
    min-height: 150px;
    max-height: 300px;
  }
  
  .no-image {
    height: 100px;
  }
}

@media (max-width: 480px) {
  .device-card {
    padding: 12px;
    min-height: 450px;
    height: 100%;
  }
  
  .image-container {
    height: 45%;
    min-height: 120px;
    max-height: 250px;
  }
  
  .no-image {
    height: 80px;
  }
  
  .indicator-item {
    margin-bottom: 4px;
    padding: 3px 0;
  }
  
  .indicator-label,
  .indicator-value {
    font-size: 0.8rem;
  }
}
</style>
