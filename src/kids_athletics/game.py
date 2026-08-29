import cv2
import random
import math
import time
import os
from datetime import datetime
from pathlib import Path

import pygame

from kids_athletics import settings
from kids_athletics.sprite import SpriteManager
from kids_athletics.pose_detector import PoseDetector


class KidsAthleticsGame:

    def __init__(self):

        # -----------------------------
        # カメラ
        # -----------------------------
        self.cap = cv2.VideoCapture(0)

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            settings.WIDTH
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            settings.HEIGHT
        )

        # -----------------------------
        # フルスクリーン
        # -----------------------------
        cv2.namedWindow(
            settings.WINDOW_NAME,
            cv2.WINDOW_NORMAL
        )

        if settings.FULLSCREEN:

            cv2.setWindowProperty(
                settings.WINDOW_NAME,
                cv2.WND_PROP_FULLSCREEN,
                cv2.WINDOW_FULLSCREEN
            )

        # -----------------------------
        # クラス生成
        # -----------------------------
        self.sprite = SpriteManager()

        self.detector = PoseDetector()

        # -----------------------------
        # 録画関連の初期化
        # -----------------------------
        self.recording = False
        self.writer = None
        self.records_folder = os.path.join(os.getcwd(), "records")

        os.makedirs(self.records_folder, exist_ok=True)

        # -----------------------------
        # ゲーム状態
        # -----------------------------
        self.score = 0

        self.objects = []

        self.last_spawn_egg = time.time()
        self.last_spawn_ball = time.time()

        self.egg_spin_sound = None
        self.bgm_ready = False
        self.load_audio()

        # ひよこ画像の読み込み
        hiyoko_path = Path(settings.HIYOKO_IMAGE_PATH)
        self.hiyoko_img = None
        # 卵画像の読み込み
        egg_path = Path(settings.EGG_IMAGE_PATH)
        self.egg_img = None
        try:
            img = cv2.imread(str(hiyoko_path), cv2.IMREAD_UNCHANGED)
            if img is not None:
                self.hiyoko_img = cv2.resize(
                    img,
                    (
                        settings.EGG_SIZE,
                        settings.EGG_SIZE
                    )
                )
        except Exception:
            self.hiyoko_img = None

        try:
            img = cv2.imread(str(egg_path), cv2.IMREAD_UNCHANGED)
            if img is not None:
                self.egg_img = cv2.resize(
                    img,
                    (
                        settings.EGG_SIZE,
                        settings.EGG_SIZE
                    )
                )
        except Exception:
            self.egg_img = None
    # ------------------------------------
    # 卵オブジェクト生成
    # ------------------------------------

    def load_audio(self):
        sound_dir = Path(settings.SOUND_DIR)
        egg_sound_path = Path(settings.EGG_SPIN_SOUND_PATH)
        bgm_path = Path(settings.BGM_SOUND_PATH)

        has_sound_files = sound_dir.is_dir() and any(sound_dir.iterdir())

        if not has_sound_files:
            self.egg_spin_sound = None
            self.bgm_ready = False
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            return

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # 卵タッチ時の効果音
        try:
            if egg_sound_path.exists() and egg_sound_path.is_file():
                self.egg_spin_sound = pygame.mixer.Sound(str(egg_sound_path))
                self.egg_spin_sound.set_volume(0.8)
            else:
                self.egg_spin_sound = None
        except Exception:
            self.egg_spin_sound = None

        # BGM
        try:
            if bgm_path.exists() and bgm_path.is_file():
                pygame.mixer.music.load(str(bgm_path))
                pygame.mixer.music.set_volume(settings.BGM_VOLUME)
                self.bgm_ready = True
            else:
                self.bgm_ready = False
        except Exception:
            self.bgm_ready = False

    def create_egg(self):

        # 卵を左右どちらかから流す設定
        from_left = random.choice([True, False])

        if from_left:
            x = -settings.EGG_SIZE
            vx = random.randint(settings.EGG_SPEED_MIN, settings.EGG_SPEED_MAX)
        else:
            x = settings.WIDTH + settings.EGG_SIZE
            vx = -random.randint(settings.EGG_SPEED_MIN, settings.EGG_SPEED_MAX)

        return {
            "x": x,
            "y": random.randint(settings.EGG_RADIUS, settings.HEIGHT - settings.EGG_RADIUS),
            "vx": vx,
            "type": "egg",
            "state": "normal",  # normal, spinning, hiyoko
            "angle": 0,
            "spin_start": None
        }

    def create_ball(self):
        size = settings.BALL_SIZE

        side = random.choice(["top", "left", "right"])

        # default (top)
        x = random.randint(size, settings.WIDTH - size)
        y = -size
        vx = 0
        vy = random.uniform(settings.BALL_VY_MIN, settings.BALL_VY_MAX)

        if side == "left":
            x = -size
            y = random.randint(size, settings.HEIGHT - size)
            vx = random.uniform(2.0, 6.0)
            vy = random.uniform(-2.0, 4.0)

        elif side == "right":
            x = settings.WIDTH + size
            y = random.randint(size, settings.HEIGHT - size)
            vx = -random.uniform(2.0, 6.0)
            vy = random.uniform(-2.0, 4.0)

        return {
            "x": x,
            "y": y,
            "vx": vx,
            "vy": vy,
            "type": "ball",
            "radius": size // 2,
            "color": (
                random.randint(40, 255),
                random.randint(40, 255),
                random.randint(40, 255),
            ),
            "last_bounce": 0,
        }

    # ------------------------------------
    # オブジェクト出現
    # ------------------------------------

    def spawn(self):

        now = time.time()

        if (now - self.last_spawn_egg) > settings.SPAWN_INTERVAL:

            self.objects.append(self.create_egg())

            self.last_spawn_egg = now

        if (now - self.last_spawn_ball) > settings.SPAWN_INTERVAL_BALL:

            self.objects.append(self.create_ball())

            self.last_spawn_ball = now

    # ------------------------------------
    # アイテム更新
    # ------------------------------------

    def update_items(self):

        remove = []

        for item in self.objects:

            # 卵は横移動、ボールは重力で落下
            if item.get("type") == "egg":
                item["x"] += item.get("vx", 0)

                if (
                    item["x"] < -settings.EGG_SIZE
                    or
                    item["x"] > settings.WIDTH + settings.EGG_SIZE
                ):
                    remove.append(item)

                # ひよこ表示が終わったら除去
                if item.get("state") == "hiyoko":
                    start = item.get("hiyoko_start")
                    if start and (time.time() - start > 2.0):
                        remove.append(item)

            elif item.get("type") == "ball":
                # 重力と垂直移動
                # 横移動も反映
                item["x"] += item.get("vx", 0)
                item["vy"] += settings.BALL_GRAVITY
                item["y"] += item.get("vy", 0)

                # 下端に到達したら少し跳ね返す（地面の反発）
                if item["y"] > settings.HEIGHT - item.get("radius", settings.BALL_SIZE // 2):
                    # 地面に衝突したら小さく跳ね返す
                    item["y"] = settings.HEIGHT - item.get("radius", settings.BALL_SIZE // 2)
                    item["vy"] = -abs(item.get("vy", 0)) * 0.5

                    # 速度が小さくなったら除去
                    if abs(item["vy"]) < 1.0:
                        remove.append(item)

            else:
                # 既存の垂直オブジェクトの処理（互換性あり）
                item["y"] += item.get("speed", 0)
                if item.get("y") > settings.HEIGHT + settings.EGG_SIZE:
                    remove.append(item)

        for item in remove:
            self.objects.remove(item)

    # ------------------------------------
    # 当たり判定
    # ------------------------------------

    def check_collision(
        self,
        body_points
    ):

        remove = []

        for item in self.objects:

            hit = False

            # 反応箇所は両手首のみ（存在しない場合はフォールバックで body_points を使う）
            wrist_points = []
            if hasattr(self.detector, "last_points") and self.detector.last_points:
                lp = self.detector.last_points
                if "l_wrist" in lp:
                    wrist_points.append(lp["l_wrist"])
                if "r_wrist" in lp:
                    wrist_points.append(lp["r_wrist"])

            if len(wrist_points) == 0:
                search_points = body_points
            else:
                search_points = wrist_points

            for bx, by in search_points:


                # 判定点とフルーツ中心の距離
                fx = item.get("x", 0)
                fy = item.get("y", 0)

                distance = math.hypot(bx - fx, by - fy)

                if distance < settings.BODY_HIT_RADIUS:

                    # 卵
                    if item.get("type") == "egg" and item.get("state") == "normal":

                        item["state"] = "spinning"
                        item["spin_start"] = time.time()

                        # 音声が指定されていれば再生
                        if self.egg_spin_sound is not None:
                            try:
                                self.egg_spin_sound.stop()
                                self.egg_spin_sound.play()
                            except Exception:
                                pass

                        hit = True
                        break

                    # ボール: 触れたら跳ね返す
                    if item.get("type") == "ball":

                        # 短時間の連続バウンスを防止
                        now = time.time()
                        if now - item.get("last_bounce", 0) > 0.15:
                            item["vy"] = settings.BALL_BOUNCE_VY
                            item["last_bounce"] = now

                        hit = True
                        break

                    # 既存の垂直オブジェクト
                    else:

                        self.score += settings.SCORE_PER_ITEM

                        hit = True

                        break

            if hit:

                # 卵とボールは当たっても削除せず挙動を継続する
                if item.get("type") not in ("egg", "ball"):
                    remove.append(item)

        for item in remove:

            self.objects.remove(item)

    # ------------------------------------
    # アイテム描画
    # ------------------------------------

    def draw_items(
        self,
        frame
    ):

        for item in self.objects:

            fx = int(item.get("x", 0))
            fy = int(item.get("y", 0))

            if item.get("type") == "egg":

                state = item.get("state", "normal")

                if self.egg_img is not None:

                    if state == "normal":
                        try:
                            self.sprite.overlay_png(
                                frame,
                                self.egg_img,
                                int(fx - settings.EGG_SIZE / 2),
                                int(fy - settings.EGG_SIZE / 2)
                            )
                        except Exception:
                            pass

                    elif state == "spinning":
                        # 回転アニメーション（卵画像がぐるぐる）
                        item["angle"] = (item.get("angle", 0) + 40) % 360
                        angle = item.get("angle", 0)
                        center = (settings.EGG_SIZE // 2, settings.EGG_SIZE // 2)
                        rot = cv2.getRotationMatrix2D(center, angle, 1.0)
                        rotated = cv2.warpAffine(
                            self.egg_img,
                            rot,
                            (settings.EGG_SIZE, settings.EGG_SIZE),
                            flags=cv2.INTER_LINEAR,
                            borderMode=cv2.BORDER_CONSTANT,
                            borderValue=(0, 0, 0, 0)
                        )
                        try:
                            self.sprite.overlay_png(
                                frame,
                                rotated,
                                int(fx - settings.EGG_SIZE / 2),
                                int(fy - settings.EGG_SIZE / 2)
                            )
                        except Exception:
                            pass

                        # スピン完了判定（1.2秒）
                        if item.get("spin_start") and (time.time() - item["spin_start"] > 1.2):

                            item["state"] = "hiyoko"
                            item["hiyoko_start"] = time.time()
                            item["vx"] = 0
                            # スコア加算
                            self.score += settings.SCORE_PER_ITEM
                    else:
                        # それ以外は卵画像をそのまま表示
                        try:
                            self.sprite.overlay_png(
                                frame,
                                self.egg_img,
                                int(fx - settings.EGG_SIZE / 2),
                                int(fy - settings.EGG_SIZE / 2)
                            )
                        except Exception:
                            pass

                else:
                    # 画像がない場合は従来の円描画でフォールバック
                    if state == "normal":
                        cv2.ellipse(
                            frame,
                            (fx, fy),
                            (settings.EGG_RADIUS, int(settings.EGG_RADIUS * 1.2)),
                            0,
                            0,
                            360,
                            settings.WHITE,
                            -1
                        )
                    elif state == "spinning":
                        item["angle"] = (item.get("angle", 0) + 40) % 360
                        angle = int(item.get("angle", 0))
                        cv2.ellipse(
                            frame,
                            (fx, fy),
                            (settings.EGG_RADIUS, int(settings.EGG_RADIUS * 1.2)),
                            angle,
                            0,
                            360,
                            settings.WHITE,
                            -1
                        )

                        if item.get("spin_start") and (time.time() - item["spin_start"] > 1.2):
                            item["state"] = "hiyoko"
                            item["hiyoko_start"] = time.time()
                            item["vx"] = 0
                            self.score += settings.SCORE_PER_ITEM
                    elif state == "hiyoko":
                        pass

                # ひよこ表示は卵描画の後で共通処理
                if state == "hiyoko":

                    # ひよこ画像を卵の位置に重ねる（存在しない場合はテキスト）
                    if self.hiyoko_img is not None:

                        h, w = self.hiyoko_img.shape[:2]

                        x0 = int(fx - w / 2)
                        y0 = int(fy - h / 2)

                        try:
                            self.sprite.overlay_png(frame, self.hiyoko_img, x0, y0)
                        except Exception:
                            pass

                    else:

                        cv2.putText(frame, "(ひよこ)", (fx - 30, fy), cv2.FONT_HERSHEY_SIMPLEX, 0.8, settings.YELLOW, 2)

            elif item.get("type") == "ball":

                # カラフルなボールを描画
                r = int(item.get("radius", settings.BALL_SIZE // 2))
                color = item.get("color", (255, 128, 128))
                cv2.circle(frame, (fx, fy), r, color, -1)
                cv2.circle(frame, (fx, fy), r, (0, 0, 0), 2)

            else:

                # 既存のPNGオブジェクトはSpriteManagerに描画を任せる
                self.sprite.draw(frame, item.get("type"), fx, fy)

    # ------------------------------------
    # GOOD表示
    # ------------------------------------

    def draw_effect(
        self,
        frame
    ):

        # エフェクトは完全に無効化（GOOD! と黄色い円を表示しない）
        return

    # ------------------------------------
    # スコア表示
    # ------------------------------------

    def draw_score(
        self,
        frame
    ):
        # スコア表示は無効化
        return

    # ------------------------------------
    # メインループ
    # ------------------------------------

    def run(self):
        try:
            while True:

                ret, frame = self.cap.read()

                if not ret:
                    break

                # 左右反転
                frame = cv2.flip(frame, 1)

                # 解像度を統一
                frame = cv2.resize(
                    frame,
                    (
                        settings.WIDTH,
                        settings.HEIGHT
                    )
                )

                # -----------------------------
                # Pose検出
                # -----------------------------

                body_points = self.detector.detect(frame)

                # デバッグ表示
                self.detector.draw(
                    frame,
                    body_points
                )

                # -----------------------------
                # ゲーム更新
                # -----------------------------

                self.spawn()

                self.update_items()

                self.check_collision(
                    body_points
                )

                # -----------------------------
                # 描画
                # -----------------------------

                self.draw_items(frame)

                self.draw_effect(frame)

                self.draw_score(frame)

                # BGM再生開始
                if self.bgm_ready and not pygame.mixer.music.get_busy():
                    try:
                        pygame.mixer.music.play(-1)
                    except Exception:
                        pass

                # 終了方法表示
                cv2.putText(

                    frame,

                    "ESC : EXIT",

                    (
                        settings.WIDTH - 260,
                        50
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.9,

                    settings.WHITE,

                    2

                )

                # 録画フレーム書き出し
                if self.recording and self.writer is not None:
                    try:
                        self.writer.write(frame)
                    except Exception:
                        pass

                # 表示
                cv2.imshow(
                    settings.WINDOW_NAME,
                    frame
                )

                key = cv2.waitKey(1) & 0xFF

                # ESCで終了
                if key == 27:
                    break

                # 'r'で録画開始/停止トグル
                if key == ord("r"):
                    if not self.recording:
                        self.start_recording()
                    else:
                        self.stop_recording()
        finally:
            self.close()

    # ------------------------------------
    # 終了処理
    # ------------------------------------

    def close(self):

        self.detector.release()

        self.cap.release()

        # 録画停止
        if self.writer is not None:
            try:
                self.writer.release()
            except Exception:
                pass

        cv2.destroyAllWindows()

    # ------------------------------------
    # 録画制御
    # ------------------------------------

    def start_recording(self):

        if self.recording:
            return

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = os.path.join(
            self.records_folder,
            f"record_{ts}.mp4"
        )

        try:
            self.writer = cv2.VideoWriter(
                filename,
                fourcc,
                20.0,
                (settings.WIDTH, settings.HEIGHT)
            )

            if not self.writer.isOpened():
                self.writer = None
                return

            self.recording = True
        except Exception:
            self.writer = None
            self.recording = False

    def stop_recording(self):

        if not self.recording:
            return

        try:
            if self.writer is not None:
                self.writer.release()
        except Exception:
            pass

        self.writer = None
        self.recording = False

    def draw_recording_indicator(self, frame):

        if not self.recording:
            return

        # 赤丸とRECテキスト
        cv2.circle(
            frame,
            (settings.WIDTH - 60, 40),
            12,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            frame,
            "REC",
            (settings.WIDTH - 110, 48),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )
