<template>
  <div v-if="visible" class="image-preview-overlay" @click="handleOverlayClick">
    <div class="image-preview-container" :style="containerStyle" @click.stop>
      <!-- 关闭按钮 -->
      <div class="preview-close" @click="close">
        <i class="icon-close">×</i>
      </div>
      
      <!-- 图片容器 -->
      <div class="image-container" :style="imageContainerStyle" ref="imageContainer">
        <img 
          :src="imageUrl" 
          :alt="alt"
          class="preview-image"
          :style="imageStyle"
          @load="handleImageLoad"
          @error="handleImageError"
        />
        
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <div class="loading-text">加载中...</div>
        </div>
        
        <!-- 错误状态 -->
        <div v-if="error" class="error-overlay">
          <div class="error-icon">⚠️</div>
          <div class="error-text">图片加载失败</div>
        </div>
      </div>
      
      <!-- 工具栏 -->
      <div class="preview-toolbar">
        <div class="toolbar-left">
          <span class="image-info">{{ alt || '图片预览' }}</span>
        </div>
        <div class="toolbar-center">
          <button class="toolbar-btn" @click="zoomOut" :disabled="scale <= 0.5">
            <i class="icon-zoom-out">-</i>
          </button>
          <span class="zoom-info">{{ Math.round(scale * 100) }}%</span>
          <button class="toolbar-btn" @click="zoomIn" :disabled="scale >= 3">
            <i class="icon-zoom-in">+</i>
          </button>
          <button class="toolbar-btn" @click="resetZoom">
            <i class="icon-reset">↻</i>
          </button>
        </div>
        <div class="toolbar-right">
          <button class="toolbar-btn" @click="toggleFullscreen" :title="isFullscreen ? '退出全屏' : '全屏显示'">
            <i class="icon-fullscreen">{{ isFullscreen ? '⤢' : '⤡' }}</i>
          </button>
          <button class="toolbar-btn" @click="rotateLeft">
            <i class="icon-rotate-left">↶</i>
          </button>
          <button class="toolbar-btn" @click="rotateRight">
            <i class="icon-rotate-right">↷</i>
          </button>
          <button class="toolbar-btn" @click="downloadImage">
            <i class="icon-download">↓</i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  imageUrl: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  isFullscreen: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['close', 'toggle-fullscreen'])

// 响应式数据
const loading = ref(true)
const error = ref(false)
const scale = ref(1)
const rotate = ref(0)
const translateX = ref(0)
const translateY = ref(0)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const imageContainer = ref(null)

// 计算属性
const imageStyle = computed(() => ({
  transform: `scale(${scale.value}) rotate(${rotate.value}deg) translate(${translateX.value}px, ${translateY.value}px)`,
  transition: isDragging.value ? 'none' : 'transform 0.3s ease'
}))

const containerStyle = computed(() => ({
  width: props.isFullscreen ? '100vw' : '95vw',
  height: props.isFullscreen ? '100vh' : '95vh',
  maxWidth: props.isFullscreen ? '100vw' : '95vw',
  maxHeight: props.isFullscreen ? '100vh' : '95vh',
  borderRadius: props.isFullscreen ? '0' : '12px'
}))

const imageContainerStyle = computed(() => ({
  minHeight: props.isFullscreen ? 'calc(100vh - 80px)' : 'calc(95vh - 80px)'
}))

// 监听visible变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetTransform()
    loading.value = true
    error.value = false
  }
})

// 方法
const close = () => {
  emit('close')
}

const handleOverlayClick = (e) => {
  if (e.target === e.currentTarget) {
    close()
  }
}

const handleImageLoad = () => {
  loading.value = false
  error.value = false
}

const handleImageError = () => {
  loading.value = false
  error.value = true
}

const zoomIn = () => {
  if (scale.value < 3) {
    scale.value = Math.min(scale.value + 0.25, 3)
  }
}

const zoomOut = () => {
  if (scale.value > 0.5) {
    scale.value = Math.max(scale.value - 0.25, 0.5)
  }
}

const resetZoom = () => {
  scale.value = 1
  translateX.value = 0
  translateY.value = 0
}

const rotateLeft = () => {
  rotate.value -= 90
}

const rotateRight = () => {
  rotate.value += 90
}

const resetTransform = () => {
  scale.value = 1
  rotate.value = 0
  translateX.value = 0
  translateY.value = 0
}

const downloadImage = () => {
  const link = document.createElement('a')
  link.href = props.imageUrl
  link.download = props.alt || 'image'
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const toggleFullscreen = () => {
  emit('toggle-fullscreen')
}

// 键盘事件处理
const handleKeydown = (e) => {
  if (!props.visible) return
  
  switch (e.key) {
    case 'Escape':
      close()
      break
    case '+':
    case '=':
      zoomIn()
      break
    case '-':
      zoomOut()
      break
    case '0':
      resetZoom()
      break
    case 'ArrowLeft':
      rotateLeft()
      break
    case 'ArrowRight':
      rotateRight()
      break
    case 'f':
    case 'F':
      toggleFullscreen()
      break
  }
}

// 鼠标滚轮缩放
const handleWheel = (e) => {
  if (!props.visible) return
  
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  const newScale = Math.max(0.5, Math.min(3, scale.value + delta))
  scale.value = newScale
}

// 生命周期
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('wheel', handleWheel, { passive: false })
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('wheel', handleWheel)
})
</script>

<style scoped>
.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(8px);
  width: 100vw;
  height: 100vh;
}

.image-preview-container {
  position: relative;
  width: 95vw;
  height: 95vh;
  max-width: 95vw;
  max-height: 95vh;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.preview-close {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 45px;
  height: 45px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.preview-close:hover {
  background: rgba(255, 0, 0, 0.8);
  transform: scale(1.1);
  border-color: rgba(255, 255, 255, 0.8);
}

.preview-close .icon-close {
  color: white;
  font-size: 28px;
  font-weight: bold;
  line-height: 1;
}

.image-container {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(95vh - 80px);
  background: #f8f9fa;
  overflow: hidden;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  cursor: grab;
  user-select: none;
  transition: transform 0.3s ease;
}

.preview-image:active {
  cursor: grabbing;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

.loading-text {
  color: #666;
  font-size: 14px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.error-text {
  color: #f56c6c;
  font-size: 16px;
}

.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 25px;
  background: #fff;
  border-top: 1px solid #e0e0e0;
  min-height: 60px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.image-info {
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.toolbar-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #dcdfe6;
  background: #fff;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #606266;
  font-size: 16px;
}

.toolbar-btn:hover:not(:disabled) {
  border-color: #409eff;
  color: #409eff;
  background: #ecf5ff;
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.toolbar-btn i {
  font-size: 16px;
  font-weight: bold;
}

.zoom-info {
  min-width: 50px;
  text-align: center;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .image-preview-container {
    width: 98vw;
    height: 98vh;
    max-width: 98vw;
    max-height: 98vh;
  }
  
  .image-container {
    min-height: calc(98vh - 100px);
  }
  
  .preview-toolbar {
    flex-direction: column;
    gap: 10px;
    padding: 15px;
    min-height: 80px;
  }
  
  .toolbar-center {
    order: 1;
  }
  
  .toolbar-left,
  .toolbar-right {
    order: 2;
  }
  
  .toolbar-btn {
    width: 40px;
    height: 40px;
  }
  
  .toolbar-btn i {
    font-size: 18px;
  }
  
  .preview-close {
    width: 50px;
    height: 50px;
    top: 10px;
    right: 10px;
  }
  
  .preview-close .icon-close {
    font-size: 32px;
  }
}
</style>