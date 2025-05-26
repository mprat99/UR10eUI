from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QRadialGradient, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF, QPointF
from ui.ring_manager import RingManager

class RingViewWidget(QWidget):
    def __init__(self, ring_manager: RingManager, center: QPointF = None, is_ring_screen=False):
        super().__init__()
        self.ring_manager = ring_manager
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background-color: transparent;")

        self.center_point = center or QPointF(self.width() / 2, self.height() / 2)

        self.ring_manager.rings_updated.connect(self.update)
        self.is_ring_screen = is_ring_screen



    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        global_center = self.ring_manager.center
        center = self.mapFromGlobal(global_center)


        for ring in self.ring_manager.rings:
            R = ring.radius()
            T = ring.thickness()
            if T < 1.0:
                continue

            outer_radius = R + T / 2
            gradient = QRadialGradient(center.x(), center.y(), outer_radius)
            inner_stop = max(0, R - T / 2) / outer_radius
            mid_stop = R / outer_radius

            base_color = QColor(*ring.state.color)
            base_color.setAlpha(int(255 * ring.fade_factor()))

            gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
            gradient.setColorAt(inner_stop, QColor(0, 0, 0, 0))
            gradient.setColorAt(mid_stop, base_color)
            gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(
                center.x() - outer_radius,
                center.y() - outer_radius,
                2 * outer_radius,
                2 * outer_radius
            ))


    def resizeEvent(self, event):
        if self.is_ring_screen:
            local_center = QPointF(self.width() / 2, self.height() / 2)
            global_center = self.mapToGlobal(local_center)
            self.ring_manager.set_center(global_center)
            super().resizeEvent(event)


    def update_ring_center(self):
        if not self.is_ring_screen:
            return
        local_center = QPointF(self.width() / 2, self.height() / 2)
        global_center = self.mapToGlobal(local_center.toPoint())
        self.ring_manager.set_center(global_center)
        self.update()
