"""A widget to hold the four video playback widgets."""
from PySide6.QtWidgets import (QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
                               QFrame, QSizePolicy)

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
        self.setLayout(self.video_frame_layout)

    def addWidget(self, *args):
        """Add a QVideoWidget to the QGridLayout."""
        #print(args)
        if len(args) == 3:
            self.video_frame_layout.addWidget(args[0], args[1], args[2])
        elif len(args) == 5:
            self.video_frame_layout.addWidget(args[0], args[1], args[2], args[3], args[4])
        else:
            print(f'Siganture {args} not matched.')

    def columnCount(self):
        return self.video_frame_layout.columnCount()



