import sys

from PySide6.QtGui import QIcon  # 1. Import thêm QIcon
from PySide6.QtWidgets import QApplication

from window import MainWindow


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    # 2. Đặt setWindowIcon ở đây, sau khi window đã được tạo
    window.setWindowIcon(QIcon("assets/icon.ico"))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()