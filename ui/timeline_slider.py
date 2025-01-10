"""A widget to scrub through the video timeline manually."""

from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt

class TimelineSliderWidget(QSlider):
    def __init__(self, media_player_video_widget_dict, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent=parent)
        self.is_dragging = False
        self.media_player_video_widget_dict = media_player_video_widget_dict
        self.main_player = media_player_video_widget_dict['front']['media_player']
        self.setup_connections()
        self.setup_ui()

    def setup_connections(self):
        """Setup the widget's connections."""
        self.sliderMoved.connect(self.on_slider_moved)
        self.sliderPressed.connect(self.on_slider_pressed)
        self.sliderReleased.connect(self.on_slider_released)
        # self.slider.valueChanged.connect(self.on_slider_value_changed)

    def setup_ui(self):
        self.setRange(0, 1000)  # Set the range based on video duration later

    def on_slider_pressed(self):
        self.is_dragging = True
        for camera_name, widgets_dict in self.media_player_video_widget_dict.items():
            media_player = self.media_player_video_widget_dict[camera_name]['media_player']
            media_player.pause()

    def on_slider_released(self):
        self.is_dragging = False
        duration = self.main_player.duration()  # Total video duration in milliseconds
        if duration:
            # Map the slider value to the video's position in milliseconds
            #new_position = int((self.slider.value() / 1000) * duration)
            new_position = int(self.value())
            for camera_name, widgets_dict in self.media_player_video_widget_dict.items():
                media_player = self.media_player_video_widget_dict[camera_name]['media_player']
                media_player.setPosition(new_position)  # Seek to new position
                media_player.play()

    def on_slider_moved(self, position):
        """Seek video when slider is moved."""
        duration = self.main_player.duration()  # Get total video duration in milliseconds
        if duration:
            #new_position = int((position / 1000) * duration)
            new_position = position
            for camera_name, widgets_dict in self.media_player_video_widget_dict.items():
                media_player = self.media_player_video_widget_dict[camera_name]['media_player']
                media_player.setPosition(new_position)  # Seek to new position

    def on_slider_value_changed(self, value):
        if self.is_dragging:
            # Optionally: Throttle updates or visually sync slider without stuttering
            pass