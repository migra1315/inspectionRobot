<template>
  <div class="robot-status">
    <div class="robot-header">
      <h3 class="robot-title">巡检机器人状态</h3>
      <div class="connection-status" :class="connectionClass">
        <span class="connection-dot"></span>
        <span class="connection-text">{{ connectionText }}</span>
        <button v-if="!isConnected" class="reconnect-btn" @click="reconnectHardware" :disabled="isReconnecting">
          <i class="icon-refresh" :class="{ 'spinning': isReconnecting }"></i>
          {{ isReconnecting ? '重连中...' : '重新连接' }}
        </button>
      </div>
    </div>
    
    <div class="robot-info">
      <div class="info-item">
        <span class="info-label">当前位置:</span>
        <span class="info-value">{{ currentPosition }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">巡检状态:</span>
        <span class="info-value" :class="inspectionStatusClass">{{ inspectionStatus }}</span>
      </div>
    </div>
    

    
    <div class="robot-path">
      <div class="path-title">巡检路径</div>
      <div class="path-visualization">
        <div class="path-point" 
             v-for="(point, index) in pathPoints" 
             :key="point.id || index"
             :class="{ 
               'active': index === currentPathIndex && currentPathIndex >= 0,
               'completed': index < currentPathIndex && currentPathIndex >= 0,
               'pending': index > currentPathIndex || (currentPathIndex < 0 && index > 0),
               'base-station': index === 0 && currentPathIndex === -1
             }"
        >
          <div class="point-number">{{ point.inspection_order || index + 1 }}</div>
          <div class="point-label">{{ point.name }}</div>
          <!-- <div class="point-location">{{ point.location }}</div> -->
        </div>
      </div>
    </div>
    
    <div class="robot-controls">
      <div class="control-buttons">
        <button 
          class="control-btn start-btn" 
          :disabled="isStartButtonDisabled"
          @click="startInspection"
        >
          <i class="icon-play"></i>
          {{ startButtonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
// WebSocket服务已移除，使用HTTP轮询
import { taskApi } from '../../services/api_v2.js'

// 响应式数据
const isConnected = ref(false)
const currentPosition = ref('基站')
const inspectionStatus = ref('待机中')
const isInspecting = ref(false)
const progress = ref(0)
const currentTask = ref('等待任务')
const estimatedTime = ref('0分钟')
const currentPathIndex = ref(-1) // -1表示在基站，0开始表示巡检路径

// 自动刷新控制
const autoRefresh = ref(true)
const refreshTimer = ref(null)
const refreshInterval = 1000 // 1秒刷新间隔（巡检过程中提高实时性）

// 巡检路径点 - 从数据库动态获取
const pathPoints = ref([])

// 硬件连接状态
const hardwareStatus = ref({})
const isReconnecting = ref(false)

// 计算属性
const connectionClass = computed(() => {
  return isConnected.value ? 'connected' : 'disconnected'
})

const connectionText = computed(() => {
  return isConnected.value ? '已连接' : '连接断开'
})

const inspectionStatusClass = computed(() => {
  if (isInspecting.value) return 'status-inspecting'
  if (currentPathIndex.value === -1) return 'status-idle' // 在基站待机
  return 'status-idle'
})

// 计算按钮状态
const isStartButtonDisabled = computed(() => {
  return isInspecting.value || !isConnected.value
})

// 计算按钮文本
const startButtonText = computed(() => {
  if (isInspecting.value) return '巡检进行中...'
  if (currentPathIndex.value === -1) return '开始巡检'
  return '开始巡检'
})

// 获取任务进度
const loadTaskProgress = async () => {
  try {
    const response = await taskApi.getProgress()
    if (response.success) {
      const task = response.data
      isConnected.value = true  // 假设总是连接状态，除非明确断开
      
      // 更新状态 - 优先处理idle状态
      if (task.status === 'idle') {
        // idle状态 - 在基站待机
        isInspecting.value = false
        inspectionStatus.value = '待机中'
        currentPathIndex.value = -1  // 待机时在基站
        currentPosition.value = '基站'
        progress.value = 0
      } else if (task.status === 'running') {
        // running状态 - 正在巡检
        isInspecting.value = true
        inspectionStatus.value = '巡检中'
        
        // 更新路径索引
        if (task.current_step === 0) {
          currentPathIndex.value = -1  // 在基站
        } else if (task.current_step === 5) {
          currentPathIndex.value = -1  // 返回基站
        } else {
          currentPathIndex.value = Math.min(task.current_step, pathPoints.value.length - 1)
        }
        
        progress.value = Math.round((task.current_step / task.total_steps) * 100)
      } else if (task.status === 'completed') {
        // completed状态 - 巡检完成
        isInspecting.value = false
        inspectionStatus.value = '巡检结束'
        currentPathIndex.value = -1  // 完成后回到基站
        currentPosition.value = '基站'
        progress.value = 100
      } else {
        // 其他状态 - 默认为待机
        isInspecting.value = false
        inspectionStatus.value = '待机中'
        currentPathIndex.value = -1
        currentPosition.value = '基站'
        progress.value = 0
      }
      
      console.log('🔍 任务进度:', task)
    }
  } catch (error) {
    console.error('获取任务进度失败:', error)
  }
}

const reconnectHardware = async () => {
  try {
    isReconnecting.value = true
    ElMessage.info('正在重新连接...')
    
    // 重新加载任务进度
    await loadTaskProgress()
    ElMessage.success('连接成功！')
  } catch (error) {
    console.error('重新连接失败:', error)
    ElMessage.error('重新连接失败，请检查网络连接')
  } finally {
    isReconnecting.value = false
  }
}

const loadDevicePositions = async () => {
  try {
    // 使用固定的设备路径点（5个站点：基站 + 4个设备巡检点，返回基站就是返回第一个站点）
    pathPoints.value = [
      { id: 'home', name: '基站', location: '起点基站', position: { x: 20, y: 30 }, inspection_order: 0 },
      { id: 'device_001', name: '1号低温冰箱', location: '巡检点1', position: { x: 40, y: 30 }, inspection_order: 1 },
      { id: 'device_002', name: '2号低温冰箱', location: '巡检点2', position: { x: 60, y: 30 }, inspection_order: 2 },
      { id: 'device_003', name: '3号低温冰箱', location: '巡检点3', position: { x: 80, y: 30 }, inspection_order: 3 },
      { id: 'device_004', name: '1号液氮罐', location: '巡检点4', position: { x: 100, y: 30 }, inspection_order: 4 },
   ]
    console.log('📍 加载设备位置信息:', pathPoints.value)
  } catch (error) {
    console.error('获取设备位置信息失败:', error)
  }
}

// 从后端数据更新机器人状态
const updateRobotStatusFromData = (robotData) => {
  console.log('🤖 更新机器人状态数据:', robotData)
  
  if (robotData.current_location) {
    currentPosition.value = robotData.current_location
  }
  
  if (robotData.current_step !== undefined) {
    // 修复逻辑：current_step 0=基站，1=1号设备，2=2号设备，3=3号设备，4=4号设备，5=返回基站
    if (robotData.current_step === 0) {
      currentPathIndex.value = -1  // -1表示在基站，不激活任何路径点
    } else if (robotData.current_step === 5) {
      currentPathIndex.value = -1  // 第5步是返回基站，回到基站状态
    } else {
      // current_step 1-4对应路径点索引1-4
      currentPathIndex.value = Math.min(robotData.current_step, pathPoints.value.length - 1)
    }
    console.log('🔄 更新巡检路径索引:', currentPathIndex.value, '当前步骤:', robotData.current_step, '巡检状态:', robotData.inspection_status)
  }
  
  if (robotData.progress_percentage !== undefined) {
    progress.value = Math.round(robotData.progress_percentage)
  }
  
  // 更新巡检状态和按钮状态
  if (robotData.inspection_status === 'running') {
    inspectionStatus.value = '巡检中'
    isInspecting.value = true
  } else if (robotData.inspection_status === 'completed') {
    inspectionStatus.value = '巡检结束'
    isInspecting.value = false
    // 巡检完成后回到基站
    currentPathIndex.value = -1
    currentPosition.value = '基站'
  } else {
    // 待机状态：在基站且未执行任务
    inspectionStatus.value = '待机中'
    isInspecting.value = false
    // 确保在基站时路径索引为-1
    if (robotData.current_step === 0 || robotData.current_step === undefined) {
      currentPathIndex.value = -1
      currentPosition.value = '基站'
    }
  }
  
  // 更新连接状态
  isConnected.value = robotData.is_connected === 1 || robotData.is_connected === true
  
  // 更新当前任务 - 基于实际路径点数据
  if (currentPathIndex.value < 0) {
    currentTask.value = '在基站待机'
  } else {
    const currentPoint = pathPoints.value[currentPathIndex.value]
    currentTask.value = currentPoint ? `检查${currentPoint.name}` : '巡检任务'
  }
}

// 方法
const startInspection = async () => {
  // 防止重复点击
  if (isInspecting.value || !isConnected.value) {
    return
  }
  
  try {
    ElMessage.info('正在启动巡检...')
    
    // 立即更新状态，禁用开始按钮
    isInspecting.value = true
    inspectionStatus.value = '巡检中'
    currentPathIndex.value = 0 // 开始巡检，激活第一个路径点
    
    // 通过API启动巡检
    const response = await taskApi.startInspection('巡检任务')
    
    if (response.success) {
      ElMessage.success('巡检启动成功！机器人开始执行完整巡检任务')
    } else {
      ElMessage.error(`启动巡检失败: ${response.error || '未知错误'}`)
      // 启动失败，恢复状态
      isInspecting.value = false
      inspectionStatus.value = '待机中'
      currentPathIndex.value = -1 // 回到基站状态
    }
  } catch (error) {
    console.error('启动巡检失败:', error)
    ElMessage.error('启动巡检失败，请检查网络连接')
    
    // 启动失败，恢复状态
    isInspecting.value = false
    inspectionStatus.value = '待机中'
    currentPathIndex.value = -1 // 回到基站状态
  }
}



// WebSocket事件处理函数已移除
const handleRobotStatusUpdate = (data) => {
  console.log('收到机器人状态更新:', data)
  updateRobotStatusFromData(data)
}

const handleInspectionProgressUpdate = (data) => {
  console.log('收到巡检进度更新:', data)
  updateRobotStatusFromData(data)
}

const handleInspectionResult = (data) => {
  console.log('收到巡检结果:', data)
  if (data.success) {
    if (data.message && data.message.includes('启动')) {
      isInspecting.value = true
      inspectionStatus.value = '巡检中'
      console.log('🔄 巡检启动确认，按钮状态已更新')
    } else if (data.message && data.message.includes('完成')) {
      // 巡检完成通知
      isInspecting.value = false
      inspectionStatus.value = '已完成'
      ElMessage.success({
        message: '🎉 巡检任务已完成！机器人已返回基站',
        duration: 5000,
        showClose: true
      })
      console.log('✅ 巡检完成确认，按钮状态已更新')
    }
  } else {
    // 如果操作失败，根据消息内容恢复状态
    if (data.message && data.message.includes('启动')) {
      isInspecting.value = false
      inspectionStatus.value = '待机中'
      console.log('❌ 巡检启动失败，按钮状态已恢复')
    } else if (data.message && data.message.includes('完成')) {
      // 巡检完成但可能有异常
      isInspecting.value = false
      inspectionStatus.value = '异常完成'
      ElMessage.warning({
        message: '⚠️ 巡检任务完成，但过程中出现异常',
        duration: 5000,
        showClose: true
      })
      console.log('⚠️ 巡检异常完成，按钮状态已更新')
    }
  }
}

// 自动刷新控制
const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    refreshTimer.value = setInterval(async () => {
      await refreshRobotStatus()
    }, refreshInterval)
    console.log('🔄 机器人状态自动刷新已启用，间隔:', refreshInterval + 'ms')
  } else {
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = null
      console.log('🛑 机器人状态自动刷新已禁用')
    }
  }
}

