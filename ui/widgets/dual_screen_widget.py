from PyQt6.QtWidgets import QWidget, QStackedLayout

class DualScreenWidget(QWidget):
    def __init__(self, widget_0: QWidget, widget_1: QWidget):
        super().__init__()
        self.layout = QStackedLayout(self)
        self.layout.addWidget(widget_0)
        self.layout.addWidget(widget_1)
        self.layout.setCurrentIndex(0)

        self.widget_0 = widget_0
        self.widget_1 = widget_1

    def update_state(self, message):
        for widget in [self.widget_0, self.widget_1]:
            if hasattr(widget, "update_state"):
                widget.update_state(message)

    def rotate(self, angle):
        for widget in [self.widget_0, self.widget_1]:
            if hasattr(widget, "rotate"):
                widget.rotate(angle)

    def update_live_stats(self, message):
        for widget in [self.widget_0, self.widget_1]:
            if hasattr(widget, "update_live_stats"):
                widget.update_live_stats(message)

    def update_global_stats(self, message):
        for widget in [self.widget_0, self.widget_1]:
            if hasattr(widget, "update_global_stats"):
                widget.update_global_stats(message)

    def show_next(self):
        current_index = self.layout.currentIndex()
        self.layout.setCurrentIndex((current_index + 1) % 2)
