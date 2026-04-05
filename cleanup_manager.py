import threading
import time
from datetime import datetime, timedelta
import database_manager

def cleanup_old_records():
    """清理超过127天的记录和照片"""
    threshold = (datetime.now() - timedelta(days=127)).strftime("%Y-%m-%d %H:%M:%S")
    deleted, photos = database_manager.delete_old_records_and_photos(threshold)
    if deleted > 0 or photos > 0:
        print(f"已清理 {deleted} 条记录和 {photos} 张照片")

def start_cleanup_task():
    """启动后台清理线程（每小时执行一次）"""
    def task_loop():
        while True:
            try:
                cleanup_old_records()
            except Exception as e:
                print(f"清理任务出错: {e}")
            time.sleep(3600)  # 1小时
    thread = threading.Thread(target=task_loop, daemon=True)
    thread.start()
