# Lost-And-Found-System

失物招领系统 使用Python语言编写

运行main_app.py以启动

以下是失物招领管理系统中所有函数的意义解释，按模块划分。

---

## 1. config.py

| 变量名 | 意义 |
|--------|------|
| `BASE_DIR` | 获取当前文件所在目录的绝对路径，用于定位所有文件资源。 |
| `FILES_DIR` | 存放所有数据文件的根目录（`files/`）。 |
| `TEMP_DIR` | 临时文件目录（`files/temp/`），用于存放拍照时的临时照片。 |
| `IMAGES_DIR` | 存储正式物品照片的目录（`files/images/`）。 |
| `DB_PATH` | SQLite 数据库文件的完整路径（`files/lost_and_found.db`）。 |
| `LOCK_INFO_PATH` | 锁信息文本文件的路径（`files/lock_info`），记录每个柜子的占用状态。 |
| `COUNT_FILE_PATH` | 计数器文件的路径（`files/count`），用于生成唯一照片文件名。 |

> 文件加载时自动创建 `TEMP_DIR` 和 `IMAGES_DIR` 目录。

---

## 2. lock_manager.py

| 函数名 | 参数 | 返回值 | 意义 |
|--------|------|--------|------|
| `read_lock_info()` | 无 | `dict` (lock_id → status) | 读取 `lock_info` 文件，返回所有柜子的状态字典（0=空闲，1=已用）。若文件不存在则自动初始化8个空闲柜子。 |
| `update_lock_info()` | `lock_status_dict=None, lock_id=None, status=None` | `bool` | 更新锁信息。支持两种调用：①传入完整字典 `lock_status_dict`；②传入单个柜子ID和新状态。成功写入文件返回 `True`，否则返回 `False`。 |

---

## 3. photo_manager.py

| 函数名 | 参数 | 返回值 | 意义 |
|--------|------|--------|------|
| `take_photo()` | 无 | `bool` | 打开摄像头，按空格键拍照并保存到 `TEMP_DIR/a.jpg`，按ESC取消。拍照成功返回 `True`，否则 `False`。 |
| `show_photo_preview()` | `photo_label` (tkinter.Label), `photo_path` (str) | 无 | 在指定的 `Label` 控件上显示给定路径的照片，自动缩放至400x300以内保持比例。 |
| `save_temp_photo_to_images()` | `photo_name` (str) | `str` (新路径) | 将临时照片 `a.jpg` 复制到 `IMAGES_DIR` 并重命名为 `photo_name`，返回新文件的完整路径。 |

---

## 4. database_manager.py

| 函数名 | 参数 | 返回值 | 意义 |
|--------|------|--------|------|
| `init_database()` | 无 | 无 | 初始化数据库，创建 `item_records` 表（如果不存在）。表中字段包括：id、存物时间、物品类型、照片名、柜子编号、取物时间、取物人。 |
| `save_item_record()` | `store_time, item_type, photo_name, locker_id` | 无 | 插入一条新的存物记录（取物时间和取物人留空）。 |
| `update_take_record()` | `locker_id, taker_name, take_time` | 无 | 更新指定柜子中**尚未取出**的那条记录，填写取物时间和取物人姓名。 |
| `get_locker_items()` | 无 | `dict` | 查询所有尚未取出的物品，返回字典：`{locker_id: {'item_type':..., 'photo_name':...}}`。 |
| `get_all_records()` | 无 | `list of tuples` | 获取数据库中的所有记录（按ID降序），用于数据预览窗口。 |
| `delete_old_records_and_photos()` | `before_date_str` (str) | `(deleted_count, photo_deleted_count)` | 删除 `store_time` 早于指定日期的记录，同时删除对应的照片文件。返回删除的记录数和照片数。 |

---

## 5. cleanup_manager.py

| 函数名 | 参数 | 返回值 | 意义 |
|--------|------|--------|------|
| `cleanup_old_records()` | 无 | 无 | 计算127天前的日期，调用 `database_manager.delete_old_records_and_photos()` 执行清理，并打印结果。 |
| `start_cleanup_task()` | 无 | 无 | 启动一个后台守护线程，每小时调用一次 `cleanup_old_records()`，实现自动定期清理。 |

---

## 6. counter_manager.py

| 函数名 | 参数 | 返回值 | 意义 |
|--------|------|--------|------|
| `get_next_count()` | 无 | `int` | 读取 `count` 文件中的数字，返回当前值并将文件中的数字加1。若文件不存在则初始化为1并返回1。用于生成递增的照片文件名（如 `1.jpg`、`2.jpg`）。 |

---

## 7. store_ui.py (类 `StoreUI`)

