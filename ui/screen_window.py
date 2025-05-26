from PyQt6.QtWidgets import QMainWindow, QStackedLayout, QWidget
from PyQt6.QtCore import pyqtSignal, Qt
from config.settings import SCREEN_CLASSES_BY_INDEX
from ui.widgets.ring_view_widget import RingViewWidget
from ui.screens.ring_screen import RingScreen
from ui.screens.bar_chart_info_screen import BarChartInfoScreen
from ui.screens.live_stats_screen import LiveStatsScreen

SCREEN_CLASS_MAP = {
    "RingScreen": RingScreen,
    "BarChartInfoScreen": BarChartInfoScreen,
    "LiveStatsScreen": LiveStatsScreen,
}

class ScreenWindow(QMainWindow):
    key_pressed = pyqtSignal()

    def __init__(self, screen, screen_index, total_screens, client, ring_manager, is_ring_screen=False):
        super().__init__()
        self.screen = screen
        self.screen_index = screen_index
        self.total_screens = total_screens
        self.client = client

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QStackedLayout()
        self.central.setLayout(self.layout)
        self.central.setStyleSheet("background-color: black;")
        self.is_ring_screen = is_ring_screen

        self.ring_view = RingViewWidget(ring_manager, is_ring_screen=is_ring_screen)
        self.layout.addWidget(self.ring_view)

        screen_class = self.get_screen_class()
        self.content_widget = screen_class({"state": "normal"})
        self.layout.addWidget(self.content_widget)
        self.layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self.ring_view.lower()

    def get_screen_class(self):
        screen_list = SCREEN_CLASSES_BY_INDEX.get(self.total_screens, [])
        if self.screen_index < len(screen_list):
            entry = screen_list[self.screen_index]

            if isinstance(entry, str):
                return SCREEN_CLASS_MAP.get(entry, lambda config: QWidget())

            if isinstance(entry, list) and len(entry) == 2:
                cls_0 = SCREEN_CLASS_MAP.get(entry[0], lambda config: QWidget())
                cls_1 = SCREEN_CLASS_MAP.get(entry[1], lambda config: QWidget())

                def create_dual_widget(config):
                    from ui.widgets.dual_screen_widget import DualScreenWidget
                    return DualScreenWidget(cls_0(config), cls_1(config))

                return create_dual_widget


        return lambda config: QWidget()


    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.key_pressed.emit()
        super().keyPressEvent(event)

    def update_robot_state(self, state):
        if hasattr(self.content_widget, "update_robot_state"):
            self.content_widget.update_robot_state(state)

    def rotate(self, angle):
        if hasattr(self.content_widget, "rotate"):
            self.content_widget.rotate(angle)

    def moveEvent(self, event):
        super().moveEvent(event)
        if self.is_ring_screen:
            self.ring_view.update_ring_center()


