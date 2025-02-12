"""Widgets which belong to the app's QMainWindow."""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import Qt

class CommandButtonsRow(QWidget):
    def __init__(self, add_video: QPushButton, copy_liked_videos: QPushButton, parent: QWidget=None):
        super().__init__(parent=parent)
        self._copy_liked_videos = copy_liked_videos
        self._add_video = add_video
        self.setup_ui()

    def setup_ui(self):
        """Setup the widget's ui."""
        self.set_style()
        command_buttons_hlayout = QHBoxLayout()
        self.setLayout(command_buttons_hlayout)
        add_video_button = QPushButton("Scan A Directory For Videos")
        add_video_button.setFocusPolicy(Qt.NoFocus)
        add_video_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        add_video_button.clicked.connect(self._add_video)
        command_buttons_hlayout.addWidget(add_video_button)
        command_buttons_hlayout.addStretch(stretch=50)
        copy_liked_videos_button = QPushButton("Copy Liked Events")
        copy_liked_videos_button.setFocusPolicy(Qt.NoFocus)
        copy_liked_videos_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        copy_liked_videos_button.clicked.connect(self._copy_liked_videos)
        command_buttons_hlayout.addWidget(copy_liked_videos_button)
        command_buttons_hlayout.addStretch(stretch=400)

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
        """
        self.setStyleSheet(qml)

