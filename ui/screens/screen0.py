from PyQt6.QtWidgets import QWidget, QSpacerItem, QSizePolicy, QFrame, QStackedLayout, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtSvg import QSvgRenderer 
from PyQt6.QtGui import QPainter, QPixmap, QFont
from PyQt6.QtCore import QRectF, QPointF, QTimer

class Screen0(QWidget):
    """Screen 0 with a 2x2 grid of widgets, centered properly with fixed spacing."""
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: 0px solid red;")

        # Outer Layout: Centers the grid itself
        outer_layout = QHBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Ensure full layout is centered

        # Grid Layout (Holds widgets in a 2x2 structure)
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        grid_layout.setVerticalSpacing(10)  # Fixed spacing between widgets
        grid_layout.setHorizontalSpacing(20)  # Fixed spacing between widgets

        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center everything
        
        # Add widgets to the grid
        # grid_layout.addWidget(LiveStat(), 0, 0)
        # grid_layout.addWidget(LiveStat(), 0, 1)
        # grid_layout.addWidget(LiveStat(), 1, 0)
        # grid_layout.addWidget(LiveStat(), 1, 1)

        # Suppose you have 4 stats to display
        # Provide your actual SVG path, value text, and label text
        self.widget1 = LiveStatsWidget("assets/live_speed_fast.svg", "20", "pick/min")
        self.widget2 = LiveStatsWidget("assets/box.svg", "4220", "/ 5000")
        self.widget3 = LiveStatsWidget("assets/time_change_pallet.svg", "220", "min")
        self.widget4 = LiveStatsWidget("assets/pallet.svg", "0", "/ 200")

        grid_layout.addWidget(self.widget1, 0, 0)
        grid_layout.addWidget(self.widget2, 0, 1)
        grid_layout.addWidget(self.widget3, 1, 0)
        grid_layout.addWidget(self.widget4, 1, 1)
        self.widget1.setMaximumWidth(200)  # Adjust max width
        self.widget2.setMaximumWidth(200)
        self.widget3.setMaximumWidth(200)
        self.widget4.setMaximumWidth(200)
        # widget1.setMinimumWidth(50)  # Adjust max width
        # widget2.setMinimumWidth(50)
        # widget3.setMinimumWidth(50)
        # widget4.setMinimumWidth(50)

        self.widget1.update_content(value_text="200")

        # Wrap the grid inside the outer layout
        outer_layout.addLayout(grid_layout)

        # Apply the main layout
        self.setLayout(outer_layout)
        # --- Rotation timer ---
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.increment_rotation)
        self.rotation_timer.start(16)  # ~60 FPS
        self.increment_rotation()

    def resizeEvent(self, event):
        """Update max width of widgets dynamically based on window size."""
        window_height = self.height()
        max_widget_width = int(window_height * 0.7)  # Each widget can take up to 20% of the window width

        for widget in [self.widget1, self.widget2, self.widget3, self.widget4]:
            widget.setMaximumWidth(max_widget_width)

        super().resizeEvent(event)  # Call parent resizeEvent

    def increment_rotation(self):
        """Rotate the widgets by 1 degree every frame."""
        for widget in [self.widget1, self.widget2, self.widget3, self.widget4]:
            widget.set_rotation(widget.rotation_angle + 1)

        self.update()


class LiveStatsWidget(QWidget):
    def __init__(self, svg_path, value_text, label_text, parent=None):
        super().__init__(parent)
        self.svg_renderer = QSvgRenderer(svg_path)
        self.value_text = value_text
        self.label_text = label_text
        self.rotation_angle = 0  # Default rotation
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update()

    def update_content(self, svg_path=None, value_text=None, label_text=None):
        """Dynamically update SVG, value, and label."""
        if svg_path:
            self.svg_renderer = QSvgRenderer(svg_path)
        if value_text:
            self.value_text = value_text
        if label_text:
            self.label_text = label_text
        self.update()  # Trigger repaint

    def set_rotation(self, angle):
        """Set rotation and repaint."""
        self.rotation_angle = angle
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

         # Apply rotation
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.rotation_angle)
        painter.translate(-self.width() / 2, -self.height() / 2)

        widget_width = self.width()
        widget_height = self.height()

        # Get SVG size and aspect ratio
        svg_size = self.svg_renderer.defaultSize()
        svg_aspect_ratio = svg_size.width() / svg_size.height()

        # Fit SVG within widget bounds
        if widget_width / widget_height > svg_aspect_ratio:
            svg_height = widget_height * 0.9  # Reduce height to leave space for label
            svg_width = svg_height * svg_aspect_ratio
        else:
            svg_width = widget_width * 0.9
            svg_height = svg_width / svg_aspect_ratio

        # Center SVG
        svg_x = (widget_width - svg_width) / 2
        svg_y = (widget_height - svg_height) * 0.2  # Move up slightly
        svg_rect = QRectF(svg_x, svg_y, svg_width, svg_height)
        self.svg_renderer.render(painter, svg_rect)

        # Draw the numeric value
        value_font_size = svg_height * 0.15
        value_font = QFont()
        value_font.setFamily("DM Sans")
        value_font.setPointSizeF(value_font_size)
        painter.setFont(value_font)
        painter.setPen(Qt.GlobalColor.white)

        value_bounds = QRectF(svg_rect)
        value_bounds.moveCenter(QPointF(svg_rect.center().x(), svg_rect.center().y() + svg_height * 0.09))
        painter.drawText(value_bounds, Qt.AlignmentFlag.AlignCenter, self.value_text)

        # Draw label text **inside the widget boundaries**
        label_font_size = svg_height * 0.1
        label_font = QFont()
        label_font.setFamily("DM Sans")
        label_font.setPointSizeF(label_font_size)
        painter.setFont(label_font)

        # Place label text within the widget, just below the SVG
        label_bounds = QRectF(svg_rect)
        label_bounds = label_bounds.adjusted(0, svg_height * 0.23, 0, svg_height * 0.58)  # Shift within bounds
        painter.drawText(label_bounds, Qt.AlignmentFlag.AlignCenter, self.label_text)
