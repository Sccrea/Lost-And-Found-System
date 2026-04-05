import cv2
import os
import shutil
from PIL import Image, ImageTk
import config
import tkinter.messagebox as messagebox

def take_photo():
    """拍照，保存到临时文件 config.TEMP_DIR/a.jpg，返回是否成功"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("错误", "无法打开摄像头")
        return False

    temp_path = os.path.join(config.TEMP_DIR, "a.jpg")
    photo_taken = False

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("错误", "无法读取摄像头画面")
            break

        cv2.imshow('Press ESC to quit, Space to take photo', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            cv2.imwrite(temp_path, frame)
            photo_taken = True
            messagebox.showinfo("拍照成功", f"照片已保存")
            break
        elif key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()
    return photo_taken

def show_photo_preview(photo_label, photo_path):
    """在给定的Label控件上显示照片预览"""
    if not os.path.exists(photo_path):
        return
    image = Image.open(photo_path)
    # 限制预览大小
    max_width, max_height = 400, 300
    img_width, img_height = image.size
    scale = min(max_width / img_width, max_height / img_height)
    new_size = (int(img_width * scale), int(img_height * scale))
    resized = image.resize(new_size, Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(resized)
    photo_label.config(image=photo, text="")
    photo_label.image = photo  # 保持引用

def save_temp_photo_to_images(photo_name):
    """将临时照片复制到 images 目录，返回新路径"""
    temp_path = os.path.join(config.TEMP_DIR, "a.jpg")
    new_path = os.path.join(config.IMAGES_DIR, photo_name)
    shutil.copy2(temp_path, new_path)
    return new_path
