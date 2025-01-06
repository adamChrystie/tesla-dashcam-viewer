import os.path
import sys
import shutil
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
        self.is_dragging = False
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
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderReleased.connect(self.on_slider_released)
        #self.slider.valueChanged.connect(self.on_slider_value_changed)

        self._main_player = self.media_player_video_widget_dict['front']['media_player']
        self._main_player.positionChanged.connect(self.update_slider)
        self._main_player.durationChanged.connect(self.update_slider_range)

        video_widget_frame.setLayout(frame_layout)
        main_layout.addWidget(video_widget_frame, 3)

        # Video clip list column
        self.clip_list = QVBoxLayout()
        self.clip_list.setSizeConstraint(QLayout.SetFixedSize)

        add_video_button = QPushButton("Scan A Directory For Videos")
        add_video_button.clicked.connect(self.add_video)
        self.clip_list.addWidget(add_video_button)

        copy_liked_videos_button = QPushButton("Copy Liked Events")
        copy_liked_videos_button.clicked.connect(self.copy_liked_videos)
        self.clip_list.addWidget(copy_liked_videos_button)

        self.clip_list_widget = QVBoxLayout()
        self.clip_list.addLayout(self.clip_list_widget, stretch=0)

        clip_widget = QWidget()
        clip_widget.setLayout(self.clip_list)
        main_layout.addWidget(clip_widget, stretch=1)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def copy_liked_videos(self):
        """Copy the liked videos to a specified directory."""
        src_fpaths = []
        for i in range(self.clip_list_widget.count()):
            item = self.clip_list_widget.itemAt(i)
            widget = item.widget()
            if isinstance(widget, VideoEventWidget):
                if widget._is_liked:
                    src_fpaths.extend(widget._video_files)

        file_dialog = QFileDialog(self)
        dir_path = file_dialog.getExistingDirectory()
        if dir_path:
            for src_fpath in src_fpaths:
                f_name = os.path.basename(src_fpath)
                dst_fpath = os.path.join(dir_path, f_name)
                shutil.copy2(src_fpath, dst_fpath)


    def on_slider_pressed(self):
        self.is_dragging = True
        for camera_name, widgets_dict in self.media_player_video_widget_dict.items():
            media_player = self.media_player_video_widget_dict[camera_name]['media_player']
            media_player.pause()

    def on_slider_released(self):
        self.is_dragging = False
        duration = self._main_player.duration()  # Total video duration in milliseconds
        if duration:
            # Map the slider value to the video's position in milliseconds
            #new_position = int((self.slider.value() / 1000) * duration)
            new_position = int(self.slider.value())
            for camera_name, widgets_dict in self.media_player_video_widget_dict.items():
                media_player = self.media_player_video_widget_dict[camera_name]['media_player']
                media_player.setPosition(new_position)  # Seek to new position
                media_player.play()

    def on_slider_value_changed(self, value):
        if self.is_dragging:
            # Optionally: Throttle updates or visually sync slider without stuttering
            pass

    def update_slider_range(self, duration):
        """Update the slider range when video duration changes."""
        self.slider.setRange(0, duration)

    def on_slider_moved(self, position):
        """Seek video when slider is moved."""
        duration = self._main_player.duration()  # Get total video duration in milliseconds
        if duration:
            #new_position = int((position / 1000) * duration)
            new_position = position
            for camera_name, widgets_dict in self.media_player_video_widget_dict.items():
                media_player = self.media_player_video_widget_dict[camera_name]['media_player']
                media_player.setPosition(new_position)  # Seek to new position

    def update_slider(self, position):
        """Update slider to match current video playback position."""
        duration = self._main_player.duration()
        if duration:
            #slider_position = int((position / duration) * 1000)
            slider_position = position
        #print(f'update_slider set slider position to:{slider_position}')
        self.slider.setValue(slider_position)


    def add_video(self):
        file_dialog = QFileDialog(self)
        dir_path = file_dialog.getExistingDirectory()
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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
