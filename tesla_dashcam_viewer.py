import sys

import file_utils.video_events
from constants import TESLAS_CAMERA_NAMES
from file_utils.video_events import make_event_data_objects_for_a_dir_path

from PySide6.QtWidgets import (
    QSizePolicy, QApplication, QWidget, QLayout, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QMainWindow, QFileDialog, QFrame)

from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from ui.video_widget import VideoEventWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player Tool")
        self.setGeometry(0, 0, 1000, 600)
        #self.setStyleSheet("background-color: lightblue;")
        self._camera_names = TESLAS_CAMERA_NAMES
        self.media_player_video_widget_dict = {}
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        # Video display area
        video_widget_frame = QFrame()
        video_widget_frame.setFrameShape(QFrame.Box)
        video_widget_frame.setLineWidth(3)
        #frame_layout = QHBoxLayout(video_widget_frame)
        frame_layout = QGridLayout(video_widget_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        #frame_layout.setSpacing(0)
        for count, camera_name in enumerate(self._camera_names):
            video_widget = QVideoWidget()
            video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
            frame_layout.addWidget(video_widget, count // 2, count % 2)
            media_player = QMediaPlayer()
            audio_output = QAudioOutput()
            audio_output.setMuted(True)
            media_player.setAudioOutput(audio_output)
            media_player.setVideoOutput(video_widget)
            self.media_player_video_widget_dict[camera_name] = {'video_widget': video_widget, 'media_player': media_player,
                                                 'audio_output': audio_output}
        video_widget_frame.setLayout(frame_layout)
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
        vide_files = []
        file_dialog = QFileDialog(self)
        dir_path = file_dialog.getExistingDirectory()
        print('%%%%', dir_path)
        if dir_path:
            event_data_objs = make_event_data_objects_for_a_dir_path(dir_path)
            for event_data in event_data_objs:
                pass
        # video_files, _ = QFileDialog.getOpenFileNames(
        #     None, "Select Files", "", "All Files (*);;Text Files (*.txt);;Python Files (*.py)")
        # if video_files:
        #     self.add_video_clip_widget(video_files)
        #     print(f'Added video clip widget for:{','.join(video_files)}')

    def add_video_clip_widget(self, video_files):
        video_clip_widget = VideoEventWidget("test", self.media_player_video_widget_dict, video_files)
        self.clip_list_widget.addWidget(video_clip_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
