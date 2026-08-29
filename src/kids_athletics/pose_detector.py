import cv2
import mediapipe as mp
import math
from kids_athletics import settings


class PoseDetector:

    def __init__(self):

        self.pose = mp.solutions.pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # 使用するランドマークの定義
        self.ids = {
            "nose": 0,

            "l_shoulder": 11,
            "r_shoulder": 12,

            "l_elbow": 13,
            "r_elbow": 14,

            "l_wrist": 15,
            "r_wrist": 16,

            "l_hip": 23,
            "r_hip": 24,

            "l_knee": 25,
            "r_knee": 26,

            "l_ankle": 27,
            "r_ankle": 28,
        }
        # 直近の検出済みランドマーク座標を保持
        self.last_points = {}

    # --------------------------

    def _interpolate(self, p1, p2, step=30):

        x1, y1 = p1
        x2, y2 = p2

        dist = math.hypot(x2 - x1, y2 - y1)

        if dist == 0:
            return [p1]

        count = max(1, int(dist / step))

        pts = []

        for i in range(count + 1):

            t = i / count

            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)

            pts.append((x, y))

        return pts

    # --------------------------

    def detect(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self.pose.process(rgb)

        if not result.pose_landmarks:
            return []

        h, w = frame.shape[:2]

        points = {}

        for name, idx in self.ids.items():

            lm = result.pose_landmarks.landmark[idx]

            if lm.visibility < settings.POSE_VISIBILITY:
                continue

            points[name] = (
                int(lm.x * w),
                int(lm.y * h)
            )

        body = []

        # 主要なランドマーク
        body.extend(points.values())

        # ゲーム側で必要に応じて参照できるよう保持
        self.last_points = points

        # 骨格ライン
        bones = [

            ("nose", "l_shoulder"),
            ("nose", "r_shoulder"),

            ("l_shoulder", "r_shoulder"),

            ("l_shoulder", "l_elbow"),
            ("l_elbow", "l_wrist"),

            ("r_shoulder", "r_elbow"),
            ("r_elbow", "r_wrist"),

            ("l_shoulder", "l_hip"),
            ("r_shoulder", "r_hip"),

            ("l_hip", "r_hip"),

            ("l_hip", "l_knee"),
            ("l_knee", "l_ankle"),

            ("r_hip", "r_knee"),
            ("r_knee", "r_ankle"),
        ]

        for a, b in bones:

            if a not in points:
                continue

            if b not in points:
                continue

            body.extend(
                self._interpolate(
                    points[a],
                    points[b]
                )
            )

        return body

    # --------------------------

    def draw(self, frame, body_points):

        if not settings.SHOW_BODY_POINTS:
            return

        for x, y in body_points:

            cv2.circle(
                frame,
                (x, y),
                5,
                settings.BLUE,
                -1
            )
    # ---------------------------------
    # 終了処理
    # ---------------------------------
    def release(self):
        self.pose.close()
