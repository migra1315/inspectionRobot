#!/usr/bin/env python3
"""
巡检监控系统快速启动脚本
"""
import subprocess
import sys
import time
import os
import webbrowser
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要3.8+")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def check_node_version():
    """检查Node.js版本"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js版本: {version}")
            return True
    except FileNotFoundError:
        print("❌ Node.js未安装，请先安装Node.js 16+")
        return False

def install_backend_deps():
    """安装后端依赖"""
    print("\n📦 安装后端依赖...")
    backend_dir = Path("backend2")
    if not backend_dir.exists():
        print("❌ backend2目录不存在")
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      cwd=backend_dir, check=True)
        print("✅ 后端依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 后端依赖安装失败: {e}")
        return False

def install_frontend_deps():
    """安装前端依赖"""
    print("\n📦 安装前端依赖...")
    web_dir = Path("web")
    if not web_dir.exists():
        print("❌ web目录不存在")
        return False
    
    try:
        subprocess.run(["npm", "install"], cwd=web_dir, check=True)
        print("✅ 前端依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 前端依赖安装失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("\n🚀 启动后端服务...")
    backend_dir = Path("backend2")
    
    try:
        # 在后台启动后端服务
        process = subprocess.Popen([sys.executable, "app.py"], 
                                 cwd=backend_dir, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待一下确保服务启动
        time.sleep(3)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ 后端服务启动成功 (http://localhost:5000)")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ 后端服务启动失败: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def start_detector():
    """启动安防监控推送服务"""
    print("\n🚀 启动安防监控推送服务...")
    backend_dir = Path("backend2")
    
    try:
        # 在后台启动DetectorHandler服务
        process = subprocess.Popen([sys.executable, "DetectorHandler.py"], 
                                 cwd=backend_dir, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待一下确保服务启动
        time.sleep(2)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ 安防监控推送服务启动成功 (http://localhost:15001)")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ 安防监控推送服务启动失败: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ 启动安防监控推送服务失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("\n🚀 启动前端服务...")
    web_dir = Path("web")
    
    try:
        # 在后台启动前端服务
        process = subprocess.Popen(["npm", "run", "dev"], 
                                 cwd=web_dir, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # 等待一下确保服务启动
        time.sleep(5)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ 前端服务启动成功 (http://localhost:3000)")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ 前端服务启动失败: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ 启动前端服务失败: {e}")
        return None

def open_browser():
    """打开浏览器"""
    print("\n🌐 打开浏览器...")
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ 浏览器已打开")
    except Exception as e:
        print(f"⚠️ 无法自动打开浏览器: {e}")
        print("请手动打开: http://localhost:3000")

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 巡检监控系统快速启动")
    print("=" * 60)
    
    # 检查环境
    if not check_python_version():
        return
    
    if not check_node_version():
        return
    
    # 安装依赖
    if not install_backend_deps():
        return
    
    if not install_frontend_deps():
        return
    
    # 启动服务
    backend_process = start_backend()
    if not backend_process:
        return
    
    detector_process = start_detector()
    if not detector_process:
        backend_process.terminate()
        return
    
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        detector_process.terminate()
        return
    
    # 打开浏览器
    open_browser()
    
    print("\n" + "=" * 60)
    print("🎉 系统启动完成！")
    print("=" * 60)
    print("📱 前端地址: http://localhost:3000")
    print("🔧 后端地址: http://localhost:5000")
    print("🚨 安防推送: http://localhost:15001")
    print("📊 API文档: http://localhost:5000/api")
    print("\n💡 提示:")
    print("- 按 Ctrl+C 停止服务")
    print("- 查看README.md了解详细使用说明")
    print("- 系统支持真实设备和模拟模式")
    print("- 安防监控推送服务可选启动")
    
    try:
        # 等待用户中断
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        backend_process.terminate()
        detector_process.terminate()
        frontend_process.terminate()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
