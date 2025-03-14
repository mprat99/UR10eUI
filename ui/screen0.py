"""Screen 0 widget - Top monitor of the UI."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

class Screen0(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 50);
        """)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) 