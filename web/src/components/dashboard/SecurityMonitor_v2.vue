<template>
  <div class="security-monitor">
    <div class="monitor-header">
      <h3 class="monitor-title">安防监控</h3>
    </div>
    
    <div class="monitor-content">
      <!-- 左侧：报警图片显示 -->
      <div class="alert-image-container">
        <div class="alert-image-header">
          <span class="image-title">最新报警图片</span>
          <span class="image-timestamp" v-if="latestAlert">{{ formatTime(latestAlert.created_at) }}</span>
        </div>
        <div class="alert-image-content">
          <div v-if="latestAlert && latestAlert.image_url" class="alert-image">
            <img :src="latestAlert.image_url" :alt="latestAlert.message" @error="handleImageError" class="cover-image">
          </div>
          <div v-else class="no-image">
            <i class="icon-camera"></i>
            <p>暂无报警</p>
          </div>
        </div>
      </div>
      
      <!-- 右侧：报警履历 -->
      <div class="alert-history-container">
        <div class="alert-history-header">
          <span class="history-title">报警履历</span>
          <span class="history-count">{{ alerts.length }} 条记录</span>
        </div>
        <div class="alert-history-content">
          <div class="alert-list scrollable" ref="alertList">
            <div v-for="alert in displayAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
              <div class="alert-time">{{ formatTime(alert.created_at) }}</div>
              <div class="alert-message">{{ alert.message }}</div>
              <div class="alert-type">{{ alert.alert_type }}</div>
            </div>
            <div v-if="displayAlerts.length === 0" class="no-alerts">
              <i class="icon-shield"></i>
              <p>暂无报警记录</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { alertApi } from '../../services/api_v2.js'

// 响应式数据
const alerts = ref([])
const latestAlert = ref(null)
const refreshTimer = ref(null)
const alertList = ref(null)

// 计算属性
const displayAlerts = computed(() => {
  return alerts.value.slice(0, 20) // 显示最新20条
})

// 方法
const refreshAlerts = async () => {
  try {
    const response = await alertApi.getLatest(50) // 获取更多数据
    if (response.success) {
      alerts.value = response.data
      if (response.data.length > 0) {
        const newLatestAlert = response.data[0]
        
        // 比对图片地址，只有不一样时才替换
        if (!latestAlert.value || 
            newLatestAlert.image_url !== latestAlert.value.image_url) {
          console.log('检测到新报警图片:', {
            old: latestAlert.value?.image_url,
            new: newLatestAlert.image_url
          })
          
          // 添加图片更新动画
          updateImageWithAnimation(newLatestAlert)
        } else {
          // 图片地址相同，只更新其他信息（时间戳等）
          if (latestAlert.value && newLatestAlert.id !== latestAlert.value.id) {
            latestAlert.value = newLatestAlert
          }
        }
      }
    }
  } catch (error) {
    console.error('获取报警信息失败:', error)
  }
}

// 自动刷新功能
const startAutoRefresh = () => {
  refreshTimer.value = setInterval(refreshAlerts, 2000)
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

const handleImageError = (event) => {
  console.error('报警图片加载失败:', event)
  event.target.style.display = 'none'
}

// 图片更新动画方法
const updateImageWithAnimation = (newAlert) => {
  const imageElement = document.querySelector('.alert-image img')
  if (imageElement) {
    // 添加更新动画类
    imageElement.classList.add('image-updating')
    
    // 更新图片数据
    latestAlert.value = newAlert
    
    // 动画结束后移除类
    setTimeout(() => {
      imageElement.classList.remove('image-updating')
    }, 600)
  } else {
    // 如果没有图片元素，直接更新
    latestAlert.value = newAlert
  }
}

// 生命周期
onMounted(() => {
  refreshAlerts()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.security-monitor {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 12px;
  padding: 20px;
  color: #ffffff;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.monitor-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #ffffff;
}

.monitor-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}


.monitor-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  flex: 1;
}

.alert-image-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  height: 45%; /* 增加高度 */
  max-height: 60%; /* 确保不超过外层组件的一半 */
}

.alert-image-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.image-title {
  font-size: 16px;
  font-weight: 600;
}

