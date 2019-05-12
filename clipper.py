import os
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *

# Preventing Windows's icon choice function for grouped processes (pythonw.exe -> PyClipper,...)
# See 'https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105'
# for further details.
import ctypes
myappid = 'Clipper.v1'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

scriptDir = os.path.dirname(os.path.realpath(__file__))

app = QApplication(sys.argv)

screen_resolution = app.desktop().screenGeometry()
screen_width, screen_height = screen_resolution.width(), screen_resolution.height()

window_width = 350
window_height = 600


class SoundHandler:

	@staticmethod
	def play_clip_sound(volume=100):
		filename = f'{os.path.sep}'.join([scriptDir, 'sounds', 'clipsound.wav'])
		fullpath = QDir.current().absoluteFilePath(filename)
		url = QUrl.fromLocalFile(fullpath)

		content = QMediaContent(url)
		player = QMediaPlayer()
		player.setMedia(content)
		player.setVolume(volume)
		player.play()
		time.sleep(0.3)


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
		self.setMaximumHeight(200)
		self.setStyleSheet("background-color: white; border: 0px 0px 0px white; color: black;")

		self.layout = QVBoxLayout(self)
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.layout.setAlignment(Qt.AlignTop)

		self.text_label = DraggableLabel(self)
		self.text_label.move(0, 30)
		self.text_label.setWordWrap(True)
		self.text_label.mousePressEvent = self.cpy_to_clipboard
		self.text_label.setMinimumHeight(170)
		self.text_label.setMaximumHeight(170)
		self.text_label.setMinimumWidth(self.width())
		self.text_label.setMaximumWidth(self.width())

		self.titlebar = QFrame(self)
		self.titlebar.setMinimumHeight(30)
		self.titlebar.setMaximumHeight(30)
		self.titlebar.setStyleSheet("background-color: rgba(50, 50, 50, 0.8);")

		self.delete_button = QPushButton(self)
		self.delete_button.resize(30, 30)
		self.delete_button.clicked.connect(self.delete_button_clicked)
		self.delete_button.setStyleSheet("background-color: red;")

		self.layout.addWidget(self.titlebar)

	def cpy_to_clipboard(self, event):
		QApplication.clipboard().setText(self.text_label.text())

	def delete_button_clicked(self):
		self.setParent(None)

	def setClipperText(self, text):
		self.text_label.setText(text)
		self.text_label.setStyleSheet("padding: 5px;")

		self.layout.addWidget(self.text_label)


