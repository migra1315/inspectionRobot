<template>
  <div class="security-monitor">
    <div class="monitor-header">
      <h3 class="monitor-title">安防监控</h3>

    </div>
    
    <div class="monitor-content">
      <!-- 左侧：RTMP推流 -->
      <div class="video-container single">
        <div class="video-item" 
             v-for="(camera, index) in displayCameras" 
             :key="camera.id"
        >
        <div class="video-header">
          <div class="camera-info">
            <span class="camera-name">{{ camera.name }}</span>
            <span class="camera-status" :class="camera.status">
              <span class="status-dot"></span>
              {{ getStatusText(camera.status) }}
            </span>
          </div>
          <div class="video-controls">
            <button class="control-btn" @click="toggleRecording(camera)">
              <i :class="camera.recording ? 'icon-stop' : 'icon-record'"></i>
            </button>
            <button class="control-btn" @click="toggleFullscreen(camera)">
              <i class="icon-expand"></i>
            </button>
          </div>
        </div>
        
        <div class="video-content">
          <div class="video-placeholder" v-if="!camera.isOnline">
            <div class="placeholder-content">
              <i class="icon-camera"></i>
              <p>摄像头离线</p>
              <div class="camera-details" v-if="camera.ip">
                <p class="detail-text">IP: {{ camera.ip }}:{{ camera.port }}</p>
                <p class="detail-text" v-if="camera.rtspUrl">RTSP: {{ camera.rtspUrl }}</p>
              </div>
            </div>
          </div>
          <div class="video-stream" v-else-if="camera.streamUrl">
            <img :src="camera.streamUrl" :alt="camera.name" @error="handleStreamError" @load="handleStreamLoad">
            <div class="stream-overlay">
              <div class="timestamp">{{ currentTime }}</div>
              <div class="recording-indicator" v-if="camera.recording">
                <span class="rec-dot"></span>
                REC
              </div>
            </div>
          </div>
          <div class="video-connecting" v-else>
            <div class="placeholder-content">
              <i class="icon-loading"></i>
              <p>连接RTSP流中...</p>
              <div class="camera-details">
                <p class="detail-text">{{ camera.name }}</p>
                <p class="detail-text">{{ camera.ip }}:{{ camera.port }}</p>
                <p class="detail-text" v-if="camera.rtspUrl">{{ camera.rtspUrl }}</p>
              </div>
              <button class="retry-btn" @click="retryConnection(camera)">重试连接</button>
            </div>
          </div>
        </div>
        
        <div class="video-footer">
          <div class="video-stats">
            <span class="stat-item">
              <i class="icon-eye"></i>
              {{ camera.viewCount }}
            </span>
            <span class="stat-item">
              <i class="icon-clock"></i>
              {{ camera.uptime }}
            </span>
          </div>
          <div class="video-quality">
            <span class="quality-label">画质:</span>
            <span class="quality-value">{{ camera.quality }}</span>
          </div>
        </div>
        </div>
      </div>
      
      <!-- 右侧：报警信息区域 -->
      <div class="alert-container">
        <!-- 报警图像组件 -->
        <SecurityAlertImage 
          :alert-image="currentAlert?.image_url"
          :alert-type="currentAlert?.alert_type"
        />
        
        <!-- 报警信息说明组件 -->
        <SecurityAlertInfo 
          :alert-info="currentAlert"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
// WebSocket服务已移除，使用HTTP轮询
import apiService from '../../services/api.js'
import SecurityAlertImage from './SecurityAlertImage.vue'
import SecurityAlertInfo from './SecurityAlertInfo.vue'

// Props - 移除测试模式相关props

// 响应式数据
const currentTime = ref('')
const snapshotTimer = ref(null)

// 摄像头数据
const cameras = ref([])

// 安全告警数据
const alerts = ref([])

// 当前报警信息
const currentAlert = ref(null)

// 计算属性 - 默认显示第一个摄像头
const displayCameras = computed(() => {
  return cameras.value.slice(0, 1) // 只显示第一个摄像头
})





// 方法
const getStatusText = (status) => {
  const statusMap = {
    'active': '在线',
    'inactive': '离线',
    'online': '在线',
    'warning': '警告',
    'offline': '离线'
  }
  return statusMap[status] || status || '未知'
}

const getStatusClass = (status) => {
  if (status === 'active' || status === 'online') return 'online'
  if (status === 'inactive' || status === 'offline') return 'offline'
  if (status === 'warning') return 'warning'
  return 'offline'
}

