from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QStackedWidget, QSizePolicy
)

from PyQt6.QtCore import (
    Qt, QTimer
)

from ..widgets.bar_chart_widget import (BarChartView, RotatableContainer)
from ..widgets.info_widget import InfoWidget

from utils.enums import State


# ----------------- Screen -----------------
class Screen2(QWidget):
    def __init__(self, init_config):
        super().__init__()
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")
        self.layout: QVBoxLayout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.increment = 1

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setStyleSheet("background: transparent; border: 0px;")
        self.stacked_widget.setFixedSize(300, 300)
        # Create the bar chart view.
        self.chart_view = BarChartView()
        self.chart_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.chart_view.show()
        self.info_widget = InfoWidget()
        self.info_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Add them to the stacked widget
        self.stacked_widget.addWidget(self.chart_view)  # index 0
        self.stacked_widget.addWidget(self.info_widget)   # index 1

        # Wrap the circle container in a rotatable container.
        # self.rot_container = RotatableContainer(self.chart_view)
         # Wrap the stacked widget in a single RotatableContainer
        self.rot_container = RotatableContainer(self.stacked_widget)

        self.layout.addWidget(self.rot_container)
        

        # Use a QTimer to rotate the container continuously.
        self.rotation_angle = 0
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_rotation)
        # self.timer.start(16)  # Adjust the speed (ms).
        self.update_state(init_config)

    def update_rotation(self):
        if self.rotation_angle > abs(37):
            self.increment *= -1
        self.rotation_angle = (self.rotation_angle + self.increment) % 360
        self.rot_container.rotate(self.rotation_angle)

    def rotate(self, angle):
        """Rotate the whole screen"""
        self.rot_container.rotate(angle)

    def update_state(self, message):
        """Update the state of the screen based on the received message."""
        state = message.get("state")

        match State(state):
            case State.NORMAL | State.IDLE:
                # self.layout.removeWidget(self.rot_container)
                # # self.rot_container.deleteLater()
                # self.chart_view = BarChartView()
                # self.rot_container = RotatableContainer(self.chart_view)
                # self.layout.addWidget(self.rot_container)
                self.stacked_widget.setCurrentWidget(self.chart_view)
                data = {"chart": {"units": "min", "bars": [{"label": "Max. Speed", "value": 99}, {"label": "Reduced Speed", "value": 50}, {"label": "Stopped", "value": 2}]}, "statMetric": "Avg. Speed", "statValue": "45", "statUnits": "pick/min"}
                QTimer.singleShot(15000, lambda: self.chart_view.receive_data(data))
            case State.REDUCED_SPEED | State.WARNING:
                # self.rot_container = RotatableContainer(self.info_widget)
                self.info_widget.update_state(message)
                self.stacked_widget.setCurrentWidget(self.info_widget)
                
            case State.STOPPED | State.ERROR:
                # self.layout.removeWidget(self.rot_container)
                # self.rot_container = RotatableContainer(self.info_widget)
                # self.layout.addWidget(self.rot_container)
                # self.rot_container = RotatableContainer(self.info_widget)
                self.info_widget.update_state(message)
                self.stacked_widget.setCurrentWidget(self.info_widget)
            case State.IDLE | _:
                # self.rot_container = RotatableContainer(self.chart_view)
                self.info_widget.update_state(message)
                self.stacked_widget.setCurrentWidget(self.info_widget)
