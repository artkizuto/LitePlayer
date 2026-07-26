import os
import random

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QKeySequence, QAction
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
    QFrame,
    QMenu,
    QColorDialog,
    QMessageBox,
)

from player import AudioPlayer
from settings import (
    load_settings,
    save_settings,
    is_developer_unlocked,
    set_developer_unlocked,
)
from background import BackgroundWidget
from glass import GlassWidget
from developer_window import DeveloperWindow


# =========================
# CLICKABLE LABEL SUBCLASS
# =========================
class ClickableLabel(QLabel):
  clicked = Signal()

  def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
      self.clicked.emit()
    super().mousePressEvent(event)


# =========================
# COMMIT HASH
# =========================
MANUAL_GIT_HASH = "373c892"


def get_git_hash():
  return MANUAL_GIT_HASH


class MainWindow(QWidget):

  def __init__(self):
    super().__init__()

    # =========================
    # Player & Developer State
    # =========================
    self.player = AudioPlayer()
    self.playlists = {}
    self.current_playlist = []
    self.current_index = -1

    # Developer Mode Setup
    self.dev_window = DeveloperWindow(self)
    self.ctrl_shift_active = False
    self.dev_counter = 0
    self.dev_timer = QTimer()
    self.dev_timer.setSingleShot(True)
    self.dev_timer.timeout.connect(self.reset_dev_counter)

    # Logo click counter for Easter Egg
    self.logo_click_count = 0
    self.logo_click_timer = QTimer()
    self.logo_click_timer.setSingleShot(True)
    self.logo_click_timer.timeout.connect(self.reset_logo_click_count)

    # Load Settings
    self.settings = load_settings()
    self.shuffle = self.settings.get("shuffle", False)
    self.loop = self.settings.get("loop", False)

    # =========================
    # Window
    # =========================
    self.setWindowTitle("LitePlayer")
    self.resize(700, 500)

    # Background Manager
    self.bg = BackgroundWidget(self.settings)
    self.bg.setParent(self)
    self.bg.lower()
    self.bg.resize(self.size())

    # Sliders & Controls
    self.opacity_label = QLabel("Opacity")
    self.opacity = QSlider(Qt.Horizontal)
    self.opacity.setRange(0, 100)
    self.opacity.setValue(self.settings.get("background_opacity", 30))
    self.opacity.setMaximumWidth(120)

    # =========================
    # Title & Search
    # =========================
    self.title = ClickableLabel("🎵 LitePlayer")
    self.title.setStyleSheet("""
            font-size:24px;
            font-weight:bold;
        """)
    self.title.clicked.connect(self.logo_clicked)

    self.search = QLineEdit()
    self.search.setPlaceholderText("🔍 Search...")

    # =========================
    # Widgets
    # =========================
    self.add_playlist_btn = QPushButton("➕ Add Playlist")
    self.background_btn = QPushButton("🖼 Background")

    self.bg_menu = QMenu(self)
    action_default = QAction("No Background", self)
    action_default.triggered.connect(self.set_bg_default)
    self.bg_menu.addAction(action_default)

    action_solid = QAction("Solid Color", self)
    action_solid.triggered.connect(self.set_bg_solid)
    self.bg_menu.addAction(action_solid)

    action_upload = QAction("Upload Image", self)
    action_upload.triggered.connect(self.choose_background)
    self.bg_menu.addAction(action_upload)

    self.background_btn.setMenu(self.bg_menu)

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

    self.volume = QSlider(Qt.Vertical)
    self.volume.setRange(0, 100)
    self.volume.setValue(self.settings.get("volume", 50))

    self.volume_btn = QPushButton("🔊")

    self.volume_popup = QFrame(self)
    self.volume_popup.hide()
    self.volume_popup.setFrameShape(QFrame.NoFrame)
    self.volume_popup.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid lightgray;
                border-radius: 10px;
            }
        """)

    popup_layout = QVBoxLayout(self.volume_popup)
    popup_layout.setContentsMargins(10, 10, 10, 10)
    popup_layout.addWidget(self.volume)

    self.update_volume_icon(self.volume.value())

    if self.shuffle:
      self.shuffle_btn.setStyleSheet("background:#66ccff;")
    if self.loop:
      self.loop_btn.setStyleSheet("background:#66cc66;")

    if hasattr(self.player, "audio_output"):
      self.player.audio_output.setVolume(self.volume.value() / 100)

    # =========================
    # Signals
    # =========================
    self.search.textChanged.connect(self.filter_songs)
    self.add_playlist_btn.clicked.connect(self.add_playlist)
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

    self.player.player.mediaStatusChanged.connect(self.media_status_changed)

    self.progress.sliderMoved.connect(self.seek)
    self.progress.sliderPressed.connect(self.pause_timer)
    self.progress.sliderReleased.connect(self.resume_timer)

    self.volume.valueChanged.connect(self.on_volume_changed)
    self.volume_btn.clicked.connect(self.toggle_volume_popup)

    # =========================
    # Layout UI
    # =========================
    main_layout = QVBoxLayout()

    # ---------- Top ----------
    top_layout = QHBoxLayout()
    top_layout.addWidget(self.title)
    top_layout.addWidget(self.search)
    top_layout.addStretch()
    top_layout.addWidget(self.opacity_label)
    top_layout.addWidget(self.opacity)
    top_layout.addWidget(self.background_btn)
    top_layout.addWidget(self.background_mode)
    top_layout.addWidget(self.add_playlist_btn)

    # ---------- Center ----------
    center_layout = QHBoxLayout()

    left_panel = GlassWidget()
    left_layout = QVBoxLayout(left_panel)
    self.playlist_label = QLabel("Playlists (0)")
    left_layout.addWidget(self.playlist_label)
    left_layout.addWidget(self.playlist_list)

    right_panel = GlassWidget()
    right_layout = QVBoxLayout(right_panel)
    self.song_label = QLabel("Songs (0)")
    right_layout.addWidget(self.song_label)
    right_layout.addWidget(self.song_list)

    song_layout = QHBoxLayout()
    song_layout.addWidget(self.now_playing)
    song_layout.addStretch()
    song_layout.addWidget(self.volume_btn)

    right_layout.addLayout(song_layout)
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

    center_layout.addWidget(left_panel, 1)
    center_layout.addWidget(right_panel, 2)

    # ---------- Footer Layout ----------
    footer_layout = QHBoxLayout()

    self.dev_status = QLabel("")
    self.dev_status.setStyleSheet(
        "color: #e74c3c; font-size: 10px; font-weight: bold;"
    )

    git_hash = get_git_hash()
    footer = QLabel(
        f"LitePlayer v0.4.5 (git {git_hash}) | Made by Kizuto | Powered by"
        " Python + Qt | AI-assisted development"
    )
    footer.setStyleSheet("color: gray; font-size: 10px;")

    footer_layout.addWidget(self.dev_status)
    footer_layout.addStretch()
    footer_layout.addWidget(footer)

    # Assemble
    main_layout.addLayout(top_layout)
    main_layout.addLayout(center_layout)
    main_layout.addLayout(footer_layout)

    ui_widget = QWidget(self)
    ui_widget.setLayout(main_layout)

    root_layout = QVBoxLayout(self)
    root_layout.setContentsMargins(0, 0, 0, 0)
    root_layout.addWidget(ui_widget)

    self.timer = QTimer()
    self.timer.timeout.connect(self.update_progress)
    self.timer.start(200)

    self.restore_playlists()
    self.update_background_ui()
    self.update_dev_status_label()

  # =========================
  # Developer Mode Logic
  # =========================

  def reset_dev_counter(self):
    """Hết 3s mà chưa đủ 5 lần D -> Reset đếm & hủy trạng thái giữ Ctrl+Shift."""
    self.dev_counter = 0
    self.ctrl_shift_active = False

  def reset_logo_click_count(self):
    self.logo_click_count = 0

  def keyPressEvent(self, event):
    # Kiểm tra xem có đang giữ cả Ctrl và Shift không
    has_ctrl_shift = (
        event.modifiers() == (Qt.ControlModifier | Qt.ShiftModifier)
    )

    if has_ctrl_shift:
      # CHƯA UNLOCK: Bắt đầu kích hoạt bom hẹn giờ 3s từ lúc đè Ctrl + Shift
      if not is_developer_unlocked():
        if not getattr(self, "ctrl_shift_active", False):
          self.ctrl_shift_active = True
          self.dev_counter = 0
          self.dev_timer.start(3000)  # Đồng hồ 3s tíc tắc chạy!

        # Nếu bấm phím D trong lúc đồng hồ 3s vẫn còn chạy
        if event.key() == Qt.Key_D:
          if self.dev_timer.isActive():
            self.dev_counter += 1

            # Spam đủ 5 lần D trong 3s -> KÍCH HOẠT!
            if self.dev_counter >= 5:
              self.dev_timer.stop()
              self.dev_counter = 0
              self.ctrl_shift_active = False
              set_developer_unlocked(True)
              QMessageBox.information(
                  self, "Developer Mode Enabled", "Welcome, Developer."
              )
              self.update_dev_status_label()

      # ĐÃ UNLOCK: Bấm Ctrl + Shift + D để Toggle Window
      else:
        if event.key() == Qt.Key_D:
          self.toggle_developer_window()
    else:
      super().keyPressEvent(event)

  def keyReleaseEvent(self, event):
    # Nếu trót buông tay khỏi phím Ctrl hoặc Shift trước khi đủ 5 lần D -> Reset ngay
    if event.key() in (Qt.Key_Control, Qt.Key_Shift):
      self.ctrl_shift_active = False
      self.dev_counter = 0
      self.dev_timer.stop()

    super().keyReleaseEvent(event)

  def toggle_developer_window(self):
    if self.dev_window.isVisible():
      self.dev_window.hide()
    else:
      self.dev_window.show_normal()
      self.dev_window.show()
      self.dev_window.activateWindow()

    self.update_dev_status_label()

  def logo_clicked(self):
    if not is_developer_unlocked():
      return  # Chưa unlock thì click logo không làm gì

    # Đã unlock -> Tính năng bấm Logo
    self.logo_click_count += 1
    self.logo_click_timer.start(2000)  # Click 5 lần trong 2 giây

    if self.logo_click_count >= 5:
      self.logo_click_count = 0
      self.logo_click_timer.stop()
      self.dev_window.show_experimental_tab()
    else:
      self.toggle_developer_window()

  def update_dev_status_label(self):
    if not is_developer_unlocked():
      self.dev_status.setText("")
      self.title.setCursor(Qt.ArrowCursor)
    else:
      self.title.setCursor(Qt.PointingHandCursor)
      if self.dev_window.isVisible():
        self.dev_status.setText("Developer Mode ON")
      else:
        self.dev_status.setText("Developer Mode OFF (Click to Show)")

  # =========================
  # Other Methods & Events
  # =========================

  def set_bg_default(self):
    self.bg.set_default()
    self.update_background_ui()
    self.persist_settings()

  def set_bg_solid(self):
    color = QColorDialog.getColor(parent=self)
    if color.isValid():
      self.bg.set_color(color)
      self.update_background_ui()
      self.persist_settings()

  def choose_background(self):
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Select Background Image",
        "",
        "Images (*.png *.jpg *.jpeg *.bmp *.gif)",
    )
    if file_path:
      self.bg.set_background(file_path)
      self.update_background_ui()
      self.persist_settings()

  def update_background_ui(self):
    bg_type = self.settings.get("background_type", "app_default")
    if bg_type == "image":
      self.opacity_label.show()
      self.opacity.show()
      self.background_mode.show()
    else:
      self.opacity_label.hide()
      self.opacity.hide()
      self.background_mode.hide()

  def toggle_volume_popup(self):
    if self.volume_popup.isVisible():
      self.volume_popup.hide()
      return

    self.volume_popup.resize(60, 180)
    button = self.volume_btn
    pos = button.mapTo(self, button.rect().topLeft())
    x = pos.x()
    y = pos.y() - self.volume_popup.height() - 8

    self.volume_popup.move(x, y)
    self.volume_popup.raise_()
    self.volume_popup.show()

  def mousePressEvent(self, event):
    if self.volume_popup.isVisible():
      if not self.volume_popup.geometry().contains(
          event.pos()
      ) and not self.volume_btn.geometry().contains(event.pos()):
        self.volume_popup.hide()
    super().mousePressEvent(event)

  def update_volume_icon(self, value):
    if value == 0:
      icon = "🔇"
    elif value <= 33:
      icon = "🔈"
    elif value <= 66:
      icon = "🔉"
    else:
      icon = "🔊"
    self.volume_btn.setText(icon)

  def on_volume_changed(self, value):
    if hasattr(self.player, "audio_output"):
      real_volume = (value / 100) ** 2
      self.player.audio_output.setVolume(real_volume)
    self.update_volume_icon(value)
    self.persist_settings()

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
      self.song_label.setText(f"Songs ({len(self.current_playlist)})")

  def restore_playlists(self):
    saved_folders = self.settings.get("playlists", [])
    for folder in saved_folders:
      if os.path.exists(folder):
        playlist_name = os.path.basename(folder)
        if playlist_name not in self.playlists:
          self.playlists[playlist_name] = folder
          self.playlist_list.addItem(playlist_name)

    self.playlist_label.setText(f"Playlists ({len(self.playlists)})")

  def persist_settings(self):
    self.settings["volume"] = self.volume.value()
    self.settings["shuffle"] = self.shuffle
    self.settings["loop"] = self.loop
    self.settings["playlists"] = list(self.playlists.values())
    save_settings(self.settings)

  def add_playlist(self):
    folder = QFileDialog.getExistingDirectory(self, "Select Playlist Folder")
    if not folder:
      return

    playlist_name = os.path.basename(folder)
    if playlist_name in self.playlists:
      return

    self.playlists[playlist_name] = folder
    self.playlist_list.addItem(playlist_name)
    self.playlist_label.setText(f"Playlists ({len(self.playlists)})")
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
        self.current_playlist.append({"title": file_name, "path": full_path})
        self.song_list.addItem(file_name)

    self.song_label.setText(f"Songs ({len(self.current_playlist)})")

    if self.shuffle and self.current_playlist:
      self.player.create_shuffle_queue(len(self.current_playlist))

  def play_current(self):
    if not self.current_playlist or self.current_index < 0:
      return

    song = self.current_playlist[self.current_index]
    self.player.load(song["path"])

    if hasattr(self.player, "audio_output"):
      init_val = self.volume.value() / 100
      self.player.audio_output.setVolume(init_val**2)

    self.player.play()
    self.song_list.setCurrentRow(self.current_index)
    self.now_playing.setText(f"Now Playing: {song['title']}")

  def play_song(self, item):
    title = item.text()
    for index, song in enumerate(self.current_playlist):
      if song["title"] == title:
        self.current_index = index
        if hasattr(self.player, "play_song"):
          self.player.play_song(index, self.shuffle)
        self.play_current()
        break

  def play_next(self, is_auto=False):
    if not self.current_playlist:
      return

    if is_auto and self.loop:
      self.play_current()
      return

    if self.shuffle:
      self.current_index = self.player.play_next(
          is_shuffle=True,
          total_songs=len(self.current_playlist),
          current_index=self.current_index,
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

    if self.shuffle:
      self.current_index = self.player.play_previous(
          is_shuffle=True,
          total_songs=len(self.current_playlist),
          current_index=self.current_index,
      )
    else:
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
      if self.current_playlist:
        self.player.create_shuffle_queue(len(self.current_playlist))
        if self.current_index != -1 and hasattr(self.player, "play_song"):
          self.player.play_song(self.current_index, self.shuffle)
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