from PySide6.QtCore import Qt

from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
)

from PySide6.QtWidgets import QWidget


class GlassWidget(QWidget):

    def __init__(self):

        super().__init__()

        self.setAttribute(
            Qt.WA_StyledBackground,
            False
        )

        self.setAutoFillBackground(False)

    # --------------------------

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        rect = self.rect().adjusted(
            1,
            1,
            -1,
            -1
        )

        painter.setPen(
            QPen(
                QColor(
                    255,
                    255,
                    255,
                    130
                ),
                1
            )
        )

        painter.setBrush(
            QColor(
                255,
                255,
                255,
                90
            )
        )

        painter.drawRoundedRect(
            rect,
            12,
            12
        )

        super().paintEvent(event)