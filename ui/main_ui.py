
from PyQt6.QtCore import Qt, QRect, QPointF
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QMainWindow
from ui.screen_window import ScreenWindow
from ui.widgets.ring_widget import RingWidget
from config.settings import CLIENT_TYPE
from network.tcp_client import TCPClient
from network.uart_client import UARTClient


def launch_ui(app, client, on_escape_callback):
    """Launch the UI with black background, ring effect, and per-screen windows."""

    combined_rect, ring_center, screens = get_display_config()

    # Background with ring effect
    bg_window = QMainWindow()
    bg_window.setWindowFlags(
        Qt.WindowType.FramelessWindowHint |
        Qt.WindowType.WindowStaysOnTopHint |
        Qt.WindowType.Tool |
        Qt.WindowType.WindowTransparentForInput
    )
    bg_window.setGeometry(combined_rect)
    bg_window.setStyleSheet("background-color: black;")
    ring_widget = RingWidget({"state": "normal"}, ring_center)
    bg_window.setCentralWidget(ring_widget)
    bg_window.show()
    bg_window.move(combined_rect.topLeft())
    bg_window.resize(combined_rect.size())
    ui_windows = []
    # UI windows
    for i, screen in enumerate(screens):
        window = ScreenWindow(screen, i, len(screens), client)
        window.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        window.setGeometry(screen.geometry())
        window.show()
        window.key_pressed.connect(on_escape_callback)
        ui_windows.append(window)

    return bg_window, ui_windows, ring_widget


def get_display_config():
    """Calculate combined screen geometry and ring center point."""
    screens = sorted(QGuiApplication.screens(), key=lambda s: (s.geometry().top(), s.geometry().left()))
    
    combined_rect = QRect()
    for screen in screens:
        combined_rect = combined_rect.united(screen.geometry())

    if len(screens) == 1:
        target_screen = screens[0]
    elif len(screens) == 2:
        target_screen = screens[0]
    else:
        target_screen = screens[1]

    target_geo = target_screen.geometry()
    absolute_center = QPointF(
        target_geo.left() + target_geo.width() / 2,
        target_geo.top() + target_geo.height() / 2
    )

    relative_center = absolute_center - QPointF(combined_rect.topLeft())
    return combined_rect, relative_center, screens