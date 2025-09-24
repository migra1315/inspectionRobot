import asyncio
import websockets
import requests
import numpy as np
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from database import db
from ErrorMonitorwithLLM import ErrorMonitor

# 可选导入
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    print("警告: opencv-python未安装，图片处理功能将被禁用")

try:
    import pyrealsense2 as rs
    HAS_REALSENSE = True
except ImportError:
    HAS_REALSENSE = False
    print("警告: pyrealsense2未安装，相机功能将被禁用")

try:
    from piper_control import piper_connect, piper_interface, piper_init
    HAS_PIPER = True
except ImportError:
    HAS_PIPER = False
    print("警告: piper_control未安装，机械臂功能将被禁用")

from PIL import Image

AGV_IP = "192.168.8.5"
AGV_PORT = 8080
AGV_USERNAME = "admin"
AGV_PASSWORD = "admin"

class RobotController():
    # 初始化机器人
    def __init__(self, task_id: int = None):
        self.task_id = task_id
        self.llm_analyzer = ErrorMonitor()
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # 创建图片存储目录
        self.upload_dir = Path("uploads/robot")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.arm_robot = self.connect_arm_robot() if HAS_PIPER else None
        self.AGV_token = self.connect_agv_robot()
        
        # 初始化相机
        if HAS_REALSENSE:
            self.pipeline = rs.pipeline()
            self.config = rs.config()
            self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 15)
            self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 15)
            self.profile = self.pipeline.start(self.config)
            align_to = rs.stream.color
            self.align = rs.align(align_to)
            print("RealSense 相机已初始化")
        else:
            self.pipeline = None
            self.config = None
            self.profile = None
            self.align = None
            print("相机功能已禁用")
        
    # 连接机械臂
    def connect_arm_robot(self, can_name="can0"):
        if not HAS_PIPER:
            print("机械臂功能已禁用")
            return None
        try:
            # 可编程激活 CAN
            ports = piper_connect.find_ports()
            print("发现 CAN 端口:", ports)
            piper_connect.activate()
            active = piper_connect.active_ports()
            print("激活端口:", active)
        except Exception as e:
            print(f"机械臂连接失败: {e}")
            return None

        # 实例化机器人接口
        robot = piper_interface.PiperInterface(can_port=can_name)

        # 重置机械臂并启用运动
        piper_init.reset_arm(
            robot,
            arm_controller=piper_interface.ArmController.POSITION_VELOCITY,
            move_mode=piper_interface.MoveMode.JOINT
        )
        piper_init.reset_gripper(robot)
        time.sleep(0.1)
        print(f"机械臂已连接（CAN: {can_name}）")
        return robot

    # 连接AGV
    def connect_agv_robot(self):
        """
        登录AGV后台系统，获取 token
        """
        print("🚗 尝试连接AGV机器人...")
        url = f"http://{AGV_IP}:{AGV_PORT}/api/user/login"
        payload = {"username": AGV_USERNAME, "password": AGV_PASSWORD}
        headers = {"Content-Type": "application/json"}

        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=5)
            if resp.status_code == 200 and resp.headers.get("authorization"):
                token = resp.headers["authorization"]
                print("✅ AGV登录成功，获取到 token:", token)
                return token
            else:
                print("❌ AGV登录失败:", resp.text)
                return None
        except Exception as e:
            print(f"⚠️ AGV连接异常: {e}")
            print("🔧 使用模拟模式运行（无真实AGV设备）")
            return "simulation_mode"
    
    # 启动导航
    def start_navigation(self, map_name):
        if self.AGV_token == "simulation_mode":
            print(f"🔧 模拟启动导航: {map_name}")
            return
        url = f"http://{AGV_IP}:{AGV_PORT}/api/roslaunch/navigation/{map_name}"
        headers = {"authorization": self.AGV_token}
        resp = requests.get(url, headers=headers)
        print("启动导航:", resp.text)
    
    # 监听 WebSocket 等待事件
    async def wait_for_event(self, target_code=13):
        if self.AGV_token == "simulation_mode":
            print(f"🔧 模拟等待事件: {target_code}")
            await asyncio.sleep(2)  # 模拟等待时间
            return True
        ws_url = f"ws://{AGV_IP}:{AGV_PORT}/api/ws?token={self.AGV_token}"
        async with websockets.connect(ws_url) as websocket:
            flag = 0
            while True:
                msg = await websocket.recv()
                data = json.loads(msg)
                if data.get("type") == 1028:  # O_EVENT
                    event_code = data["data"].get("code")
                    event_msg = data["data"].get("msg")
                    print(f"<<< 事件: {event_code} - {event_msg}")
                    if event_msg == "开始执行任务":
                        flag = flag + 1
                    if event_msg == "完成任务":  # 到达目标点
                        flag = flag + 1
                        if flag >= 2:
                            return True
    
    # 移动AGV到指定地点
    async def move_agv(self, name, stations) -> bool:
        if self.AGV_token == "simulation_mode":
            print(f"🔧 模拟AGV移动到站点: {stations}")
            await asyncio.sleep(3)  # 模拟移动时间
            return True
        url = f"http://{AGV_IP}:{AGV_PORT}/api/task/set"
        headers = {"authorization": self.AGV_token, "Content-Type": "application/json"}
        task = {
            "name": name,
            "mode": 0,   # 即时任务
            "loop": 1,
            "minute": None,
            "hour": None,
            "opt": None,
            "actions": [
                {"type": 5, "value": stations}  # 5 表示预设的拓扑站点
            ]
        }
        resp = requests.post(url, headers=headers, data=json.dumps(task))
        print("下发任务:", resp.text)
        return await self.wait_for_event(target_code=13)  # 等待到达目标点事件
    
    # 读取机械臂当前姿态
    def get_joint_angles(self):
        if not hasattr(self, "arm_robot") or self.arm_robot is None:
            print("机械臂未连接")
            return None
        confirm = input("是否读取关节角度？请输入‘yes’确认：")
        if confirm.strip().lower() != "yes":
            print("取消读取关节角度")
            return None

        try:
            joint_angles = self.arm_robot.get_joint_positions()
            print("当前关节角度：", joint_angles)
            return joint_angles
        except Exception as e:
            print("读取关节角度失败：", e)
            return None

    # 移动机械臂到指定地点
    async def move_arm(self, joint_targets: list):
        if not HAS_PIPER or not self.arm_robot:
            print("机械臂功能已禁用，模拟移动")
            await asyncio.sleep(2)  # 模拟移动时间
            return True
        # 假设 joint_targets 是长度为 6 的目标关节角度（弧度）
        print("下发目标关节位置:", joint_targets)
        self.arm_robot.command_joint_positions(joint_targets)
        return True
    
    # 巡检设备
    async def inspection(self, name, stations, pose, device_id: str, device_name: str, step_order: int) -> bool:
        print(f"🤖 开始巡检任务 {name} -> {stations}")
        print(f"📋 设备信息: {device_name} (ID: {device_id})")
        print(f"📍 目标站点: {stations}")
        print(f"🎯 机械臂位置: {pose}")
        
        # 更新任务进度
        if self.task_id:
            db.update_task_progress(self.task_id, step_order)
            print(f"📊 任务进度已更新: 步骤 {step_order}")
        
        print("🚗 开始AGV导航...")
        agv_done = await self.move_agv(name, stations) # 判断AGV是否到达
        print(f"🚗 AGV导航结果: {'成功' if agv_done else '失败'}")
        
        if agv_done:
            print("🦾 开始机械臂移动...")
            arm_done = await self.move_arm(pose)
            print(f"🦾 机械臂移动结果: {'成功' if arm_done else '失败'}")
            time.sleep(3)
            if arm_done:
                print("📸 开始拍照...")
                if HAS_REALSENSE:
                    print("📸 使用RealSense相机拍照")
                    rgb, depth, aligned_depth_frame = self.get_aligned_images()
                else:
                    print("📸 使用模拟相机拍照（无真实设备）")
                    # 模拟图片数据
                    rgb = np.zeros((480, 640, 3), dtype=np.uint8)
                    depth = np.zeros((480, 640), dtype=np.uint16)
                    aligned_depth_frame = None
                
                # 保存图片到本地
                timestamp = int(time.time())
                image_filename = f"{device_id}_{timestamp}.png"
                image_path = self.upload_dir / image_filename
                

                print(f"💾 保存图片: {image_filename}")
                if HAS_CV2:
                    cv2.imwrite(str(image_path), rgb)
                    print("💾 使用OpenCV保存图片")
                else:
                    # 使用PIL保存图片
                    from PIL import Image
                    pil_image = Image.fromarray(rgb)
                    pil_image.save(str(image_path))
                    print("💾 使用PIL保存图片")
                
                print(f"✅ 巡检任务 {name} 完成，图片已保存: {image_path}")
                
                # 创建设备巡检记录
                inspection_id = None
                if self.task_id:
                    inspection_id = db.create_device_inspection(
                        self.task_id, device_id, device_name, step_order, str(image_path)
                    )
                
                # 异步调用LLM分析
                if inspection_id:
                    self.executor.submit(self._analyze_image_async, inspection_id, str(image_path))
                
                time.sleep(1)
                await self.nod_head(2, 0.3)
                await self.move_arm([0.09501572285777778, -0.02441715581888889, 0.021694442232222225, 0.05136503901, 0.3852290659288889, 0.20415115912333331])
                self.llm_analyzer.forward(image_path)
                
                return True
        return False
    
    def _analyze_image_async(self, inspection_id: int, image_path: str):
        """异步分析图片"""
        try:
            print(f"开始LLM分析: {image_path}")
            result = self.llm_analyzer.analyze_image(image_path)
            
            if result:
                # 更新数据库
                db.update_device_inspection(inspection_id, json.dumps(result, ensure_ascii=False))
                print(f"LLM分析完成: {result}")
            else:
                print("LLM分析失败，未返回结果")
                db.update_device_inspection(inspection_id, json.dumps({"error": "未返回结果"}, ensure_ascii=False), "failed")
            
        except Exception as e:
            print(f"LLM分析失败: {e}")
            # 更新为失败状态，确保数据库操作不失败
            try:
                db.update_device_inspection(inspection_id, json.dumps({"error": str(e)}, ensure_ascii=False), "failed")
            except Exception as db_error:
                print(f"更新数据库失败: {db_error}")
                # 确保数据库操作失败不影响主流程
    
    # 机械臂点头
    async def nod_head(self, cycles: int = 2, amplitude: float = 0.2):
        """
        机械臂点头动作：让第5个关节上下摆动
        cycles: 摆动次数（一次 cycle = 上+下）
        amplitude: 摆动幅度 (弧度)
        """
        # if not hasattr(self, "arm_robot") or self.arm_robot is None:
        #     print("机械臂未连接")
        #     return False

        # 获取当前姿态
        if not hasattr(self, "arm_robot") or self.arm_robot is None:
            print("机械臂未连接，模拟点头动作")
            await asyncio.sleep(cycles * 2)  # 模拟点头时间
            return True
            
        base_pose = self.arm_robot.get_joint_positions()
        print("点头动作基准姿态:", base_pose)

        for i in range(cycles):
            # 向下点头
            pose_down = base_pose.copy()
            pose_down[4] += amplitude
            print(f"点头动作: 向下 {i+1}/{cycles}")
            await self.move_arm(pose_down)
            time.sleep(1)

            # 向上点头
            pose_up = base_pose.copy()
            pose_up[4] -= amplitude
            print(f"点头动作: 向上 {i+1}/{cycles}")
            await self.move_arm(pose_up)
            time.sleep(1)

        return True

    # 回到基站
    async def home(self) -> bool:
        print("🏠 准备回到起点（base）...")
        await self.move_arm([0.09501572285777778, -0.02441715581888889, 0.021694442232222225, 0.05136503901, 0.3852290659288889, 0.20415115912333331])
        time.sleep(3)
        return await self.move_agv("go_home", ["base"])

    # 拍照
    def get_aligned_images(self):
        if not HAS_REALSENSE or not self.pipeline:
            # 返回模拟数据
            depth_image = np.zeros((480, 640), dtype=np.uint16)
            color_image = np.zeros((480, 640, 3), dtype=np.uint8)
            return color_image, depth_image, None
        
        frames = self.pipeline.wait_for_frames()  #等待获取图像帧
        aligned_frames = self.align.process(frames)  #获取对齐帧
        aligned_depth_frame = aligned_frames.get_depth_frame()  #获取对齐帧中的depth帧
        color_frame = aligned_frames.get_color_frame()   #获取对齐帧中的color帧
    
        depth_image = np.asanyarray(aligned_depth_frame.get_data())  #深度图（默认16位）
        if HAS_CV2:
            depth_image_8bit = cv2.convertScaleAbs(depth_image, alpha=0.03)  #深度图（8位）
            depth_image_3d = np.dstack((depth_image_8bit,depth_image_8bit,depth_image_8bit))  #3通道深度图
        else:
            # 简单的深度图转换
            depth_image_8bit = (depth_image / 256).astype(np.uint8)
            depth_image_3d = np.dstack((depth_image_8bit,depth_image_8bit,depth_image_8bit))  #3通道深度图
        color_image = np.asanyarray(color_frame.get_data())  # RGB图
    
        #返回相机内参、深度参数、彩色图、深度图、齐帧中的depth帧
        return color_image, depth_image, aligned_depth_frame

