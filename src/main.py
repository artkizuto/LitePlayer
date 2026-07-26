import sys
import time

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from splash import SplashScreen
from window import MainWindow


def main():
    start = time.perf_counter()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("assets/icon.ico"))

    # Splash
    splash = SplashScreen()
    splash.show()

    # Cho Splash kịp render
    app.processEvents()

    # Thời gian Splash tối thiểu
    MIN_SPLASH = 1.0
    elapsed = time.perf_counter() - start
    remaining = max(0, int(round((MIN_SPLASH - elapsed) * 1000)))

    # Giữ reference để tránh bị garbage collection
    window = None

    def finish_startup():
        nonlocal window

        window = MainWindow()
        window.setWindowIcon(QIcon("assets/icon.ico"))

        window.show()
        splash.close()

    QTimer.singleShot(remaining, finish_startup)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()