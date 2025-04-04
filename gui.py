import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import keyboard
from shortcut_manager import ShortcutManager
from PIL import Image, ImageTk  # 需要安装pillow库：pip install pillow

class ShortcutApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("快捷键管理器")
        self.geometry("600x400")
        self.resizable(True, True)
        
        self.shortcut_manager = ShortcutManager()
        
        # 设置图标
        self.iconbitmap("favicon.ico")
        
        
        self.create_widgets()
        self.shortcut_manager.register_all_hotkeys()
        
        # 关闭窗口时注销快捷键
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # 快捷键列表
        self.create_shortcut_list(main_frame)
        
        # 操作按钮
        self.create_buttons(main_frame)
    
    def create_shortcut_list(self, parent):
        """创建快捷键列表"""
        # 标题标签
        ttk.Label(parent, text="已配置的快捷键", font=("黑体", 12)).pack(anchor=tk.W, pady=(0, 5))
        
        # 快捷键列表框架
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = ('快捷键', '类型', '值')
        self.shortcut_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        # 设置列标题
        for col in columns:
            self.shortcut_tree.heading(col, text=col)
            self.shortcut_tree.column(col, width=100)
        
        # 设置列宽
        self.shortcut_tree.column('快捷键', width=150)
        self.shortcut_tree.column('类型', width=100)
        self.shortcut_tree.column('值', width=250)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.shortcut_tree.yview)
        self.shortcut_tree.configure(yscroll=scrollbar.set)
        
        # 放置组件
        self.shortcut_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 填充数据
        self.refresh_shortcut_list()
    
    def create_buttons(self, parent):
        """创建操作按钮"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 添加快捷键按钮
        ttk.Button(button_frame, text="添加快捷键", command=self.add_shortcut).pack(side=tk.LEFT, padx=5)
        
        # 删除快捷键按钮
        ttk.Button(button_frame, text="删除快捷键", command=self.remove_shortcut).pack(side=tk.LEFT, padx=5)
        
        # 刷新列表按钮
        ttk.Button(button_frame, text="刷新列表", command=self.refresh_shortcut_list).pack(side=tk.LEFT, padx=5)
        
        # 重新注册快捷键按钮
        ttk.Button(button_frame, text="重新注册快捷键", command=self.register_hotkeys).pack(side=tk.LEFT, padx=5)
    
    def refresh_shortcut_list(self):
        """刷新快捷键列表"""
        # 清空列表
        for item in self.shortcut_tree.get_children():
            self.shortcut_tree.delete(item)
        
        # 添加快捷键到列表
        for hotkey, action in self.shortcut_manager.shortcuts.items():
            action_type = self.get_action_type_name(action["type"])
            self.shortcut_tree.insert('', tk.END, values=(hotkey, action_type, action["value"]))
    
    def get_action_type_name(self, action_type):
        """获取操作类型的中文名称"""
        type_names = {
            "open_app": "打开应用",
            "open_website": "打开网站",
            "type_text": "输入文本"
        }
        return type_names.get(action_type, action_type)
    
    def add_shortcut(self):
        """添加新的快捷键"""
        # 创建对话框
        dialog = ShortcutDialog(self)
        self.wait_window(dialog)
        
        # 如果用户提交了数据
        if dialog.result:
            hotkey, action_type, action_value = dialog.result
            
            # 检查快捷键是否已存在
            if hotkey in self.shortcut_manager.shortcuts:
                if not messagebox.askyesno("快捷键已存在", f"快捷键 '{hotkey}' 已存在，是否覆盖？"):
                    return
            
            # 添加快捷键
            if self.shortcut_manager.add_shortcut(hotkey, action_type, action_value):
                messagebox.showinfo("成功", "快捷键添加成功！")
                self.refresh_shortcut_list()
                self.register_hotkeys()
            else:
                messagebox.showerror("错误", "快捷键添加失败！")
    
    def remove_shortcut(self):
        """删除选中的快捷键"""
        # 获取选中的项
        selected_item = self.shortcut_tree.selection()
        if not selected_item:
            messagebox.showinfo("提示", "请先选择要删除的快捷键")
            return
        
        # 获取快捷键
        hotkey = self.shortcut_tree.item(selected_item[0], 'values')[0]
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除快捷键 '{hotkey}' 吗？"):
            if self.shortcut_manager.remove_shortcut(hotkey):
                messagebox.showinfo("成功", "快捷键删除成功！")
                self.refresh_shortcut_list()
                self.register_hotkeys()
            else:
                messagebox.showerror("错误", "快捷键删除失败！")
    
    def register_hotkeys(self):
        """重新注册所有快捷键"""
        self.shortcut_manager.register_all_hotkeys()
        messagebox.showinfo("成功", "快捷键已重新注册！")
    
    def on_closing(self):
        """关闭窗口时的处理"""
        self.shortcut_manager.unregister_all_hotkeys()
        self.destroy()


class ShortcutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("添加快捷键")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # 模态对话框
        self.transient(parent)
        self.grab_set()
        
        # 结果
        self.result = None
        
        # 创建界面
        self.create_widgets()
        
        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.focus_set()
    
    def create_widgets(self):
        """创建对话框组件"""
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 快捷键
        ttk.Label(frame, text="快捷键:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.hotkey_var = tk.StringVar()
        self.hotkey_entry = ttk.Entry(frame, textvariable=self.hotkey_var, width=30)
        self.hotkey_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(frame, text="录制", command=self.record_hotkey).grid(row=0, column=2, padx=5, pady=5)
        
        # 操作类型
        ttk.Label(frame, text="操作类型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.action_type_var = tk.StringVar()
        action_types = [
            ("打开应用", "open_app"),
            ("打开网站", "open_website"),
            ("输入文本", "type_text")
        ]
        self.action_type_combo = ttk.Combobox(frame, textvariable=self.action_type_var, width=28)
        self.action_type_combo['values'] = [t[0] for t in action_types]
        self.action_type_combo.current(0)
        self.action_type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # 操作值
        ttk.Label(frame, text="操作值:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.action_value_var = tk.StringVar()
        self.action_value_entry = ttk.Entry(frame, textvariable=self.action_value_var, width=30)
        self.action_value_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(frame, text="浏览", command=self.browse_file).grid(row=2, column=2, padx=5, pady=5)
        
        # 提示
        ttk.Label(frame, text="操作值说明:", font=("黑体", 10)).grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        
        desc_text = """打开应用：输入应用程序的完整路径，如 C:\\Windows\\notepad.exe
