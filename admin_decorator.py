import sys
from ctypes import windll
import os
import platform

def requireAdministrator(f):
    """
    管理员权限装饰器
    确保被装饰的函数在管理员权限下运行
    
    Args:
        f: 需要以管理员权限运行的函数
    """
    def inner(*args, **kwargs):
        # 检查是否为 Windows 系统
        if platform.system() != 'Windows':
            print("错误：此功能仅支持 Windows 系统")
            sys.exit(1)
            
        try:
            if windll.shell32.IsUserAnAdmin():
                # 如果已经是管理员权限，直接执行函数
                return f(*args, **kwargs)
            else:
                # 获取当前脚本的完整路径
                script = os.path.abspath(sys.argv[0])
                # 处理命令行参数，确保包含空格的参数正确引用
                params = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in sys.argv[1:]])
                
                # 使用 ShellExecuteW 重新以管理员权限运行
                ret = windll.shell32.ShellExecuteW(
                    None,  # 父窗口句柄
                    "runas",  # 请求管理员权限
                    sys.executable,  # Python解释器路径
                    f'"{script}" {params}',  # 脚本和参数
                    None,  # 工作目录
                    1  # 正常显示窗口
                )
                
                if ret <= 32:  # ShellExecute 返回值小于等于32表示失败
                    raise RuntimeError('权限提升失败（错误码：{ret}）')
                
                sys.exit(0)  # 退出当前进程
                
        except Exception as e:
            print(f"获取管理员权限时发生错误: {str(e)}")
            sys.exit(1)
            
    return inner 