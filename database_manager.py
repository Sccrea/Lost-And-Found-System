import sqlite3
import config
from datetime import datetime

def init_database():
    """初始化数据库表"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_time TEXT NOT NULL,
            item_type TEXT NOT NULL,
            photo_name TEXT NOT NULL,
            locker_id INTEGER NOT NULL,
            take_time TEXT,
            taker_name TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_item_record(store_time, item_type, photo_name, locker_id):
    """存入物品记录"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO item_records (store_time, item_type, photo_name, locker_id) VALUES (?, ?, ?, ?)",
        (store_time, item_type, photo_name, locker_id)
    )
    conn.commit()
    conn.close()

def update_take_record(locker_id, taker_name, take_time):
    """更新取物记录（将对应柜子的未取记录标记为已取）"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE item_records SET take_time = ?, taker_name = ? WHERE locker_id = ? AND take_time IS NULL",
        (take_time, taker_name, locker_id)
    )
    conn.commit()
    conn.close()

def get_locker_items():
    """获取所有柜子中尚未取出的物品信息，返回 {locker_id: {'item_type':..., 'photo_name':...}}"""
    locker_items = {}
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT locker_id, item_type, photo_name FROM item_records WHERE take_time IS NULL")
    for locker_id, item_type, photo_name in cursor.fetchall():
        locker_items[locker_id] = {'item_type': item_type, 'photo_name': photo_name}
    conn.close()
    return locker_items

def get_all_records():
    """获取所有记录（用于数据预览）"""
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM item_records ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_old_records_and_photos(before_date_str):
    """
    删除指定日期之前的记录及对应照片，返回 (删除记录数, 删除照片数)
    before_date_str: 格式 "YYYY-MM-DD HH:MM:SS"
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    # 查询要删除的记录中的照片名
    cursor.execute("SELECT photo_name FROM item_records WHERE store_time < ?", (before_date_str,))
    old_records = cursor.fetchall()
    photo_deleted = 0
    for (photo_name,) in old_records:
        if photo_name:
            photo_path = os.path.join(config.IMAGES_DIR, photo_name)
            try:
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                    photo_deleted += 1
            except Exception as e:
                print(f"删除照片失败 {photo_path}: {e}")
    # 删除数据库记录
    cursor.execute("DELETE FROM item_records WHERE store_time < ?", (before_date_str,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count, photo_deleted
