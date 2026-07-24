import os

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
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

        # Lưu tên playlist -> đường dẫn
        self.playlists = {}

        # =========================
        # Window
        # =========================
        self.setWindowTitle("LitePlayer")
        self.resize(700, 500)

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
        self.song_list = QListWidget()

        self.play_btn = QPushButton("▶ Play")
        self.pause_btn = QPushButton("⏸ Pause")

        # =========================
        # Signals
        # =========================
        self.add_playlist_btn.clicked.connect(self.add_playlist)

        self.playlist_list.itemClicked.connect(self.load_playlist)

        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)

        # =========================
        # Layout
        # =========================

        # Main Layout
        main_layout = QVBoxLayout()

        # ---------- Top ----------
        top_layout = QHBoxLayout()

        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(self.add_playlist_btn)

        # ---------- Center ----------
        center_layout = QHBoxLayout()

        # Left Panel
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Playlists"))
        left_layout.addWidget(self.playlist_list)

        # Right Panel
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Songs"))
        right_layout.addWidget(self.song_list)

        center_layout.addLayout(left_layout)
        center_layout.addLayout(right_layout)

        # ---------- Bottom ----------
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.play_btn)
        bottom_layout.addWidget(self.pause_btn)

        # Assemble
        main_layout.addLayout(top_layout)
        main_layout.addLayout(center_layout)
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def add_playlist(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Playlist Folder"
        )

        if not folder:
            return

        playlist_name = os.path.basename(folder)

        # Không thêm trùng playlist
        if playlist_name in self.playlists:
            return

        self.playlists[playlist_name] = folder

        self.playlist_list.addItem(playlist_name)

    def load_playlist(self, item):
        self.song_list.clear()

        playlist_name = item.text()

        folder = self.playlists[playlist_name]

        for file_name in sorted(os.listdir(folder)):
            if file_name.lower().endswith((".mp3", ".wav", ".flac")):
                self.song_list.addItem(file_name)