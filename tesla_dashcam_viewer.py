import os
import platform
import sys
import shutil
from constants import TESLAS_CAMERA_NAMES
from file_utils.video_events import make_event_data_objects_for_a_dir_path

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,QMainWindow,
    QFileDialog, QSizePolicy)

from PySide6.QtCore import Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from ui.video_widget import VideoEventWidget
from ui.timeline_slider import TimelineSliderWidget
from ui.pop_up_info_window import InfoPopup
from ui.event_list_widget import ScrollableWidget
from ui.video_screens import QVideoScreenGrid
from ui.main_window_widgets import CommandButtonsRow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tesla Dashcam Reviewer")
        self._main_window_width = 1765
        self.main_window_height = 1080
        if platform.system() == "Windows":
            #self.setGeometry(0, 0,  self._main_window_width * 0.70, self.main_window_height * 0.70)
            self.setFixedSize(int(self._main_window_width * 0.70), int(self.main_window_height * 0.70))
        else:
            #self.setGeometry(0, 0, self._main_window_width, self.main_window_height)
            self.setFixedSize(self._main_window_width, self.main_window_height)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._camera_names = TESLAS_CAMERA_NAMES
        self.media_player_video_widget_dict = {}
        self.is_dragging = False
        # Main layout
        main_widget = QWidget()
        main_vlayout = QVBoxLayout()
        main_hlayout = QHBoxLayout()

        # Video display area
        self.video_screens = QVideoScreenGrid()
        main_hlayout.addWidget(self.video_screens, 3)
        for count, camera_name in enumerate(self._camera_names):
            video_widget = QVideoWidget()
            video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
            self.video_screens.addWidget(video_widget, count // 2, count % 2)
            media_player = QMediaPlayer()
            audio_output = QAudioOutput()
            audio_output.setMuted(True)
            media_player.setAudioOutput(audio_output)
            media_player.setVideoOutput(video_widget)
            self.media_player_video_widget_dict[camera_name] = {
                'video_widget': video_widget, 'media_player': media_player, 'audio_output': audio_output}

        # Playback slider
        self.slider = TimelineSliderWidget(self.media_player_video_widget_dict)
        self._main_player = self.media_player_video_widget_dict['front']['media_player']
        self._main_player.positionChanged.connect(self.update_slider)
        self._main_player.durationChanged.connect(self.update_slider_range)

        # Video clip list column
        self.video_widget_layout = ScrollableWidget()
        main_hlayout.addWidget(self.video_widget_layout, stretch=True)
        command_buttons_row = CommandButtonsRow(self.add_video, self.copy_liked_videos)
        main_vlayout.addWidget(command_buttons_row)
        main_vlayout.addLayout(main_hlayout)
        main_vlayout.addWidget(self.slider, stretch=False)
        main_widget.setLayout(main_vlayout)
        self.setCentralWidget(main_widget)

    def resizeEvent(self, event):
        size = self.size()
        print(f'MainWindows size is now: width = {size.width()} height = {size.height()}')
        super().resizeEvent(event)

    def pause_others(self):
        sender = self.sender()
        for i in range(self.video_widget_layout.count()):
            item = self.video_widget_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, VideoEventWidget):
                if widget != sender and widget.play_pause_button.text() == " Pause ":
                    widget.play_pause_button.click()  # Trigger a pause
                    break # We only can have one actively playing VideoEventWidget. Exiting the loop dramatically
                          # increases ui responsiveness. Verified via testing.

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
                if widget.is_liked:
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
                for camera_name, video_fpath in event_data.camera_files_dict.items():
                    vide_files.append(video_fpath.as_posix())
                event_name = event_data.timestamp
                self.add_video_clip_widget(event_name, vide_files)

    def add_video_clip_widget(self, event_name, video_files):
        video_clip_widget = VideoEventWidget(event_name, self.media_player_video_widget_dict, video_files)
        video_clip_widget.play_pressed.connect(self.pause_others)
        self.video_widget_layout.add_widget(video_clip_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
