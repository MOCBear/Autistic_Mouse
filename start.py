"""
程序统一启动入口
处理管理员权限提升并启动主程序
"""

import sys
import os
import win32api
import win32con
import win32security
import logging
from datetime import datetime

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

def is_admin():
    """检查当前是否具有管理员权限"""
    try:
        return win32security.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新运行程序"""
    try:
        if not is_admin():
            logging.info("正在请求管理员权限...")
            # 获取当前脚本的完整路径
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in sys.argv[1:]])
            
            # 使用 ShellExecuteW 重新以管理员权限运行
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
            
            return False  # 表示需要退出当前实例
        
        return True  # 表示已经具有管理员权限
        
    except Exception as e:
        logging.error(f"权限提升过程中发生错误: {str(e)}")
        print(f"错误: {str(e)}")
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
    try:
        # 设置日志
        setup_logging()
        logging.info("程序启动...")
        
        # 检查并提升权限
        if not run_as_admin():
            logging.info("等待权限提升...")
            sys.exit(0)
        
        logging.info("已获取管理员权限")
        
        # 启动主程序
        start_application()
        
    except Exception as e:
        logging.error(f"程序运行时发生错误: {str(e)}")
        print(f"程序错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 