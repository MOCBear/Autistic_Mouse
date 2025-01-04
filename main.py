import threading
import logging
from mouse_recorder import start_recording
from session_manager import start_session
from mouse_controller import mouse_controller

def main():
    """主程序入口"""
    try:
        # 启动记录器线程
        recorder_thread = threading.Thread(target=start_recording)
        recorder_thread.daemon = True
        recorder_thread.start()
        
        # 启动会话管理
        start_session()
        
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