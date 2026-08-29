import cv2

from kids_athletics import settings


class SpriteManager:

    def __init__(self):
        self.images = {}

    def get_names(self):
        return list(self.images.keys())

    def get(self, name):
        return self.images.get(name)

    def draw(
        self,
        frame,
        name,
        center_x,
        center_y
    ):

        if name not in self.images:
            return

        png = self.images[name]

        h, w = png.shape[:2]

        x = int(center_x - w / 2)
        y = int(center_y - h / 2)

        self.overlay_png(
            frame,
            png,
            x,
            y
        )

    # ------------------------------------
    # PNG重ね合わせ
    # ------------------------------------

    def overlay_png(
        self,
        frame,
        png,
        x,
        y
    ):

        h, w = png.shape[:2]

        if x < 0:
            return

        if y < 0:
            return

        if x + w > frame.shape[1]:
            return

        if y + h > frame.shape[0]:
            return

        if png.shape[2] == 3:

            frame[
                y:y+h,
                x:x+w
            ] = png

            return

        roi = frame[
            y:y+h,
            x:x+w
        ]

        alpha = png[:, :, 3] / 255.0

        for c in range(3):

            roi[:, :, c] = (
                alpha * png[:, :, c]
                + (1 - alpha) * roi[:, :, c]
            )

        frame[
            y:y+h,
            x:x+w
        ] = roi


