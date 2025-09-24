<template>
  <div class="environment-monitor">
    <div class="monitor-header">
      <h3 class="monitor-title">环境参数监控</h3>
      <div class="update-time">
        更新时间: {{ lastUpdateTime }}
      </div>
    </div>
    
    <div class="environment-grid">
      <div class="env-item" 
           v-for="param in environmentParams" 
           :key="param.name"
           :class="{ 'alert': param.isAlert }"
      >
        <div class="env-header">
          <div class="env-icon">
            <i :class="param.icon"></i>
          </div>
          <div class="env-info">
            <div class="env-name">{{ param.name }}</div>
            <div class="env-unit">{{ param.unit }}</div>
          </div>
          <div class="env-status" :class="param.statusClass">
            <span class="status-dot"></span>
          </div>
        </div>
        
        <div class="env-value">
          <span class="value-number">{{ param.value }}</span>
          <span class="value-trend" :class="param.trendClass">
            <i :class="param.trendIcon"></i>
            {{ param.trend }}
          </span>
        </div>
        
        <div class="env-range">
          <div class="range-bar">
            <div class="range-fill" 
                 :style="{ 
                   width: param.percentage + '%',
                   background: param.rangeColor
                 }"
            ></div>
          </div>
          <div class="range-labels">
            <span class="range-min">{{ param.min }}</span>
            <span class="range-max">{{ param.max }}</span>
          </div>
        </div>
        
        <div class="env-threshold" v-if="param.isAlert">
          <span class="threshold-text">超出阈值范围</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { systemApi } from '../../services/api_v2.js'
import frontendLogger from '../../utils/logger.js'

// Props - 移除测试模式相关props

// 响应式数据
const lastUpdateTime = ref('')
const hasError = ref(false)
const errorMessage = ref('')


// 环境参数数据
const environmentParams = ref([
  {
    name: '温度',
    unit: '℃',
    value: 25.0,
    min: 20,
    max: 30,
    icon: 'icon-thermometer',
    trend: '+0.2',
    trendIcon: 'icon-arrow-up',
    trendClass: 'trend-up',
    statusClass: 'status-normal',
    isAlert: false,
    percentage: 60,
    rangeColor: '#4fc3f7',
    key: 'temperature'
  },
  {
    name: '湿度',
    unit: '%',
    value: 60.0,
    min: 50,
    max: 70,
    icon: 'icon-droplet',
    trend: '-1.5',
    trendIcon: 'icon-arrow-down',
    trendClass: 'trend-down',
    statusClass: 'status-normal',
    isAlert: false,
    percentage: 52,
    rangeColor: '#66bb6a',
    key: 'humidity'
  },
  {
    name: '氮气浓度',
    unit: '%',
    value: 78.0,
    min: 75,
    max: 80,
    icon: 'icon-wind',
    trend: '0.0',
    trendIcon: 'icon-minus',
    trendClass: 'trend-stable',
    statusClass: 'status-normal',
    isAlert: false,
    percentage: 65,
    rangeColor: '#ab47bc',
    key: 'n2_concentration'
  },
  {
    name: '氧气浓度',
    unit: '%',
    value: 21.0,
    min: 19,
    max: 22,
    icon: 'icon-wind',
    trend: '0.0',
    trendIcon: 'icon-minus',
    trendClass: 'trend-stable',
    statusClass: 'status-normal',
    isAlert: false,
    percentage: 45,
    rangeColor: '#4caf50',
    key: 'o2_concentration'
  },
  {
    name: '二氧化碳',
    unit: '%',
    value: 0.04,
    min: 0.03,
    max: 0.05,
    icon: 'icon-cloud',
    trend: '+0.001',
    trendIcon: 'icon-arrow-up',
    trendClass: 'trend-up',
    statusClass: 'status-normal',
    isAlert: false,
    percentage: 50,
    rangeColor: '#ff7043',
    key: 'co2_concentration'
  }
])