// 刷新机器人状态
const refreshRobotStatus = async () => {
  try {
    const response = await robotApi.getStatus()
    if (response && response.success) {
      updateRobotStatusFromData(response.data)
      console.log('🔄 机器人状态已刷新:', response.data)
    }
  } catch (error) {
    console.error('刷新机器人状态失败:', error)
  }
}

// 加载初始数据
const loadInitialData = async () => {
  try {
    const response = await robotApi.getStatus()
    if (response && response.success) {
      updateRobotStatusFromData(response.data)
    } else {
      // 如果API返回失败，使用默认数据
      console.warn('机器人状态API返回失败，使用默认数据')
      updateRobotStatusFromData({
        current_location: '基站',
        inspection_status: 'idle',
        current_step: 0,
        progress_percentage: 0,
        is_connected: false
      })
    }
  } catch (error) {
    console.error('获取机器人状态失败:', error)
    // 即使连接失败，也显示默认状态
    console.warn('使用默认机器人状态数据')
    updateRobotStatusFromData({
      current_location: '基站',
      inspection_status: 'idle',
      current_step: 0,
      progress_percentage: 0,
      is_connected: false
    })
  }
}

onMounted(async () => {
  // 加载任务进度
  await loadTaskProgress()
  
  // 加载设备位置信息
  await loadDevicePositions()
  
  // 启动自动刷新
  if (autoRefresh.value) {
    refreshTimer.value = setInterval(() => {
      loadTaskProgress()
    }, refreshInterval)
  }
})

