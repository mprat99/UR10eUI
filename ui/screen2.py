"""Screen 2 widget - Bottom monitor of the UI."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class Screen2(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 50);
        """)
        
        # Create main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("Screen 2")
        label.setStyleSheet("""
            font-size: 24px;
            font: DM Sans;
            background: transparent;
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
