# ui/screen_window.py

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QSizePolicy, QStackedLayout
)

from config.settings import SCREEN_CLASSES_BY_INDEX
from ui.screens.ring_screen import RingScreen
from ui.screens.live_stats_screen import LiveStatsScreen
from ui.screens.bar_chart_info_screen import BarChartInfoScreen

# Maps string names from settings to actual widget classes
CLASS_MAP = {
    "RingScreen": RingScreen,
    "LiveStatsScreen": LiveStatsScreen,
    "BarChartInfoScreen": BarChartInfoScreen,
}


class ScreenWindow(QMainWindow):
    key_pressed = pyqtSignal()

    def __init__(self, target_screen, screen_index, num_screens, client):
        super().__init__()
        self.setWindowTitle(f"UI for Screen {screen_index} ({target_screen.name()})")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self.screen_index = screen_index
        self.num_screens = num_screens
        self.robot_state = "normal"
        self.current_screen_state = 0
        self.client = client

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)

        self.stack = QStackedLayout()
        central_widget.setLayout(self.stack)

        # Load screen configuration from settings
        layout_config = SCREEN_CLASSES_BY_INDEX.get(self.num_screens, [])
        screen_config = layout_config[self.screen_index] if self.screen_index < len(layout_config) else "RingScreen"

        # If screen_config is a list, assume alternating widgets
        if isinstance(screen_config, list) and len(screen_config) == 2:
            class1 = CLASS_MAP.get(screen_config[0], RingScreen)
            class2 = CLASS_MAP.get(screen_config[1], RingScreen)

            self.alt_widget_0 = class1({"state": "normal"})
            self.alt_widget_1 = class2({"state": "normal"})

            self.stack.addWidget(self.alt_widget_0)  # index 0
            self.stack.addWidget(self.alt_widget_1)  # index 1
            self.stack.setCurrentIndex(0)

            self.start_alternating_timer()
        else:
            # Show a single widget
            class_name = screen_config if isinstance(screen_config, str) else "RingScreen"
            content_class = CLASS_MAP.get(class_name, RingScreen)

            self.content_widget = content_class({"state": "normal"})
            self.content_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            self.stack.addWidget(self.content_widget)

    def start_alternating_timer(self):
        self.alternating_timer = QTimer(self)
        self.alternating_timer.timeout.connect(self.toggle_screen_content)
        self.alternating_timer.start(10000)

    def stop_alternating_timer(self):
        if hasattr(self, 'alternating_timer') and self.alternating_timer.isActive():
            self.alternating_timer.stop()

    def restart_alternating_timer(self):
        self.stop_alternating_timer()
        self.current_screen_state = 0
        self.stack.setCurrentIndex(self.current_screen_state)
        self.start_alternating_timer()

    def toggle_screen_content(self):
        if self.robot_state in {"normal", "task_finished"}:
            self.current_screen_state = 1 - self.current_screen_state
            self.stack.setCurrentIndex(self.current_screen_state)
        else:
            self.stack.setCurrentIndex(0)
        if hasattr(self.alt_widget_0, "update_state"):
            self.alt_widget_0.update_state({"state": self.robot_state})

    def update_robot_state(self, new_state):
        self.robot_state = new_state

        if hasattr(self, 'alt_widget_0'):
            if new_state in {"normal", "task_finished"}:
                self.restart_alternating_timer()
            else:
                self.stop_alternating_timer()
                self.stack.setCurrentIndex(0)
                if hasattr(self.alt_widget_0, "update_state"):
                    self.alt_widget_0.update_state({"state": new_state})

    def get_active_content_widget(self):
        if hasattr(self, 'alt_widget_0'):
            return self.alt_widget_1 if self.current_screen_state == 1 else self.alt_widget_0
        return getattr(self, "content_widget", None)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.key_pressed.emit()
        super().keyPressEvent(event)
