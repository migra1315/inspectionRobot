<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Dashboard from './views/Dashboard.vue'
// WebSocket服务已移除，使用HTTP轮询
import imagePreviewService from './services/imagePreviewService.js'
import ImagePreview from './components/common/ImagePreview.vue'


// 全局图片预览状态
const previewState = ref({
  visible: false,
  imageUrl: '',
  alt: '',
  isFullscreen: true
})





// 图片预览事件处理
const handlePreviewClose = () => {
  imagePreviewService.closePreview()
}

const handlePreviewToggleFullscreen = () => {
  imagePreviewService.toggleFullscreen()
}



// 组件挂载时初始化
onMounted(async () => {
  console.log('应用已启动，使用HTTP轮询通信')
  
  
  // 添加图像预览服务事件监听器
  removePreviewListener = imagePreviewService.addListener({
    onOpen: (imageUrl, alt) => {
      console.log('预览打开事件:', { imageUrl, alt })
      previewState.value.visible = true
      previewState.value.imageUrl = imageUrl
      previewState.value.alt = alt
      previewState.value.isFullscreen = true
    },
    onClose: () => {
      console.log('预览关闭事件')
      previewState.value.visible = false
      previewState.value.imageUrl = ''
      previewState.value.alt = ''
      previewState.value.isFullscreen = true
    }
  })
  
})

// 存储监听器移除函数
let removePreviewListener = null

// 组件卸载时清理
onUnmounted(() => {
  // 清理预览监听器
  if (removePreviewListener) {
    removePreviewListener()
  }
})
</script>

<template>
  <div id="app">
    
    <!-- 统一使用Dashboard组件 -->
    <Dashboard />
    
    <!-- 全局图片预览组件 -->
    <ImagePreview 
      :visible="previewState.visible"
      :imageUrl="previewState.imageUrl"
      :alt="previewState.alt"
      :isFullscreen="previewState.isFullscreen"
      @close="handlePreviewClose"
      @toggle-fullscreen="handlePreviewToggleFullscreen"
    />
  </div>
</template>

<style>
@import './assets/styles/dashboard.css';
@import './assets/styles/components.css';

</style>
