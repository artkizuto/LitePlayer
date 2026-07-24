from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import (
    QMediaPlayer,
    QAudioOutput,
)


class AudioPlayer:
    def __init__(self):
        self.audio_output = QAudioOutput()

        self.player = QMediaPlayer()

        self.player.setAudioOutput(self.audio_output)

        self.audio_output.setVolume(0.5)

    def load(self, file_path):
        self.player.setSource(QUrl.fromLocalFile(file_path))

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def duration(self):
        return self.player.duration()

    def position(self):
        return self.player.position()

    def set_position(self, position):
        self.player.setPosition(position)

    def set_loop(self, loop: bool):
    # -1 là Loop vô tận bài hiện tại, 1 là chạy 1 lần rồi dừng
        if loop:
            self.player.setLoops(-1)
        else:
            self.player.setLoops(1)