import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QMouseEvent

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QListWidget,
    QProgressBar,
    QSlider,
)

from player import AudioPlayer


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # =========================
        # Player
        # =========================
        self.player = AudioPlayer()

        # Playlist -> Folder
        self.playlists = {}

        # Song name -> Full path
        self.song_paths = {}

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
            font-size:24px;
            font-weight:bold;
        """)

        # =========================
        # Widgets
        # =========================
        self.add_playlist_btn = QPushButton("➕ Add Playlist")

        self.playlist_list = QListWidget()
        self.song_list = QListWidget()

        self.now_playing = QLabel("Now Playing: Nothing")

        self.progress = QSlider(Qt.Horizontal)
        self.progress.setRange(0, 1000)

        self.current_time = QLabel("00:00")
        self.total_time = QLabel("00:00")

        time_layout = QHBoxLayout()
        time_layout.addWidget(self.current_time)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time)

        self.now_playing.setStyleSheet("font-weight:bold;")

        self.play_btn = QPushButton("▶ Play")
        self.pause_btn = QPushButton("⏸ Pause")

        # =========================
        # Signals
        # =========================
        self.add_playlist_btn.clicked.connect(self.add_playlist)

        self.playlist_list.itemClicked.connect(self.load_playlist)

        self.song_list.itemDoubleClicked.connect(self.play_song)

        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)

        self.progress.sliderMoved.connect(self.seek)
        self.progress.sliderPressed.connect(self.pause_timer)
        self.progress.sliderReleased.connect(self.resume_timer)

        # =========================
        # Layout
        # =========================

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

        right_layout.addWidget(self.now_playing)

        right_layout.addWidget(self.progress)
        right_layout.addLayout(time_layout)

        right_layout.addWidget(self.play_btn)
        right_layout.addWidget(self.pause_btn)

        center_layout.addLayout(left_layout, 1)
        center_layout.addLayout(right_layout, 2)

        # Assemble
        main_layout.addLayout(top_layout)
        main_layout.addLayout(center_layout)

        self.setLayout(main_layout)

        self.timer = QTimer()

        self.timer.timeout.connect(self.update_progress)

        self.timer.start(200)

    def add_playlist(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Playlist Folder"
        )

        if not folder:
            return

        playlist_name = os.path.basename(folder)

        if playlist_name in self.playlists:
            return

        self.playlists[playlist_name] = folder

        self.playlist_list.addItem(playlist_name)

    def load_playlist(self, item):
        self.song_list.clear()
        self.song_paths.clear()

        playlist_name = item.text()

        folder = self.playlists[playlist_name]

        for file_name in sorted(os.listdir(folder)):
            if file_name.lower().endswith((".mp3", ".wav", ".flac")):

                full_path = os.path.join(folder, file_name)

                self.song_paths[file_name] = full_path

                self.song_list.addItem(file_name)

    def play_song(self, item):
        file_name = item.text()

        file_path = self.song_paths[file_name]

        self.player.load(file_path)
        self.player.play()

        self.now_playing.setText(f"Now Playing: {file_name}")

    def format_time(self, ms):
        seconds = ms // 1000

        minutes = seconds // 60

        seconds %= 60

        return f"{minutes:02}:{seconds:02}"

    def update_progress(self):
        duration = self.player.duration()

        if duration <= 0:
            return

        position = self.player.position()

        value = int(position / duration * 1000)

        if not self.progress.isSliderDown():
            self.progress.setValue(value)

        self.current_time.setText(self.format_time(position))

        self.total_time.setText(self.format_time(duration))

    def seek(self, value):
        duration = self.player.duration()

        if duration <= 0:
            return

        position = duration * value // 1000

        self.player.set_position(position)

    def pause_timer(self):
        self.timer.stop()

    def resume_timer(self):
        self.timer.start(200)