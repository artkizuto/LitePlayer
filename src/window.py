from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LitePlayer")
        self.resize(420, 600)

        layout = QVBoxLayout()

        title = QLabel("🎵 LitePlayer")
        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        open_btn = QPushButton("Open MP3")

        play_btn = QPushButton("▶ Play")

        pause_btn = QPushButton("⏸ Pause")

        layout.addWidget(title)
        layout.addWidget(open_btn)
        layout.addStretch()
        layout.addWidget(play_btn)
        layout.addWidget(pause_btn)

        self.setLayout(layout)