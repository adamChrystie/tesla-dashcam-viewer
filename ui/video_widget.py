from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy)
from PySide6.QtCore import QUrl, Signal

class VideoEventWidget(QWidget):
    """A single multi view video event to represent a specific time."""

    play_pressed = Signal()

    def __init__(self, event_name: str, media_video_players: dict, video_files: list, parent=None):
        super().__init__(parent=parent)
        self._is_playing = False
        self._event_name = event_name
        self._backup_player = media_video_players['back']['media_player']
        self._front_upper_player = media_video_players['front']['media_player']
        self._left_repeater_player = media_video_players['left_repeater']['media_player']
        self._right_repeater_player = media_video_players['right_repeater']['media_player']
        self._video_files = video_files
        self._is_liked = False
        self.setup_ui()
        #print(f'Video Widget {self.event_name} size hint:{self.sizeHint()}')

    @property
    def video_files(self):
        return self._video_files
    @video_files.setter
    def video_files(self, value):
        self._video_files = value
    @property
    def event_name(self):
        return self._event_name
    @event_name.setter
    def event_name(self, value):
        self._event_name = value

    def setup_ui(self):
        self.set_style()
        # Set up layout
        layout = QHBoxLayout()
        #layout.setContentsMargins(2, 4, 2, 4)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addSpacing(0)

        # Label to display the video file name
        self.label = QLabel(self.event_name)
        layout.addWidget(self.label)

        # Play/Pause button
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        layout.addWidget(self.play_pause_button)

        # Like/Heart Clip Button
        self.like_clip_button = QPushButton("\u2764")  # Unicode for a heart icon
        self.like_clip_button.clicked.connect(self.toggle_is_liked)
        layout.addWidget(self.like_clip_button)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # Wrap up
        self.setLayout(layout)
        self.adjustSize()
        self.update()

    def toggle_is_liked(self):
        """Handle the heart button being pressed."""
        self._is_liked = not self._is_liked
        if self._is_liked:
            self.like_clip_button.setStyleSheet("color: red;")
        else:
            self.like_clip_button.setStyleSheet("color: white;")

    def set_style(self):
        """Apply a stylesheet."""
        qml = """
        QWidget {
                font-size: 12px;
                font-weight: normal;
                background-color: #f0f0f0;
                border-radius: 0px;
                border: 0px solid #d0d0d0;
                padding: 0px 0px;
            }
        QLabel {
            background-color: #0078d7;
            color: white;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
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
            self.play_pressed.emit()
            self.play_pause_button.setText("Pause")
            self._backup_player.setSource(QUrl.fromLocalFile(self._video_files[0]))
            self._front_upper_player.setSource(QUrl.fromLocalFile(self._video_files[1]))
            self._left_repeater_player.setSource(QUrl.fromLocalFile(self._video_files[2]))
            self._right_repeater_player.setSource(QUrl.fromLocalFile(self._video_files[3]))
            self._backup_player.play()
            self._front_upper_player.play()
            self._left_repeater_player.play()
            self._right_repeater_player.play()
        self._is_playing = not self._is_playing

