import cv2
import numpy as np

from kids_athletics import settings
from kids_athletics.game import KidsAthleticsGame


def show_title_screen():
    cv2.namedWindow(settings.WINDOW_NAME, cv2.WINDOW_NORMAL)

    if settings.FULLSCREEN:
        cv2.setWindowProperty(
            settings.WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )

    while True:
        frame = np.zeros((settings.HEIGHT, settings.WIDTH, 3), dtype=np.uint8)
        frame[:] = (60, 120, 180)

        cv2.putText(
            frame,
            "Kids Athletics",
            (int(settings.WIDTH * 0.08), int(settings.HEIGHT * 0.35)),
            cv2.FONT_HERSHEY_DUPLEX,
            3.0,
            settings.WHITE,
            6,
        )

        cv2.putText(
            frame,
            "Press SPACE to Start",
            (int(settings.WIDTH * 0.08), int(settings.HEIGHT * 0.55)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.6,
            settings.WHITE,
            3,
        )

        cv2.putText(
            frame,
            "Press ESC to Exit",
            (int(settings.WIDTH * 0.08), int(settings.HEIGHT * 0.65)),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            settings.WHITE,
            2,
        )

        cv2.imshow(settings.WINDOW_NAME, frame)

        key = cv2.waitKey(30) & 0xFF

        if key == 27:
            return False

        if key == 32:
            return True


def main():
    while True:
        start = show_title_screen()

        if not start:
            break

        game = KidsAthleticsGame()
        game.run()
