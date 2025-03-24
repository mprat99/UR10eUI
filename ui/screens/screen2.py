from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)

from PyQt6.QtCore import (
    Qt, QTimer
)

from ..widgets.bar_chart_widget import (BarChartView, RotatableContainer)


# ----------------- Screen -----------------
class Screen2(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.increment = 1
        # Create the bar chart view.
        self.chart_view = BarChartView()

        # Wrap the bar chart view in a circle container.
        # self.circle_container = CircleContainer(self.chart_view)
        # Wrap the circle container in a rotatable container.
        self.rot_container = RotatableContainer(self.chart_view)

        layout.addWidget(self.rot_container)

        # Use a QTimer to rotate the container continuously.
        self.rotation_angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rotation)
        self.timer.start(16)  # Adjust the speed (ms).

    def update_rotation(self):
        if self.rotation_angle > abs(37):
            self.increment *= -1
        self.rotation_angle = (self.rotation_angle + self.increment) % 360
        self.rot_container.rotate(self.rotation_angle)

