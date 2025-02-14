"""A widget to hold the four video playback widgets."""
from PySide6.QtWidgets import QGridLayout, QFrame

class QVideoScreenGrid(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setup_ui()

    def setup_ui(self):
        # Video display area
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(2)
        self.video_frame_layout = QGridLayout(self)
        self.video_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.video_frame_layout.setSpacing(2)
        self.setLayout(self.video_frame_layout)

    def addWidget(self, *args):
        """Add a QVideoWidget to the QGridLayout."""
        self.video_frame_layout.addWidget(*args)

    def columnCount(self):
        return self.video_frame_layout.columnCount()



