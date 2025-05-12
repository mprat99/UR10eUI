import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QRect, QPointF
from PyQt6.QtGui import QGuiApplication
from ui.main_window import MainWindow
from ui.widgets.ring_widget import RingWidget

def get_display_config():
    """Get combined geometry and center point based on display count"""
    screens = sorted(QGuiApplication.screens(), key=lambda s: (s.geometry().top(), s.geometry().left()))
    
    # Calculate combined geometry of all screens
    combined_rect = QRect()
    for screen in screens:
        combined_rect = combined_rect.united(screen.geometry())
    
    # Determine target screen for ring center
    if len(screens) == 1:
        target_screen = screens[0]
    elif len(screens) == 2:
        target_screen = screens[0]  # Top display
    else:  # 3+ displays
        target_screen = screens[1]  # Middle display
    
    # Calculate absolute center of target screen
    target_geo = target_screen.geometry()
    absolute_center = QPointF(
        target_geo.left() + target_geo.width()/2,
        target_geo.top() + target_geo.height()/2
    )
    
    # Convert to coordinates relative to combined rect
    relative_center = absolute_center - QPointF(combined_rect.topLeft())
    
    return combined_rect, relative_center, screens

def main():
    app = QApplication(sys.argv)
    combined_rect, ring_center, screens = get_display_config()

    # 1. BACKGROUND WINDOW (SPANS ALL DISPLAYS)
    bg_window = QMainWindow()
    bg_window.setWindowFlags(
        Qt.WindowType.FramelessWindowHint |
        Qt.WindowType.WindowStaysOnTopHint |
        Qt.WindowType.Tool |
        Qt.WindowType.WindowTransparentForInput  # Allow clicks to pass through
    )
    
    # CRITICAL: Set the window to span all displays
    bg_window.setGeometry(combined_rect)
    bg_window.setStyleSheet("background-color: black;")
    
    # Add ring widget at calculated center
    ring_widget = RingWidget({"state": "normal"}, ring_center)
    bg_window.setCentralWidget(ring_widget)
    
    # CRITICAL: Show normal (not fullscreen) and move to correct position
    bg_window.show()
    bg_window.move(combined_rect.topLeft())
    bg_window.resize(combined_rect.size())  # Explicitly set size

    # 2. UI WINDOWS (ONE PER PHYSICAL DISPLAY)
    ui_windows = []
    num_screens = len(screens)
    for i, screen in enumerate(screens):
        window = MainWindow(screen, i, num_screens)
        window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        # CRITICAL: Use setGeometry instead of showFullScreen
        window.setGeometry(screen.geometry())
        window.show()
        ui_windows.append(window)

    # ESC to quit
    def handle_escape():
        app.quit()
    
    for window in ui_windows:
        window.key_pressed.connect(handle_escape)

    app.exec()

if __name__ == "__main__":
    main()