import tkinter as tk
from tkinter import ttk, messagebox
import photo_manager
import lock_manager
import database_manager
import counter_manager
from datetime import datetime
import os

class StoreUI:
    """存物品界面及逻辑"""
    def __init__(self, parent_app):
        self.parent = parent_app  # 主应用实例，用于切换界面
        self.root = parent_app.root
        self.temp_item_type = None
        self.temp_photo_name = None

    def show(self):
        """显示存物品主界面（物品类型选择、拍照等）"""
        self._clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # 滚动条支持
        canvas = tk.Canvas(main_frame, bg='#f0f0f0')
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f0f0')
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 返回按钮
        back_btn = tk.Button(scrollable_frame, text="返回", bg='#CCCCCC', font=('微软雅黑', 10), width=8,
                             command=self.parent.show_main_interface)
        back_btn.grid(row=0, column=0, sticky='nw', pady=(0,20))

        # 物品类型选择
        tk.Label(scrollable_frame, text="选择物品类型:", bg='#f0f0f0', font=('微软雅黑',12)).grid(row=1,column=0,sticky='w',pady=(20,10))
        self.item_type_var = tk.StringVar()
        type_combo = ttk.Combobox(scrollable_frame, textvariable=self.item_type_var,
                                  values=["水杯","饭卡","手机","钱包","钥匙","书包","衣物","文具","电子产品","其他"],
                                  state='readonly', width=15)
        type_combo.set("请选择物品类型")
        type_combo.grid(row=2, column=0, sticky='w', pady=(0,20))

        # 拍照按钮
        photo_btn = tk.Button(scrollable_frame, text="拍照", bg='#2196F3', fg='white', font=('微软雅黑',12,'bold'),
                              width=10, height=2, command=self._take_photo_wrapper)
        photo_btn.grid(row=3, column=0, sticky='w', pady=(10,10))

        # 照片预览区域
        preview_frame = tk.Frame(scrollable_frame, bg='#f0f0f0')
        preview_frame.grid(row=4, column=0, sticky='w', pady=(0,20))
        tk.Label(preview_frame, text="照片预览:", bg='#f0f0f0', font=('微软雅黑',10)).pack(anchor='w', pady=(0,5))
        self.photo_label = tk.Label(preview_frame, text="暂无照片", bg='#e0e0e0', relief='solid', borderwidth=1)
        self.photo_label.pack(anchor='w')
        self.photo_status = tk.Label(scrollable_frame, text="未拍照", bg='#f0f0f0', font=('微软雅黑',10), fg='red')
        self.photo_status.grid(row=5, column=0, sticky='w', pady=(0,20))

        # 下一步按钮
        next_btn = tk.Button(scrollable_frame, text="下一步", bg='#4CAF50', fg='white', font=('微软雅黑',12,'bold'),
                             width=10, command=self._next_step)
        next_btn.grid(row=6, column=0, sticky='w', pady=(10,0))

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _take_photo_wrapper(self):
        if photo_manager.take_photo():
            self.photo_status.config(text="已拍照 (a.jpg)", fg='green')
            temp_path = photo_manager.config.TEMP_DIR + "/a.jpg"
            photo_manager.show_photo_preview(self.photo_label, temp_path)

    def _next_step(self):
        item_type = self.item_type_var.get()
        if item_type == "请选择物品类型" or not item_type:
            messagebox.showwarning("输入错误", "请选择物品类型！")
            return
        temp_photo = photo_manager.config.TEMP_DIR + "/a.jpg"
        if not os.path.exists(temp_photo):
            messagebox.showwarning("输入错误", "请先拍照！")
            return

        # 生成新照片名并保存
        new_number = counter_manager.count()
        new_photo_name = f"{new_number}.jpg"
        photo_manager.save_temp_photo_to_images(new_photo_name)

        self.temp_item_type = item_type
        self.temp_photo_name = new_photo_name
        self._show_locker_selection()

    def _show_locker_selection(self):
        self._clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        canvas = tk.Canvas(main_frame, bg='#f0f0f0')
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg='#f0f0f0')
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 返回按钮
        back_btn = tk.Button(scrollable, text="返回", bg='#CCCCCC', font=('微软雅黑',10), width=8,
                             command=self.show)
        back_btn.grid(row=0, column=0, sticky='nw', pady=(0,20))

        tk.Label(scrollable, text="选择柜子", bg='#f0f0f0', font=('微软雅黑',16,'bold')).grid(row=1, column=0, columnspan=4, pady=(0,20))

        # 图例
        legend = tk.Frame(scrollable, bg='#f0f0f0')
        legend.grid(row=2, column=0, columnspan=4, pady=(0,20))
        tk.Label(legend, text="空闲", bg='#4CAF50', fg='white', width=8, height=1).pack(side=tk.LEFT, padx=5)
        tk.Label(legend, text="已用", bg='#F44336', fg='white', width=8, height=1).pack(side=tk.LEFT, padx=5)

        lock_status = lock_manager.read_lock_info()
        for i in range(1, 9):
            row = 3 + (i-1)//4
            col = (i-1)%4
            status = lock_status.get(i, 0)
            bg = '#4CAF50' if status == 0 else '#F44336'
            state = tk.NORMAL if status == 0 else tk.DISABLED
            btn = tk.Button(scrollable, text=f"{i}号柜", bg=bg, fg='white', font=('微软雅雅',12,'bold'),
                            width=10, height=2, state=state,
                            command=lambda lid=i: self._confirm_store(lid))
            btn.grid(row=row, column=col, padx=10, pady=10)

    def _confirm_store(self, locker_id):
        confirm = messagebox.askyesno("确认存放",
                                      f"确认存放物品到 {locker_id} 号柜吗？\n\n"
                                      f"物品类型: {self.temp_item_type}\n照片: {self.temp_photo_name}")
        if not confirm:
            return
        store_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 更新锁状态为已用
        lock_manager.update_lock_info(lock_id=locker_id, status=1)
        # 保存到数据库
        database_manager.save_item_record(store_time, self.temp_item_type, self.temp_photo_name, locker_id)
        messagebox.showinfo("操作成功", f"正在打开 {locker_id} 号柜...\n\n物品存放成功！\n类型：{self.temp_item_type}\n柜子：{locker_id}号柜")
        self.parent.show_main_interface()
