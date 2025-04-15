from PyQt6.QtWidgets import QWidget, QSpacerItem, QSizePolicy, QFrame, QStackedLayout, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtSvg import QSvgRenderer 
from PyQt6.QtGui import QPainter, QPixmap, QFont
from PyQt6.QtCore import QRectF, QPointF, QTimer,QPropertyAnimation, pyqtProperty, QEasingCurve
from utils.enums import State

class Screen0(QWidget):
    """Screen 0 with a 2x2 grid of widgets, centered properly with fixed spacing."""
    def __init__(self, state):
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

        # Wrap the grid inside the outer layout
        outer_layout.addLayout(grid_layout)

        # Apply the main layout
        self.setLayout(outer_layout)
        self.update_state(state)

    # Property for scale
    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value
        self.update()  # Repaint with new scale

    scale = pyqtProperty(float, get_scale, set_scale)

    def update_state(self, message):
        """Update speed SVG."""
        state = message.get("state")

        match State(state):
            case State.NORMAL:
                self.widget1.svg_renderer.load("assets/live_speed_fast.svg")
            case State.REDUCED_SPEED | State.WARNING:
                self.widget1.svg_renderer.load("assets/live_speed_slow.svg")
            case State.STOPPED | State.ERROR | State.IDLE | State.TASK_FINISHED:
                self.widget1.svg_renderer.load("assets/live_speed_stopped.svg")
                self.widget1.set_value(0)
            case _:
                self.widget1.svg_renderer.load("assets/live_speed_fast.svg")

    def update_live_stats(self, message):
        stats = {
        "currentSpeed": self.widget1,
        "currentBox": self.widget2,
        "remainingTime": self.widget3,
        "currentPallet": self.widget4,
        }

        total = {
            "totalBoxes": self.widget2,
            "totalPallets": self.widget4,
        }

        for key, widget in stats.items():
            if (value := message.get(key)) is not None and isinstance(value, int):
                widget.set_value(str(value))

        for key, widget in total.items():
            if (value := message.get(key)) is not None and isinstance(value, int):
                widget.set_label("/ " + str(value))


    def resizeEvent(self, event):
        """Update max width of widgets dynamically based on window size."""
        window_height = self.height()
        max_widget_width = int(window_height * 0.7)  # Each widget can take up to 20% of the window width

        for widget in [self.widget1, self.widget2, self.widget3, self.widget4]:
            widget.setMaximumWidth(max_widget_width)

        super().resizeEvent(event)  # Call parent resizeEvent

    def rotate(self, angle):
        """Rotate the widgets by 1 degree every frame."""
        for widget in [self.widget1, self.widget2, self.widget3, self.widget4]:
            widget.rotate(angle)

        self.update()


class LiveStatsWidget(QWidget):

    def __init__(self, svg_path, value_text, label_text, parent=None):
        super().__init__(parent)
        self.svg_renderer = QSvgRenderer(svg_path)
        self._value_text = value_text  # Use private attributes
        self._label_text = label_text
        self._rotation = 0  
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update()

    # Initialize the rotation animation
        self.rotate_anim = QPropertyAnimation(self, b"rotation")
        self._init_rotation_animation(self.rotate_anim)

        self.update()
    # Register the custom rotation property with pyqtProperty
    def get_rotation(self):
        return self._rotation

    def set_rotation(self, angle):
        """Set the rotation angle and trigger a repaint."""
        self._rotation = angle
        self.update()  # Repaint the widget with the new rotation angle

    rotation = pyqtProperty(float, get_rotation, set_rotation)  # Register the property

    def _init_rotation_animation(self, animation):
        """Initialize the rotation animation for this widget."""
        # animation.setDuration(500)  # Half second duration for smooth transition
        # animation.setEasingCurve(QEasingCurve.Type.Linear)

    # def rotate(self, target_angle):
    #     """Rotate the widget by a smooth transition with threshold handling."""
    #     # Get the current rotation angle
    #     current_angle = self._rotation  

    #     # Calculate the delta for rotation
    #     delta_angle = target_angle - current_angle

    #     # Threshold logic for rotation (only animate if difference is significant)
    #     threshold = 5  # For example, 5 degrees threshold
    #     if abs(delta_angle) > threshold:
    #         self.rotate_anim.setDuration(16 * int(abs(delta_angle)/5))
    #         self._animate_rotation(current_angle, target_angle)
    #     else:
    #         self.set_rotation(target_angle)

    def rotate(self, target_rotation):

        difference = int(abs(self._rotation - target_rotation))
        if self.rotate_anim.state() == QPropertyAnimation.State.Running:
            self._rotation = self.rotate_anim.currentValue()
            self.rotate_anim.stop()

        if difference > 10:
            self.rotate_anim.setStartValue(self._rotation)
            self.rotate_anim.setEndValue(target_rotation)
            self.rotate_anim.setDuration(min(300, 10 * difference))
            self.rotate_anim.finished.connect(self._on_rotation_animation_finished)
            self.rotate_anim.start()
        else:
            self.set_rotation(target_rotation)


    def _on_rotation_animation_finished(self):
        self._rotation = self.rotate_anim.currentValue()

    def _animate_rotation(self, start_angle, end_angle):
        """Helper function to animate the rotation of this widget."""
        self.rotate_anim.setStartValue(start_angle)
        self.rotate_anim.setEndValue(end_angle)
        self.rotate_anim.start()

    # def set_rotation(self, angle):
    #     """Directly set the rotation of this widget."""
    #     self._rotation = angle
    #     self.update()

    def set_value(self, value):
        """Update the numeric value and repaint."""
        self._value_text = str(value)  # Ensure it's a string
        self.update()

    def set_label(self, label):
        """Update the label text and repaint."""
        self._label_text = label
        self.update()

    # def set_rotation(self, angle):
    #     """Set rotation and repaint."""
    #     self._rotation = angle
    #     self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

         # Apply rotation
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._rotation)
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
        painter.drawText(value_bounds, Qt.AlignmentFlag.AlignCenter, self._value_text)

        # Draw label text **inside the widget boundaries**
        label_font_size = svg_height * 0.1
        label_font = QFont()
        label_font.setFamily("DM Sans")
        label_font.setPointSizeF(label_font_size)
        painter.setFont(label_font)

        # Place label text within the widget, just below the SVG
        label_bounds = QRectF(svg_rect)
        label_bounds = label_bounds.adjusted(0, svg_height * 0.23, 0, svg_height * 0.58)  # Shift within bounds
        painter.drawText(label_bounds, Qt.AlignmentFlag.AlignCenter, self._label_text)
