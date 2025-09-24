<template>
  <div class="system-title">
    <div class="title-content">
      <h1 class="main-title">智能巡检监控系统</h1>
      <p class="subtitle">Intelligent Inspection Monitoring System</p>
    </div>
    <div class="title-decoration">
      <div class="decoration-line"></div>
      <div class="decoration-dot"></div>
      <div class="decoration-line"></div>
    </div>
  </div>
</template>

<script setup>
// 系统标题组件 - 显示系统名称和装饰元素
</script>

<style scoped>
.system-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.system-title::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.title-content {
  text-align: center;
  z-index: 1;
  position: relative;
}

.main-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #ffffff;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 2px;
}

.subtitle {
  font-size: 1rem;
  color: #b3d9ff;
  margin: 0;
  font-weight: 300;
  letter-spacing: 1px;
}

.title-decoration {
  display: flex;
  align-items: center;
  margin-top: 1rem;
  z-index: 1;
  position: relative;
}

.decoration-line {
  width: 40px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #4fc3f7, transparent);
  border-radius: 1px;
}

.decoration-dot {
  width: 8px;
  height: 8px;
  background: #4fc3f7;
  border-radius: 50%;
  margin: 0 10px;
  box-shadow: 0 0 10px #4fc3f7;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

/* 响应式设计 */
@media (max-width: 1920px) {
  .main-title {
    font-size: 2rem;
  }
  .subtitle {
    font-size: 0.9rem;
  }
}

@media (max-width: 1440px) {
  .main-title {
    font-size: 1.8rem;
  }
  .subtitle {
    font-size: 0.8rem;
  }
}
</style>
