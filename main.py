"""
主程序模块
负责启动鼠标记录和控制功能
"""

import threading
import logging
import time
from mouse_recorder import start_recording
from mouse_controller import mouse_controller

def main():
    """主程序入口"""
    try:
        logging.info("等待智造协同平台初始化完成...")
        time.sleep(2)  # 给智造协同平台一些初始化时间
        
        logging.info("开始启动鼠标记录功能...")
        # 启动记录器线程
        recorder_thread = threading.Thread(target=start_recording)
        recorder_thread.daemon = True
        recorder_thread.start()
        
        # 等待记录器线程结束
        recorder_thread.join()
        
    except Exception as e:
        logging.error(f"程序运行错误: {str(e)}")
        print(f"程序运行错误: {str(e)}")
    finally:
        # 确保鼠标被禁用
        mouse_controller.disable()

if __name__ == "__main__":
    print("请使用 start.py 启动程序") 