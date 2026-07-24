from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
)

from player import AudioPlayer


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.player = AudioPlayer()

        self.setWindowTitle("LitePlayer")
        self.resize(420, 600)

        layout = QVBoxLayout()

        title = QLabel("🎵 LitePlayer")
        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        self.open_btn = QPushButton("Open MP3")
        self.play_btn = QPushButton("▶ Play")
        self.pause_btn = QPushButton("⏸ Pause")

        self.open_btn.clicked.connect(self.open_file)
        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)

        layout.addWidget(title)
        layout.addWidget(self.open_btn)
        layout.addStretch()
        layout.addWidget(self.play_btn)
        layout.addWidget(self.pause_btn)

        self.setLayout(layout)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open MP3",
            "",
            "Music Files (*.mp3 *.wav *.flac)"
        )

        if file_path:
            self.player.load(file_path)