from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPixmap,
)
from PySide6.QtWidgets import QWidget


class BackgroundWidget(QWidget):

    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        self.pixmap = QPixmap()

        self.opacity = self.settings.get(
            "background_opacity",
            30
        ) / 100

        self.mode = self.settings.get(
            "background_mode",
            "Fit"
        )

        self.load_background()

    # ------------------------------

    def load_background(self):

        path = self.settings.get(
            "background",
            ""
        )

        if path:
            self.pixmap.load(path)

        self.update()

    # ------------------------------

    def set_background(self, path):

        self.settings["background"] = path

        self.load_background()

    # ------------------------------

    def set_opacity(self, value):

        self.opacity = value / 100

        self.settings["background_opacity"] = value

        self.update()

    # ------------------------------

    def set_mode(self, mode):

        self.mode = mode

        self.settings["background_mode"] = mode

        self.update()

    # ------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.SmoothPixmapTransform
        )

        if not self.pixmap.isNull():

            painter.setOpacity(self.opacity)

            rect = self.rect()

            # ----------------------
            # FIT
            # ----------------------

            if self.mode == "Fit":

                scaled = self.pixmap.scaled(
                    rect.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                x = (rect.width() - scaled.width()) // 2
                y = (rect.height() - scaled.height()) // 2

                painter.drawPixmap(x, y, scaled)

            # ----------------------
            # FILL
            # ----------------------

            elif self.mode == "Fill":

                scaled = self.pixmap.scaled(
                    rect.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )

                x = (scaled.width() - rect.width()) // 2
                y = (scaled.height() - rect.height()) // 2

                painter.drawPixmap(
                    rect,
                    scaled,
                    QRect(
                        x,
                        y,
                        rect.width(),
                        rect.height()
                    )
                )

            # ----------------------
            # STRETCH
            # ----------------------

            else:

                painter.drawPixmap(
                    rect,
                    self.pixmap
                )

        # Overlay

        painter.setOpacity(1)

        painter.fillRect(
            self.rect(),
            QColor(
                255,
                255,
                255,
                35
            )
        )