from PyQt6.QtWidgets import QWidget, QSpacerItem, QSizePolicy, QFrame, QStackedLayout, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtSvgWidgets import QSvgWidget

class Screen0(QWidget):
    """Screen 0 with a 2x2 grid of widgets, centered properly with fixed spacing."""
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 1px solid red;")

        # Outer Layout: Centers the grid itself
        outer_layout = QHBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Ensure full layout is centered

        # Grid Layout (Holds widgets in a 2x2 structure)
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        grid_layout.setVerticalSpacing(20)  # Fixed spacing between widgets
        grid_layout.setHorizontalSpacing(40)  # Fixed spacing between widgets

        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center everything

        # Add widgets to the grid
        grid_layout.addWidget(LiveStat(), 0, 0)
        grid_layout.addWidget(LiveStat(), 0, 1)
        grid_layout.addWidget(LiveStat(), 1, 0)
        grid_layout.addWidget(LiveStat(), 1, 1)

        # Wrap the grid inside the outer layout
        outer_layout.addLayout(grid_layout)

        # Apply the main layout
        self.setLayout(outer_layout)

class LiveStat(QWidget):
    def __init__(self, label_offset_ratio=0.3):
        """
        :param label_offset_ratio: Adjusts vertical position relative to SVG center (0 = center, 0.2 = slightly lower)
        """
        super().__init__()

        self.label_offset_ratio = label_offset_ratio  # Store desired offset ratio
         # Stacked layout to overlay elements
        self.stacked_layout = QStackedLayout(self)
        self.stacked_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        # **Container for the SVG** to keep it centered
        svg_container = QWidget()
        svg_layout = QVBoxLayout(svg_container)
        svg_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # **Base layer: SVG widget**
        self.svg_widget = QSvgWidget("assets/live_speed_fast.svg")
        self.svg_widget.setStyleSheet("background: transparent;")
        svg_layout.addWidget(self.svg_widget)

        self.stacked_layout.addWidget(svg_container)

        # **Container for the label** to center it properly inside the SVG
        label_container = QWidget()
        label_layout = QVBoxLayout(label_container)
        label_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # **Spacer to adjust vertical position dynamically**
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        label_layout.addItem(self.spacer)

        self.label = QLabel("40")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: white; background: transparent;")

        label_layout.addWidget(self.label)
        self.stacked_layout.addWidget(label_container)

    def resizeEvent(self, event):
        """Override resizeEvent to handle scaling aspect ratio."""
        super().resizeEvent(event)

        width = self.width()
        height = self.height()

        # Maintain SVG aspect ratio
        svg_size = self.svg_widget.renderer().defaultSize()
        aspect_ratio = svg_size.width() / svg_size.height()

        if width / height > aspect_ratio:
            new_height = height
            new_width = int(new_height * aspect_ratio)
        else:
            new_width = width
            new_height = int(new_width / aspect_ratio)

        self.svg_widget.setFixedSize(QSize(new_width, new_height))

        # Scale font size dynamically
        font_size = max(10, new_height // 4)
        self.label.setStyleSheet(f"color: white; font-size: {font_size}px; background: transparent;")

        # Adjust label position based on offset ratio
        label_offset = int(new_height * self.label_offset_ratio)
        self.spacer.changeSize(20, label_offset, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout().invalidate()  # Force layout update

