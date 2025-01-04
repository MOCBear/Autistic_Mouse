from pynput.mouse import Listener, Button
import logging
import os
import time
import platform
import sys
import matplotlib.pyplot as plt
import numpy as np

# 检查操作系统
if platform.system() != 'Windows':
    print("错误：此功能仅支持 Windows 系统")
    sys.exit(1)

# 确保日志目录存在
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
logging.basicConfig(
    filename=os.path.join(log_dir, 'mouse_events.log'),
    level=logging.INFO,
    format='%(asctime)s: %(message)s'
)

class MouseTracker:
    def __init__(self):
        self.points = []  # 存储鼠标轨迹点
        self.timestamps = []  # 存储时间戳
        self.recording = True
        
    def add_point(self, x, y):
        """添加轨迹点"""
        try:
            self.points.append((x, y))
            self.timestamps.append(time.time())
        except Exception as e:
            logging.error(f"添加轨迹点时发生错误: {str(e)}")
    
    def save_trajectory(self, filename='mouse_trajectory.txt'):
        """保存轨迹到文件"""
        if not self.points:
            logging.warning("没有轨迹点可供保存")
            return
        
        try:
            filepath = os.path.join(log_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("时间戳,X坐标,Y坐标\n")
                for t, (x, y) in zip(self.timestamps, self.points):
                    f.write(f"{t},{x},{y}\n")
            logging.info(f"轨迹已保存到: {filepath}")
        except Exception as e:
            logging.error(f"保存轨迹时发生错误: {str(e)}")
    
    def plot_trajectory(self, save_plot=True):
        """可视化鼠标轨迹"""
        if not self.points:
            logging.warning("没有轨迹点可供绘制")
            return
            
        try:
            points = np.array(self.points)
            plt.figure(figsize=(10, 8))
            
            # 绘制轨迹线
            plt.plot(points[:, 0], points[:, 1], 'b-', alpha=0.5, label='移动轨迹')
            
            # 标记起点和终点
            plt.plot(points[0, 0], points[0, 1], 'go', label='起点')
            plt.plot(points[-1, 0], points[-1, 1], 'ro', label='终点')
            
            plt.title('鼠标移动轨迹图')
            plt.xlabel('X坐标')
            plt.ylabel('Y坐标')
            plt.legend()
            plt.grid(True)
            
            if save_plot:
                plot_path = os.path.join(log_dir, 'mouse_trajectory.png')
                plt.savefig(plot_path)
                logging.info(f"轨迹图已保存到: {plot_path}")
            plt.close()
        except Exception as e:
            logging.error(f"绘制轨迹图时发生错误: {str(e)}")

# 创建全局追踪器实例
tracker = MouseTracker()

def on_move(x, y):
    """处理鼠标移动事件"""
    try:
        if tracker.recording:
            tracker.add_point(x, y)
        logging.info(f'鼠标移动到 {(x, y)}')
    except Exception as e:
        logging.error(f"处理鼠标移动事件时发生错误: {str(e)}")

def on_click(x, y, button, pressed):
    """处理鼠标点击事件"""
    try:
        action = '按下' if pressed else '释放'
        button_name = '左键' if button == Button.left else '右键' if button == Button.right else '中键'
        logging.info(f'鼠标{action} {button_name} 在位置 {(x, y)}')
        
        if button == Button.right and pressed:
            logging.info('检测到右键点击，停止记录')
            tracker.recording = False
            tracker.save_trajectory()
            tracker.plot_trajectory()
            return False
        
        return True
    except Exception as e:
        logging.error(f"处理鼠标点击事件时发生错误: {str(e)}")
        return False

def on_scroll(x, y, dx, dy):
    """处理鼠标滚轮事件"""
    try:
        scroll_direction = '向上' if dy > 0 else '向下'
        logging.info(f'鼠标在位置 {(x, y)} {scroll_direction}滚动')
    except Exception as e:
        logging.error(f"处理鼠标滚轮事件时发生错误: {str(e)}")

def start_mouse_listener():
    """启动鼠标监听"""
    try:
        print(f"开始记录鼠标轨迹... (右键点击停止并保存)")
        print(f"日志和轨迹文件将保存在: {os.path.abspath(log_dir)}")
        
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
        # 确保数据被保存
        if tracker.points:
            tracker.save_trajectory()
            tracker.plot_trajectory()

if __name__ == "__main__":
    start_mouse_listener() 