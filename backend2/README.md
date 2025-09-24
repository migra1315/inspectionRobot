# 巡检监控系统后端 v2.0

## 项目简介
简化版的巡检监控系统后端，专注于核心业务逻辑实现，使用Flask + SQLite架构。

## 功能特性
- 机器人巡检任务管理
- 异步LLM图片分析
- 实时系统信息监控
- 报警信息处理
- 图片存储和管理

## 项目结构
```
backend2/
├── app.py                    # Flask主应用
├── database.py              # 数据库操作
├── RobotController.py       # 机器人控制（已修改）
├── ErrorMonitorwithLLM.py   # LLM分析（已修改）
├── DetectorHandler.py       # 报警处理（已修改）
├── start.py                 # 启动脚本
├── inspection_system.db     # SQLite数据库
└── uploads/                 # 图片存储
    ├── robot/               # 机器人拍照
    └── alerts/              # 报警图片
```

## 安装依赖
```bash
pip install flask sqlite3 openai pillow opencv-python numpy pyrealsense2
```

## 启动服务

### 方式1：使用启动脚本（推荐）
```bash
python start.py
```

### 方式2：分别启动
```bash
# 终端1：启动主应用
python app.py

# 终端2：启动报警处理
python DetectorHandler.py
```

## API接口

### 巡检任务
- `POST /api/task/start` - 开始巡检任务
- `GET /api/task/progress` - 获取任务进度

### 设备状态
- `GET /api/devices/status` - 获取设备状态和图片

### 系统信息
- `GET /api/system/info` - 获取系统环境参数

### 报警信息
- `GET /api/alerts/latest` - 获取最新报警记录

### 图片服务
- `GET /api/images/robot/<filename>` - 机器人图片
- `GET /api/images/alerts/<filename>` - 报警图片

## 数据流程

### 巡检流程
1. 前端调用 `/api/task/start` 开始巡检
2. 后端创建任务记录，启动机器人巡检
3. 机器人拍照 → 保存图片 → 异步LLM分析 → 更新数据库
4. 前端定时轮询获取进度和设备状态

### 系统信息流程
1. 定时任务每2秒更新系统信息
2. 前端定时获取最新系统信息

### 报警流程
1. DetectorHandler接收报警数据
2. 保存报警图片到本地
3. 写入数据库
4. 前端定时获取最新报警信息

## 数据库表结构

### tasks（巡检任务）
- id, task_name, status, current_step, total_steps, start_time, end_time

### device_inspections（设备巡检记录）
- id, task_id, device_id, device_name, step_order, image_path, llm_result, status

### system_info（系统信息）
- id, param_name, param_value, reference_value, status, updated_at

### security_alerts（报警记录）
- id, alert_type, message, image_path, severity, created_at

## 配置说明

### 机器人配置
- AGV_IP: 192.168.8.5
- AGV_PORT: 8080
- 设备坐标在 RobotController.py 中配置

### LLM配置
- 使用阿里云通义千问API
- API密钥在 ErrorMonitorwithLLM.py 中配置

### 端口配置
- 主应用: 5000
- 报警处理: 15001

## 注意事项
1. 确保机器人硬件连接正常
2. 配置正确的LLM API密钥
3. 确保图片存储目录有写入权限
4. 数据库文件会自动创建和初始化

## 故障排除
1. 检查端口是否被占用
2. 检查数据库文件权限
3. 检查图片存储目录权限
4. 查看控制台日志输出
