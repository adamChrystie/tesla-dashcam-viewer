import os
import sys
import shutil
from typing import List
import  logging

import file_utils.updates
from constants import (
    APP_VERSION,
    TESLAS_CAMERA_NAMES)
from file_utils.video_events import make_event_data_objects_for_a_dir_path

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,QMainWindow,
    QFileDialog, QSizePolicy)

from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtGui import QScreen

from ui.video_widget import VideoEventWidget
from ui.timeline_slider import TimelineSliderWidget
from ui.pop_up_info_window import InfoPopup
from ui.event_list_widget import ScrollableWidget
from ui.video_screens import QVideoScreenGrid
from ui.main_window_widgets import CommandButtonsRow

from file_utils.settings import AppSettings
from file_utils.updates import should_check_for_update

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Get App Settings
        self._settings = AppSettings()
        self.is_dragging = False
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        self.aspect_ratio = 1.63
        startup_height = int(screen.height() * 0.9)
        startup_width = int(startup_height * self.aspect_ratio)
        x = (screen.width() - startup_width) // 2
        y = (screen.height() - startup_height) // 2
        # MainWindows appears in center of display using 90% of height, width is based on
        # desired UI aspect ratio.
        self.setGeometry(x, y, startup_width, startup_height)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._camera_names = TESLAS_CAMERA_NAMES
        self.media_player_video_widget_dict = {}
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
        self.setWindowTitle(f"Tesla Dashcam Reviewer {APP_VERSION}")
        #self.setAttribute(Qt.WA_OpaquePaintEvent)
        if should_check_for_update(self._settings):
            update_available = file_utils.updates.check_for_new_version()
            if update_available:
                popup = InfoPopup(
                    title='Update Available',
                    message=f"A newer version {update_available} is available. You are currently " \
                            f"running {APP_VERSION}.\nGet the new version at \nhttps://www.adamchrystie.com/tesla_dashcam_viewer.html",
                    parent=self)
                popup.show()

    def closeEvent(self, event):
        """Handle cleanup when the window is closed."""
        # Supposedly the below is not needed since QSettings objects handle writing changed
        # settings to disk periodically and when the object is destroyed.
        #self._settings.sync()
        pass

    def resizeEvent(self, event: QEvent) -> None:
        """Resize the window.
        Args:
            event (QEvent): The resize event.
        """
        self.setUpdatesEnabled(False)
        height = self.height()
        width = int(height * self.aspect_ratio)
        self.resize(QSize(width, height))
        super().resizeEvent(event)
        self.setUpdatesEnabled(True)

    def pause_others(self) -> None:
        """Pause all other media players except the one that triggered the signal."""
        sender = self.sender()
        for i in range(self.video_widget_layout.count()):
            item = self.video_widget_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, VideoEventWidget):
                if widget != sender and widget.play_pause_button.text() == "Pause":
                    widget.play_pause_button.click()  # Trigger a pause
                    break # We only can have one actively playing VideoEventWidget. Exiting the loop dramatically
                          # increases ui responsiveness. Verified via testing.

    def pause_all_media_players(self) -> None:
        """Pause all the media players."""
        for widgets_dict in self.media_player_video_widget_dict.values():
            widgets_dict['media_player'].pause()

    def copy_liked_videos(self) -> None:
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
                event_name = widget.event_name
                if widget.liked_folder_name_widget.text() != "":
                    event_tag = widget.liked_folder_name_widget.text().replace(' ','-')
                    event_name = f'{event_name}_{event_tag}'
                for src_fpath in widget.video_files:
                    f_name = os.path.basename(src_fpath)
                    dst_dir_path = os.path.join(dir_path, event_name)
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
            logger.warning(long_msg)
            info_popup = InfoPopup(message=long_msg, parent=self)
        else:
            msg = 'Done copying files.'
            info_popup = InfoPopup(message=msg, parent=self)
            logger.info(msg)
        info_popup.show()

    def update_slider_range(self, duration: int) -> None:
        """Update the slider range when video duration changes.
        Args:
            duration (int): The duration of the video.
        """
        self.slider.setRange(0, duration)

    def update_slider(self, position: int) -> None:
        """Update slider to match current video playback position.
        Args:
            position (int): The current position of the video.
        """
        duration = self._main_player.duration()
        if duration:
            slider_position = position
            self.slider.setValue(slider_position)

    def add_video(self) -> None:
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

    def add_video_clip_widget(self, event_name: str, video_files: List[str]) -> None:
        """Add a video clip widget to the layout.
        Args:
            event_name (str): The name of the event.
            video_files (List[str]): A list of video files to play.
        """
        video_clip_widget = VideoEventWidget(event_name, self.media_player_video_widget_dict, video_files)
        video_clip_widget.play_pressed.connect(self.pause_others)
        self.video_widget_layout.add_widget(video_clip_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
