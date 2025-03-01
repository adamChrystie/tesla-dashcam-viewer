"""A widget to hold all the video event widgets."""

from PySide6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QSizePolicy, QLayoutItem

class ScrollableWidget(QWidget):
    def __init__(self, parent: QWidget=None) -> None:
        super().__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a vertical layout for the custom widget
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create a container widget to hold all child widgets
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container.setLayout(self.container_layout)
        # Ensure the container expands horizontally
        self.container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Add the container to a scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.container)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scroll_area)

        # Ensure the scroll area expands in both directions
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def count(self) -> int:
        """Return the number of widgets in the container layout.
        Returns:
            int: The number of widgets in the container layout.
        """
        return self.container_layout.count()

    def itemAt(self, value: int) -> QLayoutItem:
        """Return the layout item at the given index.
        Args:
            value (int): The index of the layout item to return.
        Returns:
            QLayoutItem: The layout item at the given index.
        """
        return self.container_layout.itemAt(value)

    def add_widget(self, widget: QWidget) -> None:
        """ Add a widget to the container layout.
        Args:
            widget (QWidget): The widget to add.
        """
        self.container_layout.addWidget(widget)
        # Adjust the container's minimum width based on the added widget
        self._adjust_width(widget)

    def _adjust_width(self, widget: QWidget) -> None:
        """Adjust the container's width to fit the new widget.
        Args:
            widget (QWidget): The widget to add.
        """
        # Get the width of the widget
        widget_width = widget.sizeHint().width()
        current_width = self.container.minimumSizeHint().width()
        new_width = max(current_width, widget_width)
        # Update the container's minimum width
        self.setMinimumWidth(new_width)
