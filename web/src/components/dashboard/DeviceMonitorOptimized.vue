<template>
  <div class="device-monitor">
    <div class="monitor-header">
      <h3 class="monitor-title">设备状态监控</h3>

    </div>
    
    <!-- 设备监控内容区域 - 智能更新，无全局加载 -->
    <div class="device-content">
      <!-- 水平滑动容器 -->
      <div class="device-scroll-container">
        <div class="device-grid-horizontal">
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
          <div class="indicator-item">
            <span class="indicator-label">核心参数:</span>
            <span class="indicator-value">{{ device.coreParameter || '--' }}</span>
          </div>
          <div class="indicator-item">
            <span class="indicator-label">参考值:</span>
            <span class="indicator-value">{{ device.referenceValue || '--' }}</span>
          </div>
          <div class="indicator-item">
            <span class="indicator-label">实际值:</span>
            <span class="indicator-value" :class="getDataStatusClass(device)">
              {{ getDisplayValue(device) }}
            </span>
          </div>
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
    </div>
    

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
// WebSocket服务已移除，使用HTTP轮询
import frontendLogger from '../../utils/logger.js'
import apiService from '../../services/api.js'
import imagePreviewService from '../../services/imagePreviewService.js'
import smartUpdateManager from '../../utils/smartUpdateManager.js'

// 响应式数据
const autoRefresh = ref(true)
const refreshTimer = ref(null)
const hasError = ref(false)
const errorMessage = ref('')
const isAnalyzing = ref(false)

// 设备数据
const devices = ref([])



// 计算属性：显示前4个设备用于四组件并排显示
const displayDevices = computed(() => {
  return devices.value.slice(0, 4)
})

// 获取显示卡片（包括占位符）
const getDisplayCards = () => {
  const cards = [...displayDevices.value]
  // 确保始终显示4个卡片
  while (cards.length < 4) {
    cards.push({ id: null, name: '', status: '', placeholder: true })
  }
  return cards
}

// 获取图片标签
const getImageLabel = (index) => {
  const labels = ['第一张', '第二张', '第三张', '第四张']
  return labels[index] || '第' + (index + 1) + '张'
}

// 获取设备图标
const getDeviceIcon = (deviceType) => {
  const iconMap = {
    '低温冰箱': 'icon-refrigerator',
    '液氮罐': 'icon-tank',
  }
  return iconMap[deviceType] || 'icon-device'
}

