from pynput.mouse import Listener, Controller
import win32api
import win32con
import win32gui
import threading
import logging

class MouseController:
    """
    鼠标控制器类
    用于实现鼠标的禁用和启用功能，通过Windows钩子实现系统级的鼠标控制
    """
    def __init__(self):
        self.mouse = Controller()  # pynput的鼠标控制器
        self.original_pos = (0, 0)  # 存储鼠标初始位置
        self.disabled = False  # 鼠标禁用状态标志
        self.hook = None  # Windows鼠标钩子句柄
        self._setup_logging()  # 初始化日志系统
    
    def _setup_logging(self):
        """配置日志系统"""
        logging.basicConfig(
            filename='mouse_control.log',
            level=logging.INFO,
            format='%(asctime)s: %(message)s'
        )
    
    def disable(self):
        """
        禁用鼠标功能
        通过设置系统钩子来捕获并阻止鼠标事件
        """
        if not self.disabled:
            self.disabled = True
            # 记录当前鼠标位置，用于固定鼠标
            self.original_pos = win32gui.GetCursorPos()
            self._start_hook()  # 启动鼠标钩子
            logging.info("鼠标已禁用")
    
    def enable(self):
        """
        启用鼠标功能
        移除系统钩子，恢复鼠标正常功能
        """
        if self.disabled:
            self.disabled = False
            # 移除系统钩子
            if self.hook:
                win32api.UnhookWindowsHookEx(self.hook)
                self.hook = None
            logging.info("鼠标已启用")
    
    def _mouse_hook_proc(self, nCode, wParam, lParam):
        """
        鼠标钩子回调函数
        处理所有鼠标事件，在禁用状态下阻止事件传递
        
        Args:
            nCode: 钩子代码
            wParam: 鼠标消息类型
            lParam: 鼠标事件详细信息
        """
        if self.disabled:
            # 将鼠标位置重置到初始位置
            win32api.SetCursorPos(self.original_pos[0], self.original_pos[1])
            return 1  # 返回1表示阻止事件继续传递
        # 允许事件继续传递
        return win32api.CallNextHookEx(self.hook, nCode, wParam, lParam)
    
    def _start_hook(self):
        """
        启动系统级鼠标钩子
        设置底层鼠标钩子来捕获所有鼠标事件
        """
        if not self.hook:
            # 设置全局鼠标钩子
            self.hook = win32api.SetWindowsHookEx(
                win32con.WH_MOUSE_LL,  # 底层鼠标钩子
                self._mouse_hook_proc,  # 回调函数
                None,  # 应用程序实例句柄
                0  # 全局钩子
            )

# 创建全局鼠标控制器实例，供其他模块使用
mouse_controller = MouseController() 