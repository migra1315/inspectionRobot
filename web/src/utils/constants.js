/**
 * 常量定义
 */

// 机器人状态
export const ROBOT_STATUS = {
  IDLE: 'idle',
  RUNNING: 'running',
  COMPLETED: 'completed',
  ERROR: 'error',
  STOPPED: 'stopped'
}

// 机器人位置
export const ROBOT_LOCATIONS = [
  { id: 0, name: '基站', position: 'base' },
  { id: 1, name: '设备A', position: 'device_a' },
  { id: 2, name: '设备B', position: 'device_b' },
  { id: 3, name: '设备C', position: 'device_c' },
  { id: 4, name: '设备D', position: 'device_d' }
]

// 环境参数类型
export const ENVIRONMENT_PARAMS = {
  TEMPERATURE: 'temperature',
  HUMIDITY: 'humidity',
  N2_CONCENTRATION: 'n2_concentration',
  O2_CONCENTRATION: 'o2_concentration',
  CO2_CONCENTRATION: 'co2_concentration'
}

// 环境参数配置
export const ENVIRONMENT_CONFIG = {
  [ENVIRONMENT_PARAMS.TEMPERATURE]: {
    name: '温度',
    unit: '℃',
    threshold: 25.0,
    range: { min: -50, max: 100 }
  },
  [ENVIRONMENT_PARAMS.HUMIDITY]: {
    name: '湿度',
    unit: '%',
    threshold: 60.0,
    range: { min: 0, max: 100 }
  },
  [ENVIRONMENT_PARAMS.N2_CONCENTRATION]: {
    name: 'N2浓度',
    unit: '%',
    threshold: 78.0,
    range: { min: 0, max: 100 }
  },
  [ENVIRONMENT_PARAMS.O2_CONCENTRATION]: {
    name: 'O2浓度',
    unit: '%',
    threshold: 21.0,
    range: { min: 0, max: 100 }
  },
  [ENVIRONMENT_PARAMS.CO2_CONCENTRATION]: {
    name: 'CO2浓度',
    unit: '%',
    threshold: 0.04,
    range: { min: 0, max: 1 }
  }
}

// 设备类型
export const DEVICE_TYPES = {
  REFRIGERATOR: 'refrigerator',
  LIQUID_NITROGEN_TANK: 'liquid_nitrogen_tank'
}

// 设备配置
export const DEVICE_CONFIG = {
  device_a: {
    id: 'device_a',
    name: '设备A',
    type: DEVICE_TYPES.REFRIGERATOR,
    core_parameter: '温度',
    reference_value: '-80℃'
  },
  device_b: {
    id: 'device_b',
    name: '设备B',
    type: DEVICE_TYPES.LIQUID_NITROGEN_TANK,
    core_parameter: '液氮液位',
    reference_value: '40L'
  },
  device_c: {
    id: 'device_c',
    name: '设备C',
    type: DEVICE_TYPES.LIQUID_NITROGEN_TANK,
    core_parameter: '液氮液位',
    reference_value: '40L'
  }
}

// 状态颜色
export const STATUS_COLORS = {
  NORMAL: '#67C23A',
  ABNORMAL: '#F56C6C',
  WARNING: '#E6A23C',
  INFO: '#409EFF',
  SUCCESS: '#67C23A',
  ERROR: '#F56C6C'
}

// WebSocket事件已移除，使用HTTP轮询

// API端点
export const API_ENDPOINTS = {
  ROBOT: {
    STATUS: '/robot/status',
    CONNECT: '/robot/connect',
    START_INSPECTION: '/robot/start-inspection',
    STOP_INSPECTION: '/robot/stop-inspection',
    GO_HOME: '/robot/go-home',
    PROGRESS: '/robot/progress'
  },
  ENVIRONMENT: {
    PARAMETERS: '/environment/parameters',
    THRESHOLDS: '/environment/thresholds',
    STATUS: '/environment/status'
  },
  DEVICE: {
    STATUS: '/device/status',
    IMAGE: '/device/image',
    ANALYZE: '/device/analyze',
    HISTORY: '/device/history'
  },
  SECURITY: {
    STREAMS: '/security/streams',
    ALERTS: '/security/alerts'
  }
}

// 视频流配置
export const VIDEO_STREAM_CONFIG = {
  STREAM_1: {
    id: 'stream_1',
    name: '监控画面1',
    url: 'http://192.168.1.100:8080/video'
  },
  STREAM_2: {
    id: 'stream_2',
    name: '监控画面2',
    url: 'http://192.168.1.101:8080/video'
  }
}

// 系统配置
export const SYSTEM_CONFIG = {
  REFRESH_INTERVAL: 5000, // 5秒
  // WebSocket相关常量已移除
  MAX_RECONNECT_ATTEMPTS: 5,
  API_TIMEOUT: 10000 // 10秒
}
