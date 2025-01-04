"""
程序统一启动入口
处理管理员权限提升并启动主程序
"""

import sys
import os
import win32api
import win32con
import win32security
import win32event
import winerror
import logging
from datetime import datetime
import ctypes

# 定义互斥体名称（使用唯一的名称）
MUTEX_NAME = "Global\\MouseRecorderSingleInstance"

class SingleInstanceException(Exception):
    """单实例异常"""
    pass

def setup_logging():
    """配置日志系统"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_file = os.path.join('logs', f'startup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s: %(message)s'
    )

def ensure_single_instance():
    """
    确保程序只运行一个实例
    返回互斥体句柄，如果已有实例运行则抛出异常
    """
    try:
        # 尝试创建互斥体
        handle = win32event.CreateMutex(None, 1, MUTEX_NAME)
        if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
            # 如果互斥体已存在，关闭句柄并抛出异常
            if handle:
                win32api.CloseHandle(handle)
            raise SingleInstanceException("程序已经在运行中")
        return handle
    except Exception as e:
        logging.error(f"检查程序实例时发生错误: {str(e)}")
        raise

def cleanup_mutex(handle):
    """清理互斥体"""
    try:
        if handle:
            win32api.CloseHandle(handle)
    except Exception as e:
        logging.error(f"清理互斥体时发生错误: {str(e)}")

def is_admin():
    """
    检查当前进程是否具有管理员权限
    使用多种方法进行检查以确保准确性
    """
    try:
        # 方法1：使用 ctypes 检查
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            pass
        
        # 方法2：使用 win32security 检查
        try:
            return win32security.IsUserAnAdmin()
        except:
            pass
        
        # 方法3：尝试访问一个需要管理员权限的操作
        try:
            temp = os.listdir(os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp'))
            return True
        except:
            pass
        
        return False
        
    except Exception as e:
        logging.error(f"权限检查时发生错误: {str(e)}")
        return False

def request_admin_privileges():
    """
    请求管理员权限
    返回是否成功获取权限
    """
    try:
        logging.info("正在请求管理员权限...")
        
        # 获取当前脚本的完整路径
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in sys.argv[1:]])
        
        # 使用 ShellExecute 重新以管理员权限运行
        ret = win32api.ShellExecute(
            None,  # 父窗口句柄
            "runas",  # 请求管理员权限
            sys.executable,  # Python解释器路径
            f'"{script}" {params}',  # 脚本和参数
            None,  # 工作目录
            win32con.SW_SHOWNORMAL  # 正常显示窗口
        )
        
        if ret <= 32:  # ShellExecute 返回值小于等于32表示失败
            raise RuntimeError(f'权限提升失败（错误码：{ret}）')
        
        return True
        
    except Exception as e:
        logging.error(f"请求管理员权限时发生错误: {str(e)}")
        print(f"错误: {str(e)}")
        return False

def ensure_admin_privileges():
    """
    确保程序运行在管理员权限下
    返回是否应该继续执行程序
    """
    # 首先检查当前权限
    if is_admin():
        logging.info("当前已具有管理员权限")
        return True
    
    logging.info("当前不具有管理员权限，尝试提升...")
    print("需要管理员权限才能运行此程序...")
    
    # 请求提升权限
    if request_admin_privileges():
        logging.info("权限提升请求已发送")
        return False  # 返回 False 表示当前实例应该退出
    else:
        logging.error("无法获取管理员权限")
        print("错误：无法获取管理员权限，程序将退出")
        return False

def start_application():
    """启动主应用程序"""
    try:
        # 导入主程序模块
        from main import main
        logging.info("正在启动主程序...")
        main()
        
    except Exception as e:
        logging.error(f"启动主程序时发生错误: {str(e)}")
        print(f"启动失败: {str(e)}")
        sys.exit(1)

def main():
    """主函数"""
    mutex_handle = None
    try:
        # 设置日志
        setup_logging()
        logging.info("程序启动...")
        
        # 确保单实例运行
        try:
            mutex_handle = ensure_single_instance()
            logging.info("单实例检查通过")
        except SingleInstanceException as e:
            logging.warning(f"程序已在运行: {str(e)}")
            print("错误：程序已经在运行中")
            sys.exit(0)
        
        # 检查并确保管理员权限
        if not ensure_admin_privileges():
            logging.info("等待权限提升或程序退出...")
            sys.exit(0)
        
        # 启动主程序
        start_application()
        
    except Exception as e:
        logging.error(f"程序运行时发生错误: {str(e)}")
        print(f"程序错误: {str(e)}")
        sys.exit(1)
    finally:
        # 清理互斥体
        if mutex_handle:
            cleanup_mutex(mutex_handle)

if __name__ == "__main__":
    main() 