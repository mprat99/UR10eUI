
from PyQt6.QtCore import Qt, QRect, QPointF
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QMainWindow
from ui.screen_window import ScreenWindow
from ui.widgets.ring_widget import RingWidget
from config.settings import CLIENT_TYPE, UI_SCREEN_INDICES, SCREEN_CLASSES_BY_INDEX
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


# def get_display_config():
#     """Calculate combined screen geometry and ring center point."""
#     screens = sorted(QGuiApplication.screens(), key=lambda s: (s.geometry().top(), s.geometry().left()))
    
#     try:
#         screens = [screens[i] for i in UI_SCREEN_INDICES] if UI_SCREEN_INDICES else screens
#         screens = sorted(screens, key=lambda s: (s.geometry().top(), s.geometry().left()))
#     except IndexError:
#         raise RuntimeError("Invalid UI_SCREEN_INDICES in settings.")
    
#     combined_rect = QRect()
#     for screen in screens:
#         combined_rect = combined_rect.united(screen.geometry())

#     if len(screens) == 1 or len(screens) == 2:
#         target_screen = screens[0]
#     else:
#         target_screen = screens[1]

#     target_geo = target_screen.geometry()
#     absolute_center = QPointF(
#         target_geo.left() + target_geo.width() / 2,
#         target_geo.top() + target_geo.height() / 2
#     )

#     relative_center = absolute_center - QPointF(combined_rect.topLeft())
#     return combined_rect, relative_center, screens

def get_display_config():
    """Calculate combined screen geometry and ring center point, adjusted for screen layout."""
    screens = QGuiApplication.screens()

    print("\n[DEBUG] Detected screens and their geometries:")
    for i, s in enumerate(screens):
        print(f"  Screen {i}: {s.geometry()}")

    try:
        screens = [screens[i] for i in UI_SCREEN_INDICES] if UI_SCREEN_INDICES else screens
    except IndexError:
        raise RuntimeError("Invalid UI_SCREEN_INDICES in settings.")

    # Sort for deterministic layout (optional, depends on UI_SCREEN_INDICES use)
    screens = sorted(screens, key=lambda s: (s.geometry().top(), s.geometry().left()))

    combined_rect = QRect()
    for screen in screens:
        combined_rect = combined_rect.united(screen.geometry())

    ring_screen_index = get_ring_screen_index(len(screens))
    ring_screen = screens[ring_screen_index]
    ring_geo = ring_screen.geometry()

    absolute_center = QPointF(
        ring_geo.left() + ring_geo.width() / 2,
        ring_geo.top() + ring_geo.height() / 2
    )

    relative_center = absolute_center - QPointF(combined_rect.left(), combined_rect.top())

    print(f"\n[DEBUG] Combined screen rect: {combined_rect}")
    print(f"[DEBUG] Ring screen index: {ring_screen_index}, geometry: {ring_geo}")
    print(f"[DEBUG] Absolute ring center: {absolute_center}")
    print(f"[DEBUG] Relative ring center (for combined background): {relative_center}\n")

    return combined_rect, relative_center, screens

def get_ring_screen_index(num_screens):
    screen_list = SCREEN_CLASSES_BY_INDEX.get(num_screens, [])
    for i, class_name in enumerate(screen_list):
        if class_name == "RingScreen":
            return i
    return 0  # fallback if not found