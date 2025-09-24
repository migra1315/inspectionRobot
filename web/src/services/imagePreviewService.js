import { ref, reactive } from 'vue'

// 全局图片预览状态
const previewState = reactive({
  visible: false,
  imageUrl: '',
  alt: '',
  isFullscreen: true
})

// 事件监听器
const listeners = []

// 全局图片预览服务
const imagePreviewService = {
  // 打开图片预览
  openPreview(imageUrl, alt = '') {
    console.log('imagePreviewService.openPreview 被调用:', { imageUrl, alt })
    previewState.visible = true
    previewState.imageUrl = imageUrl
    previewState.alt = alt
    previewState.isFullscreen = true
    
    console.log('预览状态已更新:', previewState)
    
    // 通知所有监听器
    listeners.forEach(listener => {
      if (listener.onOpen) {
        listener.onOpen(imageUrl, alt)
      }
    })
  },

  // 关闭图片预览
  closePreview() {
    previewState.visible = false
    previewState.imageUrl = ''
    previewState.alt = ''
    previewState.isFullscreen = true
    
    // 通知所有监听器
    listeners.forEach(listener => {
      if (listener.onClose) {
        listener.onClose()
      }
    })
  },

  // 切换全屏模式
  toggleFullscreen() {
    previewState.isFullscreen = !previewState.isFullscreen
    
    // 通知所有监听器
    listeners.forEach(listener => {
      if (listener.onToggleFullscreen) {
        listener.onToggleFullscreen(previewState.isFullscreen)
      }
    })
  },

  // 获取预览状态
  getState() {
    return previewState
  },

  // 添加事件监听器
  addListener(listener) {
    listeners.push(listener)
    
    // 返回移除监听器的函数
    return () => {
      const index = listeners.indexOf(listener)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  },

  // 移除所有监听器
  removeAllListeners() {
    listeners.length = 0
  }
}

export default imagePreviewService
