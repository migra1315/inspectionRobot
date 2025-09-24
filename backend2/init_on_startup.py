"""
后端服务启动时的初始化脚本
"""
import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path

def init_on_startup():
    """后端服务启动时初始化"""
    print("=== 后端服务启动初始化 ===")
    
    db_path = "inspection_system.db"
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 重置所有运行中的任务为idle状态
        print("\n1. 重置任务状态:")
        print("-" * 50)
        
        cursor.execute("""
            UPDATE tasks 
            SET status = 'idle', 
                current_step = 0
            WHERE status = 'running'
        """)
        
        updated_tasks = cursor.rowcount
        print(f"✅ 重置了 {updated_tasks} 个运行中的任务")
        
        # 2. 清理设备巡检记录（保留最新的用于显示）
        print("\n2. 清理设备巡检记录:")
        print("-" * 50)
        
        # 只保留最新的任务记录
        cursor.execute("""
            DELETE FROM device_inspections 
            WHERE task_id NOT IN (
                SELECT id FROM tasks 
                ORDER BY created_at DESC 
                LIMIT 1
            )
        """)
        
        deleted_inspections = cursor.rowcount
        print(f"✅ 清理了 {deleted_inspections} 条旧设备巡检记录")
        
        # 3. 清理报警记录（保留最新的20条）
        print("\n3. 清理报警记录:")
        print("-" * 50)
        
        cursor.execute("""
            DELETE FROM security_alerts 
            WHERE id NOT IN (
                SELECT id FROM security_alerts 
                ORDER BY created_at DESC 
                LIMIT 20
            )
        """)
        
        deleted_alerts = cursor.rowcount
        print(f"✅ 清理了 {deleted_alerts} 条旧报警记录")
        
        # 4. 清理图片文件
        print("\n4. 清理图片文件:")
        print("-" * 50)
        
        # 清理机器人图片
        robot_dir = Path("uploads/robot")
        if robot_dir.exists():
            robot_files = list(robot_dir.glob("*.png")) + list(robot_dir.glob("*.jpg"))
            for file in robot_files:
                file.unlink()
            print(f"✅ 清理了 {len(robot_files)} 个机器人图片文件")
        
        # 清理报警图片
        alerts_dir = Path("uploads/alerts")
        if alerts_dir.exists():
            alert_files = list(alerts_dir.glob("*.png")) + list(alerts_dir.glob("*.jpg"))
            for file in alert_files:
                file.unlink()
            print(f"✅ 清理了 {len(alert_files)} 个报警图片文件")
        
        # 5. 创建初始测试数据
        print("\n5. 创建初始测试数据:")
        print("-" * 50)
        
        # 创建新的idle任务
        task_name = f"巡检任务_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cursor.execute("""
            INSERT INTO tasks (task_name, status, current_step, total_steps, created_at)
            VALUES (?, 'idle', 0, 5, ?)
        """, (task_name, datetime.now().isoformat()))
        
        task_id = cursor.lastrowid
        print(f"✅ 创建初始任务: {task_name} (ID: {task_id})")
        
        # 复制示例图片到uploads目录
        source_images = [
            ("device_0022.png", "device_001"),
            ("device_0033.png", "device_002"), 
            ("device_0044.png", "device_003"),
            ("device_0055.png", "device_004")
        ]
        
        robot_dir.mkdir(exist_ok=True)
        alerts_dir.mkdir(exist_ok=True)
        
        for source_img, device_id in source_images:
            source_path = f"../backend/static/images/{source_img}"
            if os.path.exists(source_path):
                # 复制到机器人图片目录
                timestamp = int(datetime.now().timestamp())
                robot_filename = f"{device_id}_{timestamp}.png"
                robot_path = robot_dir / robot_filename
                shutil.copy2(source_path, robot_path)
                
                # 复制到报警图片目录
                alert_filename = f"alert_{timestamp}.jpg"
                alert_path = alerts_dir / alert_filename
                shutil.copy2(source_path, alert_path)
                
                print(f"✅ 复制示例图片: {source_img} -> {robot_filename}")
            else:
                print(f"⚠️ 源图片不存在: {source_img}")
        
        # 6. 创建设备巡检记录
        print("\n6. 创建设备巡检记录:")
        print("-" * 50)
        
        devices = [
            ("device_001", "1号低温冰箱", 1),
            ("device_002", "2号低温冰箱", 2),
            ("device_003", "3号低温冰箱", 3),
            ("device_004", "1号液氮罐", 4)
        ]
        
        for device_id, device_name, step_order in devices:
            # 创建LLM结果
            if step_order == 4:  # 液氮罐
                llm_result = '{"当前余量": "40L", "安全余量": "60L", "系统状态": "正常", "设备类型": "液氮罐"}'
            else:  # 低温冰箱
                llm_result = '{"当前温度": "-79.8°C", "设定温度": "-80°C", "系统状态": "正常", "设备类型": "低温冰箱"}'
            
            timestamp = int(datetime.now().timestamp())
            image_path = f"uploads/robot/{device_id}_{timestamp}.png"
            
            cursor.execute("""
                INSERT INTO device_inspections 
                (task_id, device_id, device_name, step_order, status, image_path, llm_result, inspected_at, created_at)
                VALUES (?, ?, ?, ?, 'completed', ?, ?, ?, ?)
            """, (task_id, device_id, device_name, step_order, image_path, llm_result, 
                  datetime.now().isoformat(), datetime.now().isoformat()))
            
            print(f"✅ 创建设备记录: {device_name} (步骤{step_order})")
        
        # 7. 创建报警记录
        print("\n7. 创建报警记录:")
        print("-" * 50)
        
        # 生成唯一的alert_id，避免与现有记录冲突
        timestamp = int(datetime.now().timestamp())
        alert_id = f"alert_{timestamp}"
        
        # 检查alert_id是否已存在，如果存在则添加随机数
        while True:
            cursor.execute("SELECT COUNT(*) FROM security_alerts WHERE alert_id = ?", (alert_id,))
            if cursor.fetchone()[0] == 0:
                break
            alert_id = f"alert_{timestamp}_{int(datetime.now().microsecond)}"
        
        alert_image_path = f"uploads/alerts/alert_{timestamp}.jpg"
        
        cursor.execute("""
            INSERT INTO security_alerts 
            (alert_id, alert_type, alert_message, message, severity, image_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (alert_id, "设备异常报警", "检测到设备温度异常", "检测到设备温度异常", "high", alert_image_path, 
              datetime.now().isoformat()))
        
        print(f"✅ 创建报警记录 (ID: {alert_id})")
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 后端服务启动初始化完成")
        print("=" * 60)
        print("✅ 任务状态已重置为idle")
        print("✅ 设备状态数据已重置")
        print("✅ 报警图片和信息已重置")
        print("✅ 示例数据已创建")
        print("✅ 开始巡检按钮现在可用")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_on_startup()
