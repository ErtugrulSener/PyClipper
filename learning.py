import sys

from PyQt5.QtWidgets import (QApplication, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.init_main_elements()
        self.init_main_window()

    def init_main_window(self):
        self.setGeometry(50, 50, 1000, 500)
        self.setWindowTitle("Testing")
        self.show()

    def init_main_elements(self):
        box = QVBoxLayout(self)
        self.setLayout(box)

        scroll = QScrollArea(self)
        box.addWidget(scroll)

        scrollContent = QWidget(scroll)
        scrollLayout = QVBoxLayout(scrollContent)
        scrollContent.setLayout(scrollLayout)

        for i in range(0, 100):
            scrollLayout.addWidget(QPushButton(str(i)))

        scroll.setWidget(scrollContent)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = Window()
    sys.exit(app.exec_())
