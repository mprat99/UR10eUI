"""Main window implementation for the UR10e UI."""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QStackedLayout, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication

from config.settings import WINDOW_TITLE, WINDOW_ASPECT_RATIO
from .ring_widget import RingWidget
from .screen0 import Screen0
from .screen1 import Screen1
from .screen2 import Screen2

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        
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
        self.ring_widget = RingWidget()
        
        # Create a widget for the vertical content
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background: transparent;
            padding: 0px;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(3, 3, 3, 3)  # Thin margin around all screens
        content_layout.setSpacing(3)  # Small gap between screens to create visual separation
        
        # Create the three screen widgets
        self.screen0 = Screen0()
        self.screen1 = Screen1()
        self.screen2 = Screen2()
        
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
    
    def center_on_screen(self):
        """Position the window on the right side of the screen."""
        screen = QGuiApplication.primaryScreen().availableGeometry()
        
        # Calculate position that puts the window on the right with margin
        right_margin = 250  # pixels from right edge
        x = screen.width() - self.width() - right_margin
        y = (screen.height() - self.height()) // 2  # Still center vertically
        
        self.move(x, y)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            self.close() 