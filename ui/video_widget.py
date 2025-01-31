from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QLineEdit)
from PySide6.QtCore import QUrl, Signal

class VideoEventWidget(QWidget):
    """A single multi view video event to represent a specific time."""

    play_pressed = Signal()

    def __init__(self, event_name: str, media_video_players: dict, video_files: list, parent=None):
        super().__init__(parent=parent)
        self._is_playing = False
        self._event_name = event_name
        self._liked_folder_name = None
        self._backup_player = media_video_players['back']['media_player']
        self._front_upper_player = media_video_players['front']['media_player']
        self._left_repeater_player = media_video_players['left_repeater']['media_player']
        self._right_repeater_player = media_video_players['right_repeater']['media_player']
        self._video_files = video_files
        self._is_liked = False
        self.setup_ui()
        self.setup_connections()

    @property
    def liked_folder_name(self):
        """An optional name to use as the events parent folder when copying liked events.
        This can help users find their liked events by a named folder."""
        return self._liked_folder_name

    @property
    def is_liked(self):
        return self._is_liked

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
        layout.setContentsMargins(1, 2, 1, 2)
        layout.addSpacing(0)
        # Label to display the video file name
        self.label = QLabel(self.event_name)
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.label)
        # Play/Pause button
        self.play_pause_button = QPushButton("Play")
        self.play_pause_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.play_pause_button)
        # Like/Heart Clip Button
        self.like_clip_button = QPushButton("\u2764")  # Unicode for a heart icon
        self.like_clip_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.like_clip_button)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        # Optional liked event parent folder name description.
        liked_folder_name_label = QLabel("Event's Folder Tag")
        self.liked_folder_name_widget = QLineEdit()
        self.liked_folder_name_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(liked_folder_name_label)
        layout.addWidget(self.liked_folder_name_widget)
        # Wrap up
        layout.addStretch()
        self.setLayout(layout)

    def setup_connections(self):
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        self.like_clip_button.clicked.connect(self.toggle_is_liked)
        self._front_upper_player.mediaStatusChanged.connect(self.handle_media_status_change)

    def handle_media_status_change(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._is_playing:
                self.toggle_play_pause()

    def toggle_is_liked(self):
        """Handle the heart button being pressed."""
        self._is_liked = not self._is_liked
        if self._is_liked:
            self.like_clip_button.setStyleSheet("color: red;")
        else:
            self.like_clip_button.setStyleSheet("color: white;")

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

    def set_style(self):
        """Apply a stylesheet."""
        qml = """
        QWidget {
                font-size: 14px;
                font-weight: normal;
                background-color: #f0f0f0;
                border-radius: 4px;
                border: 0px solid #d0d0d0;
                padding: 4px 0px;
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
        QLineEdit { 
            color: black;
        }
        """
        self.setStyleSheet(qml)

