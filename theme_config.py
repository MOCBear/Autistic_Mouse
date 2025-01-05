"""
主题配置模块
管理界面主题和样式设置
"""

import json
import os
import logging
from typing import Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class ThemeConfig:
    # 主题颜色
    primary_color: str = '#1976D2'  # 主色
    secondary_color: str = '#424242'  # 次色
    accent_color: str = '#82B1FF'  # 强调色
    
    # 背景颜色
    background_color: str = '#FFFFFF'  # 背景色
    surface_color: str = '#F5F5F5'  # 表面色
    
    # 文字颜色
    text_primary: str = '#000000'  # 主要文字
    text_secondary: str = '#666666'  # 次要文字
    
    # 圆角设置
    border_radius: int = 8  # 默认圆角大小
    card_radius: int = 12  # 卡片圆角
    button_radius: int = 6  # 按钮圆角
    
    # 其他样式
    shadow_level: int = 2  # 阴影级别 (0-4)
    transition_time: float = 0.3  # 过渡动画时间(秒)

class ThemeManager:
    def __init__(self):
        self.config_file = 'config/theme.json'
        self.theme = ThemeConfig()
        self._setup_logging()
        self._load_config()
    
    def _setup_logging(self):
        """配置日志"""
        self.logger = logging.getLogger('theme')
        self.logger.setLevel(logging.INFO)
    
    def _load_config(self):
        """加载主题配置"""
        try:
            os.makedirs('config', exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    # 更新主题配置
                    for key, value in config_data.items():
                        if hasattr(self.theme, key):
                            setattr(self.theme, key, value)
            else:
                # 保存默认配置
                self.save_config()
        except Exception as e:
            self.logger.error(f"加载主题配置时发生错误: {str(e)}")
    
    def save_config(self):
        """保存主题配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.theme), f, indent=2, ensure_ascii=False)
            self.logger.info("主题配置已保存")
        except Exception as e:
            self.logger.error(f"保存主题配置时发生错误: {str(e)}")
    
    def update_theme(self, **kwargs):
        """更新主题设置"""
        try:
            for key, value in kwargs.items():
                if hasattr(self.theme, key):
                    setattr(self.theme, key, value)
            self.save_config()
            return True
        except Exception as e:
            self.logger.error(f"更新主题设置时发生错误: {str(e)}")
            return False
    
    def get_css_variables(self) -> Dict[str, str]:
        """获取CSS变量"""
        return {
            '--primary-color': self.theme.primary_color,
            '--secondary-color': self.theme.secondary_color,
            '--accent-color': self.theme.accent_color,
            '--background-color': self.theme.background_color,
            '--surface-color': self.theme.surface_color,
            '--text-primary': self.theme.text_primary,
            '--text-secondary': self.theme.text_secondary,
            '--border-radius': f'{self.theme.border_radius}px',
            '--card-radius': f'{self.theme.card_radius}px',
            '--button-radius': f'{self.theme.button_radius}px',
            '--shadow-level': str(self.theme.shadow_level),
            '--transition-time': f'{self.theme.transition_time}s'
        }
    
    def apply_theme(self, element):
        """应用主题到元素"""
        css_vars = self.get_css_variables()
        style = ';'.join([f'{k}:{v}' for k, v in css_vars.items()])
        element.style(style)

# 创建全局主题管理器实例
theme_manager = ThemeManager() 