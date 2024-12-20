from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import QUrl

class VideoWidget(QWidget):
    def __init__(self, video_file, media_player):
        super().__init__()
        self.video_file = video_file
        self.media_player = media_player

        layout = QHBoxLayout()

        # Label to display the video file name
        self.label = QLabel(video_file.split('/')[-1])
        layout.addWidget(self.label)

        # Play/Pause button
        self.play_pause_button = QPushButton("Play/Pause")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        layout.addWidget(self.play_pause_button)

        self.setLayout(layout)

    def toggle_play_pause(self):
        if self.media_player.source().toLocalFile() != self.video_file:
            self.media_player.setSource(QUrl.fromLocalFile(self.video_file))
            self.media_player.play()
            self.play_pause_button.setText("Pause")
        elif self.media_player.playbackState() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.play_pause_button.setText("Play")
        else:
            self.media_player.play()
            self.play_pause_button.setText("Pause")