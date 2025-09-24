from flask import Flask, request, jsonify, send_from_directory
import logging
from datetime import datetime
import os
import time
import base64
from pathlib import Path
from database import db
'''
测试输出（未打印）
2025-09-01 16:23:49,082 - INFO - 接收到报警数据
nn_output:
  [0]:
    cid: 0
    gcid: 768
    aid: 0
    class_name: 人脸[纪宇][61.67]
    name: 纪宇
    phone:
    identity_card:
    base_pic: /userdata/mpp/face/.jpg
    conf: 0.9216537475585938
    x1: 0.666290581226349
    x2: 0.708709418773651
    y1: 0.3890734314918518
    y2: 0.49308454990386963
gcids:
  [0]:
    768
detect_line:
ncid: 0
chid: 1
location: 1
ip: 192.168.8.10
sn: 57fd13d068a622f1
sn32: 1d7183f357fd13d068a622f1c69c0397
geid: 3
engine_name: 人脸识别
desc:
filter_type: 0
pub_freq: 5
dwidth: 640
dheight: 360
swidth: 2560
sheight: 1440
timestamp: 1577904363
2025-09-01 16:23:49,092 - INFO - 192.168.8.39 - - [01/Sep/2025 16:23:49] "POST /aibox HTTP/1.1" 200 -
'''
# 初始化Flask应用
app = Flask(__name__)

# 数据库实例已从database模块导入

# 创建图片存储目录
upload_dir = Path("uploads/alerts")
upload_dir.mkdir(parents=True, exist_ok=True)

# 确保图片目录存在
image_dir = Path("uploads/alerts")
image_dir.mkdir(parents=True, exist_ok=True)

# 配置日志
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'alarm_receiver_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)
def print_json_data(data, indent=0):
    """递归打印JSON数据中的所有键值对"""
    indent_str = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'pic_data' or key == 'video' or key == 'spic_data':
                continue
            if isinstance(value, (dict, list)):
                print(f"{indent_str}{key}:")
                print_json_data(value, indent + 1)
            else:
                print(f"{indent_str}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{indent_str}[{i}]:")
            print_json_data(item, indent + 1)
    else:
        print(f"{indent_str}{data}")

