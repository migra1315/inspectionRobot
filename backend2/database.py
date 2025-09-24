"""
数据库操作模块 - 简化的SQLite数据库管理
"""
import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "inspection_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 巡检任务表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name VARCHAR(100) NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'running',
                    current_step INTEGER DEFAULT 0,
                    total_steps INTEGER DEFAULT 5,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 检查并更新total_steps默认值
            self._migrate_total_steps(cursor)
            
            # 检查并更新security_alerts表结构
            self._migrate_security_alerts_table(cursor)
            
            # 设备巡检记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS device_inspections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    device_id VARCHAR(50) NOT NULL,
                    device_name VARCHAR(100) NOT NULL,
                    step_order INTEGER NOT NULL,
                    image_path VARCHAR(500),
                    llm_result TEXT,
                    status VARCHAR(20) DEFAULT 'pending',
                    inspected_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            ''')
            
            # 系统信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    param_name VARCHAR(50) NOT NULL UNIQUE,
                    param_value VARCHAR(50) NOT NULL,
                    reference_value VARCHAR(50) NOT NULL,
                    status VARCHAR(20) DEFAULT 'normal',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 报警记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id VARCHAR(100) UNIQUE,
                    alert_type VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    image_path VARCHAR(500),
                    severity VARCHAR(20) DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 初始化系统信息
            self._init_system_info(cursor)
            
            conn.commit()
    
    def _migrate_total_steps(self, cursor):
        """迁移total_steps默认值从4到5"""
        try:
            # 检查表结构中的默认值
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'")
            create_sql = cursor.fetchone()[0]
            
            # 如果默认值还是4，则更新现有记录的total_steps
            if "total_steps INTEGER DEFAULT 4" in create_sql:
                print("检测到旧版本数据库，正在迁移total_steps...")
                cursor.execute("UPDATE tasks SET total_steps = 5 WHERE total_steps = 4")
                
                # 重建表以更新默认值
                print("正在重建tasks表以更新默认值...")
                cursor.execute("""
                    CREATE TABLE tasks_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task_name VARCHAR(100) NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'running',
                        current_step INTEGER DEFAULT 0,
                        total_steps INTEGER DEFAULT 5,
                        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("INSERT INTO tasks_new SELECT * FROM tasks")
                cursor.execute("DROP TABLE tasks")
                cursor.execute("ALTER TABLE tasks_new RENAME TO tasks")
                print("数据库迁移完成：total_steps默认值已更新为5")
        except Exception as e:
            print(f"数据库迁移失败: {e}")
    
    def _migrate_security_alerts_table(self, cursor):
        """迁移security_alerts表结构"""
        try:
            # 检查表是否存在必要字段
            cursor.execute("PRAGMA table_info(security_alerts)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 添加缺失的字段
            if 'message' not in columns:
                print("检测到旧版本security_alerts表，正在添加message字段...")
                cursor.execute("ALTER TABLE security_alerts ADD COLUMN message TEXT")
                print("已添加message字段")
            
            if 'image_path' not in columns:
                print("正在添加image_path字段...")
                cursor.execute("ALTER TABLE security_alerts ADD COLUMN image_path VARCHAR(500)")
                print("已添加image_path字段")
            
            if 'severity' not in columns:
                print("正在添加severity字段...")
                cursor.execute("ALTER TABLE security_alerts ADD COLUMN severity VARCHAR(20) DEFAULT 'medium'")
                print("已添加severity字段")
            
            if 'alert_id' not in columns:
                print("正在添加alert_id字段...")
                cursor.execute("ALTER TABLE security_alerts ADD COLUMN alert_id VARCHAR(100)")
                print("已添加alert_id字段")
                
            print("security_alerts表迁移完成")
        except Exception as e:
            print(f"security_alerts表迁移失败: {e}")
    
    def _init_system_info(self, cursor):
        """初始化系统信息数据"""
        system_params = [
            ('temperature', '25.0', '25.0', 'normal'),
            ('humidity', '60.0', '60.0', 'normal'),
            ('n2_concentration', '78.0', '78.0', 'normal'),
            ('o2_concentration', '21.0', '21.0', 'normal'),
            ('co2_concentration', '0.04', '0.04', 'normal')
        ]
        
        for param in system_params:
            cursor.execute('''
                INSERT OR IGNORE INTO system_info (param_name, param_value, reference_value, status)
                VALUES (?, ?, ?, ?)
            ''', param)
    
    def create_task(self, task_name: str) -> int:
        """创建巡检任务"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks (task_name, status, current_step, total_steps)
                    VALUES (?, 'running', 0, 5)
                ''', (task_name,))
                return cursor.lastrowid
        except Exception as e:
            print(f"创建任务失败: {e}")
            raise
    
    def update_task_progress(self, task_id: int, current_step: int, status: str = None):
        """更新任务进度"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('''
                    UPDATE tasks SET current_step = ?, status = ?, end_time = ?
                    WHERE id = ?
                ''', (current_step, status, datetime.now() if status == 'completed' else None, task_id))
            else:
                cursor.execute('''
                    UPDATE tasks SET current_step = ? WHERE id = ?
                ''', (current_step, task_id))
    
    def get_task_progress(self, task_id: int) -> Optional[Dict]:
        """获取任务进度"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_latest_task(self) -> Optional[Dict]:
        """获取最新任务"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC LIMIT 1')
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_device_inspection(self, task_id: int, device_id: str, device_name: str, 
                               step_order: int, image_path: str = None) -> int:
        """创建设备巡检记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO device_inspections 
                (task_id, device_id, device_name, step_order, image_path, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            ''', (task_id, device_id, device_name, step_order, image_path))
            return cursor.lastrowid
    
    def update_device_inspection(self, inspection_id: int, llm_result: str, status: str = 'completed'):
        """更新设备巡检记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE device_inspections 
                SET llm_result = ?, status = ?, inspected_at = ?
                WHERE id = ?
            ''', (llm_result, status, datetime.now(), inspection_id))
    
    def get_device_inspections(self, task_id: int) -> List[Dict]:
        """获取设备巡检记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM device_inspections 
                WHERE task_id = ? 
                ORDER BY step_order
            ''', (task_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def update_system_info(self, param_name: str, param_value: str, status: str = 'normal'):
        """更新系统信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE system_info 
                SET param_value = ?, status = ?, updated_at = ?
                WHERE param_name = ?
            ''', (param_value, status, datetime.now(), param_name))
    
    def get_system_info(self) -> List[Dict]:
        """获取系统信息"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM system_info ORDER BY param_name')
            return [dict(row) for row in cursor.fetchall()]
    
    def create_security_alert(self, alert_id: str, alert_type: str, message: str, severity: str = 'medium', image_path: str = None) -> int:
        """创建报警记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO security_alerts (alert_id, alert_type, alert_message, image_path, severity, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (alert_id, alert_type, message, image_path, severity, datetime.now().isoformat()))
            return cursor.lastrowid
    
    def update_device_inspection_llm_result(self, inspection_id: int, llm_result: str) -> bool:
        """更新设备巡检记录的LLM结果"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE device_inspections 
                SET llm_result = ?
                WHERE id = ?
            ''', (llm_result, inspection_id))
            return cursor.rowcount > 0
    
    def get_latest_alerts(self, limit: int = 10) -> List[Dict]:
        """获取最新报警记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM security_alerts 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_random_environment_data(self) -> Optional[Dict]:
        """从environment_data表随机选择一条环境数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM environment_data 
                ORDER BY RANDOM() 
                LIMIT 1
            ''')
            row = cursor.fetchone()
            return dict(row) if row else None

# 全局数据库实例
db = DatabaseManager()
