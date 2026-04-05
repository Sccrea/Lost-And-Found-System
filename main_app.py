import tkinter as tk
from tkinter import ttk, messagebox
import database_manager
import cleanup_manager
import lock_manager
from store_ui import StoreUI
from take_ui import TakeUI
import config

class LostAndFoundApp:
    def __init__(self, root):
        self.root = root
        self.root.title("失物招领管理系统")
        self.root.geometry("700x600")
        self.root.configure(bg='#f0f0f0')

        # 初始化数据库和锁信息
        database_manager.init_database()
        # 确保锁信息文件存在（调用一次读取即可自动初始化）
        lock_manager.read_lock_info()

        # 启动后台清理任务
        cleanup_manager.start_cleanup_task()

        # 初始化UI子模块
        self.store_ui = StoreUI(self)
        self.take_ui = TakeUI(self)

        # 显示主界面
        self.show_main_interface()

    def show_main_interface(self):
        self._clear_window()
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both')

        take_btn = tk.Button(main_frame, text="取物品", bg='#4A90E2', fg='white',
                             font=('微软雅黑',16,'bold'), width=15, height=3,
                             command=self.take_ui.show_name_input)
        take_btn.pack(pady=20)

        store_btn = tk.Button(main_frame, text="存物品", bg='#F5A623', fg='white',
                              font=('微软雅黑',16,'bold'), width=15, height=3,
                              command=self.store_ui.show)
        store_btn.pack(pady=10)

        preview_btn = tk.Button(main_frame, text="数据预览", bg='#9C27B0', fg='white',
                                font=('微软雅黑',10), width=10,
                                command=self._show_data_preview)
        preview_btn.pack(side=tk.BOTTOM, anchor=tk.SW, padx=10, pady=10)

    def _show_data_preview(self):
        """数据预览窗口（数据库查看）"""
        preview = tk.Toplevel(self.root)
        preview.title("物品存取记录")
        preview.geometry("900x500")
        preview.configure(bg='#f0f0f0')

        frame = tk.Frame(preview)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("ID","存物时间","物品类型","照片名称","柜子编号","取物时间","取物人")
        tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=scrollbar.set)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor=tk.CENTER)
        tree.column("ID", width=50)
        tree.column("存物时间", width=150)
        tree.column("物品类型", width=100)
        tree.column("照片名称", width=120)
        tree.column("柜子编号", width=80)
        tree.column("取物时间", width=150)
        tree.column("取物人", width=100)

        rows = database_manager.get_all_records()
        for row in rows:
            processed = ["" if v is None else v for v in row]
            tree.insert("", tk.END, values=processed)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)

        close_btn = tk.Button(preview, text="关闭", bg='#CCCCCC', font=('微软雅黑',10), width=10,
                              command=preview.destroy)
        close_btn.pack(pady=10)

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

def main():
    root = tk.Tk()
    app = LostAndFoundApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