@app.route('/aibox', methods=['POST'])
def receive_alarm():
    """接收报警数据的接口"""
    try:
        # 检查请求是否包含JSON数据
        if not request.is_json:
            app.logger.warning("接收到非JSON格式的数据")
            return jsonify({"status": "error", "message": "请求必须包含JSON数据"}), 400
        
        # 解析JSON数据
        alarm_data = request.get_json()

        app.logger.info(f"接收到报警数据")
        # app.logger.info(f"接收到报警数据: {alarm_data}")

        print_json_data(alarm_data)
        
        # 处理报警数据
        result = process_alarm_data(alarm_data)
        
        # 返回成功响应
        return jsonify({
            "status": "success", 
            "message": "报警数据已接收", 
            "received_at": datetime.now().isoformat(),
            "alert_id": result.get('alert_id')
        }), 200
    
    except Exception as e:
        app.logger.error(f"处理报警数据时发生错误: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"处理数据时发生错误: {str(e)}"}), 500

def process_alarm_data(alarm_data):
    """处理报警数据"""
    try:
        # 提取报警信息
        alert_info = extract_alert_info(alarm_data)
        
        # 提取图片数据
        image_data = extract_image_data(alarm_data)
        
        # 保存图片到本地
        image_path = None
        if image_data:
            try:
                timestamp = int(time.time())
                image_filename = f"alert_{timestamp}.jpg"
                image_path = image_dir / image_filename
                
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                app.logger.info(f"报警图片已保存: {image_path}")
            except Exception as img_error:
                app.logger.error(f"保存报警图片失败: {img_error}")
                # 继续处理，不因图片保存失败而中断
        
        # 保存报警记录到数据库
        # 生成唯一的alert_id
        alert_id = f"alert_{int(time.time())}"
        db.create_security_alert(
            alert_id=alert_id,
            alert_type=alert_info['type'],
            message=alert_info['message'],
            image_path=str(image_path) if image_path else None,
            severity=alert_info['severity']
        )
        
        if alert_id:
            app.logger.info(f"报警记录已保存到数据库: {alert_id}")
        
        return {'alert_id': alert_id}
        
    except Exception as e:
        app.logger.error(f"处理报警数据失败: {e}")
        return {'alert_id': None}

def extract_alert_info(alarm_data):
    """从报警数据中提取信息"""
    # 根据AI盒子的数据格式提取信息
    alert_info = {
        'type': '人脸识别报警',
        'message': '检测到未授权人员',
        'severity': 'high',
        'camera_id': 'camera_001',
        'camera_name': '主入口摄像头'
    }
    
    # 如果有具体的识别结果
    if 'nn_output' in alarm_data and alarm_data['nn_output']:
        nn_output = alarm_data['nn_output'][0] if alarm_data['nn_output'] else {}
        if 'class_name' in nn_output:
            # 提取人员姓名和置信度
            class_name = nn_output['class_name']
            if '[' in class_name and ']' in class_name:
                # 格式: "人脸[姓名][置信度]"
                name_part = class_name.split('[')[1].split(']')[0] if '[' in class_name else '未知人员'
                conf_part = class_name.split('[')[2].split(']')[0] if class_name.count('[') >= 2 else '0'
                alert_info['message'] = f"检测到人员: {name_part} (置信度: {conf_part}%)"
            else:
                alert_info['message'] = f"检测到: {class_name}"
        
        if 'name' in nn_output and nn_output['name']:
            alert_info['message'] = f"检测到人员: {nn_output['name']}"
    
    # 如果有摄像头信息
    if 'detect_line' in alarm_data:
        detect_line = alarm_data['detect_line']
        if 'ip' in detect_line:
            alert_info['camera_id'] = f"camera_{detect_line['ip'].replace('.', '_')}"
            alert_info['camera_name'] = f"摄像头 {detect_line['ip']}"
        
        # 提取时间戳
        if 'timestamp' in detect_line:
            alert_info['timestamp'] = detect_line['timestamp']
    
    return alert_info

def extract_image_data(alarm_data):
    """从报警数据中提取图片数据"""
    # 根据AI盒子的数据格式提取图片
    # 示例：如果图片数据在base64格式中
    if 'pic_data' in alarm_data:
        import base64
        try:
            image_data = base64.b64decode(alarm_data['pic_data'])
            return image_data
        except Exception as e:
            app.logger.error(f"解码图片数据失败: {e}")
    
    return None

def send_websocket_notification(alert_id, alert_info):
    """发送WebSocket通知"""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
        
        from app.services.websocket_service import WebSocketService
        websocket_service = WebSocketService()
        
        websocket_service.emit_security_alert({
            'alert_id': alert_id,
            'type': alert_info['type'],
            'message': alert_info['message'],
            'severity': alert_info['severity'],
            'timestamp': time.time(),
            'image_url': f'/api/security/alerts/{alert_id}/image'
        })
        
    except Exception as e:
        app.logger.error(f"发送WebSocket通知失败: {e}")

@app.route('/test-alarm', methods=['POST'])
def test_alarm():
    """模拟测试报警接口"""
    try:
        # 生成模拟报警数据
        test_data = generate_test_alarm_data()
        
        app.logger.info("开始模拟测试报警")
        
        # 处理模拟数据
        result = process_alarm_data(test_data)
        
        return jsonify({
            "status": "success",
            "message": "模拟报警测试完成",
            "test_data": test_data,
            "alert_id": result.get('alert_id'),
            "received_at": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        app.logger.error(f"模拟测试报警失败: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"模拟测试失败: {str(e)}"}), 500

@app.route('/api/alerts/latest', methods=['GET'])
def get_latest_alerts():
    """获取最新报警信息 - 与backend2/app.py保持一致"""
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

@app.route('/api/images/alerts/<filename>')
def serve_alert_image(filename):
    """提供报警图片服务 - 与backend2/app.py保持一致"""
    return send_from_directory('uploads/alerts', filename)

def generate_test_alarm_data():
    """生成模拟报警数据"""
    import random
    import base64
    
    # 模拟人脸识别结果
    test_persons = [
        {"name": "张三", "confidence": 0.95},
        {"name": "李四", "confidence": 0.87},
        {"name": "王五", "confidence": 0.92},
        {"name": "未知人员", "confidence": 0.75}
    ]
    
    person = random.choice(test_persons)
    
    # 生成模拟图片数据（简单的测试图片）
    test_image_data = generate_test_image()
    
    test_data = {
        "nn_output": [{
            "cid": 0,
            "gcid": 768,
            "aid": 0,
            "class_name": f"人脸[{person['name']}][{person['confidence']:.2f}]",
            "name": person['name'],
            "phone": "",
            "identity_card": "",
            "base_pic": "/userdata/mpp/face/.jpg",
            "conf": person['confidence'],
            "x1": 0.666290581226349,
            "x2": 0.708709418773651,
            "y1": 0.3890734314918518,
            "y2": 0.49308454990386963
        }],
        "gcids": [768],
        "detect_line": {
            "ncid": 0,
            "chid": 1,
            "location": 1,
            "ip": "192.168.8.10",
            "sn": "57fd13d068a622f1",
            "sn32": "1d7183f357fd13d068a622f1c69c0397",
            "geid": 3,
            "engine_name": "人脸识别",
            "desc": "",
            "filter_type": 0,
            "pub_freq": 5,
            "dwidth": 640,
            "dheight": 360,
            "swidth": 2560,
            "sheight": 1440,
            "timestamp": int(time.time())
        }
    }
    
    # 如果有测试图片数据，添加到请求中
    if test_image_data:
        test_data['pic_data'] = base64.b64encode(test_image_data).decode('utf-8')
    
    return test_data

def generate_test_image():
    """生成测试图片数据"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # 创建一个简单的测试图片
        img = Image.new('RGB', (640, 480), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # 添加一些文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            # 如果没有找到字体，使用默认字体
            font = ImageFont.load_default()
        
        draw.text((50, 50), "测试报警图片", fill='black', font=font)
        draw.text((50, 100), f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fill='black', font=font)
        draw.text((50, 150), "AI盒子模拟测试", fill='red', font=font)
        
        # 转换为字节数据
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        
        return img_byte_arr
        
    except Exception as e:
        app.logger.error(f"生成测试图片失败: {e}")
        return None

if __name__ == '__main__':
    # 启动服务器，监听所有网络接口的15001端口
    # 生产环境中建议使用更安全的配置和WSGI服务器（如Gunicorn）
    app.run(host='0.0.0.0', port=15001, debug=False)

