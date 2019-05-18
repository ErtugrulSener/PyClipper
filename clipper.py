import ctypes
import os
import pickle
import random
import sys
import time
from collections import OrderedDict

import win32gui
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QPainter
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QFrame, QGroupBox,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QPushButton, QScrollArea, QSlider, QVBoxLayout,
                             QWidget)

from handlers import SoundHandler
from objects import ClassicQHBoxLayout, ClassicQPushButton, ClassicQVBoxLayout
from utils import WidgetUtils

# Preventing Windows's icon choice function for grouped processes (pythonw.exe -> PyClipper,...)
# See https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
# for further details.
myappid = 'Clipper_v1.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

app = QApplication(sys.argv)

screen_resolution = app.desktop().screenGeometry()
screen_width, screen_height = screen_resolution.width(), screen_resolution.height()

window_width = 350
window_height = 600
window_clippers = OrderedDict()


class DraggableLabel(QLabel):

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


class Clipper(QPushButton):

    def __init__(self):
        super().__init__()

        self._id = 0

        self.setMinimumHeight(200)
        self.setStyleSheet("background-color: white; border: 0px 0px 0px white; color: black;")

        self.titlebar = QFrame(self)
        self.titlebar.resize(330, 30)
        self.titlebar.setStyleSheet("background-color: rgba(50, 50, 50, 0.8);")

        self._titlebar_text = QLineEdit(self.titlebar)
        self._titlebar_text.resize(self.width() - 30, 30)
        self._titlebar_text.move(35, 0)
        self._titlebar_text.setText("New Clipper")
        self._titlebar_text.setStyleSheet("background-color: transparent; color: #ccc;")

        self.text_label_frame = QFrame(self)
        self.text_label_frame.resize(330, 170)
        self.text_label_frame.move(0, 30)
        self.text_label_frame.mousePressEvent = lambda event: self.text_label_pressed()

        self._text_label = DraggableLabel(self.text_label_frame)
        self._text_label.resize(self.text_label_frame.frameGeometry().width() - 15, self.text_label_frame.frameGeometry().height() - 15)
        self._text_label.move(5, 5)
        self._text_label.mousePressEvent = lambda event: self.text_label_pressed()
        self._text_label.setWordWrap(True)
        self._text_label.setAlignment(Qt.AlignTop)

        self.delete_button = ClassicQPushButton(self)
        self.delete_button.resize(30, 30)
        self.delete_button.clicked.connect(self.delete_button_clicked)
        self.delete_button.setStyleSheet("background-color: red;")

    def text_label_pressed(self):
        if len(self._text_label.text()) > 0:
            QApplication.clipboard().setText(self._text_label.text())

    def delete_button_clicked(self):
        window_clippers.pop(self.id)
        self.setParent(None)

    @property
    def text(self):
        return self._text_label.text()

    @text.setter
    def text(self, text):
        self.title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        self._text_label.setText(text)

    @property
    def title(self):
        return self._titlebar_text.text()

    @title.setter
    def title(self, text):
        self._titlebar_text.setText(text)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.clipboard_text = QApplication.clipboard().text()
        self.volume = 100

        self.init_main_window()
        self.init_elements()
        self.init_events()

        self.load_data()

    def load_data(self):
        if not os.path.isfile("data.pkl"):
            return False

        with open("data.pkl", "rb") as read_data:
            window_clippers = pickle.load(read_data)

            for clipper_id, pair in window_clippers.items():
                label_text = pair["text"]
                titlebar_text = pair["title"]

                self.add_clipper(0, label_text, titlebar_text, clipper_id)

    # GUI Initialization
    def init_main_window(self):
        self.setGeometry(screen_width - window_width, (screen_height // 2) - (window_height // 2), window_width, window_height)
        self.setFixedSize(self.size())
        self.setWindowTitle("PyClipper")
        self.setWindowIcon(QIcon("images/favicon.png"))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setStyleSheet('background-color:#333;color:#ccc')

    def init_elements(self):
        # Clipper Button Area
        self.add_clipper_button = ClassicQPushButton('Add clipper', self)
        self.add_clipper_button.resize(100, 32)

        self.add_clipper_button_frame, self.add_clipper_button_layout = WidgetUtils.add_widget_with_alignment(self, self.add_clipper_button, QHBoxLayout, Qt.AlignCenter)

        # Clipper Scroll Area
        self.clipper_scroll_area = QScrollArea(self)
        self.clipper_scroll_area.resize(self.width(), 472)
        self.clipper_scroll_area.move(0, 42)
        self.clipper_scroll_area.setWidgetResizable(True)

        self.scroll_area_layout = QVBoxLayout(self.clipper_scroll_area)

        self.scroll_widget = QWidget(self)
        self.scroll_widget.setLayout(self.scroll_area_layout)

        self.clipper_scroll_area.setWidget(self.scroll_widget)

        # Sound Setting Elements
        self.sound_groupbox = QGroupBox("Sound Settings", self)
        self.sound_groupbox.resize(330, 60)

        self.sound_groupbox_frame, self.sound_groupbox_layout = WidgetUtils.add_widget_with_alignment(self, self.sound_groupbox, QHBoxLayout, False)
        self.sound_groupbox_frame.resize(400, 75)
        self.sound_groupbox_frame.move(0, 520)

        self.sound_checkbox = QCheckBox(self)
        self.sound_checkbox.resize(13, 13)
        self.sound_checkbox.move(100, 520)
        self.sound_checkbox.toggle()

        self.sound_scrollbar = QSlider(Qt.Horizontal, self.sound_groupbox)
        self.sound_scrollbar.resize(300, 20)
        self.sound_scrollbar.move(22, 30)
        self.sound_scrollbar.setMaximum(100)
        self.sound_scrollbar.setValue(100)

        self.sound_scrollbar_value = QLabel(self.sound_groupbox)
        self.sound_scrollbar_value.setText("100%")
        self.sound_scrollbar_value.setAlignment(Qt.AlignCenter)

        text_width = WidgetUtils.get_label_size(self.sound_scrollbar_value)[0]
        self.sound_scrollbar_value.move(WidgetUtils.horizontal_align_center(self.sound_scrollbar, text_width), 0)

    def init_events(self):
        # Events for application
        self.destroyed.connect(self._on_destroyed)

        # Events for widgets on applicaton
        self.add_clipper_button.clicked.connect(self.add_clipper_pressed)
        self.sound_checkbox.stateChanged.connect(self.sound_state_changed)
        self.sound_scrollbar.valueChanged.connect(self.slider_value_changed)
        self.sound_scrollbar.sliderReleased.connect(self.slider_released)

        # Global events
        QApplication.clipboard().dataChanged.connect(self.clipboard_changed)

    # Event functions
    def slider_value_changed(self):
        self.sound_scrollbar_value.setText("{}%".format(self.sound_scrollbar.value()))

    def slider_released(self):
        self.set_clipper_volume(self.sound_scrollbar.value())

    def sound_state_changed(self):
        state = self.sound_checkbox.checkState() == 2
        self.sound_groupbox.setEnabled(state)

    def clipboard_changed(self, index=0):
        """
        This method executes when the actual string in clipboard changes.
        Furthermore plays a little clipsound using the SoundHandler by PyQT.
        """
        if self.clipboard_text != QApplication.clipboard().text():
            self.clipboard_text = QApplication.clipboard().text()

            if self.sound_groupbox.isEnabled():
                SoundHandler.play_clip_sound(self.volume)

            self.add_clipper(index, self.clipboard_text)

    def add_clipper_pressed(self, index=0):
        """
        This method executes when the "Add clipper" button is pressed.
        It adds a new Clipper on index 0 to the vertical layout in the scroll area.
        """
        self.add_clipper(index)

    def add_clipper(self, index, text="", title="", random_id=None):
        clip = Clipper()
        self.scroll_area_layout.insertWidget(index, clip)

        if len(text) > 0:
            clip.text = text

        if len(title) > 0:
            clip.title = title

        # Create new random id, if not a specific id is given
        if random_id is None:
            random_id = random.randint(100000, 999999)

        # Reroll id if it exists already
        while(window_clippers.get(random_id)):
            random_id = random.randint(100000, 999999)

        clip.id = random_id
        window_clippers[clip.id] = {"title": clip.title, "text": clip.text}

    def set_clipper_volume(self, volume):
        self.volume = volume

    @staticmethod
    def _on_destroyed(self):
        """
        This method executes when the window is destroyed.
        Saves the window_clippers in a file, so that it can be loaded afterwards.
        """
        with open("data.pkl", "bw") as write_data:
            pickle.dump(window_clippers, write_data)


if __name__ == "__main__":
    root = Window()
    root.show()

    # Delete window on close to trigger self.on_destroy
    # This method has to be called after root.show()
    root.setAttribute(Qt.WA_DeleteOnClose, True)

    sys.exit(app.exec_())
