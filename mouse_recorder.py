"""
鼠标操作记录器模块
实现鼠标轨迹和事件的记录、可视化和保存功能
包含悬浮窗提示和用户会话管理
"""

from pynput.mouse import Listener, Button
import logging
import os
import time
import platform
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import tkinter as tk
import threading
import win32gui
import win32con
from mouse_controller import mouse_controller
from mouse_mirror import mouse_mirror

class FloatingWindow:
    """
    悬浮窗口类
    在屏幕左下角显示提示信息的置顶窗口
    """
    def __init__(self):
        self.root = tk.Tk()  # 创建主窗口
        self.root.overrideredirect(True)  # 无边框模式
        self.root.attributes('-topmost', True)  # 窗口置顶
        self.root.configure(bg='yellow')  # 设置背景色
        
        # 计算窗口位置（左下角）
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 200
        window_height = 50
        x = 10
        y = screen_height - window_height - 40
        
        # 设置窗口属性
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        self.label = tk.Label(
            self.root,
            text="操作结束后请右键点击\n以保存记录并退出",
            bg='yellow',
            fg='red',
            font=('Arial', 10, 'bold')
        )
        self.label.pack(expand=True)
        
        # 窗口透明度设置
        self.root.attributes('-alpha', 0.8)
        
        # 设置为工具窗口（不在任务栏显示）
        hwnd = win32gui.GetParent(self.root.winfo_id())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        style = style | win32con.WS_EX_TOOLWINDOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)

class MouseRecorder:
    """
    鼠标记录器类
    记录鼠标移动轨迹和事件，支持数据保存和可视化
    """
    def __init__(self):
        # 初始化存储目录
        self.log_dir = 'mouse_records'
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 使用临时ID初始化记录
        self.record_id = 'temp_' + datetime.now().strftime('%Y%m%d_%H%M%S')
        self.username = None
        
        self._setup_logging()  # 配置日志系统
        
        # 初始化数据存储
        self.points = []  # 存储坐标点
        self.timestamps = []  # 存储时间戳
        self.events = []  # 存储事件信息
        self.recording = True  # 记录状态标志
        
        self.floating_window = None  # 悬浮窗实例
        
        # 启动镜像记录
        mouse_mirror.start_mirror()
    
    def _setup_logging(self):
        """设置日志"""
        log_file = os.path.join(self.log_dir, f'record_{self.record_id}.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s: %(message)s'
        )
    
    def update_user_info(self, username):
        """更新用户信息并重命名文件"""
        self.username = username
        new_record_id = f'{username}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        
        # 重命名现有文件
        old_log = os.path.join(self.log_dir, f'record_{self.record_id}.log')
        new_log = os.path.join(self.log_dir, f'record_{new_record_id}.log')
        
        if os.path.exists(old_log):
            os.rename(old_log, new_log)
        
        self.record_id = new_record_id
        logging.info(f"记录ID更新为: {self.record_id}")
        
        # 显示浮窗
        self.show_floating_window()
    
    def show_floating_window(self):
        """显示浮窗"""
        def create_window():
            self.floating_window = FloatingWindow()
            self.floating_window.root.mainloop()
        
        # 在新线程中创建浮窗
        threading.Thread(target=create_window, daemon=True).start()

    def add_point(self, x, y, event_type='move', **kwargs):
        """添加轨迹点和事件"""
        try:
            timestamp = time.time()
            self.points.append((x, y))
            self.timestamps.append(timestamp)
            self.events.append({
                'type': event_type,
                'position': (x, y),
                'timestamp': timestamp,
                'params': kwargs
            })
            
            # 添加到镜像记录
            mouse_mirror.add_event(event_type, x, y, **kwargs)
            
        except Exception as e:
            logging.error(f"添加轨迹点时发生错误: {str(e)}")
    
    def save_recording(self):
        """保存记录数据"""
        if not self.events:
            logging.warning("没有记录数据可供保存")
            return
        
        try:
            # 保存事件数据
            data_file = os.path.join(self.log_dir, f'record_{self.record_id}.json')
            import json
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'events': self.events,
                    'record_id': self.record_id,
                    'username': self.username,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            # 绘制并保存轨迹图
            self._save_trajectory_plot()
            
            logging.info(f"记录数据已保存到: {data_file}")
            
            # 关闭浮窗
            if self.floating_window:
                self.floating_window.root.destroy()
            
            # 禁用鼠标并退出登录
            mouse_controller.disable()
            from session_manager import logout_windows
            logout_windows()
            
            # 保存镜像数据
            if self.username:
                mouse_mirror.save_mirror(self.username)
            
            return data_file
            
        except Exception as e:
            logging.error(f"保存记录数据时发生错误: {str(e)}")
    
    def _save_trajectory_plot(self):
        """保存轨迹图"""
        if not self.points:
            return
            
        try:
            points = np.array(self.points)
            plt.figure(figsize=(10, 8))
            
            # 绘制轨迹线
            plt.plot(points[:, 0], points[:, 1], 'b-', alpha=0.5, label='移动轨迹')
            
            # 标记起点和终点
            plt.plot(points[0, 0], points[0, 1], 'go', label='起点')
            plt.plot(points[-1, 0], points[-1, 1], 'ro', label='终点')
            
            plt.title(f'鼠标移动轨迹图 - {self.record_id}')
            plt.xlabel('X坐标')
            plt.ylabel('Y坐标')
            plt.legend()
            plt.grid(True)
            
            plot_path = os.path.join(self.log_dir, f'record_{self.record_id}.png')
            plt.savefig(plot_path)
            plt.close()
            
            logging.info(f"轨迹图已保存到: {plot_path}")
        except Exception as e:
            logging.error(f"保存轨迹图时发生错误: {str(e)}")

