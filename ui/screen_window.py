# ui/screen_window.py

from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSizePolicy,
    QStackedLayout
)
from ui.screens.screen0 import Screen0
from ui.screens.screen1 import Screen1
from ui.screens.screen2 import Screen2

class ScreenWindow(QMainWindow):
    key_pressed = pyqtSignal()

    def __init__(self, target_screen, screen_index, num_screens, client):
        super().__init__()
        self.setWindowTitle(f"UI for Screen {screen_index} ({target_screen.name()})")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.screen_index = screen_index
        self.target_screen = target_screen
        self.num_screens = num_screens
        self.current_screen_state = 0  # For QStackedLayout index
        self.robot_state = "normal"


        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)

        self.stack = QStackedLayout()
        central_widget.setLayout(self.stack)

        if self.num_screens == 2 and self.screen_index == 1:
            self.screen2_widget = Screen2({"state": "normal"})
            self.screen0_widget = Screen0({"state": "normal"})

            self.stack.addWidget(self.screen2_widget)  # index 0
            self.stack.addWidget(self.screen0_widget)  # index 1
            self.stack.setCurrentIndex(0)

            self.start_alternating_timer()
        else:
            screen_classes_by_index = {
                1: [Screen1],
                2: [Screen1, Screen2],
                3: [Screen0, Screen1, Screen2]
            }
            default_class = Screen1
            try:
                screen_list = screen_classes_by_index.get(self.num_screens, [default_class])
                content_class = screen_list[self.screen_index]
            except IndexError:
                content_class = default_class

            self.content_widget = content_class({"state": "normal"})
            self.content_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            self.stack.addWidget(self.content_widget)


    def update_robot_state(self, new_state):
        self.robot_state = new_state

        if self.num_screens == 2 and self.screen_index == 1:
            if new_state in {"normal", "task_finished"}:
                self.restart_alternating_timer()
            else:
                self.stop_alternating_timer()
                self.stack.setCurrentWidget(self.screen2_widget)


    def restart_alternating_timer(self):
        self.stop_alternating_timer()
        self.current_screen_state = 0
        self.stack.setCurrentIndex(self.current_screen_state)
        self.start_alternating_timer()

    def start_alternating_timer(self):
        self.alternating_timer = QTimer(self)
        self.alternating_timer.timeout.connect(self.toggle_screen_content)
        self.alternating_timer.start(10000)

    def stop_alternating_timer(self):
        if hasattr(self, 'alternating_timer') and self.alternating_timer.isActive():
            self.alternating_timer.stop()


    def toggle_screen_content(self):
        if self.robot_state in {"normal", "task_finished"}:
            self.current_screen_state = 1 - self.current_screen_state
            self.stack.setCurrentIndex(self.current_screen_state)
        else:
            self.stack.setCurrentWidget(self.screen2_widget)
            self.screen2_widget.set_state({"state": self.robot_state})


    def get_active_content_widget(self):
        # Return whichever widget is currently visible
        if self.num_screens == 2 and self.screen_index == 1:
            return self.screen0_widget if self.current_screen_state == 1 else self.screen2_widget
        return getattr(self, "content_widget", None)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.key_pressed.emit()
        super().keyPressEvent(event)