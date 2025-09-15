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
from PySide6.QtGui import QScreen, QKeySequence, QShortcut

from ui.video_widget import VideoEventWidget
from ui.timeline_slider import TimelineSliderWidget
from ui.pop_up_info_window import InfoPopup
from ui.event_list_widget import ScrollableWidget
from ui.video_screens import QVideoScreenGrid
from ui.main_window_widgets import CommandButtonsRow
from ui.loading_widget import LoadingWidget, SkeletonWidget

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
        
        # Loading widget for better user feedback
        self.loading_widget = LoadingWidget("Scanning videos...", self)
        self.loading_widget.hide()
        
        command_buttons_row = CommandButtonsRow(self.add_video, self.copy_liked_videos)
        main_vlayout.addWidget(command_buttons_row)
        main_vlayout.addLayout(main_hlayout)
        main_vlayout.addWidget(self.slider, stretch=False)
        main_widget.setLayout(main_vlayout)
        self.setCentralWidget(main_widget)
        self.setWindowTitle(f"Tesla Dashcam Reviewer {APP_VERSION}")
        #self.setAttribute(Qt.WA_OpaquePaintEvent)
        
        # Setup keyboard shortcuts for better UX
        self._setup_keyboard_shortcuts()
        
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
        """Resize the window and reposition loading widget.
        Args:
            event (QEvent): The resize event.
        """
        self.setUpdatesEnabled(False)
        height = self.height()
        width = int(height * self.aspect_ratio)
        self.resize(QSize(width, height))
        super().resizeEvent(event)
        
        # Reposition loading widget if visible
        if self.loading_widget.isVisible():
            self._center_loading_widget()
            
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
        """Pause all the media players and optimize memory usage."""
        for widgets_dict in self.media_player_video_widget_dict.values():
            widgets_dict['media_player'].pause()
            # Clear media source when paused to free memory
            widgets_dict['media_player'].setSource("")
        
        # Also pause all video event widgets and clear their sources
        self._cleanup_unused_video_sources()

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
        """Add video files with improved user feedback and performance."""
        self.pause_all_media_players()
        file_dialog = QFileDialog(self)
        dir_path = file_dialog.getExistingDirectory()
        if dir_path:
            # Show loading indicator
            self.loading_widget.update_message("Scanning video files...")
            self.loading_widget.show_loading()
            
            # Center the loading widget
            self._center_loading_widget()
            
            # Process in the background (for real apps, use QThread)
            try:
                event_data_objs = make_event_data_objects_for_a_dir_path(dir_path)
                
                self.loading_widget.update_message(f"Loading {len(event_data_objs)} video events...")
                
                # Add skeleton placeholders first for perceived performance
                skeletons = []
                for _ in range(min(len(event_data_objs), 5)):  # Show up to 5 skeletons
                    skeleton = SkeletonWidget()
                    skeletons.append(skeleton)
                    self.video_widget_layout.add_widget(skeleton)
                
                # Process events and replace skeletons
                for i, event_data in enumerate(event_data_objs):
                    video_files = []
                    for camera_name, video_fpath in event_data.camera_files_dict.items():
                        video_files.append(video_fpath.as_posix())
                    event_name = event_data.timestamp
                    
                    # Remove skeleton and add real widget
                    if i < len(skeletons):
                        skeleton = skeletons[i]
                        self.video_widget_layout.container_layout.removeWidget(skeleton)
                        skeleton.deleteLater()
                    
                    self.add_video_clip_widget(event_name, video_files)
                
                # Clean up any remaining skeletons
                for i in range(len(event_data_objs), len(skeletons)):
                    skeleton = skeletons[i]
                    self.video_widget_layout.container_layout.removeWidget(skeleton)
                    skeleton.deleteLater()
                    
            except Exception as e:
                logger.error(f"Error loading videos: {e}")
            finally:
                self.loading_widget.hide_loading()

    def _center_loading_widget(self) -> None:
        """Center the loading widget over the main window."""
        main_rect = self.geometry()
        loading_rect = self.loading_widget.geometry()
        x = main_rect.x() + (main_rect.width() - loading_rect.width()) // 2
        y = main_rect.y() + (main_rect.height() - loading_rect.height()) // 2
        self.loading_widget.move(x, y)

    def add_video_clip_widget(self, event_name: str, video_files: List[str]) -> None:
        """Add a video clip widget to the layout.
        Args:
            event_name (str): The name of the event.
            video_files (List[str]): A list of video files to play.
        """
        video_clip_widget = VideoEventWidget(event_name, self.media_player_video_widget_dict, video_files)
        video_clip_widget.play_pressed.connect(self.pause_others)
        self.video_widget_layout.add_widget(video_clip_widget)

    def _setup_keyboard_shortcuts(self) -> None:
        """Setup keyboard shortcuts for improved usability."""
        # Space for play/pause
        play_pause_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        play_pause_shortcut.activated.connect(self._toggle_main_playback)
        
        # Arrow keys for navigation
        next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        next_shortcut.activated.connect(self._next_video_event)
        
        prev_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        prev_shortcut.activated.connect(self._previous_video_event)
        
        # Up/Down for scrolling through events
        down_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        down_shortcut.activated.connect(self._scroll_down_events)
        
        up_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        up_shortcut.activated.connect(self._scroll_up_events)
        
        # Ctrl+O for open folder
        open_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_O), self)
        open_shortcut.activated.connect(self.add_video)

    def _toggle_main_playback(self) -> None:
        """Toggle playback of the main player."""
        if self._main_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.pause_all_media_players()
        else:
            # Find the currently selected video event and play it
            self._play_current_video_event()

    def _play_current_video_event(self) -> None:
        """Play the currently focused video event."""
        # This is a placeholder - in a full implementation, you'd track which event is selected
        for i in range(self.video_widget_layout.count()):
            item = self.video_widget_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, VideoEventWidget):
                if widget.play_pause_button.text() == "Play":
                    widget.play_pause_button.click()
                    break

    def _next_video_event(self) -> None:
        """Navigate to next video event."""
        # Placeholder for navigation logic
        pass

    def _previous_video_event(self) -> None:
        """Navigate to previous video event."""
        # Placeholder for navigation logic
        pass

    def _scroll_down_events(self) -> None:
        """Scroll down in the events list."""
        scroll_area = self.video_widget_layout.scroll_area
        scrollbar = scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.value() + 50)

    def _scroll_up_events(self) -> None:
        """Scroll up in the events list."""
        scroll_area = self.video_widget_layout.scroll_area
        scrollbar = scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.value() - 50)

    def _cleanup_unused_video_sources(self) -> None:
        """Clean up video sources for widgets not currently in view to save memory."""
        scroll_area = self.video_widget_layout.scroll_area
        viewport = scroll_area.viewport()
        viewport_rect = viewport.rect()
        
        for i in range(self.video_widget_layout.count()):
            item = self.video_widget_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, VideoEventWidget):
                widget_rect = widget.geometry()
                # If widget is not visible in viewport and not playing, clear its sources
                if not viewport_rect.intersects(widget_rect) and not widget._is_playing:
                    widget._cleanup_media_sources()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
