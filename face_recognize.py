import cv2
import numpy as np
import json
import os
import time
from collections import Counter, deque
from insightface.app import FaceAnalysis


def filter_faces(raw_boxes, raw_scores, iou_threshold=0.25, min_ratio=0.5, max_ratio=2.0):
    if len(raw_boxes) == 0:
        return []
    valid_idx, valid_boxes, valid_scores = [], [], []
    for i, bbox in enumerate(raw_boxes):
        w, h = bbox[2], bbox[3]
        if w <= 0 or h <= 0:
            continue
        ratio = w / h
        if min_ratio <= ratio <= max_ratio:
            valid_idx.append(i)
            valid_boxes.append(bbox)
            valid_scores.append(raw_scores[i])
    if not valid_boxes:
        return []

    boxes = np.array(valid_boxes)
    scores = np.array(valid_scores)
    x1, y1 = boxes[:, 0], boxes[:, 1]
    x2, y2 = boxes[:, 0] + boxes[:, 2], boxes[:, 1] + boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter + 1e-7)
        inds = np.where(ovr <= iou_threshold)[0]
        order = order[inds + 1]
    return [valid_idx[k] for k in keep]


class FaceRecognition:
    def __init__(self, db_path="face_db_v4.json"):
        self.app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(320, 320), det_thresh=0.85)

        self.db_path = db_path
        self.face_database = self.load_database()
        self.dist_threshold = 0.35
        self.max_faces = 3

        # 跟踪
        self.next_id = 0
        self.trackers = {}
        self.max_lost = 3
        self.max_trackers = 8
        self.history_len = 15

    def load_database(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, "r") as f:
                return json.load(f)
        return {}

    def save_database(self):
        with open(self.db_path, "w") as f:
            json.dump(self.face_database, f, indent=4)

    def register_user(self, name, num_samples=15):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[错误] 无法打开摄像头")
            return
        samples = []
        print(f"录入 {name}，请面对摄像头...")
        try:
            while len(samples) < num_samples:
                ret, frame = cap.read()
                if not ret:
                    break
                faces = self._detect(frame)
                if faces:
                    face = max(faces, key=lambda f: f['bbox'][2] * f['bbox'][3])
                    emb = face['embedding']
                    rect = face['bbox']
                    h, w = frame.shape[:2]
                    if rect[2] * rect[3] >= 0.08 * h * w:
                        samples.append(emb)
                cv2.putText(frame, f"Captured: {len(samples)}/{num_samples}", (50, 50), 1, 2, (0, 255, 0), 2)
                cv2.imshow("Registration", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

        if len(samples) >= num_samples:
            avg = np.mean(samples, axis=0)
            avg /= np.linalg.norm(avg) + 1e-7
            self.face_database[str(int(time.time()))] = {"name": name, "features": avg.tolist()}
            self.save_database()
            print(f"{name} 注册成功")
        else:
            print("注册失败")

    def _detect(self, img_bgr):
        faces = self.app.get(img_bgr)
        if len(faces) == 0:
            return []
        faces_sorted = sorted(faces, key=lambda f: f.det_score, reverse=True)[:self.max_faces]
        raw_boxes, raw_scores, raw_embs = [], [], []
        for face in faces_sorted:
            bbox = face.bbox.astype(int)
            h, w = img_bgr.shape[:2]
            x1, y1, x2, y2 = max(0, bbox[0]), max(0, bbox[1]), min(w, bbox[2]), min(h, bbox[3])
            rect = [x1, y1, x2 - x1, y2 - y1]
            if rect[2] <= 0 or rect[3] <= 0:
                continue
            raw_boxes.append(rect)
            raw_scores.append(face.det_score)
            emb = face.embedding / (np.linalg.norm(face.embedding) + 1e-7)
            raw_embs.append(emb)
        keep_idx = filter_faces(raw_boxes, raw_scores, iou_threshold=0.3)
        return [{'bbox': raw_boxes[i], 'embedding': raw_embs[i]} for i in keep_idx]

    @staticmethod
    def _cosine(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-7)

    @staticmethod
    def _iou(boxA, boxB):
        xA, yA = max(boxA[0], boxB[0]), max(boxA[1], boxB[1])
        xB, yB = min(boxA[0] + boxA[2], boxB[0] + boxB[2]), min(boxA[1] + boxA[3], boxB[1] + boxB[3])
        inter = max(0, xB - xA) * max(0, yB - yA)
        areaA, areaB = boxA[2] * boxA[3], boxB[2] * boxB[3]
        return inter / (areaA + areaB - inter + 1e-7)

    def _match_name(self, emb):
        best_sim, best_name = -1.0, "Unknown"
        for uid, data in self.face_database.items():
            db = np.array(data['features'])
            if db.shape[0] != emb.shape[0]:
                continue
            sim = self._cosine(emb, db)
            if sim > best_sim and sim > self.dist_threshold:
                best_sim, best_name = sim, data['name']
        return best_name

    def run_recognition(self):
        """
        打开摄像头，实时人脸识别。
        返回: 识别到的用户名(str)，手动退出返回 None
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[错误] 无法打开摄像头")
            return None

        recognized_name = None
        self.trackers.clear()
        self.next_id = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # 检测
                faces = self._detect(frame)
                det_boxes = [f['bbox'] for f in faces]
                det_embs = [f['embedding'] for f in faces]

                # IOU 匹配
                used_ids = set()
                all_trackers = dict(self.trackers)

                for i, dbox in enumerate(det_boxes):
                    best_tid, best_iou = None, 0.3
                    for tid, tdata in all_trackers.items():
                        if tid in used_ids:
                            continue
                        iou_val = self._iou(dbox, tdata["bbox"])
                        if iou_val > best_iou:
                            best_iou, best_tid = iou_val, tid
                    if best_tid is not None:
                        self.trackers[best_tid]["bbox"] = dbox
                        self.trackers[best_tid]["lost"] = 0
                        self.trackers[best_tid]["last_emb"] = det_embs[i]
                        used_ids.add(best_tid)
                    else:
                        if len(self.trackers) < self.max_trackers:
                            new_id = self.next_id
                            self.next_id += 1
                            self.trackers[new_id] = {
                                "bbox": dbox,
                                "history": deque(maxlen=self.history_len),
                                "lost": 0,
                                "last_emb": det_embs[i]
                            }

                for tid in list(self.trackers.keys()):
                    if tid not in used_ids:
                        self.trackers[tid]["lost"] += 1
                    if self.trackers[tid]["lost"] > self.max_lost:
                        del self.trackers[tid]

                # 识别 + 绘制
                current_name = None

                for tid, tdata in self.trackers.items():
                    name = "Unknown"
                    if "last_emb" in tdata:
                        name = self._match_name(tdata["last_emb"])
                        tdata["history"].append(name)
                        if tdata["history"]:
                            name = Counter(tdata["history"]).most_common(1)[0][0]

                    bbox = tdata["bbox"]
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (bbox[0], bbox[1]),
                                  (bbox[0] + bbox[2], bbox[1] + bbox[3]), color, 2)
                    cv2.putText(frame, name, (bbox[0], bbox[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                    if name != "Unknown" and current_name is None:
                        current_name = name

                if current_name is not None:
                    recognized_name = current_name
                    cv2.putText(frame, f"Recognized: {recognized_name} - Exiting...",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.imshow("Face Recognition, Press Q to Quit", frame)
                    cv2.waitKey(1500)
                    break

                cv2.imshow("Face Recognition, Press Q to Quit", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()

        return recognized_name


# ==================== 使用示例 ====================
if __name__ == "__main__":
    fr = FaceRecognition()

    # 首次使用先注册（已有数据库可跳过）
   # fr.register_user("张三")

    # 识别
    who = fr.run_recognition()
    print(f"返回值: {who}")