打开网站：输入网站地址，如 https://www.baidu.com
输入文本：输入要自动输入的文本内容"""
        
        desc_label = ttk.Label(frame, text=desc_text, wraplength=380, justify=tk.LEFT)
        desc_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=15)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # 设置列权重
        frame.columnconfigure(1, weight=1)
    
    def record_hotkey(self):
        """录制快捷键"""
        dialog = RecordHotkeyDialog(self)
        self.wait_window(dialog)
        
        if dialog.hotkey:
            self.hotkey_var.set(dialog.hotkey)
    
    def browse_file(self):
        """浏览文件"""
        from tkinter import filedialog
        
        # 获取当前操作类型
        action_type = self.get_action_type_value()
        
        if action_type == "open_app":
            filename = filedialog.askopenfilename(
                title="选择应用程序",
                filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
            )
            if filename:
                self.action_value_var.set(filename)
    
    def get_action_type_value(self):
        """获取操作类型的实际值"""
        action_types = {
            "打开应用": "open_app",
            "打开网站": "open_website",
            "输入文本": "type_text"
        }
        return action_types.get(self.action_type_var.get(), "open_app")
    
    def on_ok(self):
        """确定按钮事件"""
        hotkey = self.hotkey_var.get().strip()
        action_type = self.get_action_type_value()
        action_value = self.action_value_var.get().strip()
        
        # 验证输入
        if not hotkey:
            messagebox.showerror("错误", "请输入快捷键")
            return
        
        if not action_value:
            messagebox.showerror("错误", "请输入操作值")
            return
        
        self.result = (hotkey, action_type, action_value)
        self.destroy()
    
    def on_cancel(self):
        """取消按钮事件"""
        self.destroy()


class RecordHotkeyDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("录制快捷键")
        self.geometry("320x220")
        self.resizable(False, False)
        
        # 模态对话框
        self.transient(parent)
        self.grab_set()
        
        # 快捷键数据
        self.hotkey = None
        self.pressed_keys = set()  # 当前按下的键集合
        
        # 创建界面
        self.create_widgets()
        
        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # 开始录制
        self.recording = True
        self.hook_handlers = []
        self.start_recording()
        
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.focus_set()
    
    def create_widgets(self):
        """创建对话框组件"""
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="请按下您想要设置的快捷键组合", font=("黑体", 10)).pack(pady=(10, 5))
        ttk.Label(frame, text="按下快捷键后点击【确定】按钮完成设置", font=("黑体", 9)).pack(pady=(0, 10))
        
        self.hotkey_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.hotkey_var, width=30, justify=tk.CENTER, font=("宋体", 12)).pack(pady=5)
        
        self.status_var = tk.StringVar()
        self.status_var.set("等待按键...")
        status_label = ttk.Label(frame, textvariable=self.status_var, foreground="blue")
        status_label.pack(pady=5)
        
        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="确定", command=self.on_ok, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除", command=self.reset_hotkey, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.on_cancel, width=10).pack(side=tk.LEFT, padx=5)
    
    def start_recording(self):
        """开始录制快捷键"""
        import keyboard
        
        # 键盘按下事件处理
        def on_key_down(event):
            if not self.recording:
                return
                
            # 获取键名并标准化
            key_name = self.normalize_key(event.name)
            
            # 检查特殊键 (确定、返回等可能与UI交互冲突的键)
            if key_name in ('enter', 'return', 'esc', 'escape'):
                return
                
            # 忽略修饰键的独立事件
            if key_name in ('ctrl', 'alt', 'shift') and len(self.pressed_keys) == 0:
                self.pressed_keys.add(key_name)
                return
                
            # 添加到已按下集合
            self.pressed_keys.add(key_name)
            
            # 更新快捷键显示
            self.update_hotkey_display()
        
        # 键盘释放事件处理
        def on_key_up(event):
            if not self.recording:
                return
                
            key_name = self.normalize_key(event.name)
            
            if key_name in self.pressed_keys:
                self.pressed_keys.remove(key_name)
            
            # 如果没有按键按下，且已设置了快捷键，则显示"录制完成"
            if not self.pressed_keys and self.hotkey:
                self.status_var.set("录制完成!")
        
        # 添加键盘钩子
        self.hook_handlers.append(keyboard.on_press(on_key_down))
        self.hook_handlers.append(keyboard.on_release(on_key_up))
    
    def normalize_key(self, key):
        """标准化键名"""
        # 处理特殊键名
        key_map = {
            'control': 'ctrl',
            'left ctrl': 'ctrl',
            'right ctrl': 'ctrl',
            'left alt': 'alt',
            'right alt': 'alt',
            'left shift': 'shift',
            'right shift': 'shift'
        }
        return key_map.get(key.lower(), key.lower())
    
    def update_hotkey_display(self):
        """更新快捷键显示"""
        if not self.pressed_keys:
            return
            
        # 排序按键 (修饰键先显示)
        modifiers = ['ctrl', 'alt', 'shift']
        modifier_keys = [k for k in self.pressed_keys if k in modifiers]
        other_keys = [k for k in self.pressed_keys if k not in modifiers]
        
        # 按特定顺序排列修饰键
        ordered_keys = []
        for mod in modifiers:
            if mod in modifier_keys:
                ordered_keys.append(mod)
        
        # 添加其他键
        ordered_keys.extend(sorted(other_keys))
        
        # 设置快捷键
        hotkey_str = '+'.join(ordered_keys)
        
        # 仅当有非修饰键或者至少两个修饰键时才设置快捷键
        if other_keys or len(modifier_keys) >= 2:
            self.hotkey = hotkey_str
            self.hotkey_var.set(hotkey_str)
            self.status_var.set("正在录制...")
    
    def reset_hotkey(self):
        """重置快捷键"""
        self.hotkey = None
        self.pressed_keys.clear()
        self.hotkey_var.set("")
        self.status_var.set("等待按键...")
    
    def on_ok(self):
        """确定按钮事件"""
        if not self.hotkey:
            messagebox.showinfo("提示", "请先录制快捷键")
            return
        self.stop_recording()
        self.destroy()
    
    def on_cancel(self):
        """取消按钮事件"""
        self.stop_recording()
        self.hotkey = None
        self.destroy()
    
    def stop_recording(self):
        """停止录制"""
        self.recording = False
        import keyboard
        
        # 移除键盘钩子
        for handler in self.hook_handlers:
            keyboard.unhook(handler)
        self.hook_handlers = [] 