const getAlertLevel = (severity) => {
  const levelMap = {
    'high': 'high',
    'medium': 'medium',
    'low': 'low'
  }
  return levelMap[severity] || 'medium'
}

const getAlertIcon = (type) => {
  const iconMap = {
    '移动检测': 'icon-person',
    '异常行为': 'icon-warning',
    '设备故障': 'icon-error',
    '网络异常': 'icon-network',
    '摄像头离线': 'icon-camera-off',
    '摄像头恢复': 'icon-camera'
  }
  return iconMap[type] || 'icon-warning'
}



const toggleRecording = (camera) => {
  camera.recording = !camera.recording
  // 这里可以调用API控制录制
}

const toggleFullscreen = (camera) => {
  // 全屏显示逻辑
  console.log('全屏显示摄像头:', camera.name)
}

const handleStreamError = (event) => {
  // 处理视频流错误
  console.error('视频流加载失败:', event.target.src)
  event.target.style.display = 'none'
  
  // 显示错误信息
  const streamContainer = event.target.parentElement
  if (streamContainer) {
    streamContainer.innerHTML = `
      <div class="placeholder-content">
        <i class="icon-warning"></i>
        <p>视频流加载失败</p>
        <p class="detail-text">${event.target.src}</p>
        <button class="retry-btn" onclick="location.reload()">刷新页面</button>
      </div>
    `
  }
}

const handleStreamLoad = (event) => {
  console.log('视频流加载成功:', event.target.src)
}

const retryConnection = async (camera) => {
  console.log('重试连接摄像头:', camera.name)
  // 重新加载摄像头数据
  await loadCameras()
}

const handleAlert = (alert) => {
  alert.handled = true
  // 处理告警逻辑
  console.log('处理告警:', alert.title)
}

const dismissAlert = async (alert) => {
  try {
    const response = await apiService.post(`/security/alerts/${alert.id}/acknowledge`)
    if (response.success) {
      const index = alerts.value.findIndex(a => a.id === alert.id)
      if (index > -1) {
        alerts.value.splice(index, 1)
      }
    }
  } catch (error) {
    console.error('确认告警失败:', error)
  }
}

// 加载最新报警
const loadLatestAlert = async () => {
  try {
    const response = await apiService.get('/security/alerts?limit=1&sort=timestamp&order=desc')
    if (response && response.success && response.data.length > 0) {
      const latestAlert = response.data[0]
      // 检查是否有新报警
      if (!currentAlert.value || latestAlert.id !== currentAlert.value.id) {
        currentAlert.value = latestAlert
        // 显示新报警通知
        showAlertNotification(latestAlert)
      }
    }
  } catch (error) {
    console.error('加载最新报警失败:', error)
  }
}

// 显示报警通知
const showAlertNotification = (alert) => {
  console.log('收到新报警:', alert)
  // 可以在这里添加通知显示逻辑
}



// 加载摄像头数据
const loadCameras = async () => {
  try {
    const response = await apiService.get('/security/streams')
    console.log('摄像头数据响应:', response)
    
    if (response && response.success) {
      // 处理摄像头数据
      cameras.value = (response.data || []).map((camera, index) => {
        // 处理RTSP流URL，对于真实摄像头，需要转换为Web可访问的格式
        let streamUrl = null
        if (camera.is_online) {
          if (camera.rtsp_url && !camera.is_simulation) {
            // 使用MJPEG长连接视频流，优化参数
            const mjpegParams = 'use_sub=1&w=640&h=360&q=50&fps=8'  // 降低质量参数
            streamUrl = `/api/security/stream/${camera.id}/mjpeg?${mjpegParams}`
          } else if (camera.url) {
            // HTTP流可以直接使用
            streamUrl = camera.url
          }
        }
        
        return {
          id: camera.id,
          name: camera.name || `摄像头${index + 1}`,
          location: camera.location || '未知位置',
          status: getStatusClass(camera.status),
          streamUrl: streamUrl,
          recording: false,
          viewCount: Math.floor(Math.random() * 1000) + 500,
          uptime: '24h 15m',
          quality: camera.resolution || '640x360',
          signalStrength: camera.signal_strength || 0,
          isOnline: camera.is_online,
          rtspUrl: camera.rtsp_url,
          isSimulation: camera.is_simulation,
          ip: camera.ip,
          port: camera.port
        }
      })
      
      // 默认显示第一个摄像头
      
      console.log('处理后的摄像头数据:', cameras.value)
    }
  } catch (error) {
    console.error('加载摄像头数据失败:', error)
    // 如果API失败，使用模拟数据
    cameras.value = [
      {
        id: 'camera1',
        name: '摄像头1 - 主入口',
        location: '主入口',
        status: 'online',
        streamUrl: null,
        recording: false,
        viewCount: 750,
        uptime: '24h 15m',
        quality: '1080p',
        signalStrength: 85,
        isOnline: true
      },
      {
        id: 'camera2',
        name: '摄像头2 - 实验室A',
        location: '实验室A',
        status: 'online',
        streamUrl: null,
        recording: false,
        viewCount: 650,
        uptime: '24h 10m',
        quality: '1080p',
        signalStrength: 90,
        isOnline: true
      }
    ]

  }
}

