import platform
from PySide6.QtCore import Qt, QTimer, qVersion
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QFrame,
    QMessageBox,
)


class DeveloperWindow(QWidget):

  def __init__(self, main_window):
    super().__init__()
    self.main = main_window

    self.setWindowTitle("LitePlayer Developer Mode")
    self.setMinimumWidth(380)

    # Main Layout
    layout = QVBoxLayout(self)
    layout.setSpacing(12)
    layout.setContentsMargins(16, 16, 16, 16)

    # Build UI Components
    layout.addWidget(self.build_header())
    layout.addWidget(self.build_system())
    layout.addWidget(self.build_playback())
    layout.addWidget(self.build_playlist())
    layout.addWidget(self.build_background())
    layout.addWidget(self.build_debug())
    layout.addWidget(self.build_footer())

    # Refresh Timer (500ms)
    self.refresh_timer = QTimer(self)
    self.refresh_timer.setInterval(500)
    self.refresh_timer.timeout.connect(self.refresh_info)
    self.refresh_timer.start()

  def build_header(self):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)

    title = QLabel("🛠 LitePlayer Developer")
    title_font = QFont()
    title_font.setPointSize(18)
    title_font.setBold(True)
    title.setFont(title_font)

    subtitle = QLabel("Welcome, Developer.")
    sub_font = QFont()
    sub_font.setPointSize(10)
    subtitle.setFont(sub_font)
    subtitle.setStyleSheet("color: gray;")

    layout.addWidget(title)
    layout.addWidget(subtitle)
    return widget

  def build_system(self):
    group = QGroupBox("System")
    layout = QGridLayout(group)

    layout.addWidget(QLabel("RAM:"), 0, 0)
    self.ram_label = QLabel("Loading...")
    layout.addWidget(self.ram_label, 0, 1)

    layout.addWidget(QLabel("CPU:"), 1, 0)
    self.cpu_label = QLabel("Loading...")
    layout.addWidget(self.cpu_label, 1, 1)

    layout.addWidget(QLabel("Python:"), 2, 0)
    self.python_label = QLabel("Loading...")
    layout.addWidget(self.python_label, 2, 1)

    layout.addWidget(QLabel("Qt:"), 3, 0)
    self.qt_label = QLabel("Loading...")
    layout.addWidget(self.qt_label, 3, 1)

    layout.addWidget(QLabel("LitePlayer:"), 4, 0)
    self.version_label = QLabel("Loading...")
    layout.addWidget(self.version_label, 4, 1)

    return group

  def build_playback(self):
    group = QGroupBox("Playback")
    layout = QGridLayout(group)

    layout.addWidget(QLabel("Current Song:"), 0, 0)
    self.song_label = QLabel("Loading...")
    layout.addWidget(self.song_label, 0, 1)

    layout.addWidget(QLabel("Current Index:"), 1, 0)
    self.index_label = QLabel("Loading...")
    layout.addWidget(self.index_label, 1, 1)

    layout.addWidget(QLabel("Shuffle:"), 2, 0)
    self.shuffle_label = QLabel("Loading...")
    layout.addWidget(self.shuffle_label, 2, 1)

    layout.addWidget(QLabel("Loop:"), 3, 0)
    self.loop_label = QLabel("Loading...")
    layout.addWidget(self.loop_label, 3, 1)

    return group

  def build_playlist(self):
    group = QGroupBox("Playlist")
    layout = QGridLayout(group)

    layout.addWidget(QLabel("Current Playlist:"), 0, 0)
    self.playlist_label = QLabel("Loading...")
    layout.addWidget(self.playlist_label, 0, 1)

    layout.addWidget(QLabel("Song Count:"), 1, 0)
    self.songcount_label = QLabel("Loading...")
    layout.addWidget(self.songcount_label, 1, 1)

    return group

  def build_background(self):
    group = QGroupBox("Background")
    layout = QGridLayout(group)

    layout.addWidget(QLabel("Background Type:"), 0, 0)
    self.bg_type = QLabel("Loading...")
    layout.addWidget(self.bg_type, 0, 1)

    layout.addWidget(QLabel("Opacity:"), 1, 0)
    self.bg_opacity = QLabel("Loading...")
    layout.addWidget(self.bg_opacity, 1, 1)

    layout.addWidget(QLabel("Mode:"), 2, 0)
    self.bg_mode = QLabel("Loading...")
    layout.addWidget(self.bg_mode, 2, 1)

    return group

  def build_debug(self):
    group = QGroupBox("Developer")
    layout = QVBoxLayout(group)

    buttons = [
        "📋 Copy Debug Info",
        "📂 Open Config Folder",
        "🔄 Reload Background",
        "⚡ Benchmark Startup",
        "🧹 Reset Settings",
        "🧪 Experimental",
    ]

    for text in buttons:
      btn = QPushButton(text)
      btn.clicked.connect(self.coming_soon)
      layout.addWidget(btn)

    return group

  def build_footer(self):
    footer_frame = QFrame()
    layout = QHBoxLayout(footer_frame)
    layout.setContentsMargins(0, 4, 0, 0)

    footer_label = QLabel("LitePlayer Internal Tool - Not intended for end users.")
    footer_label.setAlignment(Qt.AlignCenter)
    footer_font = QFont()
    footer_font.setPointSize(9)
    footer_label.setFont(footer_font)
    footer_label.setStyleSheet("color: gray;")

    layout.addWidget(footer_label)
    return footer_frame

  def refresh_info(self):
    # System
    self.ram_label.setText("Coming Soon")
    self.cpu_label.setText("Coming Soon")
    self.python_label.setText(platform.python_version())
    self.qt_label.setText(qVersion())
    self.version_label.setText("v0.4.5")

    # Playback
    if getattr(self.main, "current_index", -1) == -1:
      self.song_label.setText("Nothing")
      self.index_label.setText("-1")
    else:
      idx = self.main.current_index
      song_data = self.main.current_playlist[idx]
      song_title = (
          song_data.get("title", "Unknown")
          if isinstance(song_data, dict)
          else str(song_data)
      )
      self.song_label.setText(song_title)
      self.index_label.setText(str(idx))

    self.shuffle_label.setText(
        "ON" if getattr(self.main, "shuffle", False) else "OFF"
    )
    self.loop_label.setText(
        "ON" if getattr(self.main, "loop", False) else "OFF"
    )

    # Playlist
    current_item = (
        self.main.playlist_list.currentItem()
        if hasattr(self.main, "playlist_list")
        else None
    )
    if not current_item:
      self.playlist_label.setText("Nothing")
    else:
      self.playlist_label.setText(current_item.text())

    playlist_len = len(getattr(self.main, "current_playlist", []))
    self.songcount_label.setText(str(playlist_len))

    # Background
    bg_type_val = (
        self.main.settings.get("background_type", "Unknown")
        if hasattr(self.main, "settings")
        else "Unknown"
    )
    self.bg_type.setText(str(bg_type_val))

    opacity_val = (
        self.main.opacity.value() if hasattr(self.main, "opacity") else 0
    )
    self.bg_opacity.setText(f"{opacity_val}%")

    bg_mode_val = (
        self.main.background_mode.currentText()
        if hasattr(self.main, "background_mode")
        else "Unknown"
    )
    self.bg_mode.setText(str(bg_mode_val))

  def coming_soon(self):
    QMessageBox.information(self, "Developer", "Coming Soon.")

  def show_normal(self):
    self.showNormal()
    self.raise_()
    self.activateWindow()

  def show_experimental_tab(self):
    QMessageBox.information(self, "Experimental", "Coming Soon.")

  def closeEvent(self, event):
    event.ignore()
    self.hide()