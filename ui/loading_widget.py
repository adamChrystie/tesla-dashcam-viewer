"""Loading indicator widget for better user feedback."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QMovie, QPixmap
from PySide6.QtCore import Qt


class LoadingWidget(QWidget):
    """A modern loading widget with spinner and progress indication."""
    
    def __init__(self, message: str = "Loading...", parent: QWidget = None):
        super().__init__(parent)
        self.setFixedSize(200, 100)
        self.message = message
        self._setup_ui()
        self._setup_animations()
        
    def _setup_ui(self):
        """Setup the loading widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                color: #333;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: #f0f0f0;
                height: 6px;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 3px;
            }
        """)
        
        layout.addWidget(self.message_label)
        layout.addWidget(self.progress_bar)
        
        # Style the container
        self.setStyleSheet("""
            LoadingWidget {
                background-color: rgba(255, 255, 255, 230);
                border: 1px solid #d0d0d0;
                border-radius: 6px;
            }
        """)
        
    def _setup_animations(self):
        """Setup smooth fade in/out animations."""
        self.setWindowOpacity(0.0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def show_loading(self):
        """Show the loading widget with fade-in effect."""
        self.show()
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()
        
    def hide_loading(self):
        """Hide the loading widget with fade-out effect."""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()
        
    def update_message(self, message: str):
        """Update the loading message."""
        self.message_label.setText(message)


class SkeletonWidget(QWidget):
    """A skeleton placeholder widget shown while content loads."""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self._setup_ui()
        self._setup_animation()
        
    def _setup_ui(self):
        """Setup skeleton UI that mimics the video event widget."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Create skeleton elements
        self.skeleton_label = QLabel()
        self.skeleton_label.setFixedSize(120, 20)
        
        self.skeleton_button1 = QLabel()
        self.skeleton_button1.setFixedSize(50, 25)
        
        self.skeleton_button2 = QLabel()
        self.skeleton_button2.setFixedSize(25, 25)
        
        layout.addWidget(self.skeleton_label)
        layout.addWidget(self.skeleton_button1)
        layout.addWidget(self.skeleton_button2)
        layout.addStretch()
        
        # Apply skeleton styling
        skeleton_style = """
            QLabel {
                background-color: #e0e0e0;
                border-radius: 3px;
            }
        """
        self.setStyleSheet(skeleton_style)
        
    def _setup_animation(self):
        """Setup shimmer animation for skeleton."""
        self.shimmer_timer = QTimer()
        self.shimmer_timer.timeout.connect(self._animate_shimmer)
        self.shimmer_timer.start(1000)  # Animate every second
        self._shimmer_state = False
        
    def _animate_shimmer(self):
        """Animate the shimmer effect."""
        if self._shimmer_state:
            color = "#e0e0e0"
        else:
            color = "#f0f0f0"
        
        skeleton_style = f"""
            QLabel {{
                background-color: {color};
                border-radius: 3px;
            }}
        """
        self.setStyleSheet(skeleton_style)
        self._shimmer_state = not self._shimmer_state