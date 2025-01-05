"""
智造协同平台自动化启动模块
实现自动查找、启动和操作智造协同平台
"""

import os
import subprocess
import time
import pyautogui
import pygetwindow as gw
import logging
from typing import Optional

class EasyFASLauncher:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.path_file = os.path.join(self.script_dir, 'path.txt')
        self._setup_logging()
        
        # 禁用 pyautogui 的安全特性
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1
    
    def _setup_logging(self):
        """配置日志"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        log_file = os.path.join('logs', 'easyfas_launcher.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s: %(message)s'
        )
    
    def find_program_path(self) -> Optional[str]:
        """查找程序路径"""
        # 首先检查特定路径
        special_path = r"C:\Program Files (x86)\智造协同平台\Microsoft.ApplicationBlocks.AppStart.exe"
        if os.path.exists(special_path):
            logging.info(f"在特定路径找到程序: {special_path}")
            return special_path
        
        # 检查缓存路径
        if os.path.exists(self.path_file):
            with open(self.path_file, 'r', encoding='utf-8') as f:
                cached_path = f.read().strip()
                if os.path.exists(cached_path):
                    logging.info(f"使用缓存路径: {cached_path}")
                    return cached_path
                else:
                    os.remove(self.path_file)
                    logging.warning(f"缓存路径无效: {cached_path}")
        
        # 搜索驱动器
        target_file = 'EasyFAS.Shell.exe'
        for drive in ['C:\\', 'D:\\', 'E:\\']:
            try:
                for root, _, files in os.walk(drive):
                    if target_file in files:
                        file_path = os.path.join(root, target_file)
                        with open(self.path_file, 'w', encoding='utf-8') as f:
                            f.write(file_path)
                        logging.info(f"找到程序路径: {file_path}")
                        return file_path
            except Exception as e:
                logging.error(f"搜索驱动器 {drive} 时出错: {str(e)}")
        
        logging.error("未找到程序路径")
        return None
    
    def launch_program(self, file_path: str) -> bool:
        """启动程序"""
        try:
            subprocess.Popen([file_path, 'factory'])
            logging.info("程序启动成功")
            time.sleep(2)  # 等待程序启动
            return True
        except Exception as e:
            logging.error(f"启动程序失败: {str(e)}")
            return False
    
    def handle_windows(self) -> bool:
        """处理窗口操作"""
        try:
            # 模拟回车键
            pyautogui.press('enter')
            time.sleep(1)
            
            # 查找主窗口
            main_window = self._find_window('智造协同平台-车间扫描')
            if not main_window:
                return False
            
            # 点击指定位置
            self._click_relative_position(main_window, 2/3, 1/4)
            time.sleep(2)
            
            # 处理提示窗口
            prompt_window = self._find_window('提示')
            if prompt_window:
                self._click_window_center(prompt_window)
            
            logging.info("窗口操作完成")
            return True
            
        except Exception as e:
            logging.error(f"窗口操作失败: {str(e)}")
            return False
    
    def _find_window(self, title: str) -> Optional[gw.Window]:
        """查找窗口"""
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                window = windows[0]
                window.activate()
                time.sleep(0.5)
                return window
            logging.warning(f"未找到窗口: {title}")
            return None
        except Exception as e:
            logging.error(f"查找窗口失败: {str(e)}")
            return None
    
    def _click_relative_position(self, window: gw.Window, x_ratio: float, y_ratio: float):
        """点击窗口相对位置"""
        x = window.left + int(window.width * x_ratio)
        y = window.top + int(window.height * y_ratio)
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()
    
    def _click_window_center(self, window: gw.Window):
        """点击窗口中心"""
        x = window.left + window.width // 2
        y = window.top + window.height // 2
        pyautogui.moveTo(x, y, duration=0.5)
        pyautogui.click()

def find_easyfas_shell() -> bool:
    """查找并启动智造协同平台"""
    launcher = EasyFASLauncher()
    
    # 查找程序路径
    file_path = launcher.find_program_path()
    if not file_path:
        logging.error("未找到智造协同平台程序")
        return False
    
    # 启动程序
    if not launcher.launch_program(file_path):
        logging.error("启动智造协同平台失败")
        return False
    
    # 处理窗口操作
    if not launcher.handle_windows():
        logging.error("智造协同平台窗口操作失败")
        return False
    
    logging.info("智造协同平台启动成功")
    return True

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    find_easyfas_shell()