// 智能刷新设备数据
const refreshDevices = async () => {
  frontendLogger.info('DeviceMonitor', 'refreshDevices', null, '开始智能刷新设备数据')
  
  hasError.value = false
  errorMessage.value = ''
  
  try {
    // 按巡检顺序获取设备状态
    const response = await apiService.get('/device/status?inspection_order=true')
    frontendLogger.info('DeviceMonitor', 'refreshDevices', { 
      responseStatus: response.status,
      responseData: response.data 
    }, 'API响应数据')
    
    if (response && response.success) {
      // 使用智能更新管理器处理数据
      const updateResult = smartUpdateManager.batchUpdateDevices(response.data)
      
      // 更新设备数据
      devices.value = response.data.map(device => ({
        id: device.device_id,
        name: device.device_name,
        location: device.location,
        status: device.status,
        icon: getDeviceIcon(device.device_type),
        type: device.device_type,
        coreParameter: device.core_parameter,
        actualValue: device.actual_value,
        referenceValue: device.reference_value,
        batteryLevel: device.battery_level,
        connectionStatus: device.connection_status,
        lastUpdate: new Date(device.updated_at).toLocaleString('zh-CN'),
        dataStatus: device.actual_value ? 'ready' : 'waiting',
        imageUrl: device.image_url || null,
        imageLoaded: !!device.image_url,
        imageTimestamp: device.updated_at
      }))
      
      // 处理更新结果（移除弹窗通知）
      
      frontendLogger.info('DeviceMonitor', 'refreshDevices', { 
        processedDevices: devices.value.length,
        deviceIds: devices.value.map(d => d.id),
        updateSummary: updateResult.summary,
        highlights: updateResult.highlights.length,
        animations: updateResult.animations.length
      }, '设备数据智能更新完成')
    } else {
      frontendLogger.warn('DeviceMonitor', 'refreshDevices', { 
        response: response 
      }, 'API返回失败或无数据')
      
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
  }
}

// WebSocket事件处理已移除
const handleWebSocketDeviceStatusUpdate = (data) => {
  console.log('收到设备状态更新:', data)
  
  // 使用智能更新管理器处理单个设备更新
  const updateResult = smartUpdateManager.smartUpdateDevice(data.device_id, data)
  
  if (updateResult.success) {
    // 更新对应设备的数据
    const deviceIndex = devices.value.findIndex(d => d.id === data.device_id)
    if (deviceIndex !== -1) {
      devices.value[deviceIndex] = {
        ...devices.value[deviceIndex],
        status: data.status,
        actualValue: data.actual_value,
        connectionStatus: data.connection_status,
        lastUpdate: new Date(data.updated_at).toLocaleString('zh-CN'),
        dataStatus: data.actual_value ? 'ready' : 'waiting'
      }
      
      // 移除弹窗通知
    }
  }
}

const handleDeviceStatus = (data) => {
  console.log('收到设备状态:', data)
  handleWebSocketDeviceStatusUpdate(data)
}

// 智能设备数据更新处理
const handleDeviceDataUpdate = (data) => {
  console.log('收到设备数据更新:', data)
  
  // 使用智能更新管理器处理
  const updateResult = smartUpdateManager.smartUpdateDevice(data.device_id, data, 'value')
  
  if (updateResult.success) {
    // 更新对应设备的数据
    const deviceIndex = devices.value.findIndex(d => d.id === data.device_id)
    if (deviceIndex !== -1) {
      devices.value[deviceIndex] = {
        ...devices.value[deviceIndex],
        actualValue: data.actual_value,
        lastUpdate: new Date(data.updated_at).toLocaleString('zh-CN'),
        dataStatus: data.actual_value ? 'ready' : 'waiting'
      }
      
      // 移除弹窗通知
    }
  }
}

// 图片预览相关方法
const openPreview = (imageUrl, alt) => {
  frontendLogger.info('DeviceMonitor', 'openPreview', { imageUrl, alt }, '打开图片预览')
  imagePreviewService.openPreview(imageUrl, alt)
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
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

// 数据状态相关方法
const getDataStatusClass = (device) => {
  if (!device.id) return 'waiting'
  return device.dataStatus || 'waiting'
}

const getDisplayValue = (device) => {
  if (!device.id) return '--'
  return device.actualValue || '等待数据'
}

const getStatusText = (status) => {
  const statusMap = {
    'normal': '正常',
    'warning': '警告',
    'error': '错误',
    'waiting': '等待数据'
  }
  return statusMap[status] || status || '未知'
}

// 自动刷新控制
const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
                refreshTimer.value = setInterval(refreshDevices, 3000) // 每3秒刷新（巡检过程中提高实时性）
    frontendLogger.info('DeviceMonitor', 'toggleAutoRefresh', null, '自动刷新已启用')
  } else {
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = null
      frontendLogger.info('DeviceMonitor', 'toggleAutoRefresh', null, '自动刷新已禁用')
    }
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
  if (autoRefresh.value) {
    toggleAutoRefresh()
  }
})

onUnmounted(() => {
  // 清理定时器
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
  }
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



.device-content {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.device-scroll-container {
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 10px;
}

.device-scroll-container::-webkit-scrollbar {
  height: 8px;
}

.device-scroll-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.device-scroll-container::-webkit-scrollbar-thumb {
  background: rgba(79, 195, 247, 0.6);
  border-radius: 4px;
}

.device-scroll-container::-webkit-scrollbar-thumb:hover {
  background: rgba(79, 195, 247, 0.8);
}

.device-grid-horizontal {
  display: flex;
  gap: 20px;
  height: 100%;
  min-width: max-content;
  padding: 0 10px;
}

.device-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-width: 300px;
  width: 300px;
  height: 100%;
  flex-shrink: 0;
  min-height: 500px;
}

.device-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(79, 195, 247, 0.3);
  transform: translateY(-2px);
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
  opacity: 0.5;
  border-style: dashed;
}

.robot-image-section {
  flex: 0 0 auto;
  margin-bottom: 15px;
  min-height: 0;
}

.image-placeholder {
  height: auto;
  min-height: 12vh;
  max-height: 30vh;
  aspect-ratio: 0.7;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
  margin: 0 auto;
  text-align: center;
}

.image-label {
  font-size: 0.7rem;
  color: #90a4ae;
  margin-bottom: 8px;
  text-align: center;
}

