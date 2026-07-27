from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFixedSize(360, 200)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setStyleSheet("""
            QWidget{
                background:white;
                border-radius:18px;
                border:1px solid lightgray;
            }
        """)

        layout = QVBoxLayout(container)

        layout.addStretch()

        title = QLabel("🎵 LitePlayer")
        title.setAlignment(Qt.AlignCenter)

        font = QFont()
        font.setPointSize(24)
        font.setBold(True)

        title.setFont(font)

        loading = QLabel("Preparing Player...")
        loading.setAlignment(Qt.AlignCenter)

        loading.setStyleSheet("""
            color:gray;
            font-size:12px;
        """)

        version = QLabel("v0.4.5")
        version.setAlignment(Qt.AlignCenter)

        version.setStyleSheet("""
            color:#999999;
            font-size:10px;
        """)

        layout.addWidget(title)
        layout.addSpacing(12)
        layout.addWidget(loading)
        layout.addSpacing(6)
        layout.addWidget(version)

        layout.addStretch()

        root.addWidget(container)