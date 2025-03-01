"""A window which can be displayed and closes automatically after X number of seconds"""
from typing import Union
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, Qt

class InfoPopup(QWidget):
    def __init__(self, title: str="Information", message: str="This popup will close after 10 seconds.",
                 timeout_seconds: Union[int, None]=None, parent: QWidget=None):
        """ A popup window displaying some information. The window can be set to close automatically ot require user
        to close window.
        Args:
            title (str, optional): The title of the popup window. Defaults to "Information".
            message (str, optional): The message to display in the popup. Defaults to "This popup will close after 10 seconds.".
            timeout_seconds (Union[int, None], optional): The number of seconds to wait before closing the popup. If None, the popup will not close automatically. Defaults to None.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent=parent)
        # Make the window modal
        self.setWindowModality(Qt.ApplicationModal)
        # Set the window flags for a floating, always-on-top window
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setWindowTitle(title)
        self.setFixedSize(400, 250)
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
            label.setText(f'{label.text()}\n\nThis window will close automatically in {timeout_seconds} seconds.')
            timeout = timeout_seconds * 1000
            QTimer.singleShot(timeout, self.close)