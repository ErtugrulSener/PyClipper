from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
import sys

from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)

app = QApplication(sys.argv)


class QLabel(QLabel):
    def __init__(self, parent=None):
        if parent:
            super().__init__(parent)
        else:
            super().__init__()

        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        self.setText(e.mimeData().text())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawText(self.rect(), Qt.TextWordWrap, self.text())


c = QLabel()


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
    root = Window()
    sys.exit(app.exec_())