onUnmounted(() => {
  // 清理定时器
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
})
</script>

<style scoped>
.robot-status {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 8px;
  padding: 20px;
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 100%;
  max-height: 350px;
  display: flex;
  flex-direction: column;
}

.robot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}



.robot-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0;
  color: #4fc3f7;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.connection-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.connected .connection-dot {
  background: #4caf50;
  box-shadow: 0 0 10px #4caf50;
}

.disconnected .connection-dot {
  background: #f44336;
  box-shadow: 0 0 10px #f44336;
}

.connection-text {
  font-size: 0.9rem;
  font-weight: 500;
}

.reconnect-btn {
  margin-left: 10px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  border-radius: 4px;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.reconnect-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  border-color: #4fc3f7;
}

.reconnect-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.icon-refresh.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.robot-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.info-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 0.8rem;
  color: #b3d9ff;
}

.info-value {
  font-size: 0.9rem;
  font-weight: bold;
  color: #ffffff;
}

.info-value.status-inspecting {
  color: #4caf50;
}

.info-value.status-idle {
  color: #ff9800;
}

.robot-controls {
  margin-bottom: 20px;
}

.control-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.control-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.start-btn {
  background: linear-gradient(135deg, #4caf50, #45a049);
  color: white;
}

.start-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #45a049, #3d8b40);
  transform: translateY(-2px);
}