async def main(task_id: int = None):
    robot = RobotController(task_id)
    
    # 设备配置
    devices = [
        {"id": "device_001", "name": "1号低温冰箱", "station": "A", "pose": [1.4667921316477777, 1.6030499840266665, -0.9177988247977777, 0.10089748233666666, -0.4209908616922222, 0.12166690008111111]},
        {"id": "device_002", "name": "2号低温冰箱", "station": "B", "pose": [1.4667921316477777, 1.6030499840266665, -0.9177988247977777, 0.10089748233666666, -0.4209908616922222, 0.12166690008111111]},
        {"id": "device_003", "name": "3号低温冰箱", "station": "C", "pose": [1.2758007548599999, 1.5664678835288888, -0.7937582769744445, -0.05255186288111111, -0.5448045167166666, 0.12166690008111111]},
        {"id": "device_004", "name": "1号液氮罐", "station": "C", "pose": [-1.1388447707922222, 2.2647042921711114, -2.0471664579133333, -0.10725048070555554, -0.17011723929, 0.2844363033455556]}
    ]

    robot.start_navigation("213_0903")
    
    # 顺序执行巡检任务
    for i, device in enumerate(devices, 1):
        print(f"开始巡检设备 {i}: {device['name']}")
        done = await robot.inspection(
            f"pic_{i}", 
            [device["station"]], 
            device["pose"],
            device["id"],
            device["name"],
            i
        )
        if not done:
            print(f"设备 {device['name']} 巡检失败")
            break
    
    # 第5个任务：返回基站
    print("开始第5个任务：返回基站")
    if task_id:
        db.update_task_progress(task_id, 5)  # 更新为第5步
    
    home_done = await robot.home()
    if home_done:
        print("所有任务完成，返回基站")
        if task_id:
            db.update_task_progress(task_id, 5, "completed")
    
    # 关闭线程池
    robot.executor.shutdown(wait=True)
    
    # 预设坐标
    # robot.move_arm([0.09501572285777778, -0.02441715581888889, 0.021694442232222225, 0.05136503901, 0.3852290659288889, 0.20415115912333331])
    # [-0.4562290586888889, 1.9841775262833334, -1.8750944498944444, 0.23317598408888887, 0.29859092333777776, 0.003787364412222222]
    # [1.5217700021477778, 2.2294835484666664, -1.7336704230177777, -0.006143558862222222, -0.3592585671022222, 0.08325220389999999]
    # [1.6687092693666665, 2.2290646694533334, -1.2059177728022221, 0.024312436065555554, -0.96509724672, 0.08218755307444443]
    # [-1.3783912065422221, 1.8811681955877777, -1.7552601454966668, 0.12294099041333333, 0.14165091967555554, 0.08402014875777777]
if __name__ == "__main__":
    asyncio.run(main())