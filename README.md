# 巡检监控系统

一个基于Flask后端和Vue.js前端的智能巡检监控系统，支持机器人自动巡检、LLM图像分析、实时监控和报警推送。

## 系统架构

```
巡检监控系统/
├── backend2/          # 后端服务（Flask）
├── web/              # 前端界面（Vue.js）
└── README.md         # 本文档
```

## 后端服务 (backend2/)

### 核心文件结构

| 文件路径 | 用途 | 说明 |
|---------|------|------|
| `app.py` | Flask主应用 | 提供REST API接口，处理前端请求 |
| `database.py` | 数据库管理 | SQLite数据库操作，CRUD功能 |
| `RobotController.py` | 机器人控制 | 核心机器人控制逻辑，支持真实/模拟模式 |
| `ErrorMonitorwithLLM.py` | LLM分析 | 图像识别和异常检测 |
| `DetectorHandler.py` | 检测处理器 | 独立的Flask应用，接收安防监控推送 |
| `init_on_startup.py` | 启动初始化 | 系统启动时重置状态和数据 |
| `config.py` | 配置文件 | 系统配置参数 |
| `requirements.txt` | 依赖列表 | Python包依赖 |
| `inspection_system.db` | 数据库文件 | SQLite数据库存储 |

### 关键API接口

| 接口 | 方法 | 用途 |
|------|------|------|
| `/api/task/start` | POST | 开始巡检任务 |
| `/api/task/progress` | GET | 获取任务进度 |
| `/api/devices/status` | GET | 获取设备状态 |
| `/api/devices/inspections` | GET | 获取设备巡检记录 |
| `/api/alerts/latest` | GET | 获取最新报警信息 |
| `/api/alerts/history` | GET | 获取报警履历 |
| `/api/system/info` | GET | 获取系统信息 |
| `/aibox` | POST | 接收AI盒子推送（DetectorHandler） |
| `/test-alarm` | POST | 模拟测试报警（DetectorHandler） |

## 前端界面 (web/)

### 核心文件结构

| 文件路径 | 用途 | 说明 |
|---------|------|------|
| `src/App.vue` | 主应用组件 | Vue.js根组件 |
| `src/main.js` | 应用入口 | 应用初始化和路由配置 |
| `src/router/index.js` | 路由配置 | 页面路由管理 |
| `src/views/Dashboard.vue` | 主仪表板 | 系统主界面布局 |
| `src/components/dashboard/` | 仪表板组件 | 各功能模块组件 |
| `src/services/api_v2.js` | API服务 | 后端接口调用 |
| `src/utils/` | 工具函数 | 通用工具和数据处理 |
| `package.json` | 项目配置 | 前端依赖和脚本 |
| `vite.config.js` | 构建配置 | Vite构建工具配置 |

### 关键组件

| 组件文件 | 用途 | 说明 |
|---------|------|------|
| `RobotStatus.vue` | 机器人状态 | 显示机器人状态和巡检进度 |
| `DeviceMonitor.vue` | 设备监控 | 显示4个设备的状态和参数 |
| `SecurityMonitor_v2.vue` | 安防监控 | 显示报警图片和报警履历 |
| `SystemInfo.vue` | 系统信息 | 显示系统运行状态 |

## 安装和运行

### 环境要求

- Python 3.8+
- Node.js 16+
- SQLite3

### 后端安装和运行

1. **进入后端目录**
   ```bash
   cd backend2
   ```

2. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **可选：安装硬件支持库（真实设备环境）**
   ```bash
   # RealSense相机支持
   pip install pyrealsense2
   
   # 机械臂控制支持
   pip install piper_control
   
   # 图像处理支持
   pip install opencv-python
   ```

4. **运行后端服务**
   ```bash
   python app.py
   ```

   后端服务将在 `http://localhost:5000` 启动

5. **运行安防监控推送服务（可选）**
   ```bash
   python DetectorHandler.py
   ```

   安防监控推送服务将在 `http://localhost:15001` 启动

### 前端安装和运行

1. **进入前端目录**
   ```bash
   cd web
   ```

2. **安装Node.js依赖**
   ```bash
   npm install
   ```

3. **启动开发服务器**
   ```bash
   npm run dev
   ```

   前端服务将在 `http://localhost:3000` 启动

## 调试模式运行

### 后端调试

```bash
cd backend2
python app.py
```

后端会以调试模式运行，支持：
- 自动重载代码更改
- 详细错误信息
- 控制台日志输出

### 安防监控推送服务

```bash
cd backend2
python DetectorHandler.py
```

安防监控推送服务会以调试模式运行，支持：
- 接收AI盒子推送数据
- 模拟测试报警功能
- 详细日志记录

### 前端调试

```bash
cd web
npm run dev
```

前端会以开发模式运行，支持：
- 热重载
- 浏览器开发者工具
- 实时错误提示

## 功能特性

### 机器人巡检
- ✅ 支持真实/模拟模式自动切换
- ✅ AGV自动导航到各站点
- ✅ 机械臂精确定位拍照
- ✅ 实时任务进度跟踪

### LLM图像分析
- ✅ 自动识别设备状态
- ✅ 温度/容量参数提取
- ✅ 异常状态检测
- ✅ 结果存储到数据库

### 实时监控
- ✅ 设备状态实时显示
- ✅ 巡检进度可视化
- ✅ 系统信息监控
- ✅ 自动数据刷新

### 报警系统
- ✅ 异常自动检测
- ✅ 报警图片保存
- ✅ 报警履历记录
- ✅ 实时推送通知
- ✅ 安防监控推送接收
- ✅ 报警信息实时显示

