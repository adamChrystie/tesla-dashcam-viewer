import sys
from PySide6.QtWidgets import (
    QSizePolicy, QApplication, QWidget, QLayout, QVBoxLayout, QHBoxLayout,
    QPushButton, QMainWindow, QFileDialog, QFrame)

from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from ui.video_widget import VideoWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player Tool")
        self.setGeometry(0, 0, 1000, 600)
        #self.setStyleSheet("background-color: lightblue;")

        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Video display area
        self.video_widget = QVideoWidget()
        #self.video_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        #self.video_widget.setStyleSheet("border: none;")
        video_widget_frame = QFrame()
        video_widget_frame.setFrameShape(QFrame.Box)
        video_widget_frame.setLineWidth(3)
        frame_layout = QHBoxLayout(video_widget_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        #frame_layout.setSpacing(0)
        frame_layout.addWidget(self.video_widget, stretch=1)
        video_widget_frame.setLayout(frame_layout)
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        main_layout.addWidget(video_widget_frame, 3)

        # Video clip list column
        self.clip_list = QVBoxLayout()
        self.clip_list.setSizeConstraint(QLayout.SetFixedSize)

        add_video_button = QPushButton("Add Video")
        add_video_button.clicked.connect(self.add_video)
        self.clip_list.addWidget(add_video_button)

        self.clip_list_widget = QVBoxLayout()
        self.clip_list.addLayout(self.clip_list_widget, stretch=0)

        clip_widget = QWidget()
        clip_widget.setLayout(self.clip_list)
        main_layout.addWidget(clip_widget, stretch=1)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def add_video(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Videos (*.mp4 *.avi *.mkv)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec():
            video_file = file_dialog.selectedFiles()[0]
            self.add_video_clip_widget(video_file)

    def add_video_clip_widget(self, video_file):
        video_clip_widget = VideoWidget(video_file, self.media_player)
        self.clip_list_widget.addWidget(video_clip_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
