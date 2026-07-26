import random
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

        # --- SMART SHUFFLE VARIABLES ---
        self.shuffle_queue = []
        self.shuffle_index = 0

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

    # ==========================================
    # SMART SHUFFLE LOGIC
    # ==========================================
    def create_shuffle_queue(self, total_songs: int):
        """
        Tạo danh sách random theo số lượng bài trong playlist.
        Truyền vào total_songs (độ dài playlist hiện tại).
        """
        if total_songs <= 0:
            self.shuffle_queue = []
            self.shuffle_index = 0
            return

        # Sinh list [0, 1, 2, ..., total_songs - 1]
        self.shuffle_queue = list(range(total_songs))
        # Random xáo trộn
        random.shuffle(self.shuffle_queue)
        # Reset index về 0
        self.shuffle_index = 0

    def get_current_shuffle_song(self):
        """Trả về index thật của bài hát trong playlist"""
        if not self.shuffle_queue or self.shuffle_index >= len(self.shuffle_queue):
            return 0
        return self.shuffle_queue[self.shuffle_index]

    def play_next(self, is_shuffle: bool, total_songs: int, current_index: int) -> int:
        """Trả về index bài tiếp theo cần phát"""
        if total_songs <= 0:
            return 0

        if is_shuffle:
            self.shuffle_index += 1
            # Hết queue -> Tạo queue mới & phát bài đầu tiên của queue mới
            if self.shuffle_index >= len(self.shuffle_queue):
                self.create_shuffle_queue(total_songs)
            return self.get_current_shuffle_song()
        else:
            # Shuffle OFF: Tăng tuần tự
            next_index = current_index + 1
            if next_index >= total_songs:
                next_index = 0
            return next_index

    def play_previous(self, is_shuffle: bool, total_songs: int, current_index: int) -> int:
        """Trả về index bài trước đó cần phát"""
        if total_songs <= 0:
            return 0

        if is_shuffle:
            self.shuffle_index -= 1
            # Nhỏ hơn 0 -> Đặt bằng 0, không random lại
            if self.shuffle_index < 0:
                self.shuffle_index = 0
            return self.get_current_shuffle_song()
        else:
            # Shuffle OFF: Lùi tuần tự
            prev_index = current_index - 1
            if prev_index < 0:
                prev_index = total_songs - 1
            return prev_index

    def play_song(self, index: int, is_shuffle: bool):
        """
        Gọi khi user double click bài hát trong danh sách.
        Cập nhật shuffle_index trỏ đúng vào bài vừa bấm trong shuffle_queue.
        """
        if is_shuffle and self.shuffle_queue:
            if index in self.shuffle_queue:
                self.shuffle_index = self.shuffle_queue.index(index)