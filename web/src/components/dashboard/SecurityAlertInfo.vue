<template>
  <div class="alert-info-container">
    <div class="info-header">
      <h4>报警信息说明</h4>
      <span class="severity-badge" :class="severityClass">
        {{ severityText }}
      </span>
    </div>
    
    <div class="info-content">
      <div v-if="alertInfo" class="alert-details">
        <!-- <div class="detail-item">
          <label>报警类型:</label>
          <span>{{ alertInfo.alert_type }}</span>
        </div> -->
        
        <div class="detail-item">
          <label>报警时间:</label>
          <span>{{ formatTime(alertInfo.created_at) }}</span>
        </div>
        
        <!-- <div class="detail-item">
          <label>摄像头:</label>
          <span>{{ alertInfo.camera_name || '未知' }}</span>
        </div> -->
        
        <div class="detail-item full-width">
          <label>报警描述:</label>
          <p class="alert-message">{{ alertInfo.alert_message }}</p>
        </div>
<!--         
        <div class="alert-actions">
          <span class="alert-status">
            <i class="icon-info"></i>
            报警提示
          </span>
        </div> -->
      </div>
      
      <div v-else class="no-alert">
        <i class="icon-info"></i>
        <span>暂无报警信息</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps, defineEmits } from 'vue'

const props = defineProps({
  alertInfo: Object
})

const severityClass = computed(() => {
  if (!props.alertInfo) return 'medium'
  return props.alertInfo.severity || 'medium'
})

const severityText = computed(() => {
  const severityMap = {
    'high': '高危',
    'medium': '中危',
    'low': '低危'
  }
  return severityMap[severityClass.value] || '中危'
})

const formatTime = (timestamp) => {
  if (!timestamp) return '--'
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('zh-CN')
  } catch (error) {
    return '--'
  }
}
</script>

<style scoped>
.alert-info-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.info-header h4 {
  margin: 0;
  color: #4fc3f7;
  font-size: 1rem;
}

.severity-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.severity-badge.high {
  background: #f44336;
  color: #ffffff;
}

.severity-badge.medium {
  background: #ff9800;
  color: #ffffff;
}

.severity-badge.low {
  background: #4caf50;
  color: #ffffff;
}

.info-content {
  min-height: 80px;
}

.alert-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.detail-item.full-width {
  flex-direction: column;
  gap: 5px;
}

.detail-item label {
  color: #b3d9ff;
  font-size: 0.9rem;
  min-width: 80px;
  flex-shrink: 0;
}

.detail-item span {
  color: #ffffff;
  font-size: 0.9rem;
}

.alert-message {
  color: #ffffff;
  font-size: 0.9rem;
  line-height: 1.4;
  margin: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

.alert-actions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.alert-status {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #4fc3f7;
  font-size: 0.9rem;
  font-weight: 500;
}

.no-alert {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666666;
}

.no-alert i {
  font-size: 2rem;
  margin-bottom: 10px;
}
</style>