.image-timestamp {
  font-size: 12px;
  color: #888;
}

.alert-image-content {
  flex: 1;
  display: flex;
  align-items: flex-start; /* 改为顶部对齐 */
  justify-content: center;
  overflow: hidden; /* 防止内容溢出 */
  padding-top: 10px; /* 添加顶部间距 */
}

.alert-image {
  position: relative;
  width: 100%;
  height: 100%;
  max-height: 500px; /* 增加图片最大高度 */
  border-radius: 6px;
  overflow: hidden;
}

.alert-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: all 0.3s ease;
}

.alert-image img.image-updating {
  animation: imageUpdate 0.6s ease;
}

@keyframes imageUpdate {
  0% {
    opacity: 0.7;
    transform: scale(0.95);
  }
  50% {
    opacity: 1;
    transform: scale(1.02);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  right: 10px;
  display: flex;
  justify-content: space-between;
}

.alert-type {
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.alert-severity {
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.alert-severity.high {
  background: rgba(255, 0, 0, 0.8);
}

.alert-severity.medium {
  background: rgba(255, 165, 0, 0.8);
}

.alert-severity.low {
  background: rgba(0, 255, 0, 0.8);
}

.no-image {
  text-align: center;
  color: #888;
}

.no-image i {
  font-size: 48px;
  margin-bottom: 10px;
}

.alert-history-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  height: 45%; /* 增加高度 */
  max-height: 60%; /* 确保不超过外层组件的一半 */
}

.alert-history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.history-title {
  font-size: 16px;
  font-weight: 600;
}

.history-count {
  font-size: 12px;
  color: #888;
}

.alert-history-content {
  flex: 1;
  overflow: hidden; /* 防止内容溢出父容器 */
  min-height: 0; /* 确保flex子项可以收缩 */
  display: flex;
  flex-direction: column;
}

.alert-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
  max-height: 100%;
  min-height: 0; /* 确保可以收缩 */
}

.scrollable {
  scrollbar-width: thin;
  scrollbar-color: rgba(79, 195, 247, 0.5) transparent;
}

/* 自定义滚动条样式 */
.alert-list::-webkit-scrollbar {
  width: 6px;
}

.alert-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.alert-list::-webkit-scrollbar-thumb {
  background: rgba(79, 195, 247, 0.6);
  border-radius: 3px;
}

.alert-list::-webkit-scrollbar-thumb:hover {
  background: rgba(79, 195, 247, 0.8);
}

.scrollable::-webkit-scrollbar {
  width: 6px;
}

.scrollable::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.scrollable::-webkit-scrollbar-thumb {
  background: rgba(79, 195, 247, 0.5);
  border-radius: 3px;
}

.scrollable::-webkit-scrollbar-thumb:hover {
  background: rgba(79, 195, 247, 0.7);
}

.alert-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 8px;
  border-left: 3px solid #666;
  transition: all 0.3s ease;
}

.alert-item.high {
  border-left-color: #ff4444;
}

.alert-item.medium {
  border-left-color: #ffaa00;
}

.alert-item.low {
  border-left-color: #44ff44;
}

.alert-time {
  font-size: 12px;
  color: #888;
  margin-bottom: 4px;
}

.alert-message {
  font-size: 14px;
  margin-bottom: 4px;
}

.alert-type {
  font-size: 12px;
  color: #aaa;
}

.no-alerts {
  text-align: center;
  color: #888;
  padding: 40px 20px;
}

.no-alerts i {
  font-size: 48px;
  margin-bottom: 10px;
}

/* 滚动条样式 */
.alert-list::-webkit-scrollbar {
  width: 6px;
}

.alert-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.alert-list::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.alert-list::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 响应式设计 - 仅考虑电脑屏幕 */
@media (max-width: 1000px) {
  .alert-image-container,
  .alert-history-container {
    max-height: 350px; /* 中等电脑屏幕：350px */
  }
  
  .alert-image {
    max-height: 280px;
  }
}

@media (max-width: 1200px) {
  .alert-image-container,
  .alert-history-container {
    max-height: 300px; /* 小电脑屏幕：300px */
  }
  
  .alert-image {
    max-height: 240px;
  }
}
</style>
