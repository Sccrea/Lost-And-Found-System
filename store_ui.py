import tkinter as tk
from tkinter import ttk, messagebox
import photo_manager
import open_lock
import os
import config
import network_manager
import requests

class StoreUI:
    """存物品界面及逻辑"""
    def __init__(self, parent_app):
        self.parent = parent_app  # 主应用实例，用于切换界面
        self.root = parent_app.root
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

        # 存物品按钮
        next_btn = tk.Button(scrollable_frame, text="存物品", bg='#4CAF50', fg='white', font=('微软雅黑',12,'bold'),
                             width=10, command=self._next_step)
        next_btn.grid(row=6, column=0, sticky='w', pady=(10,0))

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _take_photo_wrapper(self):
        if photo_manager.take_photo():
            temp_path = photo_manager.config.TEMP_DIR + "/a.jpg"
            photo_manager.show_photo_preview(self.photo_label, temp_path)

    def _next_step(self):
        temp_photo = os.path.join(config.TEMP_DIR, "a.jpg")
        if not os.path.exists(temp_photo):
            messagebox.showwarning("输入错误", "请先拍照！")
            return
        # 从服务端获取柜子状态
        try:
            lockers = network_manager.get_lockers_status()
        except requests.exceptions.RequestException:
            messagebox.showerror("网络错误", "无法连接至服务器，请检查网络连接")
            return
        free_lock = None
        for lid, info in lockers.items():
            if info['status'] == 0:
                free_lock = lid
                break
        if free_lock is None:
            messagebox.showerror("无空闲柜子", "当前没有空闲柜子，请稍后再试。")
            return
        self._confirm_store(free_lock, temp_photo)

    def _confirm_store(self, locker_id, temp_photo_path):
        confirm = messagebox.askyesno("确认存放", f"确认存放物品到 {locker_id} 号柜吗？")
        if not confirm:
            return
        try:
            # 上传到服务端
            result = network_manager.store_item(locker_id, temp_photo_path)
            photo_name = result['photo_name']
            # 开锁（本地操作）
            open_lock.open_lock(lock_number=locker_id)
            messagebox.showinfo("操作成功", f"正在打开 {locker_id} 号柜...\n\n物品存放成功！")
            self.parent.show_main_interface()
        except requests.exceptions.RequestException:
            messagebox.showerror("网络错误", "无法连接至服务器，请检查网络连接")
        except Exception as e:
            messagebox.showerror("错误", f"存物失败：{e}")