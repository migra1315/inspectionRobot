<template>
  <div class="alert-image-container">
    <div class="image-header">
      <h4>报警图像</h4>
      <span class="alert-type">{{ alertType }}</span>
    </div>
    
    <div class="image-content">
      <div v-if="alertImage" class="alert-image">
        <img 
          :src="getImageUrl(alertImage)" 
          :alt="alertType"
          @error="handleImageError"
          @click="openPreview"
        >
        <div class="image-overlay">
          <div class="preview-hint">
            <i class="icon-zoom">🔍</i>
            <span>点击放大</span>
          </div>
        </div>
      </div>
      
      <div v-else class="no-image">
        <i class="icon-camera"></i>
        <span>暂无报警图像</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'
import imagePreviewService from '../../services/imagePreviewService.js'

const props = defineProps({
  alertImage: String,
  alertType: String
})

const getImageUrl = (imageUrl) => {
  if (!imageUrl) return ''
  if (imageUrl.startsWith('http')) return imageUrl
  // 处理Windows路径分隔符
  const normalizedUrl = imageUrl.replace(/\\/g, '/')
  console.log('原始URL:', imageUrl, '标准化URL:', normalizedUrl)
  return `http://localhost:5000${normalizedUrl}`
}

const handleImageError = (event) => {
  console.error('报警图像加载失败:', event.target.src)
  event.target.style.display = 'none'
}

const openPreview = () => {
  console.log('点击图像预览，alertImage:', props.alertImage)
  if (props.alertImage) {
    const fullImageUrl = getImageUrl(props.alertImage)
    const altText = `${props.alertType || '报警'}图像`
    console.log('打开预览，URL:', fullImageUrl, 'alt:', altText)
    // 直接调用imagePreviewService，与设备状态组件保持一致
    imagePreviewService.openPreview(fullImageUrl, altText)
  } else {
    console.log('没有图像数据')
  }
}
</script>

<style scoped>
.alert-image-container {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.image-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.image-header h4 {
  margin: 0;
  color: #4fc3f7;
  font-size: 1rem;
}

.alert-type {
  background: #f44336;
  color: #ffffff;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.image-content {
  height: 200px;
  position: relative;
}

.alert-image {
  width: 100%;
  height: 100%;
  position: relative;
  cursor: pointer;
}

.alert-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.alert-image img:hover {
  transform: scale(1.02);
  filter: brightness(1.1);
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
}

.alert-image:hover .image-overlay {
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
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666666;
}

.no-image i {
  font-size: 2rem;
  margin-bottom: 10px;
}
</style>
