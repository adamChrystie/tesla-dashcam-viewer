from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import QUrl

class VideoWidget(QWidget):
    def __init__(self, video_file, media_player):
        super().__init__()
        self.video_file = video_file
        self.media_player = media_player

        # Set up layout
        layout = QHBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(2, 4, 2, 4)

        # Label to display the video file name
        self.label = QLabel(video_file.split('/')[-1])
        layout.addWidget(self.label)

        # Play/Pause button
        self.play_pause_button = QPushButton("Play/Pause")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        layout.addWidget(self.play_pause_button)

        self.setLayout(layout)
        self.set_style()

    def set_style(self):
        """Apply a stylesheet."""

        qml = """
        QWidget {
                background-color: #f0f0f0;
                border-radius: 10px;
                border: 0px solid #d0d0d0;
            }
        QLabel {
            font-size: 14px;
            font-weight: normal;
            background-color: #0078d7;
            color: white;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #005bb5;
        }
        """

        self.setStyleSheet(qml)

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