.return-btn {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
}

.return-btn:hover {
  background: linear-gradient(135deg, #f57c00, #ef6c00);
  transform: translateY(-2px);
}





.estimated-time {
  color: #b3d9ff;
}

.robot-path {
  flex: 1;
  margin-bottom: 10px;
}

.path-title {
  font-size: 1.2rem;
  color: #4fc3f7;
  margin-bottom: 100px;
  min-width: 100px;
  font-weight: 555;
}

.path-visualization {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  padding: 20px 0;
  z-index: 1000;
}

.path-visualization::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 10%;
  right: 0%;
  height: 2px;
  background: linear-gradient(90deg, #4fc3f7, #2196f3, #4fc3f7);
  z-index: 1;
  border-radius: 1px;
}

.path-point {
  flex: 1;
  min-width: 130px;
  text-align: center;
  padding: 25px 10px;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  margin-right: 50px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.3);
  z-index: 1001;
}

.path-point.active {
  background: linear-gradient(135deg, #4caf50, #45a049);
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
  border: 1px solid #4caf50;
  z-index: 1002;
}

.path-point.completed {
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid #4caf50;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.2);
  z-index: 1001;
}

.path-point.pending {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  z-index: 1001;
}

.path-point.base-station {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  border: 1px solid #ff9800;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
  transform: scale(1.02);
}

.point-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px;
  font-size: 0.9rem;
  font-weight: bold;
  transition: all 0.3s ease;
}

.path-point.active .point-number {
  background: #ffffff;
  color: #4caf50;
}

.path-point.completed .point-number {
  background: #4caf50;
  color: #ffffff;
}

.point-label {
  font-size: 0.75rem;
  color: #b3d9ff;
  line-height: 1.3;
  font-weight: 500;
}

.path-point.active .point-label {
  color: #ffffff;
  font-weight: 500;
}

.point-location {
  font-size: 0.6rem;
  color: #90a4ae;
  margin-top: 1px;
  opacity: 0.8;
  line-height: 1.2;
}

.path-info {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.path-summary {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #b0bec5;
  gap: 10px;
  flex-wrap: wrap;
}

.path-summary span {
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.65rem;
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
  .robot-info {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .control-buttons {
    flex-direction: column;
  }
  
  .path-visualization {
    flex-direction: column;
  }
  
  .path-point {
    min-width: auto;
  }
}
</style>