// 切换为MJPEG视频流（长连接）
const MJPEG_PARAMS = 'use_sub=1&w=640&h=360&q=60&fps=8'
const startSnapshotRefresh = () => {
  if (snapshotTimer.value) clearInterval(snapshotTimer.value)
  cameras.value = cameras.value.map(cam => {
    if (cam.isOnline && cam.rtspUrl && !cam.isSimulation) {
      return { ...cam, streamUrl: `/api/security/stream/${cam.id}/mjpeg?${MJPEG_PARAMS}` }
    }
    return cam
  })
}

onMounted(async () => {
  await loadCameras()
  startSnapshotRefresh()
})

onUnmounted(() => {
  if (snapshotTimer.value) clearInterval(snapshotTimer.value)
})

// 加载告警数据
const loadAlerts = async () => {
  try {
    const response = await apiService.get('/security/alerts')
    if (response && response.success) {
      alerts.value = (response.data || []).map(alert => ({
        id: alert.id,
        level: getAlertLevel(alert.severity),
        title: alert.type,
        description: alert.message,
        time: new Date(alert.timestamp * 1000).toLocaleTimeString('zh-CN'),
        icon: getAlertIcon(alert.type),
        handled: alert.acknowledged,
        cameraName: alert.camera_name
      }))
    }
  } catch (error) {
    console.error('加载告警数据失败:', error)
  }
}

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 模拟数据更新
const updateCameraStats = () => {
  cameras.value.forEach(camera => {
    if (camera.status === 'online') {
      // 模拟观看人数变化
      camera.viewCount += Math.floor((Math.random() - 0.5) * 10)
      camera.viewCount = Math.max(0, camera.viewCount)
      
      // 模拟运行时间更新
      const uptimeParts = camera.uptime.split(' ')
      if (uptimeParts.length === 2) {
        const timeValue = parseInt(uptimeParts[0])
        const timeUnit = uptimeParts[1]
        if (timeUnit === 'h') {
          const minutes = parseInt(uptimeParts[1].replace('m', '')) || 0
          camera.uptime = `${timeValue}h ${minutes + 1}m`
        }
      }
    }
  })
}

// 定时器
let timeTimer = null
let statsTimer = null
let alertTimer = null

// WebSocket事件处理函数已移除
const handleSecurityStreamsUpdate = (data) => {
  console.log('收到安防视频流更新:', data)
  loadCameras()
}

const handleSecurityStreams = (data) => {
  console.log('收到安防视频流:', data)
  loadCameras()
}

// 处理安防报警事件
const handleSecurityAlert = (data) => {
  console.log('收到安防报警:', data)
  // 更新当前报警
  currentAlert.value = {
    alert_id: data.alert_id,
    alert_type: data.type,
    alert_message: data.message,
    severity: data.severity,
    image_url: data.image_url, // 使用WebSocket推送的图片URL
    acknowledged: false,
    created_at: new Date().toISOString()
  }
  
  // 显示报警通知
  showAlertNotification(currentAlert.value)
}

// 加载初始数据
const loadInitialData = async () => {
  await loadCameras()
  await loadAlerts()
  await loadLatestAlert()
}

onMounted(() => {
  // 加载初始数据
  loadInitialData()
  
  // 启动定时器
  updateTime()
  timeTimer = setInterval(updateTime, 1000)
  statsTimer = setInterval(updateCameraStats, 30000) // 每30秒更新统计
  alertTimer = setInterval(loadLatestAlert, 2000) // 每2秒检查一次新报警
})

onUnmounted(() => {
  // 清理定时器
  if (timeTimer) {
    clearInterval(timeTimer)
  }
  if (statsTimer) {
    clearInterval(statsTimer)
  }
  if (alertTimer) {
    clearInterval(alertTimer)
  }
})
</script>

