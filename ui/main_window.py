"""Main window implementation for the UR10e UI."""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QStackedLayout, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication

from config.settings import WINDOW_TITLE, WINDOW_ASPECT_RATIO
from .widgets.ring_widget import RingWidget
from .screens.screen0 import Screen0
from .screens.screen1 import Screen1
from .screens.screen2 import Screen2
from network.tcp_client import TCPClient
from utils.enums import MessageType, State

class MainWindow(QMainWindow):
    def __init__(self, client: TCPClient):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        
        self.current_rotation = 0  # Current rotation of the UI

        self.state = State.TASK_FINISHED
        init_config = {"state" : self.state}

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a container widget that will hold both the ring and the content
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        main_layout.addWidget(container)
        
        # Create the ring widget
        self.ring_widget = RingWidget(init_config)
        
        # Create a widget for the vertical content
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background: transparent;
            padding: 0px;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)  # Thin margin around all screens
        content_layout.setSpacing(0)  # Small gap between screens to create visual separation
        
        # Create the three screen widgets
        self.screen0 = Screen0(init_config)
        self.screen1 = Screen1(init_config)
        self.screen2 = Screen2(init_config)
        
        # Set size policies to force equal heights regardless of content
        for screen in [self.screen0, self.screen1, self.screen2]:
            # Ignored in vertical direction means the widget's size hint and size policy are ignored
            # The layout will force its size regardless of what the widget wants
            screen.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
            screen.setMinimumHeight(0)  # Allow shrinking to any size
            content_layout.addWidget(screen, 1)  # Equal stretch factor of 1
        
        # Stack the ring widget and content widget in the container
        stack_layout = QStackedLayout(container)
        stack_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)  # Show all widgets
        stack_layout.addWidget(content_widget)        # Add content widget second (front)
        stack_layout.addWidget(self.ring_widget)      # Add ring widget first (back)

        # Set a reasonable default size (90% of the available height)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        default_height = int(screen.height() * 0.9)
        default_width = int(default_height / WINDOW_ASPECT_RATIO)
        self.resize(default_width, default_height)
        
        # Position the window
        self.center_on_screen()

        # Connect to client message signal
        client.message_received.connect(self.check_message_type)

        # Create rotation timer
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.rotate_ui)
        
        # Store rotation state
        self.current_rotation = 0
        self.target_rotation = 180
        # self.rotation_timer.start(16)

        test_timer = QTimer(self)
        test_timer.singleShot(2000, lambda: self.update_state({"type": "state", "state": "reduced_speed"}))
        test_timer.singleShot(5000, lambda: self.update_state({"type": "state", "state": "normal"}))
        test_timer.singleShot(15000, lambda: self.update_state({"type": "state", "state": "reduced_speed"}))
        test_timer.singleShot(20000, lambda: self.update_state({"type": "state", "state": "stopped"}))
        test_timer.singleShot(23000, lambda: self.update_state({"type": "state", "state": "task_finished"}))


    def center_on_screen(self):
        """Position the window on the right side of the screen."""
        screen = QGuiApplication.primaryScreen().availableGeometry()
        
        # Calculate position that puts the window on the right with margin
        right_margin = 250  # pixels from right edge
        x = screen.width() - self.width() - right_margin
        y = (screen.height() - self.height()) // 2  # Still center vertically
        
        self.move(x, y)

    def check_message_type(self, message):
        """Check the message type and update the UI accordingly."""
        message_type = message.get("type")

        match MessageType(message_type):
            case MessageType.STATE:
                self.update_state(message)
            case MessageType.ROTATION:
                self.rotation_timer.start(16)  # Rotate every 16ms (60 FPS)
            case MessageType.LIVE_STATS:
                self.update_live_stats(message)
            case MessageType.GLOBAL_STATS:
                self.update_global_stats(message)
            case _:
                print(f"Unknown message type: {message_type}")
    
    def update_state(self, message):
        """Change the state of the UI according to the current state of the robot."""
        self.ring_widget.update_state(message)
        QTimer.singleShot(1000, lambda: {self.screen0.update_state(message), 
                                         self.screen1.update_state(message),
                                         self.screen2.update_state(message)})

    def rotate_ui(self):
        """Smoothly rotate UI towards target rotation."""
        if self.current_rotation == self.target_rotation:
            self.rotation_timer.stop()
            return

        # Calculate increment direction
        increment = 1 if (self.target_rotation - self.current_rotation) % 360 < 180 else -1

        # Update rotation
        self.current_rotation = (self.current_rotation + increment) % 360
        self.screen0.rotate(self.current_rotation)
        self.screen1.rotate(self.current_rotation)
        self.screen2.rotate(self.current_rotation)
    
    def update_live_stats(self, message):
        """Update the live stats widget."""
        self.screen0.update_live_stats(message)

    def update_global_stats(self, message):
        """Update the global stats widget."""
        self.screen2.update_global_stats(message)

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.close() 
