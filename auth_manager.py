"""
权限管理模块
管理加密账号和访问权限
"""

import json
import os
import hashlib
import logging
from typing import Dict, Optional
from datetime import datetime

class AuthManager:
    def __init__(self):
        self.auth_file = 'config/auth.json'
        self.current_user = None
        self._setup()
        self._setup_logging()
    
    def _setup_logging(self):
        """配置日志"""
        self.logger = logging.getLogger('auth')
        self.logger.setLevel(logging.INFO)
    
    def _setup(self):
        """初始化权限配置"""
        os.makedirs('config', exist_ok=True)
        if not os.path.exists(self.auth_file):
            self._save_auth_data({
                'users': {},
                'encryption_keys': {}
            })
    
    def _hash_password(self, password: str) -> str:
        """生成密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _save_auth_data(self, data: Dict) -> None:
        """保存权限数据"""
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_auth_data(self) -> Dict:
        """加载权限数据"""
        try:
            with open(self.auth_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'users': {}, 'encryption_keys': {}}
    
    def register_encryption_user(self, username: str, password: str) -> bool:
        """
        注册加密账号
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            是否注册成功
        """
        try:
            data = self._load_auth_data()
            if username in data['users']:
                self.logger.warning(f"用户 {username} 已存在")
                return False
            
            # 保存用户信息
            data['users'][username] = {
                'password_hash': self._hash_password(password),
                'created_at': datetime.now().isoformat(),
                'is_encryption_user': True
            }
            
            self._save_auth_data(data)
            self.logger.info(f"加密账号 {username} 注册成功")
            return True
            
        except Exception as e:
            self.logger.error(f"注册加密账号时发生错误: {str(e)}")
            return False
    
    def verify_encryption_user(self, username: str, password: str) -> bool:
        """验证加密账号"""
        try:
            data = self._load_auth_data()
            user_data = data['users'].get(username)
            
            if not user_data or not user_data.get('is_encryption_user'):
                return False
            
            return user_data['password_hash'] == self._hash_password(password)
            
        except Exception as e:
            self.logger.error(f"验证加密账号时发生错误: {str(e)}")
            return False
    
    def store_encryption_key(self, username: str, file_id: str, key: str) -> bool:
        """存储加密密钥"""
        try:
            data = self._load_auth_data()
            if username not in data['users'] or not data['users'][username].get('is_encryption_user'):
                return False
            
            if username not in data['encryption_keys']:
                data['encryption_keys'][username] = {}
            
            data['encryption_keys'][username][file_id] = {
                'key': key,
                'created_at': datetime.now().isoformat()
            }
            
            self._save_auth_data(data)
            return True
            
        except Exception as e:
            self.logger.error(f"存储加密密钥时发生错误: {str(e)}")
            return False
    
    def get_encryption_key(self, username: str, file_id: str) -> Optional[str]:
        """获取加密密钥"""
        try:
            data = self._load_auth_data()
            return data.get('encryption_keys', {}).get(username, {}).get(file_id, {}).get('key')
        except Exception as e:
            self.logger.error(f"获取加密密钥时发生错误: {str(e)}")
            return None
    
    def has_file_access(self, username: str, file_id: str) -> bool:
        """检查用户是否有文件访问权限"""
        try:
            data = self._load_auth_data()
            user_data = data['users'].get(username)
            
            # 非加密账号无权限
            if not user_data or not user_data.get('is_encryption_user'):
                return False
            
            # 检查是否有对应的密钥
            return bool(self.get_encryption_key(username, file_id))
            
        except Exception as e:
            self.logger.error(f"检查文件访问权限时发生错误: {str(e)}")
            return False

# 创建全局权限管理器实例
auth_manager = AuthManager() 