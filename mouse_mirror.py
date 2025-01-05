"""
鼠标轨迹镜像模块
实现鼠标操作的实时镜像和回放功能，支持数据压缩
"""

from pynput.mouse import Controller
import win32api
import win32con
import logging
import time
import json
import os
import gzip
import base64
from datetime import datetime
from typing import Dict, List, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from auth_manager import auth_manager

class MouseMirror:
    """鼠标镜像控制器"""
    def __init__(self):
        self.mouse = Controller()
        self.recording = False
        self.mirror_events: List[Dict[str, Any]] = []
        self.compression_level = 9  # 最高压缩级别
        self.encryption_enabled = False  # 加密开关
        self.encryption_level = 1  # 加密强度 (1-3)
        self._setup_logging()
    
    def _setup_logging(self):
        """配置日志"""
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        log_file = os.path.join('logs', 'mouse_mirror.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s: %(message)s'
        )
    
    def _compress_data(self, data: str) -> bytes:
        """
        压缩数据
        
        Args:
            data: 要压缩的JSON字符串
        
        Returns:
            压缩后的字节数据
        """
        try:
            # 将数据转换为字节并压缩
            return gzip.compress(
                data.encode('utf-8'),
                compresslevel=self.compression_level
            )
        except Exception as e:
            logging.error(f"数据压缩失败: {str(e)}")
            raise
    
    def _decompress_data(self, compressed_data: bytes) -> str:
        """
        解压数据
        
        Args:
            compressed_data: 压缩的字节数据
        
        Returns:
            解压后的JSON字符串
        """
        try:
            # 解压数据并转换为字符串
            return gzip.decompress(compressed_data).decode('utf-8')
        except Exception as e:
            logging.error(f"数据解压失败: {str(e)}")
            raise
    
    def _optimize_events(self) -> List[Dict[str, Any]]:
        """
        优化事件数据，减少冗余
        
        Returns:
            优化后的事件列表
        """
        if not self.mirror_events:
            return []
            
        optimized = []
        last_event = None
        
        for event in self.mirror_events:
            # 对于移动事件，只保留关键点
            if event['type'] == 'move':
                if not last_event or \
                   last_event['type'] != 'move' or \
                   abs(event['position'][0] - last_event['position'][0]) > 5 or \
                   abs(event['position'][1] - last_event['position'][1]) > 5:
                    optimized.append(event)
                    last_event = event
            else:
                # 非移动事件全部保留
                optimized.append(event)
                last_event = event
        
        return optimized
    
    def _generate_key(self, password: str, level: int) -> bytes:
        """
        根据密码和加密等级生成密钥
        
        Args:
            password: 加密密码
            level: 加密强度(1-3)
        """
        # 根据加密等级设置不同的迭代次数
        iterations = {
            1: 100000,    # 基础加密
            2: 200000,    # 中等加密
            3: 400000     # 高强度加密
        }.get(level, 100000)
        
        salt = b'mouse_recorder_salt'  # 固定盐值
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _encrypt_data(self, data: bytes, password: str) -> bytes:
        """加密数据"""
        if not self.encryption_enabled:
            return data
            
        try:
            key = self._generate_key(password, self.encryption_level)
            f = Fernet(key)
            return f.encrypt(data)
        except Exception as e:
            logging.error(f"数据加密失败: {str(e)}")
            raise
    
    def _decrypt_data(self, encrypted_data: bytes, password: str) -> bytes:
        """解密数据"""
        try:
            key = self._generate_key(password, self.encryption_level)
            f = Fernet(key)
            return f.decrypt(encrypted_data)
        except Exception as e:
            logging.error(f"数据解密失败: {str(e)}")
            raise
    
    def save_mirror(self, username: str, password: str = None) -> str:
        """保存压缩和加密的镜像记录"""
        try:
            if not self.mirror_events:
                logging.warning("没有镜像数据可供保存")
                return None
            
            # 创建镜像文件夹
            mirror_dir = 'mouse_mirrors'
            if not os.path.exists(mirror_dir):
                os.makedirs(mirror_dir)
            
            # 优化事件数据
            optimized_events = self._optimize_events()
            
            # 准备数据
            data = {
                'username': username,
                'timestamp': datetime.now().isoformat(),
                'duration': time.time() - self.start_time,
                'events': optimized_events,
                'event_count': len(optimized_events)
            }
            
            # 压缩数据
            json_str = json.dumps(data, ensure_ascii=False)
            compressed_data = self._compress_data(json_str)
            
            # 如果启用加密，验证用户权限
            if self.encryption_enabled:
                if not password or not auth_manager.verify_encryption_user(username, password):
                    logging.error("无效的加密账号")
                    return None
                
                # 生成文件ID并存储密钥
                file_id = f"{username}_{timestamp}"
                auth_manager.store_encryption_key(username, file_id, password)
            
            # 如果启用加密，则加密数据
            if self.encryption_enabled and password:
                compressed_data = self._encrypt_data(compressed_data, password)
            
            # 生成文件名（加密文件使用不同扩展名）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            ext = '.enc.gz' if self.encryption_enabled else '.gz'
            filename = f'mirror_{username}_{timestamp}{ext}'
            filepath = os.path.join(mirror_dir, filename)
            
            # 保存压缩数据
            with open(filepath, 'wb') as f:
                f.write(compressed_data)
            
            # 记录压缩信息
            original_size = len(json_str.encode('utf-8'))
            compressed_size = len(compressed_data)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            logging.info(
                f"镜像数据已保存: {filepath}\n"
                f"事件数: {len(optimized_events)}\n"
                f"原始大小: {original_size/1024:.2f}KB\n"
                f"压缩大小: {compressed_size/1024:.2f}KB\n"
                f"压缩率: {compression_ratio:.1f}%"
            )
            
            return filepath
            
        except Exception as e:
            logging.error(f"保存镜像数据时发生错误: {str(e)}")
            return None
    
    def play_mirror(self, filepath: str, username: str, password: str = None) -> None:
        """回放加密的镜像记录"""
        try:
            # 如果是加密文件，检查权限
            if filepath.endswith('.enc.gz'):
                if not password or not auth_manager.verify_encryption_user(username, password):
                    logging.error("无权访问加密文件")
                    return
                
                # 获取文件ID
                file_id = os.path.basename(filepath).replace('.enc.gz', '')
                
                # 验证访问权限
                if not auth_manager.has_file_access(username, file_id):
                    logging.error("无权访问此文件")
                    return
            
            # 加载数据
            with open(filepath, 'rb') as f:
                data = f.read()
            
            # 如果是加密文件，先解密
            if filepath.endswith('.enc.gz') and password:
                data = self._decrypt_data(data, password)
            
            # 解压数据
            json_str = self._decompress_data(data)
            data = json.loads(json_str)
            
            events = data['events']
            if not events:
                logging.warning("镜像文件中没有事件数据")
                return
            
            logging.info(
                f"开始回放镜像: {filepath}\n"
                f"用户: {data['username']}\n"
                f"事件数: {data['event_count']}\n"
                f"总时长: {data['duration']:.1f}秒"
            )
            
            # 回放事件
            start_time = time.time()
            for event in events:
                # 计算等待时间
                wait_time = event['timestamp'] - (time.time() - start_time)
                if wait_time > 0:
                    time.sleep(wait_time)
                
                # 执行事件
                self._play_event(event)
            
            logging.info("镜像回放完成")
            
        except Exception as e:
            logging.error(f"回放镜像时发生错误: {str(e)}")
    
    def _play_event(self, event: Dict[str, Any]) -> None:
        """
        执行单个事件
        
        Args:
            event: 事件数据
        """
        try:
            x, y = event['position']
            event_type = event['type']
            params = event.get('params', {})
            
            # 设置鼠标位置
            self.mouse.position = (x, y)
            
            # 根据事件类型执行操作
            if event_type == 'click':
                if params.get('pressed'):
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
                else:
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            elif event_type == 'scroll':
                win32api.mouse_event(
                    win32con.MOUSEEVENTF_WHEEL,
                    x, y,
                    params.get('dy', 0) * 120,
                    0
                )
        except Exception as e:
            logging.error(f"执行事件时发生错误: {str(e)}")
            raise

# 创建全局镜像控制器实例
mouse_mirror = MouseMirror() 