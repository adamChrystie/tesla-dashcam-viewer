"""A window which can be displayed and closes automatically after X number of seconds"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, Qt

class InfoPopup(QWidget):
    def __init__(self, message="This popup will close after 10 seconds.", timeout_seconds=None, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle("Info Popup")
        self.setFixedSize(300, 150)
        # Create and set a layout with a label
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

        # If timeout_seconds is provided, Set a QTimer to close the popup after the specified timeout.
        # Otherwise, user will have to close the pop up.
        if timeout_seconds:
            timeout = timeout_seconds * 1000
            QTimer.singleShot(timeout, self.close)