def start_recording():
    """开始记录鼠标轨迹"""
    recorder = MouseRecorder()
    
    def on_move(x, y):
        try:
            if recorder.recording:
                recorder.add_point(x, y, 'move')
            logging.info(f'鼠标移动到 {(x, y)}')
        except Exception as e:
            logging.error(f"处理鼠标移动事件时发生错误: {str(e)}")

    def on_click(x, y, button, pressed):
        try:
            action = 'press' if pressed else 'release'
            event_type = f'click_{action}'
            if recorder.recording:
                recorder.add_point(x, y, event_type)
            
            button_name = '左键' if button == Button.left else '右键' if button == Button.right else '中键'
            logging.info(f'鼠标{action} {button_name} 在位置 {(x, y)}')
            
            if button == Button.right and pressed:
                logging.info('检测到右键点击，停止记录')
                recorder.recording = False
                recorder.save_recording()
                # 这里可以添加退出登录的代码
                return False
            
            return True
        except Exception as e:
            logging.error(f"处理鼠标点击事件时发生错误: {str(e)}")
            return False

    def on_scroll(x, y, dx, dy):
        try:
            event_type = 'scroll_up' if dy > 0 else 'scroll_down'
            if recorder.recording:
                recorder.add_point(x, y, event_type)
            logging.info(f'鼠标在位置 {(x, y)} {"向上" if dy > 0 else "向下"}滚动')
        except Exception as e:
            logging.error(f"处理鼠标滚轮事件时发生错误: {str(e)}")

    try:
        print(f"开始记录鼠标轨迹... (右键点击停止并保存)")
        print(f"记录文件将保存在: {os.path.abspath(recorder.log_dir)}")
        
        with Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll
        ) as listener:
            listener.join()
            
    except Exception as e:
        logging.error(f"监听器发生错误: {str(e)}")
        print(f"监听器发生错误: {str(e)}")
    finally:
        if recorder.events:
            recorder.save_recording()

def update_recording_info(username):
    """更新记录信息（供外部调用）"""
    global current_recorder
    if current_recorder:
        current_recorder.update_user_info(username)

# 全局记录器实例
current_recorder = None

if __name__ == "__main__":
    # 测试代码
    current_recorder = MouseRecorder()
    current_recorder.update_user_info("test_user")
    start_recording() 