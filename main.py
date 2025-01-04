import threading
from mouse_recorder import start_recording
from session_manager import start_session
from mouse_controller import mouse_controller
import win32gui
import win32con
import win32api
import win32security
import sys
import logging

def main():
    try:
        # 确保程序以管理员权限运行
        if not win32security.IsUserAnAdmin():
            # 重新以管理员权限启动
            win32api.ShellExecute(
                None, 
                "runas",
                sys.executable,
                __file__,
                None,
                win32con.SW_SHOWNORMAL
            )
            return
        
        # 启动记录器线程
        recorder_thread = threading.Thread(target=start_recording)
        recorder_thread.daemon = True
        recorder_thread.start()
        
        # 启动会话管理
        start_session()
        
        # 等待记录器线程结束
        recorder_thread.join()
        
    except Exception as e:
        print(f"程序运行错误: {str(e)}")
        logging.error(f"程序运行错误: {str(e)}")
    finally:
        # 确保鼠标被禁用
        mouse_controller.disable()

if __name__ == "__main__":
    main() 