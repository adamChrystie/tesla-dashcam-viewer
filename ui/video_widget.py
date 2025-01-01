from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import QUrl


class VideoEventWidget(QWidget):
    """A single multi view video event to represent a specific time."""
    def __init__(self, event_name: str, media_video_players: dict, video_files: list):
        super().__init__()
        self._is_playing = False
        self._event_name = event_name
        self._backup_player = media_video_players['back']['media_player']
        self._front_upper_player = media_video_players['front']['media_player']
        self._left_repeater_player = media_video_players['left']['media_player']
        self._right_repeater_player = media_video_players['right']['media_player']
        self._video_files = video_files
        self.setup_ui()

    @property
    def event_name(self):
        return self._event_name
    @event_name.setter
    def event_name(self, value):
        self._event_name = value

    def setup_ui(self):
        # Set up layout
        layout = QHBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(2, 4, 2, 4)

        # Label to display the video file name
        self.label = QLabel(self.event_name)
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
        """
        self._backup_player = media_video_players['back']
        self._front_upper_player = media_video_players['front']
        self._left_repeater_player = media_video_players['left']
        self._right_repeater_player = media_video_players['right']
        :param self:
        :return:
        """
        if self._is_playing:
            self._backup_player.pause()
            self._front_upper_player.pause()
            self._left_repeater_player.pause()
            self._right_repeater_player.pause()
            self.play_pause_button.setText("Play")
        else:
            self._backup_player.setSource(QUrl.fromLocalFile(self._video_files[0]))
            self._front_upper_player.setSource(QUrl.fromLocalFile(self._video_files[1]))
            self._left_repeater_player.setSource(QUrl.fromLocalFile(self._video_files[2]))
            self._right_repeater_player.setSource(QUrl.fromLocalFile(self._video_files[3]))
            self._backup_player.play()
            self._front_upper_player.play()
            self._left_repeater_player.play()
            self._right_repeater_player.play()
            self.play_pause_button.setText("Pause")

        self._is_playing = not self._is_playing

        # if self.media_player.source().toLocalFile() != self.video_file:
        #     self.media_player.setSource(QUrl.fromLocalFile(self.video_file))
        #     self.media_player.play()
        #     self.play_pause_button.setText("Pause")
        # elif self.media_player.playbackState() == QMediaPlayer.PlayingState:
        #     self.media_player.pause()
        #     self.play_pause_button.setText("Play")
        # else:
        #     self.media_player.play()
        #     self.play_pause_button.setText("Pause")


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