import os

# 获取当前文件所在目录的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 各子目录路径
FILES_DIR = os.path.join(BASE_DIR, "files")
TEMP_DIR = os.path.join(FILES_DIR, "temp")
IMAGES_DIR = os.path.join(FILES_DIR, "images")
DB_PATH = os.path.join(FILES_DIR, "lost_and_found.db")
LOCK_INFO_PATH = os.path.join(FILES_DIR, "lock_info")
COUNT_FILE_PATH = os.path.join(FILES_DIR, "count")

# 确保目录存在
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
