import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import lock_manager
import database_manager
import photo_manager
import config
import os

class TakeUI:
    """取物品界面及逻辑"""
    def __init__(self, parent_app):
        self.parent = parent_app
        self.root = parent_app.root
        self.taker_name = None
        self.selected_locker_id = None

    def show_name_input(self):
        self._clear_window()
        frame = tk.Frame(self.root, bg='#f0f0f0')
        frame.pack(expand=True, fill='both', padx=20, pady=20)

        back_btn = tk.Button(frame, text="返回", bg='#CCCCCC', font=('微软雅黑',10), width=8,
                             command=self.parent.show_main_interface)
        back_btn.grid(row=0, column=0, sticky='nw', pady=(0,20))

        tk.Label(frame, text="请输入取物人姓名", bg='#f0f0f0', font=('微软雅黑',16,'bold')).grid(row=1, column=0, pady=(0,20))
        self.name_var = tk.StringVar()
        entry = tk.Entry(frame, textvariable=self.name_var, font=('微软雅黑',12), width=20)
        entry.grid(row=2, column=0, pady=(0,20))
        next_btn = tk.Button(frame, text="下一步", bg='#4CAF50', fg='white', font=('微软雅黑',12,'bold'), width=10,
                             command=self._show_locker_selection)
        next_btn.grid(row=3, column=0, pady=(10,0))

    def _show_locker_selection(self):
        taker = self.name_var.get().strip()
        if not taker:
            messagebox.showwarning("输入错误", "请输入取物人姓名！")
            return
        self.taker_name = taker

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

        back_btn = tk.Button(scrollable, text="返回", bg='#CCCCCC', font=('微软雅黑',10), width=8,
                             command=self.show_name_input)
        back_btn.grid(row=0, column=0, sticky='nw', pady=(0,20))

        tk.Label(scrollable, text="选择要取物的柜子", bg='#f0f0f0', font=('微软雅黑',16,'bold')).grid(row=1, column=0, columnspan=4, pady=(0,20))

        # 图例
        legend = tk.Frame(scrollable, bg='#f0f0f0')
        legend.grid(row=2, column=0, columnspan=4, pady=(0,20))
        tk.Label(legend, text="有物品", bg='#4CAF50', fg='white', width=8).pack(side=tk.LEFT, padx=5)
        tk.Label(legend, text="无物品", bg='#9E9E9E', fg='white', width=8).pack(side=tk.LEFT, padx=5)

        lock_status = lock_manager.read_lock_info()
        locker_items = database_manager.get_locker_items()
        self.locker_buttons = []

        for i in range(1, 9):
            row = 3 + (i-1)//4
            col = (i-1)%4
            status = lock_status.get(i, 0)
            bg = '#4CAF50' if status == 1 else '#9E9E9E'
            state = tk.NORMAL if status == 1 else tk.DISABLED
            item_info = locker_items.get(i, {})
            item_type = item_info.get('item_type', '')
            text = f"{i}号柜\n{item_type}" if item_type else f"{i}号柜"
            btn = tk.Button(scrollable, text=text, bg=bg, fg='white', font=('微软雅黑',10,'bold'),
                            width=10, height=3, state=state,
                            command=lambda lid=i: self._select_locker(lid, locker_items))
            btn.grid(row=row, column=col, padx=10, pady=10)
            self.locker_buttons.append(btn)

        self.info_frame = tk.Frame(scrollable, bg='#f0f0f0')
        self.info_frame.grid(row=5, column=0, columnspan=4, sticky='we', pady=(20,0))
        self._show_default_info()

    def _show_default_info(self):
        for w in self.info_frame.winfo_children():
            w.destroy()
        tk.Label(self.info_frame, text="请选择上方柜子查看物品信息", bg='#f0f0f0', font=('微软雅黑',14)).pack(expand=True, fill='both', pady=50)

    def _select_locker(self, locker_id, locker_items):
        self.selected_locker_id = locker_id
        # 高亮选中的按钮
        for i, btn in enumerate(self.locker_buttons):
            if i+1 == locker_id:
                btn.config(bg='#FF9800')
            else:
                status = 1 if (i+1) in locker_items else 0
                btn.config(bg='#4CAF50' if status==1 else '#9E9E9E')
        self._show_item_info(locker_id, locker_items)

    def _show_item_info(self, locker_id, locker_items):
        for w in self.info_frame.winfo_children():
            w.destroy()
        item = locker_items.get(locker_id)
        if not item:
            tk.Label(self.info_frame, text=f"{locker_id}号柜无物品", bg='#f0f0f0', font=('微软雅黑',14)).pack(expand=True, fill='both', pady=50)
            return
        container = tk.Frame(self.info_frame, bg='#f0f0f0')
        container.pack(expand=True, fill='both', padx=20, pady=20)
        tk.Label(container, text=f"{locker_id}号柜物品信息", bg='#f0f0f0', font=('微软雅黑',16,'bold')).pack()
        tk.Label(container, text=f"物品类型: {item['item_type']}", bg='#f0f0f0', font=('微软雅黑',12)).pack(pady=5)
        photo_path = os.path.join(config.IMAGES_DIR, item['photo_name'])
        if os.path.exists(photo_path):
            # 创建临时标签显示照片
            img_label = tk.Label(container, bg='#f0f0f0')
            img_label.pack(pady=10)
            photo_manager.show_photo_preview(img_label, photo_path)
        take_btn = tk.Button(container, text="确认取物", bg='#4CAF50', fg='white', font=('微软雅黑',12,'bold'),
                             width=15, height=2, command=lambda: self._confirm_take(locker_id, item))
        take_btn.pack(pady=20)

    def _confirm_take(self, locker_id, item):
        confirm = messagebox.askyesno("确认取物", f"确认从 {locker_id} 号柜取物吗？\n\n物品类型: {item['item_type']}\n取物人: {self.taker_name}")
        if not confirm:
            return
        take_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        database_manager.update_take_record(locker_id, self.taker_name, take_time)
        lock_manager.update_lock_info(lock_id=locker_id, status=0)
        messagebox.showinfo("取物成功", f"正在打开 {locker_id} 号柜...\n\n取物成功！\n柜子：{locker_id}号柜\n物品：{item['item_type']}\n取物人：{self.taker_name}")
        self.parent.show_main_interface()

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
