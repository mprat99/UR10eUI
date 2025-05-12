from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QBrush
from PyQt6.QtCore import QTimer, QRectF, Qt, QDateTime, QPointF

class RingState:
    def __init__(self, color, frequency, lifetime, speed, max_thickness, fade_in, fade_out):
        self.color = color
        self.frequency = frequency
        self.lifetime = lifetime
        self.speed = speed
        self.max_thickness = max_thickness
        self.fade_in = fade_in
        self.fade_out = fade_out

NORMAL_STATE = RingState((0, 255, 0), 3000, 6000, 0.05, 4000.0, 0.1, 0.9)
WARNING_STATE = RingState((255, 255, 0), 2000, 5000, 0.07, 800.0, 0.15, 0.85)
ERROR_STATE = RingState((255, 0, 0), 1000, 3000, 0.1, 600.0, 0.2, 0.8)
IDLE_STATE = RingState((0, 0, 255), 3000, 6000, 0.05, 1000.0, 0.1, 0.9)

class Ring:
    def __init__(self, state, center=None):
        self.state = state
        self.center = center
        self.creation_time = QDateTime.currentMSecsSinceEpoch()

    def progress(self):
        current_time = QDateTime.currentMSecsSinceEpoch()
        t = (current_time - self.creation_time) / self.state.lifetime
        return min(max(t, 0.0), 1.0)

    def radius(self):
        return self.progress() * self.state.speed * self.state.lifetime

    def thickness(self):
        return self.progress() * self.state.max_thickness

    def fade_factor(self):
        t = self.progress()
        if t < self.state.fade_in:
            return t / self.state.fade_in
        elif t > 1 - self.state.fade_out:
            return (1 - t) / self.state.fade_out
        return 1.0

class RingWidget(QWidget):
    def __init__(self, init_config, center=None):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")
        
        self.center_point = center if center else QPointF(self.width()/2, self.height()/2)
        self.rings = []
        self.update_state(init_config)
        self.createNewRing()
        
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.updateAnimation)
        self.anim_timer.start(33)  # ~30 FPS
        
        self.new_ring_timer = QTimer(self)
        self.new_ring_timer.timeout.connect(self.createNewRing)
        self.new_ring_timer.start(self.state.frequency)

    def createNewRing(self):
        self.rings.append(Ring(self.state, self.center_point))

    def updateAnimation(self):
        self.rings = [ring for ring in self.rings if ring.progress() < 1.0]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = self.center_point if self.center_point else QPointF(self.width()/2, self.height()/2)
        
        for ring in self.rings:
            R = ring.radius()
            T = ring.thickness()
            if T < 1.0:
                continue
                
            outer_radius = R + T/2
            gradient = QRadialGradient(center.x(), center.y(), outer_radius)
            inner_stop = max(0, R - T/2)/outer_radius
            mid_stop = R/outer_radius
            
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

    def update_state(self, message):
        state = message.get("state", "normal")
        
        if state == "normal":
            self.state = NORMAL_STATE
        elif state in ["reduced_speed", "warning"]:
            self.state = WARNING_STATE
        elif state in ["stopped", "error"]:
            self.state = ERROR_STATE
        else:  # idle, task_finished, etc
            self.state = IDLE_STATE
        
        if hasattr(self, 'new_ring_timer'):
            self.new_ring_timer.stop()
            self.new_ring_timer.setInterval(self.state.frequency)
            self.new_ring_timer.start()

    def resizeEvent(self, event):
        if not self.center_point:
            self.center_point = QPointF(self.width()/2, self.height()/2)
        super().resizeEvent(event)