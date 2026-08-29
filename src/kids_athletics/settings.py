"""
ゲーム全体の設定ファイル
"""

from pathlib import Path
import sys

if getattr(sys, "frozen", False):
	PROJECT_ROOT = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else Path(sys.executable).resolve().parent
	EXE_DIR = Path(sys.executable).resolve().parent
else:
	PROJECT_ROOT = Path(__file__).resolve().parents[2]
	EXE_DIR = PROJECT_ROOT

IMAGE_DIR = PROJECT_ROOT / "images"
SOUND_DIR = EXE_DIR / "sounds"
if not SOUND_DIR.exists():
	SOUND_DIR = PROJECT_ROOT / "sounds"

HIYOKO_IMAGE_PATH = IMAGE_DIR / "hiyoko.png"
EGG_IMAGE_PATH = IMAGE_DIR / "egg.png"
EGG_SPIN_SOUND_PATH = SOUND_DIR / "egg_spin.wav"
BGM_SOUND_PATH = SOUND_DIR / "bgm.wav"

# ============================
# 画面設定
# ============================

WINDOW_NAME = "Kids Athletics"

# カメラ解像度
WIDTH = 1280
HEIGHT = 720

# フルスクリーン
FULLSCREEN = True

# ============================
# 卵設定
# ============================

# PNG画像サイズ
EGG_SIZE = 120

# 当たり判定半径
EGG_RADIUS = EGG_SIZE // 2

# 出現間隔（秒）
SPAWN_INTERVAL = 3

# ============================
# 卵(横移動)設定
# ============================
# 卵の移動速度(ピクセル/フレーム)
EGG_SPEED_MIN = 3
EGG_SPEED_MAX = 6

# ============================
# ボール設定（カラフルに落ちて触ると跳ね返る）
# ============================
# ボールサイズ（ピクセル）
BALL_SIZE = 60

# 落下初速
BALL_VY_MIN = 4
BALL_VY_MAX = 8

# 重力 (毎フレームの vy 増分)
BALL_GRAVITY = 0.6

# 触れたときの跳ね返り速度（絶対値）
BALL_BOUNCE_VY =  -24

# ボール出現間隔（秒）
SPAWN_INTERVAL_BALL = 2

# ============================
# Pose設定
# ============================

# 全身ランドマーク表示
SHOW_BODY_POINTS = False

# 全身の当たり判定半径
BODY_HIT_RADIUS = 90

# 可視性の閾値
POSE_VISIBILITY = 0.5

# ============================
# スコア
# ============================

SCORE_PER_ITEM = 1

# ============================
# 音声設定
# ============================

# BGMの音量（0.0～1.0）
BGM_VOLUME = 0.5

# ============================
# 色定義(BGR)
# ============================

WHITE = (255, 255, 255)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
