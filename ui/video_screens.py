"""A widget to hold the four video playback widgets."""
from PySide6.QtWidgets import QGridLayout, QFrame, QWidget

class QVideoScreenGrid(QFrame):
    def __init__(self, parent: QWidget=None):
        """ Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """""
        super().__init__(parent=parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the widget's UI."""
        # Video display area
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(2)
        self.video_frame_layout = QGridLayout(self)
        self.video_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.video_frame_layout.setSpacing(2)
        self.setLayout(self.video_frame_layout)

    def addWidget(self, *args: list) -> None:
        """Add a QVideoWidget to the QGridLayout.
        Args:
            *args (list): The arguments to pass to the QGridLayout.addWidget method.
        """
        self.video_frame_layout.addWidget(*args)

    def columnCount(self) -> None:
        """Return the number of columns in the grid layout.
        Returns:
            int: The number of columns in the grid layout.
        """
        return self.video_frame_layout.columnCount()
