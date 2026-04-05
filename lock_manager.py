import config

def read_lock_info():
    """读取锁信息，返回 {lock_id: status} 字典，status: 0=空闲, 1=已用"""
    lock_status = {}
    try:
        with open(config.LOCK_INFO_PATH, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    lock_id, status = parts
                    lock_status[int(lock_id)] = int(status)
    except FileNotFoundError:
        # 初始化默认锁信息（8个柜子空闲）
        for i in range(1, 9):
            lock_status[i] = 0
        update_lock_info(lock_status)  # 写入文件
    except Exception as e:
        print(f"读取锁信息失败: {e}")
    return lock_status

def update_lock_info(lock_status_dict=None, lock_id=None, status=None):
    """
    更新锁信息。两种调用方式：
    1. update_lock_info(lock_status_dict) 直接传入完整字典
    2. update_lock_info(lock_id, status) 更新单个柜子
    """
    if lock_status_dict is not None:
        data = lock_status_dict
    else:
        data = read_lock_info()
        if lock_id is not None and status is not None:
            data[lock_id] = status
    try:
        with open(config.LOCK_INFO_PATH, 'w') as f:
            for lid, stat in data.items():
                f.write(f"{lid},{stat}\n")
        return True
    except Exception as e:
        print(f"更新锁信息失败: {e}")
        return False
