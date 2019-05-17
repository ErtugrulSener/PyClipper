from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout


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

    def __init__(self, text, parent=None):
        if parent:
            super().__init__(text, parent)
        else:
            super().__init__(text)
