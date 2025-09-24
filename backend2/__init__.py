"""
InspectionRobot模块
包含机器人控制和AI分析功能
"""

__version__ = "1.0.0"
__author__ = "巡检监控系统"

# 导入主要类
try:
    from .RobotController import RobotController
    from .RobotControllerMock import RobotControllerMock
    from .ErrorMonitorwithLLM import ErrorMonitor
except ImportError as e:
    print(f"警告: 部分模块导入失败: {e}")
    # 设置默认值以避免导入错误
    RobotController = None
    RobotControllerMock = None
    ErrorMonitor = None

__all__ = ['RobotController', 'RobotControllerMock', 'ErrorMonitor']