class Window(QMainWindow):
	def __init__(self):
		super().__init__()

		self.clipboard_text = QApplication.clipboard().text()
		self.volume = 100

		self.init_main_window()
		self.init_elements()
		self.init_events()

	def init_main_window(self):
		self.setGeometry(screen_width - window_width, (screen_height // 2) - (window_height // 2), window_width, window_height)
		self.setFixedSize(self.size())
		self.setWindowTitle("PyClipper")
		self.setWindowIcon(QIcon(f'{os.path.sep}'.join([scriptDir, 'images', 'favicon.png'])))
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.setStyleSheet('background-color:#333;color:#ccc')
		self.setFont(QFont('Serif', 10))

	def init_elements(self):
		# Clipper Button Area
		self.add_clipper_button = QPushButton('Add clipper', self)
		self.add_clipper_button.resize(100, 32)

		self.add_clipper_button_frame, self.add_clipper_button_layout = self.add_widget_with_alignment(self, self.add_clipper_button, QHBoxLayout, Qt.AlignCenter)

		# Clipper Scroll Area
		self.clipper_scroll_area = QScrollArea(self)
		self.clipper_scroll_area.resize(self.width(), 472)
		self.clipper_scroll_area.move(0, 42)
		self.clipper_scroll_area.setWidgetResizable(True)

		self.layout = QVBoxLayout(self.clipper_scroll_area)

		self.scroll_widget = QWidget(self)
		self.scroll_widget.setLayout(self.layout)

		self.clipper_scroll_area.setWidget(self.scroll_widget)

		# Sound Setting Elements
		self.sound_groupbox = QGroupBox("Sound Settings", self)
		self.sound_groupbox.resize(330, 60)

		self.sound_groupbox_frame, self.sound_groupbox_layout = self.add_widget_with_alignment(self, self.sound_groupbox, QHBoxLayout, False)
		self.sound_groupbox_frame.resize(400, 75)
		self.sound_groupbox_frame.move(0, 520)

		self.sound_checkbox = QCheckBox(self)
		self.sound_checkbox.resize(13, 13)
		self.sound_checkbox.move(100, 528)
		self.sound_checkbox.toggle()

		self.sound_scrollbar = QSlider(Qt.Horizontal, self.sound_groupbox)
		self.sound_scrollbar.resize(300, 20)
		self.sound_scrollbar.move(12, 25)
		self.sound_scrollbar.setMaximum(100)
		self.sound_scrollbar.setValue(100)

		self.sound_scrollbar_value = QLabel(self.sound_scrollbar)
		self.sound_scrollbar_value.resize(35, 10)
		self.sound_scrollbar_value.setText("100%")

		text_width, text_height = self.get_label_size(self.sound_scrollbar_value)
		self.sound_scrollbar_value.move(self.horizontal_align_center(self.sound_scrollbar, text_width), 3)

	def init_events(self):
		self.add_clipper_button.clicked.connect(self.add_clipper_pressed)
		self.sound_checkbox.stateChanged.connect(self.sound_state_changed)
		self.sound_scrollbar.valueChanged.connect(self.slider_value_changed)
		self.sound_scrollbar.sliderReleased.connect(self.slider_released)

		QApplication.clipboard().dataChanged.connect(self.clipboard_changed)

	def slider_value_changed(self):
		self.sound_scrollbar_value.setText("{}%".format(self.sound_scrollbar.value()))

	def slider_released(self):
		self.set_clipper_volume(self.sound_scrollbar.value())

	def sound_state_changed(self):
		state = self.sound_checkbox.checkState() == 2
		self.sound_groupbox.setEnabled(state)

	def clipboard_changed(self):
		if self.clipboard_text != QApplication.clipboard().text():
			self.clipboard_text = QApplication.clipboard().text()

			clip = Clipper()
			clip.setClipperText(self.clipboard_text)
			self.layout.insertWidget(0, clip)

			if self.sound_groupbox.isEnabled():
				SoundHandler.play_clip_sound(self.volume)

	def add_clipper_pressed(self):
		clip = Clipper()
		self.layout.insertWidget(0, clip)

	def set_clipper_volume(self, volume):
		self.volume = volume

	@staticmethod
	def add_widget_with_alignment(master, widget, layout, alignment=False):
		tmp_layout = layout()
		tmp_layout.addWidget(widget)

		if alignment:
			tmp_layout.setAlignment(alignment)

		tmp_frame = QFrame(master)
		tmp_frame.resize(master.width(), 50)
		tmp_frame.setLayout(tmp_layout)

		return tmp_frame, tmp_layout

	@staticmethod
	def get_label_size(elem1):
		rect = elem1.fontMetrics().boundingRect(elem1.text())
		return rect.width(), rect.height()
	
	@staticmethod
	def horizontal_align_center(elem1, elem2):
		elem1_width = elem1.frameGeometry().width() if isinstance(elem1, QWidget) else int(elem1)
		elem2_width = elem2.frameGeometry().width() if isinstance(elem2, QWidget) else int(elem2)

		return (elem1_width // 2) - (elem2_width // 2)
	
	@staticmethod
	def vertical_align_center(elem1, elem2):
		elem1_height = elem1.frameGeometry().height() if isinstance(elem1, QWidget) else int(elem1)
		elem2_height = elem2.frameGeometry().height() if isinstance(elem2, QWidget) else int(elem2)

		return (elem1_height // 2) - (elem2_height // 2)


if __name__ == "__main__":
	root = Window()
	root.show()

	sys.exit(app.exec_())
