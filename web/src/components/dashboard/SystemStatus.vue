<template>
  <div class="system-status">
    <div class="status-header">
      <h3 class="status-title">系统状态</h3>
      <div class="status-indicator" :class="systemStatusClass">
        <span class="status-dot"></span>
        <span class="status-text">{{ systemStatusText }}</span>
      </div>
    </div>
    
    <div class="status-grid">
      <div class="status-item">
        <div class="status-label">运行时间</div>
        <div class="status-value">{{ uptime }}</div>
      </div>
      <div class="status-item">
        <div class="status-label">在线设备</div>
        <div class="status-value">{{ onlineDevices }}/{{ totalDevices }}</div>
      </div>
      <div class="status-item">
        <div class="status-label">巡检次数</div>
        <div class="status-value">{{ inspectionCount }}</div>
      </div>
      <div class="status-item">
        <div class="status-label">异常告警</div>
        <div class="status-value" :class="{ 'alert': alertCount > 0 }">{{ alertCount }}</div>
      </div>
    </div>
    
    <div class="status-chart">
      <div class="chart-title">系统负载</div>
      <div class="chart-container">
        <div class="chart-bar">
          <div class="bar-fill" :style="{ width: cpuUsage + '%' }"></div>
          <span class="bar-label">CPU: {{ cpuUsage }}%</span>
        </div>
        <div class="chart-bar">
          <div class="bar-fill" :style="{ width: memoryUsage + '%' }"></div>
          <span class="bar-label">内存: {{ memoryUsage }}%</span>
        </div>
        <div class="chart-bar">
          <div class="bar-fill" :style="{ width: diskUsage + '%' }"></div>
          <span class="bar-label">磁盘: {{ diskUsage }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

// 响应式数据
const systemStatus = ref('online') // online, warning, error
const uptime = ref('00:00:00')
const onlineDevices = ref(8)
const totalDevices = ref(10)
const inspectionCount = ref(156)
const alertCount = ref(2)
const cpuUsage = ref(45)
const memoryUsage = ref(62)
const diskUsage = ref(38)

// 计算属性
const systemStatusClass = computed(() => {
  switch (systemStatus.value) {
    case 'online': return 'status-online'
    case 'warning': return 'status-warning'
    case 'error': return 'status-error'
    default: return 'status-online'
  }
})

const systemStatusText = computed(() => {
  switch (systemStatus.value) {
    case 'online': return '正常运行'
    case 'warning': return '警告状态'
    case 'error': return '故障状态'
    default: return '正常运行'
  }
})

// 定时器
let uptimeTimer = null

// 启动运行时间计时器
const startUptimeTimer = () => {
  let seconds = 0
  uptimeTimer = setInterval(() => {
    seconds++
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    uptime.value = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }, 1000)
}

// 模拟系统状态更新
const updateSystemStatus = () => {
  // 模拟CPU使用率变化
  cpuUsage.value = Math.max(10, Math.min(90, cpuUsage.value + (Math.random() - 0.5) * 10))
  // 模拟内存使用率变化
  memoryUsage.value = Math.max(20, Math.min(85, memoryUsage.value + (Math.random() - 0.5) * 5))
  // 模拟磁盘使用率变化
  diskUsage.value = Math.max(15, Math.min(80, diskUsage.value + (Math.random() - 0.5) * 3))
}

onMounted(() => {
  startUptimeTimer()
  // 每5秒更新一次系统状态
  setInterval(updateSystemStatus, 5000)
})

onUnmounted(() => {
  if (uptimeTimer) {
    clearInterval(uptimeTimer)
  }
})
</script>

<style scoped>
.system-status {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 8px;
  padding: 20px;
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.status-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0;
  color: #4fc3f7;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-online .status-dot {
  background: #4caf50;
  box-shadow: 0 0 10px #4caf50;
}

.status-warning .status-dot {
  background: #ff9800;
  box-shadow: 0 0 10px #ff9800;
}

.status-error .status-dot {
  background: #f44336;
  box-shadow: 0 0 10px #f44336;
}

.status-text {
  font-size: 0.9rem;
  font-weight: 500;
}

.status-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.status-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 12px;
  text-align: center;
}

.status-label {
  font-size: 0.8rem;
  color: #b3d9ff;
  margin-bottom: 5px;
}

.status-value {
  font-size: 1.1rem;
  font-weight: bold;
  color: #ffffff;
}

.status-value.alert {
  color: #ff6b6b;
}

.status-chart {
  flex: 1;
}

.chart-title {
  font-size: 0.9rem;
  color: #4fc3f7;
  margin-bottom: 10px;
  font-weight: 500;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-bar {
  position: relative;
  height: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #4fc3f7, #29b6f6);
  border-radius: 10px;
  transition: width 0.3s ease;
  position: relative;
}

.bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

.bar-label {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.7rem;
  color: #ffffff;
  font-weight: 500;
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

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 响应式设计 */
@media (max-width: 1440px) {
  .status-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .status-item {
    padding: 8px;
  }
  
  .status-label {
    font-size: 0.7rem;
  }
  
  .status-value {
    font-size: 1rem;
  }
}
</style>
