#!/bin/bash

echo "============================================================"
echo "🤖 巡检监控系统快速启动"
echo "============================================================"
echo

echo "📋 检查环境..."

echo
echo "🚀 启动系统..."
echo

# 启动后端服务
echo "启动后端服务..."
cd backend2
python3 app.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "等待后端服务启动..."
sleep 3

# 启动安防监控推送服务
echo "启动安防监控推送服务..."
cd backend2
python3 DetectorHandler.py &
DETECTOR_PID=$!
cd ..

# 等待安防推送服务启动
echo "等待安防推送服务启动..."
sleep 2

# 启动前端服务
echo "启动前端服务..."
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

# 等待前端启动
echo "等待前端服务启动..."
sleep 5

echo
echo "============================================================"
echo "🎉 系统启动完成！"
echo "============================================================"
echo "📱 前端地址: http://localhost:3000"
echo "🔧 后端地址: http://localhost:5000"
echo "🚨 安防推送: http://localhost:15001"
echo "📊 API文档: http://localhost:5000/api"
echo
echo "💡 提示:"
echo "- 按 Ctrl+C 停止服务"
echo "- 查看README.md了解详细使用说明"
echo "- 系统支持真实设备和模拟模式"
echo

# 打开浏览器
echo "正在打开浏览器..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
fi

# 等待用户中断
trap 'echo -e "\n🛑 正在停止服务..."; kill $BACKEND_PID $DETECTOR_PID $FRONTEND_PID 2>/dev/null; echo "✅ 服务已停止"; exit 0' INT

echo "按 Ctrl+C 停止服务..."
wait
