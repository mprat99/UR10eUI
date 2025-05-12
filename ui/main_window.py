# ui/main_window.py
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSizePolicy, QLabel
from ui.screens.screen0 import Screen0
from ui.screens.screen1 import Screen1
from ui.screens.screen2 import Screen2

class MainWindow(QMainWindow):
    key_pressed = pyqtSignal()
    
    def __init__(self, target_screen, screen_index, num_screens): # target_screen is a QScreen object
        super().__init__()
        self.setWindowTitle(f"UI for Screen {screen_index} ({target_screen.name()})")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;") # Make main window background transparent
        self.screen_index = screen_index
        self.target_screen = target_screen # Store for reference if needed
        self.num_screens = num_screens
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        # Central widget itself can be transparent or have its own background
        central_widget.setStyleSheet("background: transparent;") 
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)

        # Load correct screen content
        content_widget = None
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

        content_widget = content_class({"state": "normal"})

        if content_widget:
            content_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            layout.addWidget(content_widget)
        else:
            fallback_label = QLabel(f"No content for screen index {self.screen_index}")
            fallback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback_label.setStyleSheet("color: red; font-size: 20px;")
            layout.addWidget(fallback_label)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.key_pressed.emit()
        super().keyPressEvent(event)