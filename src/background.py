import os
import shutil

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

        # Thêm 2 biến mới theo specs
        self.background_type = self.settings.get("background_type", "app_default")
        self.background_color = self.settings.get("background_color", "#808080")

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
        
        if self.background_type == "app_default":
            self.pixmap = QPixmap()  # Fix: Gán lại QPixmap rỗng thay vì .clear()
            
        elif self.background_type == "solid":
            self.pixmap = QPixmap()  # Fix: Gán lại QPixmap rỗng thay vì .clear()
            
        elif self.background_type == "image":
            DATA_DIR = os.path.join(
                os.path.dirname(__file__),
                "data",
                "background"
            )
            os.makedirs(DATA_DIR, exist_ok=True)

            path = self.settings.get("background_file", "")

            if path:
                full_path = os.path.join(DATA_DIR, path)
                if os.path.exists(full_path):
                    self.pixmap.load(full_path)

        self.update()

    # ------------------------------

    def set_background(self, path):

        DATA_DIR = os.path.join(
            os.path.dirname(__file__),
            "data",
            "background"
        )
        os.makedirs(DATA_DIR, exist_ok=True)

        ext = os.path.splitext(path)[1]
        filename = "background" + ext

        destination = os.path.join(DATA_DIR, filename)

        shutil.copy2(path, destination)

        # Cập nhật theo API mới
        self.background_type = "image"
        self.settings["background_type"] = "image"
        self.settings["background_file"] = filename

        self.load_background()

    # ------------------------------
    
    def set_default(self):
        self.background_type = "app_default"
        self.settings["background_type"] = "app_default"
        self.settings["background_file"] = ""
        self.pixmap = QPixmap()  # Fix: Gán lại QPixmap rỗng
        self.update()
        
    # ------------------------------

    def set_color(self, color):
        self.background_type = "solid"
        self.background_color = color.name()
        self.settings["background_type"] = "solid"
        self.settings["background_color"] = self.background_color
        self.pixmap = QPixmap()  # Fix: Gán lại QPixmap rỗng
        self.update()

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
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        rect = self.rect()

        if self.background_type == "app_default":
            # Không vẽ gì cả, trả về nền trong vắt của app
            pass
            
        elif self.background_type == "solid":
            # Đổ màu solid
            painter.fillRect(rect, QColor(self.background_color))
            
        elif self.background_type == "image":
            # Bọc toàn bộ logic Fit/Fill/Stretch cũ vào đây
            if not self.pixmap.isNull():
                painter.setOpacity(self.opacity)

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
                    painter.drawPixmap(rect, self.pixmap)

        # Overlay trắng mờ
        painter.setOpacity(1)
        painter.fillRect(
            self.rect(),
            QColor(255, 255, 255, 35)
        )