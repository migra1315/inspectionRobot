# 快速启动指南

## 🚀 一键启动（推荐）

### Windows用户
```bash
# 双击运行
start_system.bat

# 或命令行运行
start_system.bat
```

### Linux/Mac用户
```bash
# 运行启动脚本
./start_system.sh

# 或使用Python脚本
python3 start_system.py
```

## 🔧 手动启动

### 1. 启动后端服务
```bash
cd backend2
pip install -r requirements.txt
python app.py
```

### 2. 启动安防监控推送服务（可选）
```bash
cd backend2
python DetectorHandler.py
```

### 3. 启动前端服务
```bash
cd web
npm install
npm run dev
```

### 4. 打开浏览器
访问: http://localhost:3000

## 📋 环境要求

- Python 3.8+
- Node.js 16+
- SQLite3

## 🎯 功能验证

启动后请验证以下功能：

1. **机器人状态模块**
   - 显示"待机中"状态
   - "开始巡检"按钮可用

2. **设备状态监控模块**
   - 显示4个设备组件
   - 每个设备显示对应参数

3. **安防监控模块**
   - 显示报警图片区域
   - 显示报警履历列表

4. **系统信息模块**
   - 显示系统运行状态
   - 自动刷新数据

5. **安防监控推送**
   - 报警图片自动显示
   - 报警履历实时更新
   - 滚动条正常工作
   - 每2秒自动刷新

## 🐛 常见问题

### 后端启动失败
```bash
# 检查Python版本
python --version

# 重新安装依赖
cd backend2
pip install -r requirements.txt --force-reinstall
```

### 前端启动失败
```bash
# 检查Node.js版本
node --version

# 清理并重新安装
cd web
rm -rf node_modules
npm install
```

### 端口被占用
```bash
# 检查端口占用
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# 杀死占用进程
taskkill /PID <进程ID> /F
```

### 安防监控推送测试
```bash
# 测试获取最新报警
curl http://localhost:5000/api/alerts/latest?limit=5

# 测试模拟报警推送
curl -X POST http://localhost:15001/test-alarm

# 测试AI盒子推送接口
curl -X POST http://localhost:15001/aibox \
  -H "Content-Type: application/json" \
  -d "{\"nn_output\":[{\"class_name\":\"人脸[测试人员][95.5]\",\"name\":\"测试人员\"}],\"detect_line\":{\"ip\":\"192.168.8.10\",\"timestamp\":1577904363}}"

# 检查数据库中的报警记录
sqlite3 backend2/inspection_system.db "SELECT * FROM security_alerts ORDER BY created_at DESC LIMIT 5;"
```

## 📚 详细文档

查看 `README.md` 了解完整的系统架构和开发说明。

---

**注意**: 系统支持真实硬件设备，但也可以在没有硬件的情况下以模拟模式运行。
