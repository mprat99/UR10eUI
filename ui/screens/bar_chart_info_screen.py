from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QSizePolicy
)


from PyQt6.QtCore import (
    Qt, QPropertyAnimation, pyqtProperty, QEasingCurve)

from ..widgets.bar_chart_widget import BarChartView
from ..widgets.rotatable_container import RotatableContainer
from ..widgets.info_widget import InfoWidget

from utils.enums import State


# ----------------- Screen -----------------
class BarChartInfoScreen(QWidget):
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
        self.stacked_widget.addWidget(self.chart_view)
        self.stacked_widget.addWidget(self.info_widget)

        # Wrap the stacked widget in a single RotatableContainer
        self.rot_container = RotatableContainer(self.stacked_widget)

        self.layout.addWidget(self.rot_container)
        

        # Animation properties
        self._opacity = 1.0
        self._scale = 1.05
        self._rotation = 0.0

        # # Animations setup
        # self.opacity_anim = QPropertyAnimation(self, b"opacity")
        # self.opacity_anim.setDuration(1500)
        # self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        # self.scale_anim = QPropertyAnimation(self, b"scale")
        # self.scale_anim.setDuration(1500)
        # self.scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.rotate_anim = QPropertyAnimation(self, b"rotation")
        self.rotate_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.update_state(init_config)

    def rotate(self, target_rotation):
        """Rotate the screen with smooth animation."""
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
        """Update the rotation value after animation finishes."""
        self._rotation = self.rotate_anim.currentValue()

    def get_rotation(self):
        """Return the current rotation value."""
        return self._rotation

    def set_rotation(self, angle):
        """Set the rotation angle and trigger a repaint."""
        self._rotation = angle
        self.rot_container.rotate(self._rotation)

    rotation = pyqtProperty(float, get_rotation, set_rotation)

    def update_state(self, message):
        """Update the state of the screen based on the received message."""
        state = message.get("state")

        match State(state):
            case State.NORMAL | State.IDLE:
                self.stacked_widget.setCurrentWidget(self.chart_view)
                self.chart_view.receive_data(message)
            case (State.REDUCED_SPEED | State.WARNING | State.STOPPED 
                  | State.ERROR | State.IDLE | State.TASK_FINISHED):
                self.info_widget.update_state(message)
                self.stacked_widget.setCurrentWidget(self.info_widget)
            case _:
                pass
    
    def update_global_stats(self, message):
        self.chart_view.receive_data(message)