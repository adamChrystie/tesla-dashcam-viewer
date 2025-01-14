"""Widgets which belong to the app's QMainWindow."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt

class CommandButtonsRow(QWidget):
    def __init__(self, add_video, copy_liked_videos, parent=None):
        super().__init__(parent=parent)
        self._copy_liked_videos = copy_liked_videos
        self._add_video = add_video
        self.setup_ui()

    def setup_ui(self):
        """Setup the widget's ui."""
        command_buttons_hlayout = QHBoxLayout()
        self.setLayout(command_buttons_hlayout)
        add_video_button = QPushButton("Scan A Directory For Videos")
        add_video_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_video_button.clicked.connect(self._add_video)
        command_buttons_hlayout.addWidget(add_video_button)
        command_buttons_hlayout.addStretch(stretch=50)
        copy_liked_videos_button = QPushButton("Copy Liked Events")
        copy_liked_videos_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        copy_liked_videos_button.clicked.connect(self._copy_liked_videos)
        command_buttons_hlayout.addWidget(copy_liked_videos_button)
        command_buttons_hlayout.addStretch(stretch=400)

