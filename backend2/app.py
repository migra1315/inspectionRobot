"""
Flask主应用 - 简化的巡检监控系统后端
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import asyncio
import threading
import time
import random
from datetime import datetime
from pathlib import Path
from database import db
from RobotController import main as robot_main
from init_on_startup import init_on_startup

app = Flask(__name__)
CORS(app)  # 启用CORS支持

# 创建上传目录
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# 全局变量
current_task_id = None
task_thread = None

@app.route('/api/task/start', methods=['POST'])
def start_inspection():
    """开始巡检任务"""
    global current_task_id, task_thread
    
    try:
        data = request.get_json() or {}
        task_name = data.get('task_name', f'巡检任务_{int(time.time())}')
        
        # 创建任务记录
        task_id = db.create_task(task_name)
        current_task_id = task_id
        
        # 异步启动机器人巡检
        def run_robot():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(robot_main(task_id))
            loop.close()
        
        task_thread = threading.Thread(target=run_robot)
        task_thread.daemon = True
        task_thread.start()
        
        return jsonify({
            'success': True,
            'data': {
                'task_id': task_id,
                'message': '巡检任务已启动'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/task/progress', methods=['GET'])
def get_task_progress():
    """获取任务进度"""
    try:
        if current_task_id:
            task = db.get_task_progress(current_task_id)
            if task:
                return jsonify({
                    'success': True,
                    'data': task
                })
        
        # 获取最新任务
        latest_task = db.get_latest_task()
        if latest_task:
            return jsonify({
                'success': True,
                'data': latest_task
            })
        
        return jsonify({
            'success': True,
            'data': {
                'id': 0,
                'task_name': '无任务',
                'status': 'idle',
                'current_step': 0,
                'total_steps': 5,
                'progress_percentage': 0
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/devices/status', methods=['GET'])
def get_devices_status():
    """获取设备状态"""
    try:
        if current_task_id:
            inspections = db.get_device_inspections(current_task_id)
        else:
            # 获取最新任务的设备状态
            latest_task = db.get_latest_task()
            if latest_task:
                inspections = db.get_device_inspections(latest_task['id'])
            else:
                inspections = []
        
        # 处理设备数据
        devices = []
        for inspection in inspections:
            device = {
                'id': inspection['device_id'],
                'name': inspection['device_name'],
                'step_order': inspection['step_order'],
                'status': inspection['status'],
                'image_path': inspection['image_path'],
                'llm_result': inspection['llm_result'],
                'inspected_at': inspection['inspected_at']
            }
            
            # 处理图片URL
            if device['image_path']:
                device['image_url'] = f'/api/images/robot/{Path(device["image_path"]).name}'
            else:
                device['image_url'] = None
            
            devices.append(device)
        
        return jsonify({
            'success': True,
            'data': devices
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """获取系统信息"""
    try:
        # 随机更新系统信息（模拟实时数据）
        print("API调用: 开始更新环境数据")
        _update_system_info_randomly()
        print("API调用: 环境数据更新完成")
        
        system_info = db.get_system_info()
        print(f"API调用: 获取到系统信息 {len(system_info)} 条")
        
        return jsonify({
            'success': True,
            'data': system_info
        })
        
    except Exception as e:
        print(f"API调用错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/alerts/latest', methods=['GET'])
def get_latest_alerts():
    """获取最新报警信息"""
    try:
        limit = request.args.get('limit', 10, type=int)
        alerts = db.get_latest_alerts(limit)
        
        # 处理图片URL
        for alert in alerts:
            if alert['image_path']:
                alert['image_url'] = f'/api/images/alerts/{Path(alert["image_path"]).name}'
            else:
                alert['image_url'] = None
        
        return jsonify({
            'success': True,
            'data': alerts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/images/robot/<filename>')
def serve_robot_image(filename):
    """提供机器人图片服务"""
    return send_from_directory('uploads/robot', filename)

@app.route('/api/images/alerts/<filename>')
def serve_alert_image(filename):
    """提供报警图片服务"""
    return send_from_directory('uploads/alerts', filename)

def _update_system_info_randomly():
    """从数据库随机选择环境数据更新系统信息"""
    try:
        print("开始随机选择环境数据...")
        # 从environment_data表随机选择一条记录
        sample_data = db.get_random_environment_data()
        if not sample_data:
            print("警告: 没有找到环境数据示例，使用默认值")
            return
        
        print(f"随机选择的数据: 温度={sample_data['temperature']}, CO2={sample_data['co2_concentration']}")
        
        # 映射字段名
        param_mapping = {
            'temperature': sample_data['temperature'],
            'humidity': sample_data['humidity'],
            'n2_concentration': sample_data['n2_concentration'],
            'o2_concentration': sample_data['o2_concentration'],
            'co2_concentration': sample_data['co2_concentration']
        }
        
        # 更新系统信息
        print("开始更新系统信息...")
        for param_name, value in param_mapping.items():
            # 所有数据都来自符合阈值的示例数据，状态都是normal
            print(f"更新 {param_name}: {value}")
            db.update_system_info(param_name, str(value), 'normal')
        
        print("系统信息更新完成")
            
    except Exception as e:
        print(f"更新系统信息失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("启动巡检监控系统后端...")
    
    # 启动时初始化
    print("正在初始化系统...")
    init_on_startup()
    
    print("API接口:")
    print("  POST /api/task/start - 开始巡检")
    print("  GET  /api/task/progress - 获取任务进度")
    print("  GET  /api/devices/status - 获取设备状态")
    print("  GET  /api/system/info - 获取系统信息")
    print("  GET  /api/alerts/latest - 获取报警信息")
    print("  GET  /api/images/robot/<filename> - 机器人图片")
    print("  GET  /api/images/alerts/<filename> - 报警图片")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
