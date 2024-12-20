import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QSplitter, QFileDialog
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import Qt, QUrl

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player Tool")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Video display area
        self.video_widget = QVideoWidget()
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        main_layout.addWidget(self.video_widget, 3)

        # Video clip list column
        self.clip_list = QVBoxLayout()

        add_video_button = QPushButton("Add Video")
        add_video_button.clicked.connect(self.add_video)
        self.clip_list.addWidget(add_video_button)

        self.clip_list_widget = QVBoxLayout()
        self.clip_list.addLayout(self.clip_list_widget)

        clip_widget = QWidget()
        clip_widget.setLayout(self.clip_list)
        main_layout.addWidget(clip_widget, 1)

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
