import os
import random

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtMultimedia import QMediaPlayer

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QListWidget,
    QSlider,
    QComboBox,
)

from player import AudioPlayer
from settings import load_settings, save_settings
from background import BackgroundWidget
from glass import GlassWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # =========================
        # Player
        # =========================
        self.player = AudioPlayer()

        # Playlist -> Folder
        self.playlists = {}

        # Playlist Engine
        self.current_playlist = []
        self.current_index = -1

        # Load Settings
        self.settings = load_settings()
        self.shuffle = self.settings.get("shuffle", False)
        self.loop = self.settings.get("loop", False)

        # =========================
        # Window
        # =========================
        self.setWindowTitle("LitePlayer")
        self.resize(700, 500)

        # Background Manager (Mới: Dùng BackgroundWidget & Đẩy xuống đáy)
        self.bg = BackgroundWidget(self.settings)
        self.bg.setParent(self)
        self.bg.lower()
        self.bg.resize(self.size())

        # Sliders & Controls
        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(0, 100)
        self.opacity.setValue(self.settings.get("background_opacity", 30))
        self.opacity.setMaximumWidth(120)

        # =========================
        # Title & Search
        # =========================
        title = QLabel("🎵 LitePlayer")
        title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search...")

        # Ctrl+F Shortcut
        shortcut_find = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_find.activated.connect(self.focus_search)

        # ESC Shortcut to clear search
        shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        shortcut_esc.activated.connect(self.clear_search)

        # =========================
        # Widgets
        # =========================
        self.add_playlist_btn = QPushButton("➕ Add Playlist")
        self.background_btn = QPushButton("🖼 Background")

        self.background_mode = QComboBox()
        self.background_mode.addItems(["Fit", "Fill", "Stretch"])
        self.background_mode.setCurrentText(
            self.settings.get("background_mode", "Fit")
        )

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

        self.previous_btn = QPushButton("⏮")
        self.play_btn = QPushButton("▶")
        self.pause_btn = QPushButton("⏸")
        self.next_btn = QPushButton("⏭")
        self.shuffle_btn = QPushButton("🔀")
        self.loop_btn = QPushButton("🔁")

        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(self.settings.get("volume", 50))

        # Set initial button styles based on settings
        if self.shuffle:
            self.shuffle_btn.setStyleSheet("background:#66ccff;")
        if self.loop:
            self.loop_btn.setStyleSheet("background:#66cc66;")

        # Set initial audio volume
        if hasattr(self.player, "audio_output"):
            self.player.audio_output.setVolume(self.volume.value() / 100)

        # =========================
        # Signals
        # =========================
        self.search.textChanged.connect(self.filter_songs)

        self.add_playlist_btn.clicked.connect(self.add_playlist)
        self.background_btn.clicked.connect(self.choose_background)
        self.background_mode.currentTextChanged.connect(self.bg.set_mode)
        self.opacity.valueChanged.connect(self.bg.set_opacity)

        self.playlist_list.itemClicked.connect(self.load_playlist)
        self.song_list.itemDoubleClicked.connect(self.play_song)

        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)

        self.previous_btn.clicked.connect(self.play_previous)
        self.next_btn.clicked.connect(self.play_next)
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.loop_btn.clicked.connect(self.toggle_loop)

        self.player.player.mediaStatusChanged.connect(
            self.media_status_changed
        )

        self.progress.sliderMoved.connect(self.seek)
        self.progress.sliderPressed.connect(self.pause_timer)
        self.progress.sliderReleased.connect(self.resume_timer)

        self.volume.valueChanged.connect(self.on_volume_changed)

        # =========================
        # Layout UI
        # =========================
        main_layout = QVBoxLayout()

        # ---------- Top ----------
        top_layout = QHBoxLayout()

        top_layout.addWidget(title)
        top_layout.addWidget(self.search)
        top_layout.addStretch()
        top_layout.addWidget(QLabel("Opacity"))
        top_layout.addWidget(self.opacity)
        top_layout.addWidget(self.background_btn)
        top_layout.addWidget(self.background_mode)
        top_layout.addWidget(self.add_playlist_btn)

        # ---------- Center (Glass Panels) ----------
        center_layout = QHBoxLayout()

        # Left Panel (Glass)
        left_panel = GlassWidget()

        left_layout = QVBoxLayout(left_panel)
        self.playlist_label = QLabel("Playlists (0)")
        left_layout.addWidget(self.playlist_label)
        left_layout.addWidget(self.playlist_list)

        # Right Panel (Glass)
        right_panel = GlassWidget()

        right_layout = QVBoxLayout(right_panel)
        self.song_label = QLabel("Songs (0)")
        right_layout.addWidget(self.song_label)
        right_layout.addWidget(self.song_list)
        right_layout.addWidget(self.now_playing)
        right_layout.addWidget(self.progress)
        right_layout.addLayout(time_layout)

        controls = QHBoxLayout()
        controls.addWidget(self.previous_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)
        controls.addWidget(self.next_btn)
        controls.addWidget(self.shuffle_btn)
        controls.addWidget(self.loop_btn)

        right_layout.addLayout(controls)

        right_layout.addWidget(QLabel("Volume"))
        right_layout.addWidget(self.volume)

        center_layout.addWidget(left_panel, 1)
        center_layout.addWidget(right_panel, 2)

        # Assemble
        main_layout.addLayout(top_layout)
        main_layout.addLayout(center_layout)

        version = QLabel("v0.2.0")
        version.setStyleSheet("""
            color:gray;
            font-size:10px;
        """)

        main_layout.addWidget(
            version,
            alignment=Qt.AlignRight
        )

        # UI Container Widget
        ui_widget = QWidget(self)
        ui_widget.setLayout(main_layout)

        # Root layout cho MainWindow
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(ui_widget)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(200)

        # Restore saved playlists
        self.restore_playlists()

    def focus_search(self):
        self.search.setFocus()
        self.search.selectAll()

    def clear_search(self):
        self.search.clear()
        self.search.clearFocus()

    def filter_songs(self, text):
        query = text.lower()
        self.song_list.clear()
        count = 0

        for song in self.current_playlist:
            if query in song["title"].lower():
                self.song_list.addItem(song["title"])
                count += 1

        if text:
            self.song_label.setText(
                f"Songs ({count}/{len(self.current_playlist)})"
            )
        else:
            self.song_label.setText(
                f"Songs ({len(self.current_playlist)})"
            )

    def restore_playlists(self):
        saved_folders = self.settings.get("playlists", [])
        for folder in saved_folders:
            if os.path.exists(folder):
                playlist_name = os.path.basename(folder)
                if playlist_name not in self.playlists:
                    self.playlists[playlist_name] = folder
                    self.playlist_list.addItem(playlist_name)

        self.playlist_label.setText(
            f"Playlists ({len(self.playlists)})"
        )

    def persist_settings(self):
        self.settings["volume"] = self.volume.value()
        self.settings["shuffle"] = self.shuffle
        self.settings["loop"] = self.loop
        self.settings["playlists"] = list(self.playlists.values())
        save_settings(self.settings)

    def choose_background(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Background Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.bg.set_background(file_path)
            self.persist_settings()

    def on_volume_changed(self, value):
        if hasattr(self.player, "audio_output"):
            self.player.audio_output.setVolume(value / 100)
        self.persist_settings()

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

        self.playlist_label.setText(
            f"Playlists ({len(self.playlists)})"
        )

        self.persist_settings()

    def load_playlist(self, item):
        self.search.clear()
        self.song_list.clear()
        self.current_playlist.clear()
        self.current_index = -1

        playlist_name = item.text()
        folder = self.playlists[playlist_name]

        for file_name in sorted(os.listdir(folder)):
            if file_name.lower().endswith((".mp3", ".wav", ".flac")):
                full_path = os.path.join(folder, file_name)
                self.current_playlist.append({
                    "title": file_name,
                    "path": full_path
                })
                self.song_list.addItem(file_name)

        self.song_label.setText(
            f"Songs ({len(self.current_playlist)})"
        )

    def play_current(self):
        if not self.current_playlist:
            return

        song = self.current_playlist[self.current_index]
        self.player.load(song["path"])

        if hasattr(self.player, "set_loop"):
            self.player.set_loop(self.loop)

        self.player.play()
        self.song_list.setCurrentRow(self.current_index)
        self.now_playing.setText(f"Now Playing: {song['title']}")

    def play_song(self, item):
        title = item.text()
        for index, song in enumerate(self.current_playlist):
            if song["title"] == title:
                self.current_index = index
                self.play_current()
                break

    def play_next(self, is_auto=False):
        if not self.current_playlist:
            return

        if is_auto and self.loop:
            self.play_current()
            return

        if self.shuffle:
            self.current_index = random.randint(
                0,
                len(self.current_playlist) - 1
            )
        else:
            self.current_index += 1
            if self.current_index >= len(self.current_playlist):
                if self.loop:
                    self.current_index = 0
                else:
                    self.current_index = len(self.current_playlist) - 1
                    return

        self.play_current()

    def play_previous(self):
        if not self.current_playlist:
            return

        self.current_index -= 1
        if self.current_index < 0:
            if self.loop:
                self.current_index = len(self.current_playlist) - 1
            else:
                self.current_index = 0
                return

        self.play_current()

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            self.shuffle_btn.setStyleSheet("background:#66ccff;")
        else:
            self.shuffle_btn.setStyleSheet("")
        self.persist_settings()

    def toggle_loop(self):
        self.loop = not self.loop
        if self.loop:
            self.loop_btn.setStyleSheet("background:#66cc66;")
        else:
            self.loop_btn.setStyleSheet("")

        if hasattr(self.player, "set_loop"):
            self.player.set_loop(self.loop)

        self.persist_settings()

    def media_status_changed(self, status):
        from PySide6.QtMultimedia import QMediaPlayer

        if status == QMediaPlayer.EndOfMedia:
            self.play_next(is_auto=True)

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

    def resizeEvent(self, event):
        self.bg.resize(self.size())
        super().resizeEvent(event)