import os.path
import sys
import shutil
from constants import TESLAS_CAMERA_NAMES
from file_utils.video_events import make_event_data_objects_for_a_dir_path

from PySide6.QtWidgets import (QApplication, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QPushButton, QMainWindow, QFileDialog, QFrame)

from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from ui.video_widget import VideoEventWidget
from ui.timeline_slider import TimelineSliderWidget
from ui.pop_up_info_window import InfoPopup
from ui.event_list_widget import ScrollableWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tesla Dashcam Reviewer")
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
        self.slider = TimelineSliderWidget(self.media_player_video_widget_dict)
        frame_layout.addWidget(self.slider, 2, 0, 1, frame_layout.columnCount())
        self._main_player = self.media_player_video_widget_dict['front']['media_player']
        self._main_player.positionChanged.connect(self.update_slider)
        self._main_player.durationChanged.connect(self.update_slider_range)

        video_widget_frame.setLayout(frame_layout)
        main_layout.addWidget(video_widget_frame, 3)
        # Video clip list column
        self.video_widget_layout = ScrollableWidget()
        main_layout.addWidget(self.video_widget_layout, stretch=1)


        self.command_buttons_vlayout = QVBoxLayout()
        # self.command_buttons_vlayout.setSizeConstraint(QLayout.SetFixedSize)

        add_video_button = QPushButton("Scan A Directory For Videos")
        add_video_button.clicked.connect(self.add_video)
        self.command_buttons_vlayout.addWidget(add_video_button)

        copy_liked_videos_button = QPushButton("Copy Liked Events")
        copy_liked_videos_button.clicked.connect(self.copy_liked_videos)
        self.command_buttons_vlayout.addWidget(copy_liked_videos_button)
        main_layout.addLayout(self.command_buttons_vlayout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def pause_all_media_players(self):
        """Pause all the media players."""
        for widgets_dict in self.media_player_video_widget_dict.values():
            widgets_dict['media_player'].pause()

    def copy_liked_videos(self):
        """Copy the liked videos to a specified directory."""
        self.pause_all_media_players()
        info_messages = []
        video_widgets = []
        for i in range(self.video_widget_layout.count()):
            item = self.video_widget_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, VideoEventWidget):
                if widget._is_liked:
                    video_widgets.append(widget)
        file_dialog = QFileDialog(self)
        dir_path = file_dialog.getExistingDirectory()
        if dir_path:
            for widget in video_widgets:
                for src_fpath in widget.video_files:
                    f_name = os.path.basename(src_fpath)
                    dst_dir_path = os.path.join(dir_path, widget.event_name)
                    try:
                        if not os.path.exists(dst_dir_path):
                            os.makedirs(dst_dir_path)
                        dst_fpath = os.path.join(dst_dir_path, f_name)
                        shutil.copy2(src_fpath, dst_fpath)
                    except OSError:
                        msg = f'There was an error copying file to {dst_dir_path} .'
                        info_messages.append((msg))
                        break

        if info_messages:
            info_messages.insert(0, 'Done copying videos but there were some issues.')
            long_msg = ""
            for msg in info_messages:
                long_msg = long_msg + f'{msg}\n'

            info_popup = InfoPopup(message=long_msg, parent=self)
        else:
            info_popup = InfoPopup(message='Done copying files.', parent=self)
        info_popup.show()

    def update_slider_range(self, duration):
        """Update the slider range when video duration changes."""
        self.slider.setRange(0, duration)

    def update_slider(self, position):
        """Update slider to match current video playback position."""
        duration = self._main_player.duration()
        if duration:
            slider_position = position
            self.slider.setValue(slider_position)

    def add_video(self):
        self.pause_all_media_players()
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
        self.video_widget_layout.add_widget(video_clip_widget)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
