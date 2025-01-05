"""
GUI管理模块
使用NICEGUI构建纯文本界面
"""

from nicegui import ui, app
import asyncio
from datetime import datetime
import logging
from session_manager import handle_login, logout_windows
from mouse_recorder import update_recording_info
from mouse_mirror import mouse_mirror
from auth_manager import auth_manager
from theme_config import theme_manager

class GUIManager:
    def __init__(self):
        self.username = None
        self.login_status = False
        self.encryption_password = None  # 存储加密密码
        self._setup_logging()
    
    def _setup_logging(self):
        """配置界面日志"""
        self.logger = logging.getLogger('gui')
        self.logger.setLevel(logging.INFO)
    
    def create_login_page(self):
        """创建登录页面"""
        with ui.card().classes('w-full max-w-lg mx-auto mt-8'):
            ui.label('系统登录').classes('text-2xl text-center mb-4')
            
            with ui.row().classes('w-full justify-center'):
                ui.label('当前状态：等待登录').classes('text-lg')
            
            with ui.row().classes('w-full justify-center mt-4'):
                ui.button('点击登录', on_click=self.handle_login_click).classes('w-32')
    
    def create_main_page(self):
        """创建主页面"""
        with ui.card().classes('w-full max-w-lg mx-auto mt-8') as main_card:
            # 应用主题
            theme_manager.apply_theme(main_card)
            
            ui.label(f'欢迎，{self.username}').classes('text-2xl text-center mb-4')
            
            with ui.row().classes('w-full justify-center'):
                ui.label('记录状态：正在记录鼠标操作').classes('text-lg')
            
            # 添加压缩等级选择
            with ui.row().classes('w-full justify-center mt-4'):
                ui.label('数据压缩等级：').classes('text-sm')
                compression_select = ui.select(
                    options=[
                        {'label': '无压缩', 'value': 0},
                        {'label': '快速压缩', 'value': 1},
                        {'label': '标准压缩', 'value': 6},
                        {'label': '最大压缩', 'value': 9}
                    ],
                    value=mouse_mirror.compression_level,
                    on_change=self.handle_compression_change
                ).classes('w-32')
            
            # 添加压缩说明
            with ui.row().classes('w-full justify-center mt-2'):
                ui.label(
                    '压缩等级说明：\n'
                    '无压缩 - 存储空间最大，保存最快\n'
                    '快速压缩 - 较小压缩，较快保存\n'
                    '标准压缩 - 平衡压缩比和速度\n'
                    '最大压缩 - 最小存储，保存最慢'
                ).classes('text-xs text-gray-600')
            
            # 添加加密设置
            with ui.row().classes('w-full justify-center mt-4'):
                ui.label('数据加密：').classes('text-sm')
                encryption_switch = ui.switch('启用加密', 
                    value=mouse_mirror.encryption_enabled,
                    on_change=self.handle_encryption_change
                ).classes('mr-4')
            
            # 加密等级选择
            with ui.row().classes('w-full justify-center mt-2'):
                ui.label('加密强度：').classes('text-sm')
                encryption_select = ui.select(
                    options=[
                        {'label': '基础加密', 'value': 1},
                        {'label': '中等加密', 'value': 2},
                        {'label': '高强度加密', 'value': 3}
                    ],
                    value=mouse_mirror.encryption_level,
                    on_change=self.handle_encryption_level_change,
                    disabled=not mouse_mirror.encryption_enabled
                ).classes('w-32')
            
            # 加密密码输入
            with ui.row().classes('w-full justify-center mt-2'):
                self.password_input = ui.input(
                    '加密密码', 
                    password=True,
                    on_change=self.handle_password_change,
                    disabled=not mouse_mirror.encryption_enabled
                ).classes('w-48')
            
            # 添加加密说明
            with ui.row().classes('w-full justify-center mt-2'):
                ui.label(
                    '加密说明：\n'
                    '基础加密 - 适用于一般保护\n'
                    '中等加密 - 提供更好的安全性\n'
                    '高强度加密 - 最高安全性，但保存较慢'
                ).classes('text-xs text-gray-600')
            
            with ui.row().classes('w-full justify-center mt-2'):
                ui.label('操作提示：右键点击任意位置以结束记录并退出').classes('text-sm text-red-500')
            
            # 添加时间显示
            self.time_label = ui.label().classes('text-center mt-4')
            asyncio.create_task(self.update_time())
            
            # 添加加密账号注册
            if not auth_manager.verify_encryption_user(self.username, ""):
                with ui.row().classes('w-full justify-center mt-4'):
                    ui.button('注册为加密账号', on_click=self.handle_register_click).classes('w-32')
            
            # 添加主题设置
            with ui.expansion('界面设置', icon='palette').classes('w-full mt-4'):
                with ui.row().classes('w-full justify-between'):
                    ui.label('主题颜色：').classes('text-sm')
                    ui.color_input(
                        value=theme_manager.theme.primary_color,
                        on_change=lambda e: self.update_theme(primary_color=e.value)
                    ).classes('w-32')
                
                with ui.row().classes('w-full justify-between mt-2'):
                    ui.label('圆角大小：').classes('text-sm')
                    ui.number(
                        value=theme_manager.theme.border_radius,
                        min=0,
                        max=24,
                        step=2,
                        on_change=lambda e: self.update_theme(border_radius=e.value)
                    ).classes('w-32')
                
                with ui.row().classes('w-full justify-between mt-2'):
                    ui.label('卡片圆角：').classes('text-sm')
                    ui.number(
                        value=theme_manager.theme.card_radius,
                        min=0,
                        max=32,
                        step=4,
                        on_change=lambda e: self.update_theme(card_radius=e.value)
                    ).classes('w-32')
                
                with ui.row().classes('w-full justify-between mt-2'):
                    ui.label('按钮圆角：').classes('text-sm')
                    ui.number(
                        value=theme_manager.theme.button_radius,
                        min=0,
                        max=20,
                        step=2,
                        on_change=lambda e: self.update_theme(button_radius=e.value)
                    ).classes('w-32')
    
    async def handle_compression_change(self, e):
        """处理压缩等级变更"""
        try:
            new_level = int(e.value)
            mouse_mirror.compression_level = new_level
            self.logger.info(f"压缩等级已更新为: {new_level}")
            
            # 显示提示信息
            compression_info = {
                0: "已设置为无压缩模式",
                1: "已设置为快速压缩模式",
                6: "已设置为标准压缩模式",
                9: "已设置为最大压缩模式"
            }
            ui.notify(compression_info.get(new_level, "压缩等级已更新"))
            
        except Exception as e:
            self.logger.error(f"更新压缩等级时发生错误: {str(e)}")
            ui.notify("更新压缩等级失败", type='negative')
    
    async def update_time(self):
        """更新时间显示"""
        while True:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.time_label.text = f'当前时间：{current_time}'
            await asyncio.sleep(1)
    
    async def handle_login_click(self):
        """处理登录点击"""
        try:
            self.username = await app.run_in_thread(handle_login)
            if self.username:
                self.login_status = True
                self.logger.info(f"用户 {self.username} 登录成功")
                update_recording_info(self.username)
                # 切换到主页面
                ui.clear()
                self.create_main_page()
            else:
                ui.notify('登录失败，请重试', type='negative')
                
        except Exception as e:
            self.logger.error(f"登录过程发生错误: {str(e)}")
            ui.notify(f'登录错误: {str(e)}', type='negative')
    
    async def handle_encryption_change(self, e):
        """处理加密开关变更"""
        try:
            enabled = bool(e.value)
            mouse_mirror.encryption_enabled = enabled
            self.logger.info(f"加密状态已更新为: {'启用' if enabled else '禁用'}")
            
            # 更新UI状态
            self.password_input.enabled = enabled
            ui.notify('加密已' + ('启用' if enabled else '禁用'))
            
        except Exception as e:
            self.logger.error(f"更新加密状态时发生错误: {str(e)}")
            ui.notify("更新加密状态失败", type='negative')
    
    async def handle_encryption_level_change(self, e):
        """处理加密等级变更"""
        try:
            new_level = int(e.value)
            mouse_mirror.encryption_level = new_level
            self.logger.info(f"加密等级已更新为: {new_level}")
            
            level_info = {
                1: "已设置为基础加密",
                2: "已设置为中等加密",
                3: "已设置为高强度加密"
            }
            ui.notify(level_info.get(new_level, "加密等级已更新"))
            
        except Exception as e:
            self.logger.error(f"更新加密等级时发生错误: {str(e)}")
            ui.notify("更新加密等级失败", type='negative')
    
    async def handle_password_change(self, e):
        """处理密码变更"""
        try:
            self.encryption_password = e.value
            self.logger.info("加密密码已更新")
        except Exception as e:
            self.logger.error(f"更新加密密码时发生错误: {str(e)}")
    
    async def handle_register_click(self):
        """处理加密账号注册"""
        try:
            if not self.encryption_password:
                ui.notify('请先设置加密密码', type='warning')
                return
            
            if auth_manager.register_encryption_user(self.username, self.encryption_password):
                ui.notify('加密账号注册成功')
                # 刷新界面
                ui.clear()
                self.create_main_page()
            else:
                ui.notify('加密账号注册失败', type='negative')
                
        except Exception as e:
            self.logger.error(f"注册加密账号时发生错误: {str(e)}")
            ui.notify('注册过程发生错误', type='negative')
    
    async def update_theme(self, **kwargs):
        """更新主题设置"""
        try:
            if theme_manager.update_theme(**kwargs):
                # 刷新界面
                ui.clear()
                self.create_main_page()
                ui.notify('主题设置已更新')
            else:
                ui.notify('更新主题设置失败', type='negative')
        except Exception as e:
            self.logger.error(f"更新主题设置时发生错误: {str(e)}")
            ui.notify('更新主题设置失败', type='negative')

def start_gui():
    """启动GUI"""
    gui_manager = GUIManager()
    
    @app.on_shutdown
    def shutdown():
        """程序关闭时的清理工作"""
        if gui_manager.login_status:
            logging.info("程序正在关闭，执行清理...")
            logout_windows()
    
    # 创建初始页面
    gui_manager.create_login_page()
    
    # 配置和启动
    ui.run(
        title='鼠标操作记录系统',
        port=8080,
        reload=False,
        show=True,
        window_size=(800, 600),
        storage_secret='mouse_recorder'
    )

if __name__ == "__main__":
    start_gui() 