// 计算属性
const updateTime = () => {
  const now = new Date()
  lastUpdateTime.value = now.toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 更新环境数据
const updateEnvironmentData = (data = null) => {
  if (data && Array.isArray(data)) {
    // 使用传入的数据更新（新格式：数组）
    environmentParams.value.forEach(param => {
      const paramData = data.find(item => item.param_name === param.key)
      if (paramData) {
        param.value = parseFloat(paramData.param_value) || 0
        param.isAlert = paramData.status !== 'normal'
        
        // 更新状态（后端数据都是normal状态，无需额外判断）
        if (param.isAlert) {
          param.statusClass = 'status-alert'
          param.rangeColor = '#f44336'
        } else {
          param.statusClass = 'status-normal'
          param.rangeColor = getDefaultColor(param.key)
        }
        
        // 计算百分比
        const range = param.max - param.min
        const normalizedValue = (param.value - param.min) / range
        param.percentage = Math.max(0, Math.min(100, normalizedValue * 100))
      }
    })
  } else {
    // 模拟数据更新（备用）
    environmentParams.value.forEach(param => {
      const variation = (Math.random() - 0.5) * 2
      param.value = Math.round((param.value + variation) * 10) / 10
      
      // 计算百分比
      const range = param.max - param.min
      const normalizedValue = (param.value - param.min) / range
      param.percentage = Math.max(0, Math.min(100, normalizedValue * 100))
      
      // 判断是否超出阈值（使用更严格的边界检查）
      param.isAlert = param.value <= param.min || param.value >= param.max
      
      // 更新状态
      if (param.isAlert) {
        param.statusClass = 'status-alert'
        param.rangeColor = '#f44336'
      } else if (param.percentage > 80 || param.percentage < 20) {
        param.statusClass = 'status-warning'
        param.rangeColor = '#ff9800'
      } else {
        param.statusClass = 'status-normal'
        param.rangeColor = getDefaultColor(param.key)
      }
    })
  }
  
  updateTime()
}

// 获取默认颜色
const getDefaultColor = (key) => {
  const colors = {
    'temperature': '#4fc3f7',
    'humidity': '#66bb6a',
    'n2_concentration': '#ab47bc',
    'o2_concentration': '#4caf50',
    'co2_concentration': '#ff7043'
  }
  return colors[key] || '#4fc3f7'
}



// 定时器
let updateTimer = null

// HTTP数据获取函数 - 随机查询数据库数据
const fetchEnvironmentData = async () => {
  frontendLogger.info('EnvironmentMonitor', 'fetchEnvironmentData', null, '开始获取环境数据')
  
  try {
    const response = await systemApi.getInfo()
    frontendLogger.info('EnvironmentMonitor', 'fetchEnvironmentData', { 
      responseStatus: response.status,
      responseData: response.data 
    }, '环境数据API响应')
    
    if (response && response.success) {
      frontendLogger.info('EnvironmentMonitor', 'fetchEnvironmentData', { 
        dataKeys: response.data.map(item => item.param_name),
        dataCount: response.data.length
      }, '获取系统信息成功')
      updateEnvironmentData(response.data)
    } else {
      frontendLogger.warn('EnvironmentMonitor', 'fetchEnvironmentData', { 
        response: response 
      }, '系统信息API返回失败，使用模拟数据')
      // 使用模拟数据更新
      updateEnvironmentData()
    }
  } catch (error) {
    frontendLogger.error('EnvironmentMonitor', 'fetchEnvironmentData', { 
      error: error.message,
      stack: error.stack,
      url: '/environment/parameters'
    }, '获取环境数据失败')
    // 即使连接失败，也使用模拟数据，不显示错误
    updateEnvironmentData()
  }
}




// 加载初始数据
const loadInitialData = async () => {
  frontendLogger.info('EnvironmentMonitor', 'loadInitialData', null, '开始加载环境数据')
  
  try {
    const response = await systemApi.getInfo()
    frontendLogger.info('EnvironmentMonitor', 'loadInitialData', { 
      response: response 
    }, '初始环境数据响应')
    
    if (response && response.success) {
      frontendLogger.info('EnvironmentMonitor', 'loadInitialData', { 
        data: response.data 
      }, '初始环境数据加载成功')
      updateEnvironmentData(response.data)
    } else {
      frontendLogger.warn('EnvironmentMonitor', 'loadInitialData', { 
        response: response 
      }, '初始环境数据加载失败，使用模拟数据')
      updateEnvironmentData()
    }
  } catch (error) {
    frontendLogger.error('EnvironmentMonitor', 'loadInitialData', { 
      error: error.message,
      stack: error.stack
    }, '加载环境数据失败')
    // 不显示错误，使用模拟数据
    updateEnvironmentData()
  }
}

onMounted(() => {
  frontendLogger.info('EnvironmentMonitor', 'onMounted', null, '环境监控组件已挂载')
  
  // 加载初始数据
  loadInitialData()
  
  // 每10秒随机查询一次数据库数据
  updateTimer = setInterval(() => {
    frontendLogger.info('EnvironmentMonitor', 'timerTrigger', null, '定时器触发，开始随机查询环境数据')
    fetchEnvironmentData()
  }, 10000)
})

onUnmounted(() => {
  // 清理定时器
  if (updateTimer) {
    clearInterval(updateTimer)
  }
})
</script>

<style scoped>
.environment-monitor {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 8px;
  padding: 10px;
  color: #ffffff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.monitor-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0;
  color: #4fc3f7;
}

.update-time {
  font-size: 0.8rem;
  color: #b3d9ff;
}

.environment-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

.env-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 5px;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.env-item.alert {
  border-color: #f44336;
  background: rgba(244, 67, 54, 0.1);
}

.env-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.env-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(79, 195, 247, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-size: 1.2rem;
  color: #4fc3f7;
}

.env-info {
  flex: 1;
}

.env-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: #ffffff;
}

.env-unit {
  font-size: 0.7rem;
  color: #b3d9ff;
}

.env-status {
  display: flex;
  align-items: center;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-normal .status-dot {
  background: #4caf50;
  box-shadow: 0 0 10px #4caf50;
}

.status-warning .status-dot {
  background: #ff9800;
  box-shadow: 0 0 10px #ff9800;
}

.status-alert .status-dot {
  background: #f44336;
  box-shadow: 0 0 10px #f44336;
}

.env-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.value-number {
  font-size: 1.5rem;
  font-weight: bold;
  color: #ffffff;
}

.value-trend {
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-up {
  color: #4caf50;
}

.trend-down {
  color: #f44336;
}

.trend-stable {
  color: #b3d9ff;
}

.env-range {
  margin-bottom: 8px;
}

.range-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 5px;
}

.range-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
  position: relative;
}

.range-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: shimmer 2s infinite;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.7rem;
  color: #b3d9ff;
}

.env-threshold {
  text-align: center;
}

.threshold-text {
  font-size: 0.7rem;
  color: #f44336;
  font-weight: 500;
}



.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-label {
  font-size: 0.8rem;
  color: #b3d9ff;
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
@media (max-width: 1920px) {
  .environment-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1440px) {
  .environment-grid {
    grid-template-columns: 1fr;
  }
  
  .env-item {
    padding: 12px;
  }
  
  .value-number {
    font-size: 1.3rem;
  }
}
</style>
