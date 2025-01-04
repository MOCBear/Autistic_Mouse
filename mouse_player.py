from pynput.mouse import Controller
import json
import time
import os
import logging
import sys
import platform

# 检查操作系统
if platform.system() != 'Windows':
    print("错误：此功能仅支持 Windows 系统")
    sys.exit(1)

class MousePlayer:
    def __init__(self):
        self.mouse = Controller()
        self.log_dir = 'mouse_records'
        
        # 配置日志
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        logging.basicConfig(
            filename=os.path.join(self.log_dir, 'playback.log'),
            level=logging.INFO,
            format='%(asctime)s: %(message)s'
        )
    
    def load_recording(self, record_file):
        """加载记录文件"""
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['events']
        except Exception as e:
            logging.error(f"加载记录文件时发生错误: {str(e)}")
            return None
    
    def play_events(self, events):
        """回放鼠标事件"""
        if not events:
            logging.error("没有可回放的事件")
            return
        
        try:
            start_time = time.time()
            first_event_time = events[0]['timestamp']
            
            for event in events:
                # 计算等待时间
                event_time = event['timestamp'] - first_event_time
                current_time = time.time() - start_time
                wait_time = event_time - current_time
                
                if wait_time > 0:
                    time.sleep(wait_time)
                
                # 移动鼠标到指定位置
                x, y = event['position']
                self.mouse.position = (x, y)
                
                # 记录事件
                logging.info(f"回放事件: {event['type']} 在位置 {(x, y)}")
                
        except Exception as e:
            logging.error(f"回放事件时发生错误: {str(e)}")

def play_recording(record_file):
    """回放指定的记录文件"""
    player = MousePlayer()
    
    try:
        print(f"开始回放记录: {record_file}")
        events = player.load_recording(record_file)
        if events:
            player.play_events(events)
            print("回放完成")
        else:
            print("加载记录文件失败")
    except Exception as e:
        print(f"回放过程中发生错误: {str(e)}")
        logging.error(f"回放过程中发生错误: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python mouse_player.py <record_file>")
        sys.exit(1)
    
    record_file = sys.argv[1]
    if not os.path.exists(record_file):
        print(f"记录文件不存在: {record_file}")
        sys.exit(1)
    
    play_recording(record_file) 