## 数据库表结构

### tasks 表
- `id`: 任务ID
- `name`: 任务名称
- `status`: 任务状态 (idle/running/completed)
- `current_step`: 当前步骤
- `created_at`: 创建时间

### device_inspections 表
- `id`: 巡检记录ID
- `task_id`: 关联任务ID
- `device_id`: 设备ID
- `device_name`: 设备名称
- `step_order`: 步骤顺序
- `image_path`: 图片路径
- `llm_result`: LLM分析结果
- `status`: 巡检状态

### security_alerts 表
- `id`: 报警ID
- `alert_id`: 报警标识
- `alert_type`: 报警类型
- `alert_message`: 报警消息
- `message`: 详细消息
- `image_path`: 报警图片路径
- `severity`: 严重程度
- `created_at`: 创建时间

## 配置说明

### 后端配置 (config.py)
```python
# AGV机器人配置
AGV_IP = "192.168.8.5"
AGV_PORT = 8080
AGV_USERNAME = "admin"
AGV_PASSWORD = "password"

# 数据库配置
DATABASE_PATH = "inspection_system.db"

# 上传目录配置
UPLOADS_DIR = "uploads"
```

### 前端配置 (vite.config.js)
```javascript
export default {
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
}
```

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查Python版本 (需要3.8+)
   - 检查依赖安装是否完整
   - 检查端口5000是否被占用

2. **前端启动失败**
   - 检查Node.js版本 (需要16+)
   - 删除node_modules重新安装
   - 检查端口3000是否被占用

3. **数据库连接失败**
   - 检查inspection_system.db文件权限
   - 确保backend2目录可写

4. **机器人连接失败**
   - 检查网络连接
   - 检查AGV设备IP配置
   - 系统会自动切换到模拟模式

5. **安防监控推送失败**
   - 检查 `DetectorHandler.py` 是否正常运行
   - 检查 `uploads/alerts/` 目录权限
   - 检查数据库 `security_alerts` 表结构
   - 检查前端轮询是否正常（每2秒）

### 调试技巧

1. **查看后端日志**
   ```bash
   # 后端控制台会显示详细日志
   python app.py
   ```

2. **查看前端控制台**
   - 打开浏览器开发者工具
   - 查看Console和Network标签

3. **检查数据库**
   ```bash
   sqlite3 inspection_system.db
   .tables
   .schema tasks
   .schema security_alerts
   ```

4. **检查安防监控推送**
   ```bash
   # 检查报警记录
   sqlite3 inspection_system.db "SELECT * FROM security_alerts ORDER BY created_at DESC LIMIT 5;"
   
   # 检查报警图片目录
   ls -la uploads/alerts/
   ```

5. **测试推送接口**
   ```bash
   # 测试获取最新报警
   curl http://localhost:5000/api/alerts/latest?limit=5
   
   # 测试推送接口
   curl -X POST http://localhost:5000/api/detector/alerts \
     -H "Content-Type: application/json" \
     -d '{"alert_id":"test_123","alert_type":"测试报警","message":"测试消息","severity":"medium"}'
   ```

## 安防监控推送系统

### 推送流程
1. **检测触发**: AI盒子检测到异常，推送到 `DetectorHandler.py`
2. **数据接收**: `DetectorHandler.py` 接收 `/aibox` 接口的推送数据
3. **图片保存**: 保存报警图片到 `uploads/alerts/` 目录
4. **数据库记录**: 在 `security_alerts` 表中创建报警记录
5. **前端轮询**: 前端每2秒轮询 `/api/alerts/latest` 接口
6. **实时显示**: 在安防监控模块显示最新报警图片和履历

### 推送接口说明

#### 接收推送接口
```http
POST http://localhost:15001/aibox
Content-Type: application/json

{
  "nn_output": [{
    "class_name": "人脸[张三][95.5]",
    "name": "张三",
    "conf": 0.955
  }],
  "detect_line": {
    "ip": "192.168.8.10",
    "timestamp": 1577904363
  },
  "pic_data": "base64编码的图片数据"
}
```

#### 模拟测试接口
```http
POST http://localhost:15001/test-alarm
Content-Type: application/json
```

#### 获取最新报警
```http
GET /api/alerts/latest?limit=10
```

#### 获取报警履历
```http
GET /api/alerts/history?limit=50
```

### 前端推送接收

#### SecurityMonitor_v2.vue 组件
- **自动刷新**: 每2秒自动获取最新报警信息
- **图片显示**: 显示最新报警图片
- **履历列表**: 显示报警履历，支持滚动
- **实时更新**: 检测到新报警时自动更新显示

#### 数据流
```
AI盒子 → DetectorHandler.py:15001 → 数据库 → app.py:5000 → 前端轮询 → 界面更新
```

## 开发说明

### 添加新功能
1. 后端：在`app.py`中添加新的API接口
2. 前端：在`src/components/`中添加新组件
3. 数据库：在`database.py`中添加新的数据操作方法

### 代码结构
- 后端采用Flask + SQLite架构
- 前端采用Vue.js 3 + Vite架构
- 支持真实设备和模拟模式
- 异步处理LLM分析
- 实时数据更新
- 安防监控推送接收

## 联系支持

如有问题，请检查：
1. 本文档的故障排除部分
2. 控制台错误日志
3. 浏览器开发者工具
4. 数据库连接状态

---

**注意**: 本系统支持真实硬件设备，但也可以在没有硬件的情况下以模拟模式运行，用于开发和测试。