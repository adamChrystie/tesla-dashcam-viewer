"""A widget to scrub through the video timeline manually."""

from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor, QSurfaceFormat

class TimelineSliderWidget(QSlider):
    def __init__(self, media_player_video_widget_dict, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent=parent)
        self._handle_size = 18 # Diameter of the slider's handle.
        # Flag to see if timeline is being manually scrolled.
        self.is_dragging = False
        # Flag to track if an arrow key is pressed
        self.arrow_key_pressed = False
        self.media_player_video_widget_dict = media_player_video_widget_dict
        self.main_player = media_player_video_widget_dict['front']['media_player']
        self.setup_ui()
        self.setup_connections()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.arrow_key_pressed = True
            self.decrease_time()
        elif event.key() == Qt.Key_Right:
            self.arrow_key_pressed = True
            self.increase_time()
        else:
            super().keyPressEvent(event)  # Call base class method for other keys

    def keyReleaseEvent(self, event):
        if event.key() in (Qt.Key_Left, Qt.Key_Right):
            self.arrow_key_pressed = False  # Reset flag when arrow key is released
            for camera_name, widgets_dict in self.media_player_video_widget_dict.items():
                media_player = self.media_player_video_widget_dict[camera_name]['media_player']
                media_player.play()
        else:
            super().keyReleaseEvent(event)  # Call base class method

    def decrease_time(self):
        current_value = self.value()
        new_value = max(current_value - 50, self.minimum())  # Adjust as needed
        self.setValue(new_value)
        self.on_slider_value_changed(new_value)

    def increase_time(self):
        current_value = self.value()
        new_value = min(current_value + 50, self.maximum())  # Adjust as needed
        self.setValue(new_value)
        self.on_slider_value_changed(new_value)


    def setup_connections(self):
        """Setup the widget's connections."""
        self.sliderMoved.connect(self.on_slider_moved)
        self.sliderPressed.connect(self.on_slider_pressed)
        self.sliderReleased.connect(self.on_slider_released)
        self.valueChanged.connect(self.on_slider_value_changed)
        #self.timer.timeout.connect(self.update_video)

    def setup_ui(self):
        format = QSurfaceFormat()
        format.setRenderableType(QSurfaceFormat.OpenGL)
        QSurfaceFormat.setDefaultFormat(format)
        self.setStyleSheet("QSlider::handle { background: transparent; }")
        #self.setFocusPolicy(Qt.StrongFocus)
        self.setRange(0, 1000)  # Set the range based on video duration later
        # Create a timer for continuous updates
        #self.timer = QTimer()

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
            # This is being detected.
            # Optionally: Throttle updates or visually sync slider without stuttering
            #print(f'on_slider_value_changed: Reacting to a drag')
            pass
        elif self.arrow_key_pressed:
            # This is being detected..just need to find a good way to have video widgets update
            # as arrow key is pressed or held down.
            pass

    # def update_video(self):
    #     pass

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        # Set the desired size for the handle (circle)
        # handle_pos = (self.valueToPosition(self.value()) - handle_size // 2) + handle_size / 2
        # # Create a square rectangle for the circle
        # handle_rect = QRect(handle_pos, (self.height() - handle_size) // 2, handle_size, handle_size)

        # Calculate the center position of the slider handle
        handle_pos_x = self.valueToPosition(self.value()) - self._handle_size // 2
        handle_pos_y = (self.height() - self._handle_size) // 2
        handle_rect = QRect(handle_pos_x, handle_pos_y, self._handle_size, self._handle_size)

        # Draw the handle as a circle
        painter.setBrush(QColor(71, 149, 179))  # Handle color
        painter.setPen(Qt.NoPen)  # Remove border
        painter.drawEllipse(handle_rect)  # Draw the circle
        painter.end()

    def valueToPosition(self, value):
        """Convert the slider value to the corresponding position."""
        try:
            position = int((value - self.minimum()) / (self.maximum() - self.minimum()) * (self.width() - 9))
        except ZeroDivisionError as e:
            position = value
            print(f'timeline_slider.valueToPosition error handled:\n{e}')
        return position

    def sizeHint(self):
       """Override sizeHint to provide enough space for the circular handle."""
       return QSize(super().sizeHint().width(), 20)  # Adjust height as needed



