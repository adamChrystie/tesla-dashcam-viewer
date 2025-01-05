import sys

import file_utils.video_events
from constants import TESLAS_CAMERA_NAMES
from file_utils.video_events import make_event_data_objects_for_a_dir_path

from PySide6.QtWidgets import (
    QSizePolicy, QApplication, QWidget, QLayout, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QMainWindow, QFileDialog, QFrame, QSlider)

from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from ui.video_widget import VideoEventWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player Tool")
        self.setGeometry(0, 0, 1000, 600)
        self._camera_names = TESLAS_CAMERA_NAMES
        self.media_player_video_widget_dict = {}
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        # Video display area
        video_widget_frame = QFrame()
        video_widget_frame.setFrameShape(QFrame.Box)
        video_widget_frame.setLineWidth(3)
        frame_layout = QGridLayout(video_widget_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
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

        # Playback slider
        self.slider = QSlider(Qt.Horizontal)
        frame_layout.addWidget(self.slider, 2, 0, 1, frame_layout.columnCount())
        self.slider.setRange(0, 1000)  # Set the range based on video duration later
        self.slider.sliderMoved.connect(self.on_slider_moved)

        self._main_player = self.media_player_video_widget_dict['front']['media_player']
        self._main_player.positionChanged.connect(self.update_slider)
        #self._main_player.durationChanged.connect(self.update_slider_range)

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

    def update_slider_range(self, duration):
        """Update the slider range when video duration changes."""
        self.slider.setRange(0, 1000)

    def on_slider_moved(self, position):
        """Seek video when slider is moved."""
        self._main_player.positionChanged.disconnect()
        duration = self._main_player.duration()  # Get total video duration in milliseconds
        if duration:
            new_position = int((position / 1000) * duration)
            print('*****', new_position)
            for camera_name, widgets_dict in self.media_player_video_widget_dict.items():
                media_player = self.media_player_video_widget_dict[camera_name]['media_player']
                media_player.setPosition(new_position)  # Seek to new position
        self._main_player.positionChanged.connect(self.update_slider)


    def update_slider(self, position):
        """Update slider to match current video playback position."""
        duration = self._main_player.duration()
        if duration:
            slider_position = int((position / duration) * 1000)
            print(f'slider position:{slider_position}')
            self.slider.setValue(slider_position)


    def add_video(self):
        file_dialog = QFileDialog(self)
        dir_path = file_dialog.getExistingDirectory()
        print('%%%%', dir_path)
        if dir_path:
            event_data_objs = make_event_data_objects_for_a_dir_path(dir_path)
            for event_data in event_data_objs:
                vide_files = []
                for camera_name, video_fpath in event_data._camera_files_dict.items():
                    vide_files.append(video_fpath.as_posix())
                event_name = event_data._timestamp
                self.add_video_clip_widget(event_name, vide_files)

    def add_video_clip_widget(self, event_name, video_files):
        video_clip_widget = VideoEventWidget(event_name, self.media_player_video_widget_dict, video_files)
        self.clip_list_widget.addWidget(video_clip_widget)

    def on_timeline_moved(self, position):
        duration = self._main_player.duration()
        if duration:
            new_position = (position / 100) * duration
            self._main_player.setPosition(new_position)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