.image-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  overflow: hidden;
  border-radius: 6px;
  margin: 0 auto;
  text-align: center;
}

.clickable-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center center;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 6px;
  display: block;
  max-width: 100%;
  max-height: 100%;
}

.clickable-image:hover {
  transform: scale(1.02);
  filter: brightness(1.1);
}

.image-status {
  position: absolute;
  bottom: 5px;
  left: 5px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.8rem;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s ease;
  pointer-events: none;
  border-radius: 6px;
}

.image-container:hover .image-overlay {
  opacity: 1;
}

.preview-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
  font-size: 0.7rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.preview-hint i {
  font-size: 20px;
  margin-bottom: 4px;
}

.preview-hint span {
  font-weight: 500;
}

.no-image {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #90a4ae;
  font-size: 0.7rem;
  text-align: center;
}

.no-image i {
  font-size: 24px;
  margin-bottom: 8px;
  opacity: 0.5;
}

.indicators-section {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
  justify-content: flex-start;
}

.indicator-item {
  display: flex;
  align-items: center;
  font-size: 0.95rem;
  gap: 8px;
}

.indicator-label {
  color: #b0bec5;
  font-weight: 500;
  font-size: 0.95rem;
  min-width: 60px;
  text-align: right;
}

.indicator-value {
  color: #ffffff;
  font-weight: 600;
  font-size: 0.95rem;
  flex: 1;
  text-align: center;
}

.indicator-value.status {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.8rem;
}

.indicator-value.ready {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.indicator-value.waiting {
  background: rgba(255, 152, 0, 0.2);
  color: #ff9800;
}



/* 设备变化高亮效果 */
.highlight-status {
  animation: highlightStatus 2s ease;
  border: 2px solid #e6a23c !important;
  box-shadow: 0 0 10px rgba(230, 162, 60, 0.5) !important;
}

.highlight-connection {
  animation: highlightConnection 2s ease;
  border: 2px solid #67c23a !important;
  box-shadow: 0 0 10px rgba(103, 194, 58, 0.5) !important;
}

.highlight-analysis {
  animation: highlightAnalysis 2s ease;
  border: 2px solid #409eff !important;
  box-shadow: 0 0 10px rgba(64, 158, 255, 0.5) !important;
}

/* 设备变化动画效果 */
.animate-value {
  animation: animateValue 0.5s ease;
}

.animate-image {
  animation: animateImage 0.5s ease;
}

/* 高亮动画 */
@keyframes highlightStatus {
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

@keyframes highlightConnection {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(103, 194, 58, 0.5);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(103, 194, 58, 0.8);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 10px rgba(103, 194, 58, 0.5);
  }
}

@keyframes highlightAnalysis {
  0% {
    transform: scale(1);
    box-shadow: 0 0 0 rgba(64, 158, 255, 0.5);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 0 20px rgba(64, 158, 255, 0.8);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 10px rgba(64, 158, 255, 0.5);
  }
}

/* 数值变化动画 */
@keyframes animateValue {
  0% {
    transform: scale(1);
    color: #ffffff;
  }
  50% {
    transform: scale(1.1);
    color: #4caf50;
  }
  100% {
    transform: scale(1);
    color: #ffffff;
  }
}

/* 图片变化动画 */
@keyframes animateImage {
  0% {
    opacity: 0.7;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1);
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

/* 全屏模式优化 */
@media (min-height: 800px) {
  .image-placeholder {
    min-height: 18vh;
    max-height: 30vh;
  }
}

@media (min-height: 1000px) {
  .image-placeholder {
    min-height: 20vh;
    max-height: 25vh;
  }
}

@media (min-height: 1200px) {
  .image-placeholder {
    min-height: 25vh;
    max-height: 70vh;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .device-card {
    min-width: 240px;
    width: 240px;
    padding: 15px;
  }
  
  .image-placeholder {
    min-height: 10vh;
    max-height: 16vh;
  }
  
  .monitor-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .monitor-controls {
    width: 100%;
    justify-content: space-between;
  }
}

@media (max-width: 480px) {
  .device-card {
    min-width: 200px;
    width: 200px;
    padding: 12px;
  }
  
  .image-placeholder {
    min-height: 10vh;
    max-height: 18vh;
  }
  
  .device-monitor {
    padding: 15px;
  }
  
  .indicators-section {
    gap: 8px;
  }
  
  .indicator-item {
    font-size: 0.85rem;
  }
}
</style>
    