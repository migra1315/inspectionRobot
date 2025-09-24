"""
启动脚本 - 同时启动主应用和报警处理服务
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def start_services():
    """启动所有服务"""
    print("正在启动巡检监控系统...")
    
    # 确保在正确的目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        # 启动主应用
        print("启动主应用 (端口 5000)...")
        main_process = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待一下确保主应用启动
        time.sleep(2)
        
        # 启动报警处理服务
        print("启动报警处理服务 (端口 15001)...")
        detector_process = subprocess.Popen([
            sys.executable, "DetectorHandler.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("所有服务已启动!")
        print("主应用: http://localhost:5000")
        print("报警处理: http://localhost:15001")
        print("按 Ctrl+C 停止所有服务")
        
        # 等待进程
        try:
            main_process.wait()
        except KeyboardInterrupt:
            print("\n正在停止服务...")
            main_process.terminate()
            detector_process.terminate()
            print("服务已停止")
            
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    start_services()
