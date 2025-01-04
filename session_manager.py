import os
import subprocess
import win32api
import win32con
import win32security
import time
from mouse_recorder import update_recording_info
from mouse_controller import mouse_controller

def get_current_username():
    """获取当前登录用户名"""
    try:
        token = win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_QUERY)
        user = win32security.GetTokenInformation(token, win32security.TokenUser)
        username = win32security.LookupAccountSid(None, user[0])[0]
        return username
    except Exception as e:
        print(f"获取用户名时发生错误: {str(e)}")
        return None

def logout_windows():
    """退出Windows登录"""
    try:
        # 先禁用鼠标
        mouse_controller.disable()
        os.system('shutdown -l')
    except Exception as e:
        print(f"退出登录时发生错误: {str(e)}")

def handle_login():
    """处理用户登录"""
    username = get_current_username()
    if username:
        # 启用鼠标
        mouse_controller.enable()
        update_recording_info(username)
        print(f"用户 {username} 已登录")
    return username

def start_session():
    """启动会话管理"""
    # 初始状态禁用鼠标
    mouse_controller.disable()
    
    # 等待用户登录
    while True:
        username = handle_login()
        if username:
            break
        time.sleep(1) 