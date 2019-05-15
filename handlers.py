import os
import time

from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

scriptDir = os.path.dirname(os.path.realpath(__file__))


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
