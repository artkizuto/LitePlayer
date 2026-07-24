import os

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QListWidget,
)

from player import AudioPlayer


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # =========================
        # Player
        # =========================
        self.player = AudioPlayer()

        # =========================
        # Window
        # =========================
        self.setWindowTitle("LitePlayer")
        self.resize(420, 600)

        layout = QVBoxLayout()

        # =========================
        # Title
        # =========================
        title = QLabel("🎵 LitePlayer")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        # =========================
        # Widgets
        # =========================
        self.add_playlist_btn = QPushButton("➕ Add Playlist")
        self.playlist_list = QListWidget()

        self.play_btn = QPushButton("▶ Play")
        self.pause_btn = QPushButton("⏸ Pause")

        # =========================
        # Signals
        # =========================
        self.add_playlist_btn.clicked.connect(self.add_playlist)
        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)

        # =========================
        # Layout
        # =========================
        layout.addWidget(title)

        layout.addWidget(self.add_playlist_btn)

        layout.addWidget(QLabel("Playlists"))
        layout.addWidget(self.playlist_list)

        layout.addStretch()

        layout.addWidget(self.play_btn)
        layout.addWidget(self.pause_btn)

        self.setLayout(layout)

    def add_playlist(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Playlist Folder"
        )

        if not folder:
            return

        playlist_name = os.path.basename(folder)

        self.playlist_list.addItem(playlist_name)