<style scoped>
/* 强制全宽度样式 */
.security-monitor,
.security-monitor * {
  max-width: none !important; 
}


.security-monitor {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 8px;
  padding: 20px;
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 100%;
  width: 100% !important;
  min-width: 100% !important;
  max-width: none !important;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  flex: 1 1 100%;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.monitor-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0;
  color: #4fc3f7;
  min-width: 200px;
}





.monitor-content {
  display: flex;
  gap: 20px;
  height: calc(100% - 60px);
}

.video-container {
  flex: 1.5;
  display: grid;
  gap: 5px;
  margin-bottom: 0px;
}

.alert-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-width: 300px;
}

.video-container.single {
  grid-template-columns: 1fr;
}

.video-container.dual {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr;
}

.video-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.video-item.active {
  border-color: #4fc3f7;
  box-shadow: 0 0 15px rgba(79, 195, 247, 0.3);
}

.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: rgba(0, 0, 0, 0.3);
}

.camera-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.camera-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: #ffffff;
}

.camera-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.8rem;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.camera-status.online .status-dot {
  background: #4caf50;
  box-shadow: 0 0 8px #4caf50;
}

.camera-status.warning .status-dot {
  background: #ff9800;
  box-shadow: 0 0 8px #ff9800;
}

.camera-status.offline .status-dot {
  background: #f44336;
  box-shadow: 0 0 8px #f44336;
}

.video-controls {
  display: flex;
  gap: 5px;
}

.control-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.video-content {
  flex: 1;
  position: relative;
  background: #000000;
}

.video-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666666;
}

.placeholder-content i {
  font-size: 3rem;
  margin-bottom: 10px;
}

.placeholder-content p {
  margin: 0;
  font-size: 0.9rem;
}

.video-stream {
  height: 100%;
  position: relative;
}

.video-stream img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.stream-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 10px;
  pointer-events: none;
}

.timestamp {
  background: rgba(0, 0, 0, 0.7);
  color: #ffffff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-family: monospace;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(244, 67, 54, 0.9);
  color: #ffffff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.rec-dot {
  width: 6px;
  height: 6px;
  background: #ffffff;
  border-radius: 50%;
  animation: pulse 1s infinite;
}

.video-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: rgba(0, 0, 0, 0.3);
  font-size: 0.8rem;
}

.video-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #b3d9ff;
}

.quality-label {
  color: #b3d9ff;
  margin-right: 5px;
}

.quality-value {
  color: #4caf50;
  font-weight: 500;
}

.security-alerts {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
  max-height: 200px;
  overflow-y: auto;
  width: 100%;
  min-width: 100%;
  box-sizing: border-box;
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.alerts-header h4 {
  margin: 0;
  color: #4fc3f7;
  font-size: 1rem;
}

.alert-count {
  background: #f44336;
  color: #ffffff;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 6px;
  border-left: 4px solid;
}

.alert-item.high {
  background: rgba(244, 67, 54, 0.1);
  border-left-color: #f44336;
}

.alert-item.medium {
  background: rgba(255, 152, 0, 0.1);
  border-left-color: #ff9800;
}

.alert-item.low {
  background: rgba(76, 175, 80, 0.1);
  border-left-color: #4caf50;
}

.alert-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.alert-item.high .alert-icon {
  color: #f44336;
}

.alert-item.medium .alert-icon {
  color: #ff9800;
}

.alert-item.low .alert-icon {
  color: #4caf50;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 2px;
}

.alert-description {
  font-size: 0.8rem;
  color: #b3d9ff;
  margin-bottom: 2px;
}

.alert-time {
  font-size: 0.7rem;
  color: #666666;
}

.alert-actions {
  display: flex;
  gap: 5px;
}

.alert-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.alert-btn:not(.dismiss) {
  background: #4fc3f7;
  color: #ffffff;
}

.alert-btn.dismiss {
  background: rgba(255, 255, 255, 0.1);
  color: #b3d9ff;
}

.alert-btn:hover {
  opacity: 0.8;
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

/* 响应式设计 */
@media (max-width: 1920px) {
  .video-container.dual {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(2, 1fr);
  }
}

@media (max-width: 1440px) {

  
  .video-header,
  .video-footer {
    padding: 8px 12px;
  }
  
  .security-alerts {
    max-height: 150px;
  }
}
</style>
