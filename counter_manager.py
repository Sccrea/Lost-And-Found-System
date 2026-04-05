import config
import os

def _read_current_count():
    """读取当前已使用的最大编号，文件不存在返回0"""
    if not os.path.exists(config.COUNT_FILE_PATH):
        return 0
    with open(config.COUNT_FILE_PATH, 'r') as f:
        return int(f.read().strip())

def _write_count(value):
    """写入计数值"""
    with open(config.COUNT_FILE_PATH, 'w') as f:
        f.write(str(value))

def count():
    """
    获取下一个照片编号（自增1），并返回新值。
    用于生成新照片文件名。
    """
    current = _read_current_count()
    next_val = current + 1
    _write_count(next_val)
    return next_val

def get_count():
    """仅获取当前已使用的最大编号，不增加计数。文件不存在时返回0。"""
    return _read_current_count()
