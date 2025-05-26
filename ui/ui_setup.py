from PyQt6.QtCore import Qt, QRect, QPointF
from PyQt6.QtGui import QGuiApplication
from ui.screen_window import ScreenWindow
from ui.ring_manager import RingManager
from config.settings import UI_SCREEN_INDICES, SCREEN_CLASSES_BY_INDEX, DEBUG_MODE, DEBUG_DISPLAY_INDEX, DEBUG_NUM_SCREENS, DEBUG_HEIGHT_RATIO, DEBUG_ASPECT_RATIO, DEBUG_FRAMELESS_WINDOW, HIDE_WINDOW_FROM_TASKBAR


def launch_ui(app, client, on_escape_callback):
    """Launch the UI with black background and per-screen windows using shared RingManager."""

    combined_rect, ring_center, screens = get_display_config()

    ring_manager = RingManager()
    ring_manager.set_center(ring_center)
    ring_manager.createNewRing()

    ui_windows = []

    ring_screen_index = get_ring_screen_index(len(screens))

    for i, screen in enumerate(screens):
        is_ring = (i == ring_screen_index)
        window = ScreenWindow(screen, i, len(screens), client, ring_manager, is_ring_screen=is_ring)

        if DEBUG_MODE:
            if DEBUG_FRAMELESS_WINDOW:
                window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        else:
            window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        if HIDE_WINDOW_FROM_TASKBAR:
            window.setWindowFlags(Qt.WindowType.Tool)

        window.setGeometry(screen.geometry())
        window.show()
        window.key_pressed.connect(on_escape_callback)
        ui_windows.append(window)

    return None, ui_windows, ring_manager


def get_ring_screen_index(num_screens):
    screen_list = SCREEN_CLASSES_BY_INDEX.get(num_screens, [])
    for i, entry in enumerate(screen_list):
        if isinstance(entry, str) and entry == "RingScreen":
            return i
    return 0


def get_display_config():
    """Calculate screen layout and ring center; supports debug mode."""
    if DEBUG_MODE:
        screens = QGuiApplication.screens()
        try:
            base_screen = screens[DEBUG_DISPLAY_INDEX]
        except IndexError:
            raise RuntimeError("Invalid DEBUG_DISPLAY_INDEX in settings.")

        available_geo = base_screen.availableGeometry()
        num = DEBUG_NUM_SCREENS

        total_height = int(available_geo.height() * DEBUG_HEIGHT_RATIO)
        height = total_height // num
        width = int(height * DEBUG_ASPECT_RATIO)

        fake_screens = []
        for i in range(num):
            offset_y = int(i * height + height * 0.2)
            offset_x = int(available_geo.width() * 0.2)
            rect = QRect(
                available_geo.left() + offset_x,
                available_geo.top() + offset_y,
                width,
                height
            )
            fake_screens.append(_FakeScreen(rect))


        combined_rect = QRect(fake_screens[0].geometry())
        for screen in fake_screens[1:]:
            combined_rect = combined_rect.united(screen.geometry())

        ring_index = get_ring_screen_index(len(fake_screens))
        ring_geo = fake_screens[ring_index].geometry()
        absolute_center = QPointF(
            ring_geo.left() + ring_geo.width() / 2,
            ring_geo.top() + ring_geo.height() / 2
        )

        return combined_rect, absolute_center, fake_screens


    else:
        screens = QGuiApplication.screens()
        print("\n[DEBUG] Detected screens and their geometries:")
        for i, s in enumerate(screens):
            print(f"  Screen {i}: {s.geometry()}")

        try:
            screens = [screens[i] for i in UI_SCREEN_INDICES] if UI_SCREEN_INDICES else screens
        except IndexError:
            raise RuntimeError("Invalid UI_SCREEN_INDICES in settings.")

        screens = sorted(screens, key=lambda s: (s.geometry().top(), s.geometry().left()))

        combined_rect = QRect()
        for screen in screens:
            combined_rect = combined_rect.united(screen.geometry())

        ring_index = get_ring_screen_index(len(screens))
        ring_geo = screens[ring_index].geometry()

        absolute_center = QPointF(
            ring_geo.left() + ring_geo.width() / 2,
            ring_geo.top() + ring_geo.height() / 2
        )

        return combined_rect, absolute_center, screens


class _FakeScreen:
    """Mimics QScreen for debug mode."""
    def __init__(self, geometry: QRect):
        self._geometry = geometry

    def geometry(self):
        return self._geometry