### 类属性
| 属性 | 意义 |
|------|------|
| `parent` | 主应用实例，用于调用界面切换方法。 |
| `root` | Tkinter 根窗口。 |
| `temp_item_type` | 暂存用户选择的物品类型，用于后续存入数据库。 |
| `temp_photo_name` | 暂存拍照后生成的照片文件名。 |
| `item_type_var` | Tkinter 变量，绑定物品类型下拉框。 |
| `photo_label` | 显示照片预览的 Label 控件。 |
| `photo_status` | 显示拍照状态的 Label（“未拍照”/“已拍照”）。 |

### 方法

| 方法名 | 参数 | 返回值 | 意义 |
|--------|------|--------|------|
| `__init__` | `parent_app` | 无 | 初始化界面模块，保存父应用引用。 |
| `show()` | 无 | 无 | 显示存物品的主界面：物品类型下拉框、拍照按钮、照片预览区域、下一步按钮。 |
| `_clear_window()` | 无 | 无 | 清空根窗口中的所有子控件，用于切换界面。 |
| `_take_photo_wrapper()` | 无 | 无 | 调用 `photo_manager.take_photo()` 拍照，若成功则更新状态标签并显示预览。 |
| `_next_step()` | 无 | 无 | 验证物品类型和照片是否已选/拍，若通过则生成新照片文件名、复制照片到正式目录，然后调用 `_show_locker_selection()` 显示柜子选择界面。 |
| `_show_locker_selection()` | 无 | 无 | 显示柜子选择界面：展示8个柜子的状态（空闲绿色/已用红色），空闲柜子可点击。 |
| `_confirm_store()` | `locker_id` (int) | 无 | 弹出确认对话框，用户确认后记录存物时间、更新锁状态为已用、保存到数据库，最后返回主界面。 |

---

## 8. take_ui.py (类 `TakeUI`)

### 类属性
| 属性 | 意义 |
|------|------|
| `parent` | 主应用实例。 |
| `root` | Tkinter 根窗口。 |
| `taker_name` | 暂存取物人姓名。 |
| `selected_locker_id` | 当前选中的柜子ID。 |
| `name_var` | Tkinter 变量，绑定取物人姓名输入框。 |
| `locker_buttons` | 存储柜子按钮的列表，用于高亮选中效果。 |
| `info_frame` | 用于显示物品详情的 Frame 容器。 |

### 方法

| 方法名 | 参数 | 返回值 | 意义 |
|--------|------|--------|------|
| `__init__` | `parent_app` | 无 | 初始化模块，保存父应用引用。 |
| `show_name_input()` | 无 | 无 | 显示姓名输入界面：一个输入框和“下一步”按钮。 |
| `_show_locker_selection()` | 无 | 无 | 根据输入的姓名，显示柜子选择界面：展示有物品的柜子（绿色）和无物品的柜子（灰色）。点击绿色柜子可查看详情。 |
| `_show_default_info()` | 无 | 无 | 在物品信息显示区域显示“请选择上方柜子查看物品信息”的提示。 |
| `_select_locker()` | `locker_id, locker_items` | 无 | 处理柜子按钮点击：高亮选中按钮，并调用 `_show_item_info()` 显示该柜子的物品信息。 |
| `_show_item_info()` | `locker_id, locker_items` | 无 | 在 `info_frame` 中显示选中柜子的物品类型、照片以及“确认取物”按钮。 |
| `_confirm_take()` | `locker_id, item` | 无 | 弹出确认对话框，用户确认后记录取物时间、更新数据库、将锁状态改为空闲，最后返回主界面。 |
| `_clear_window()` | 无 | 无 | 清空根窗口中的所有子控件。 |

---

## 9. main_app.py (类 `LostAndFoundApp`)

### 类属性
| 属性 | 意义 |
|------|------|
| `root` | Tkinter 根窗口。 |
| `store_ui` | `StoreUI` 实例，负责存物品流程。 |
| `take_ui` | `TakeUI` 实例，负责取物品流程。 |

### 方法

| 方法名 | 参数 | 返回值 | 意义 |
|--------|------|--------|------|
| `__init__` | `root` | 无 | 初始化主应用：设置窗口标题和大小、初始化数据库、确保锁信息文件存在、启动后台清理任务、创建 `StoreUI` 和 `TakeUI` 子模块、显示主界面。 |
| `show_main_interface()` | 无 | 无 | 显示主界面：两个大按钮（“取物品”、“存物品”）和一个“数据预览”按钮。 |
| `_show_data_preview()` | 无 | 无 | 创建一个新窗口，使用 `ttk.Treeview` 表格显示数据库中所有记录。 |
| `_clear_window()` | 无 | 无 | 清空根窗口中的所有子控件。 |

---

## 10. 顶层函数 `main()`

| 函数名 | 参数 | 返回值 | 意义 |
|--------|------|--------|------|
| `main()` | 无 | 无 | 程序入口：创建 `tk.Tk` 根窗口，实例化 `LostAndFoundApp`，启动 Tkinter 主事件循环。 |

---

