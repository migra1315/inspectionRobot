<template>
  <div class="dashboard-container">
    <!-- 顶部标题区域 -->
    <div class="dashboard-header">
      <div class="system-title">智能巡检系统</div>
      <div class="system-status">
        <div class="status-indicator" :class="systemStatusClass">
          <div class="dot"></div>
        </div>
        <span>系统状态 {{ systemStatusText }}</span>
      </div>
    </div>

    <!-- 上方区域：机器人状态和环境监控 -->
    <div class="top-section">
      <div class="robot-status-panel dashboard-panel">
        <RobotStatus />
      </div>
      <div class="environment-panel dashboard-panel">
        <EnvironmentMonitor />
      </div>
    </div>

    <!-- 下方区域：设备监控和安防监控 -->
    <div class="bottom-section">
      <div class="device-monitor-panel dashboard-panel">
        <DeviceMonitor />
      </div>
      <div class="security-monitor-panel dashboard-panel">
        <SecurityMonitor />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import RobotStatus from '../components/dashboard/RobotStatus.vue'
import EnvironmentMonitor from '../components/dashboard/EnvironmentMonitor.vue'
import DeviceMonitor from '../components/dashboard/DeviceMonitor.vue'
import SecurityMonitor from '../components/dashboard/SecurityMonitor_v2.vue'
// WebSocket服务已移除，使用HTTP轮询

// 系统状态
const systemStatus = ref('normal') // normal, abnormal

// 计算系统状态样式和文本
const systemStatusClass = computed(() => ({
  'status-normal': systemStatus.value === 'normal',
  'status-abnormal': systemStatus.value === 'abnormal'
}))

const systemStatusText = computed(() => {
  return systemStatus.value === 'normal' ? '正常' : '异常'
})

// WebSocket事件监听已移除
const handleSystemStatusUpdate = (data) => {
  console.log('收到系统状态更新:', data)
  // 根据数据更新系统状态
  if (data.status) {
    systemStatus.value = data.status
  }
}

const handleRobotStatusUpdate = (data) => {
  console.log('收到机器人状态更新:', data)
  // 可以在这里处理机器人状态更新
}

const handleEnvironmentUpdate = (data) => {
  console.log('收到环境数据更新:', data)
  // 可以在这里处理环境数据更新
}

const handleDeviceStatusUpdate = (data) => {
  console.log('收到设备状态更新:', data)
  // 可以在这里处理设备状态更新
}

const handleSecurityAlert = (data) => {
  console.log('收到安防告警:', data)
  // 可以在这里处理安防告警
}



// 组件挂载时初始化
onMounted(() => {
  console.log('Dashboard已启动，使用HTTP轮询通信')
})

// 组件卸载时清理
onUnmounted(() => {
  console.log('Dashboard已卸载')
})


</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  gap: 0;
  padding: 15px;
  background: linear-gradient(135deg, #0c1426 0%, #1a2332 100%);
  box-sizing: border-box;
  overflow: hidden;
}

.dashboard-container > * {
  min-width: 0;
  min-height: 0;
}

/* 上方区域：机器人状态和环境监控 */
.top-section {
  display: flex;
  gap: 10px;
  height: 400px;
  margin-bottom: 10px;
}

/* 下方区域：设备监控和安防监控 */
.bottom-section {
  display: flex;
  gap: 10px;
  flex: 1;
  min-height: 600px;
}

.dashboard-panel {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  overflow: visible; /* 允许子组件显示滚动条 */
  display: flex;
  flex-direction: column;
}


.status-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
  font-size: 14px;
}

.status-tag {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-tag.info {
  background: #909399;
  color: white;
}

.status-tag.warning {
  background: #e6a23c;
  color: white;
}

.status-tag.success {
  background: #67c23a;
  color: white;
}

.progress-info {
  color: #c0c4cc;
  font-size: 12px;
}

.robot-status-panel,
.environment-panel {
  height: 100%;
}

.device-monitor-panel,
.security-monitor-panel {
  height: 100%;
  flex: 1;
}

.dashboard-header {
  grid-column: 1 / -1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 80px;
}

.system-title {
  font-size: 32px;
  font-weight: bold;
  color: #00d4ff;
  text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
}

.system-status {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator .dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-normal .dot {
  background-color: #67c23a;
  box-shadow: 0 0 10px rgba(103, 194, 58, 0.5);
}

.status-abnormal .dot {
  background-color: #f56c6c;
  box-shadow: 0 0 10px rgba(245, 108, 108, 0.5);
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(0, 212, 255, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(0, 212, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(0, 212, 255, 0);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .top-section,
  .bottom-section {
    flex-direction: column;
    height: auto;
  }
  
  .top-section {
    height: auto;
    margin-bottom: 10px;
  }
  
  .bottom-section {
    flex: 1;
    min-height: 600px;
  }
  
  .robot-status-panel,
  .environment-panel,
  .device-monitor-panel,
  .security-monitor-panel {
    height: 300px;
    margin-bottom: 10px;
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 10px;
    gap: 10px;
  }
  
  .system-title {
    font-size: 24px;
  }
}
</style>
