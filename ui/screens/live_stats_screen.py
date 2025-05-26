from PyQt6.QtWidgets import QWidget, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtProperty
from utils.enums import State
from ..widgets.live_stats_widget import LiveStatsWidget

class LiveStatsScreen(QWidget):
    """Screen 0 with a 2x2 grid of widgets, centered properly with fixed spacing."""
    def __init__(self, state):
        super().__init__()

        self.setStyleSheet("background-color: transparent; border: 0px solid red;")

        outer_layout = QHBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setVerticalSpacing(10)
        grid_layout.setHorizontalSpacing(20)

        grid_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.widget1 = LiveStatsWidget("assets/live_speed_fast.svg", "20", "pick/min")
        self.widget2 = LiveStatsWidget("assets/box.svg", "4220", "/ 5000")
        self.widget3 = LiveStatsWidget("assets/time_change_pallet.svg", "220", "min")
        self.widget4 = LiveStatsWidget("assets/pallet.svg", "0", "/ 200")

        grid_layout.addWidget(self.widget1, 0, 0)
        grid_layout.addWidget(self.widget2, 0, 1)
        grid_layout.addWidget(self.widget3, 1, 0)
        grid_layout.addWidget(self.widget4, 1, 1)
        self.widget1.setMaximumWidth(200)
        self.widget2.setMaximumWidth(200)
        self.widget3.setMaximumWidth(200)
        self.widget4.setMaximumWidth(200)

        outer_layout.addLayout(grid_layout)

        self.setLayout(outer_layout)
        self.update_state(state)

    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value
        self.update()

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
        max_widget_width = int(window_height * 0.7)
        for widget in [self.widget1, self.widget2, self.widget3, self.widget4]:
            widget.setMaximumWidth(max_widget_width)

        super().resizeEvent(event)

    def rotate(self, angle):
        """Rotate the widgets by 1 degree every frame."""
        for widget in [self.widget1, self.widget2, self.widget3, self.widget4]:
            widget.rotate(angle)

        self.update()

