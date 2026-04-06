import tkinter as tk
from tkinter import ttk
import sqlite3
import os
from datetime import datetime
import time

class DatabaseViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("失物招领数据库查看器 - 自动展示")
        self.root.geometry("1200x700")  # 增加窗口大小以适应更多内容
        self.root.configure(bg='#f0f0f0')
        
        # 数据库文件路径
        self.db_path = 'files/lost_and_found.db'
        
        # 自动滚动相关变量
        self.auto_scroll_running = False
        self.scroll_speed = 2000  # 默认滚动速度（毫秒）
        self.current_start_index = 0  # 当前显示的开始索引
        self.items_per_page = 6  # 每页显示6个物品
        
        # 记录上次数据库记录数量
        self.last_item_count = 0
        self.is_new_cycle = True  # 是否是新的一轮循环
        
        # 创建主界面
        self.create_widgets()
        
        # 加载数据
        self.load_data()
    
    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="失物招领数据库内容 - 自动展示模式 (同时显示6个物品，实时更新)",
            bg='#f0f0f0',
            font=('微软雅黑', 16, 'bold'),
            pady=10
        )
        title_label.pack(fill=tk.X)
        
        # 控制面板
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 自动滚动控制按钮
        self.auto_scroll_btn = tk.Button(
            control_frame,
            text="开始自动滚动",
            bg='#4CAF50',
            fg='white',
            font=('微软雅黑', 10),
            width=12,
            command=self.toggle_auto_scroll
        )
        self.auto_scroll_btn.pack(side=tk.LEFT, padx=5)
        
        # 速度控制
        speed_frame = tk.Frame(control_frame, bg='#f0f0f0')
        speed_frame.pack(side=tk.LEFT, padx=20)
        
        speed_label = tk.Label(
            speed_frame,
            text="滚动速度(秒):",
            bg='#f0f0f0',
            font=('微软雅黑', 10)
        )
        speed_label.pack(side=tk.LEFT)
        
        self.speed_var = tk.StringVar(value="2")
        speed_entry = tk.Entry(
            speed_frame,
            textvariable=self.speed_var,
            font=('微软雅黑', 10),
            width=3
        )
        speed_entry.pack(side=tk.LEFT, padx=5)
        
        speed_set_btn = tk.Button(
            speed_frame,
            text="设置",
            bg='#2196F3',
            fg='white',
            font=('微软雅黑', 10),
            width=6,
            command=self.set_scroll_speed
        )
        speed_set_btn.pack(side=tk.LEFT, padx=5)
        
        # 手动控制按钮
        prev_btn = tk.Button(
            control_frame,
            text="上一页",
            bg='#FF9800',
            fg='white',
            font=('微软雅黑', 10),
            width=8,
            command=self.show_previous_page
        )
        prev_btn.pack(side=tk.LEFT, padx=5)
        
        next_btn = tk.Button(
            control_frame,
            text="下一页",
            bg='#FF9800',
            fg='white',
            font=('微软雅黑', 10),
            width=8,
            command=self.show_next_page
        )
        next_btn.pack(side=tk.LEFT, padx=5)
        
        # 立即刷新按钮
        refresh_now_btn = tk.Button(
            control_frame,
            text="立即刷新",
            bg='#9C27B0',
            fg='white',
            font=('微软雅黑', 10),
            width=10,
            command=self.load_data
        )
        refresh_now_btn.pack(side=tk.LEFT, padx=5)
        
        # 数据库状态显示
        self.db_status_label = tk.Label(
            control_frame,
            text="数据库状态: 就绪",
            bg='#f0f0f0',
            font=('微软雅黑', 9),
            fg='green'
        )
        self.db_status_label.pack(side=tk.LEFT, padx=20)
        
        # 搜索框架
        search_frame = tk.Frame(control_frame, bg='#f0f0f0')
        search_frame.pack(side=tk.RIGHT, padx=5)
        
        search_label = tk.Label(
            search_frame,
            text="搜索:",
            bg='#f0f0f0',
            font=('微软雅黑', 10)
        )
        search_label.pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('微软雅黑', 10),
            width=20
        )
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.Button(
            search_frame,
            text="搜索",
            bg='#2196F3',
            fg='white',
            font=('微软雅黑', 10),
            width=8,
            command=self.search_data
        )
        search_btn.pack(side=tk.LEFT, padx=5)
        
        clear_search_btn = tk.Button(
            search_frame,
            text="清除",
            bg='#FF9800',
            fg='white',
            font=('微软雅黑', 10),
            width=8,
            command=self.clear_search
        )
        clear_search_btn.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 - 共加载 0 条记录")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg='#e0e0e0',
            font=('微软雅黑', 10),
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建主展示区域
        self.main_display_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 初始显示提示
        self.show_default_info()
    
    def show_default_info(self):
        """显示默认信息"""
        # 清除展示区域
        for widget in self.main_display_frame.winfo_children():
            widget.destroy()
        
        # 显示提示信息
        prompt_label = tk.Label(
            self.main_display_frame,
            text="点击'开始自动滚动'按钮开始自动展示数据",
            bg='#f0f0f0',
            font=('微软雅黑', 16),
            pady=50
        )
        prompt_label.pack(expand=True, fill='both')
    
    def load_data(self):
        """从数据库加载数据"""
        if not os.path.exists(self.db_path):
            self.status_var.set(f"错误: 数据库文件不存在 - {self.db_path}")
            self.db_status_label.config(text="数据库状态: 文件不存在", fg='red')
            return
        
        try:
            # 停止自动滚动
            self.stop_auto_scroll()
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 执行查询
            cursor.execute("SELECT * FROM item_records ORDER BY id DESC")
            rows = cursor.fetchall()
            
            # 保存所有数据
            self.all_items = []
            for row in rows:
                processed_row = []
                for value in row:
                    if value is None:
                        processed_row.append("")
                    else:
                        processed_row.append(value)
                self.all_items.append(processed_row)
            
            conn.close()
            
            # 重置当前索引
            self.current_start_index = 0
            
            # 更新状态
            current_count = len(self.all_items)
            self.status_var.set(f"成功加载 {current_count} 条记录")
            self.db_status_label.config(text=f"数据库状态: {current_count} 条记录", fg='green')
            
            # 记录上次数量
            self.last_item_count = current_count
            
            # 显示第一页记录
            if self.all_items:
                self.show_current_page()
            else:
                self.show_default_info()
            
        except Exception as e:
            self.status_var.set(f"数据库错误: {str(e)}")
            self.db_status_label.config(text="数据库状态: 连接错误", fg='red')
    
    def reload_data_for_auto_scroll(self):
        """为自动滚动重新加载数据（不停止自动滚动）"""
        if not os.path.exists(self.db_path):
            self.db_status_label.config(text="数据库状态: 文件不存在", fg='red')
            return False
        
        try:
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 执行查询
            cursor.execute("SELECT * FROM item_records ORDER BY id DESC")
            rows = cursor.fetchall()
            
            # 保存所有数据
            new_items = []
            for row in rows:
                processed_row = []
                for value in row:
                    if value is None:
                        processed_row.append("")
                    else:
                        processed_row.append(value)
                new_items.append(processed_row)
            
            conn.close()
            
            # 更新数据
            self.all_items = new_items
            
            # 更新状态
            current_count = len(self.all_items)
            change_text = ""
            if current_count > self.last_item_count:
                change_text = f" (+{current_count - self.last_item_count}新增)"
            elif current_count < self.last_item_count:
                change_text = f" (-{self.last_item_count - current_count}减少)"
            
            self.status_var.set(f"已重新加载 {current_count} 条记录{change_text}")
            self.db_status_label.config(text=f"数据库状态: {current_count} 条记录{change_text}", fg='green')
            
            # 记录上次数量
            self.last_item_count = current_count
            
            return True
            
        except Exception as e:
            self.db_status_label.config(text="数据库状态: 连接错误", fg='red')
            return False
    
    def show_current_page(self):
        """显示当前页的6个物品"""
        if not self.all_items:
            return
        
        # 计算当前页的结束索引
        end_index = min(self.current_start_index + self.items_per_page, len(self.all_items))
        
        # 更新状态
        self.status_var.set(f"显示第 {self.current_start_index + 1}-{end_index} / {len(self.all_items)} 条记录")
        
        # 显示当前页的物品
        self.show_items_page(self.current_start_index, end_index)
    
    def show_items_page(self, start_index, end_index):
        """显示指定范围的物品"""
        # 清除展示区域
        for widget in self.main_display_frame.winfo_children():
            widget.destroy()
        
        # 创建滚动框架
        scroll_frame = tk.Frame(self.main_display_frame, bg='#f0f0f0')
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建画布
        canvas = tk.Canvas(scroll_frame, bg='#f0f0f0', yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        scrollbar.config(command=canvas.yview)
        
        # 创建内容框架
        content_frame = tk.Frame(canvas, bg='#f0f0f0')
        canvas.create_window((0, 0), window=content_frame, anchor='nw')
        
        # 创建3x2网格来显示6个物品
        items_to_show = self.all_items[start_index:end_index]
        row, col = 0, 0
        
        for i, item_data in enumerate(items_to_show):
            # 创建物品框架
            item_frame = tk.Frame(
                content_frame,
                bg='#ffffff',
                relief=tk.RAISED,
                bd=1,
                width=350,  # 固定宽度
                height=250  # 固定高度
            )
            item_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            item_frame.grid_propagate(False)  # 防止框架收缩
            
            # 配置网格权重
            content_frame.columnconfigure(col, weight=1)
            content_frame.rowconfigure(row, weight=1)
            
            # 显示物品信息
            self.create_item_display(item_frame, item_data, start_index + i + 1)
            
            # 更新网格位置
            col += 1
            if col >= 3:  # 每行3个物品
                col = 0
                row += 1
        
        # 如果物品不足6个，填充空白框架
        while row < 2 and (row * 3 + col) < self.items_per_page:
            empty_frame = tk.Frame(
                content_frame,
                bg='#f0f0f0',
                width=350,
                height=250
            )
            empty_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            empty_frame.grid_propagate(False)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        # 更新滚动区域
        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        content_frame.bind("<Configure>", update_scroll_region)
    
    def create_item_display(self, parent_frame, item_data, item_number):
        """在指定框架中创建物品显示"""
        # 物品编号
        number_label = tk.Label(
            parent_frame,
            text=f"物品 #{item_number}",
            bg='#ffffff',
            font=('微软雅黑', 10, 'bold'),
            pady=5
        )
        number_label.pack(fill=tk.X)
        
        # 分隔线
        separator = ttk.Separator(parent_frame, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=5, pady=2)
        
        # 创建信息框架
        info_frame = tk.Frame(parent_frame, bg='#ffffff')
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 显示关键信息
        info_labels = [
            ("类型:", item_data[2]),
            ("柜子:", item_data[4]),
            ("存物时间:", item_data[1][:16] if item_data[1] else ""),  # 只显示日期和时间，不显示秒
            ("状态:", "未取走" if not item_data[5] else "已取走")
        ]
        
        for i, (label, value) in enumerate(info_labels):
            # 标签
            label_widget = tk.Label(
                info_frame,
                text=label,
                bg='#ffffff',
                font=('微软雅黑', 8, 'bold'),
                anchor='w',
                width=6
            )
            label_widget.grid(row=i, column=0, sticky='w', pady=2)
            
            # 值
            value_widget = tk.Label(
                info_frame,
                text=value,
                bg='#ffffff',
                font=('微软雅黑', 8),
                anchor='w',
                width=20,
                wraplength=200  # 允许文本换行
            )
            value_widget.grid(row=i, column=1, sticky='w', pady=2)
        
        # 照片预览区域
        photo_frame = tk.Frame(
            parent_frame, 
            bg='#e0e0e0', 
            relief=tk.SUNKEN, 
            bd=1,
            width=100,
            height=80
        )
        photo_frame.pack(fill=tk.X, padx=5, pady=5)
        photo_frame.pack_propagate(False)  # 防止框架收缩
        
        # 尝试显示照片
        photo_name = item_data[3]
        if photo_name:
            photo_path = f"files/images/{photo_name}"
            if os.path.exists(photo_path):
                try:
                    from PIL import Image, ImageTk
                    # 加载并显示图片
                    image = Image.open(photo_path)
                    # 调整图片大小以适应框架
                    frame_width = 100
                    frame_height = 80
                    
                    # 计算缩放比例
                    img_width, img_height = image.size
                    scale = min(frame_width / img_width, frame_height / img_height)
                    new_width = int(img_width * scale)
                    new_height = int(img_height * scale)
                    
                    # 调整图片大小
                    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(resized_image)
                    
                    photo_label = tk.Label(
                        photo_frame,
                        image=photo,
                        bg='#e0e0e0'
                    )
                    photo_label.image = photo  # 保持引用
                    photo_label.pack(expand=True)
                except Exception as e:
                    # 图片显示失败
                    error_label = tk.Label(
                        photo_frame,
                        text="图片加载失败",
                        bg='#e0e0e0',
                        font=('微软雅黑', 6),
                        fg='red'
                    )
                    error_label.pack(expand=True)
            else:
                # 图片不存在
                no_photo_label = tk.Label(
                    photo_frame,
                    text="无照片",
                    bg='#e0e0e0',
                    font=('微软雅黑', 8)
                )
                no_photo_label.pack(expand=True)
        else:
            # 无照片
            no_photo_label = tk.Label(
                photo_frame,
                text="无照片",
                bg='#e0e0e0',
                font=('微软雅黑', 8)
            )
            no_photo_label.pack(expand=True)
    
    def toggle_auto_scroll(self):
        """切换自动滚动状态"""
        if self.auto_scroll_running:
            self.stop_auto_scroll()
        else:
            self.start_auto_scroll()
    
    def start_auto_scroll(self):
        """开始自动滚动"""
        if not self.all_items:
            self.status_var.set("没有数据可展示")
            return
        
        self.auto_scroll_running = True
        self.auto_scroll_btn.config(text="停止自动滚动", bg='#F44336')
        self.status_var.set("自动滚动已开始")
        self.is_new_cycle = True  # 开始新的一轮循环
        self.auto_scroll()
    
    def stop_auto_scroll(self):
        """停止自动滚动"""
        self.auto_scroll_running = False
        self.auto_scroll_btn.config(text="开始自动滚动", bg='#4CAF50')
        self.status_var.set("自动滚动已停止")
    
    def auto_scroll(self):
        """自动滚动显示下一页物品"""
        if not self.auto_scroll_running:
            return
        
        # 显示当前页
        self.show_current_page()
        
        # 移动到下一页
        self.current_start_index += self.items_per_page
        
        # 检查是否已经滚动到末尾
        if self.current_start_index >= len(self.all_items):
            # 一轮循环结束，重新读取数据库
            self.reload_data_for_auto_scroll()
            self.current_start_index = 0  # 重置为第一页
            self.is_new_cycle = True  # 标记为新的一轮循环
            
            # 更新状态
            self.status_var.set(f"已完成一轮循环，已重新加载数据库，共 {len(self.all_items)} 条记录")
        else:
            self.is_new_cycle = False
        
        # 设置下一次滚动
        self.root.after(self.scroll_speed, self.auto_scroll)
    
    def set_scroll_speed(self):
        """设置滚动速度"""
        try:
            speed_seconds = float(self.speed_var.get())
            if speed_seconds <= 0:
                raise ValueError("速度必须大于0")
            
            self.scroll_speed = int(speed_seconds * 1000)  # 转换为毫秒
            self.status_var.set(f"滚动速度已设置为 {speed_seconds} 秒")
        except ValueError as e:
            self.status_var.set(f"速度设置错误: {str(e)}")
    
    def show_previous_page(self):
        """显示上一页"""
        if not self.all_items:
            return
        
        self.current_start_index -= self.items_per_page
        if self.current_start_index < 0:
            # 计算最后一页的开始索引
            last_page_start = (len(self.all_items) - 1) // self.items_per_page * self.items_per_page
            self.current_start_index = last_page_start
        
        self.show_current_page()
    
    def show_next_page(self):
        """显示下一页"""
        if not self.all_items:
            return
        
        self.current_start_index += self.items_per_page
        if self.current_start_index >= len(self.all_items):
            self.current_start_index = 0  # 循环回到开头
        
        self.show_current_page()
    
    def search_data(self):
        """搜索数据"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_data()  # 如果没有搜索词，重新加载所有数据
            return
        
        if not os.path.exists(self.db_path):
            self.status_var.set(f"错误: 数据库文件不存在 - {self.db_path}")
            return
        
        try:
            # 停止自动滚动
            self.stop_auto_scroll()
            
            # 连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 构建搜索查询
            query = """
                SELECT * FROM item_records 
                WHERE item_type LIKE ? OR photo_name LIKE ? OR locker_id LIKE ? OR taker_name LIKE ?
                ORDER BY id DESC
            """
            search_pattern = f"%{search_term}%"
            
            # 执行查询
            cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            rows = cursor.fetchall()
            
            # 保存搜索结果
            self.all_items = []
            for row in rows:
                processed_row = []
                for value in row:
                    if value is None:
                        processed_row.append("")
                    else:
                        processed_row.append(value)
                self.all_items.append(processed_row)
            
            conn.close()
            
            # 重置当前索引
            self.current_start_index = 0
            
            # 更新状态
            self.status_var.set(f"搜索 '{search_term}' 找到 {len(self.all_items)} 条记录")
            
            # 显示第一页记录
            if self.all_items:
                self.show_current_page()
            else:
                self.show_default_info()
            
        except Exception as e:
            self.status_var.set(f"搜索错误: {str(e)}")
    
    def clear_search(self):
        """清除搜索"""
        self.search_var.set("")
        self.load_data()

def main():
    root = tk.Tk()
    app = DatabaseViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()