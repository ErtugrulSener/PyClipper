import ctypes
import os
import sys
import time

from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QFrame, QGroupBox,
                             QHBoxLayout, QLabel, QMainWindow, QPushButton,
                             QScrollArea, QSlider, QVBoxLayout, QWidget)

from handlers import SoundHandler
from objects import ClassicQHBoxLayout, ClassicQPushButton, ClassicQVBoxLayout
from utils import WidgetUtils

# Preventing Windows's icon choice function for grouped processes (pythonw.exe -> PyClipper,...)
# See https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
# for further details.
myappid = 'Clipper_v1.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

scriptDir = os.path.dirname(os.path.realpath(__file__))

app = QApplication(sys.argv)

screen_resolution = app.desktop().screenGeometry()
screen_width, screen_height = screen_resolution.width(), screen_resolution.height()

window_width = 350
window_height = 600


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


class Clipper(QPushButton):

    def __init__(self):
        super().__init__()

        self.setMinimumHeight(200)
        self.setStyleSheet("background-color: white; border: 0px 0px 0px white; color: black;")

        self.main_layout = ClassicQVBoxLayout(self)

        self.text_label = DraggableLabel(self)
        self.text_label.move(0, 30)
        self.text_label.setWordWrap(True)
        self.text_label.mousePressEvent = lambda event: self.text_label_pressed()
        self.text_label.setMinimumHeight(170)
        self.text_label.setStyleSheet("padding: 5px;")

        self.titlebar = QFrame(self)
        self.titlebar.setMinimumHeight(30)
        self.titlebar.setStyleSheet("background-color: rgba(50, 50, 50, 0.8);")

        self.titlebar_label = QLabel(self)
        self.titlebar_label.setText("New Clipper")
        self.titlebar_label.setStyleSheet("color: #ccc;")
        self.titlebar_label.setAttribute(Qt.WA_TranslucentBackground, True)
        self.titlebar_label.move(35, 0)

        self.delete_button = ClassicQPushButton(self)
        self.delete_button.resize(30, 30)
        self.delete_button.clicked.connect(self.delete_button_clicked)
        self.delete_button.setStyleSheet("background-color: red;")

        self.main_layout.addWidget(self.titlebar)
        self.main_layout.addWidget(self.text_label)

    def text_label_pressed(self):
        QApplication.clipboard().setText(self.text_label.text())

    def delete_button_clicked(self):
        self.setParent(None)

    def set_clipper_text(self, text):
        self.text_label.setText(text)


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.clipboard_text = QApplication.clipboard().text()
        self.volume = 100

        self.init_main_window()
        self.init_elements()
        self.init_events()

    # GUI Initialization
    def init_main_window(self):
        self.setGeometry(screen_width - window_width, (screen_height // 2) - (window_height // 2), window_width, window_height)
        self.setFixedSize(self.size())
        self.setWindowTitle("PyClipper")
        self.setWindowIcon(QIcon(f'{os.path.sep}'.join([scriptDir, 'images', 'favicon.png'])))
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
        self.add_clipper_button.clicked.connect(self.add_clipper_pressed)
        self.sound_checkbox.stateChanged.connect(self.sound_state_changed)
        self.sound_scrollbar.valueChanged.connect(self.slider_value_changed)
        self.sound_scrollbar.sliderReleased.connect(self.slider_released)

        QApplication.clipboard().dataChanged.connect(self.clipboard_changed)

    # Event functions
    def slider_value_changed(self):
        self.sound_scrollbar_value.setText("{}%".format(self.sound_scrollbar.value()))

    def slider_released(self):
        self.set_clipper_volume(self.sound_scrollbar.value())

    def sound_state_changed(self):
        state = self.sound_checkbox.checkState() == 2
        self.sound_groupbox.setEnabled(state)

    def clipboard_changed(self):
        """
        This method executes when the actual string in clipboard changes.
        Furthermore plays a little clipsound using the SoundHandler by PyQT.
        """
        if self.clipboard_text != QApplication.clipboard().text():
            self.clipboard_text = QApplication.clipboard().text()

            clip = Clipper()
            clip.set_clipper_text(self.clipboard_text)
            self.scroll_area_layout.insertWidget(0, clip)

            if self.sound_groupbox.isEnabled():
                SoundHandler.play_clip_sound(self.volume)

    def add_clipper_pressed(self, index=0):
        """
        This method executes when the "Add clipper" button is pressed.
        It adds a new Clipper on index 0 to the vertical layout in the scroll area.
        """
        clip = Clipper()
        self.scroll_area_layout.insertWidget(index, clip)

    def set_clipper_volume(self, volume):
        self.volume = volume


if __name__ == "__main__":
    root = Window()
    root.show()

    sys.exit(app.exec_())
