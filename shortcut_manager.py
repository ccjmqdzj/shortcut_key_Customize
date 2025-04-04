import json
import keyboard
import os
import subprocess

class ShortcutManager:
    def __init__(self, config_file="shortcuts.json"):
        self.config_file = config_file
        self.shortcuts = {}
        self.load_shortcuts()
        self.active_hotkeys = []
    
    def load_shortcuts(self):
        """从配置文件加载快捷键"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.shortcuts = json.load(f)
        except Exception as e:
            print(f"加载快捷键配置出错: {e}")
            self.shortcuts = {}
    
    def save_shortcuts(self):
        """保存快捷键到配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.shortcuts, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存快捷键配置出错: {e}")
            return False
    
    def add_shortcut(self, hotkey, action_type, action_value):
        """添加新的快捷键"""
        self.shortcuts[hotkey] = {
            "type": action_type,
            "value": action_value
        }
        return self.save_shortcuts()
    
    def remove_shortcut(self, hotkey):
        """删除快捷键"""
        if hotkey in self.shortcuts:
            del self.shortcuts[hotkey]
            return self.save_shortcuts()
        return False
    
    def execute_action(self, hotkey):
        """执行快捷键对应的动作"""
        if hotkey not in self.shortcuts:
            return False
        
        action = self.shortcuts[hotkey]
        action_type = action["type"]
        action_value = action["value"]
        
        try:
            if action_type == "open_app":
                subprocess.Popen(action_value)
            elif action_type == "open_website":
                os.system(f'start {action_value}')
            elif action_type == "type_text":
                keyboard.write(action_value)
            return True
        except Exception as e:
            print(f"执行动作出错: {e}")
            return False
    
    def register_all_hotkeys(self):
        """注册所有快捷键"""
        # 先清除已注册的快捷键
        self.unregister_all_hotkeys()
        
        # 注册新的快捷键
        for hotkey in self.shortcuts:
            try:
                keyboard.add_hotkey(hotkey, lambda h=hotkey: self.execute_action(h))
                self.active_hotkeys.append(hotkey)
            except Exception as e:
                print(f"注册快捷键 {hotkey} 失败: {e}")
    
    def unregister_all_hotkeys(self):
        """注销所有快捷键"""
        for hotkey in self.active_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
            except:
                pass
        self.active_hotkeys = [] 