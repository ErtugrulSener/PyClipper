from PyQt5.QtCore import QRect, Qt, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class ClassicQVBoxLayout(QVBoxLayout):

    def __init__(self, parent=None, spacing=0, margins=(0, 0, 0, 0)):
        if parent:
            super().__init__(parent)
        else:
            super().__init__()

        self.setSpacing(spacing)
        self.setContentsMargins(*margins)
        self.setAlignment(Qt.AlignTop)


class ClassicQHBoxLayout(QHBoxLayout):

    def __init__(self, parent=None, spacing=0, margins=(0, 0, 0, 0)):
        if parent:
            super().__init__(parent)
        else:
            super().__init__()

        self.setSpacing(spacing)
        self.setContentsMargins(*margins)
        self.setAlignment(Qt.AlignLeft)


class ClassicQPushButton(QPushButton):
    mouseHover = pyqtSignal(bool)

    def __init__(self, text="", parent=None):
        if parent:
            super().__init__(text, parent)
        else:
            super().__init__(text)

        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.mouseHover.emit(True)

    def leaveEvent(self, event):
        self.mouseHover.emit(False)


class ClassicQLabel(QLabel):

    def __init__(self, parent):
        super().__init__(parent)
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
