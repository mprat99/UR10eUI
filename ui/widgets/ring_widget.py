"""Ring animation widget for the background of the UR10e UI."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QBrush
from PyQt6.QtCore import QTimer, QRectF, QPointF, Qt, QDateTime, QRect
from utils.enums import State


class RingState:
    def __init__(self, color, frequency, lifetime, speed, max_thickness, fade_in, fade_out):
        self.color = color
        self.frequency = frequency
        self.lifetime = lifetime
        self.speed = speed
        self.max_thickness = max_thickness
        self.fade_in = fade_in
        self.fade_out = fade_out

NORMAL_STATE = RingState((0, 255, 0), 3000, 6000, 0.05, 1000.0, 0.1, 0.9)
WARNING_STATE = RingState((255, 255, 0), 2000, 5000, 0.07, 800.0, 0.15, 0.85)
ERROR_STATE = RingState((255, 0, 0), 1000, 3000, 0.1, 600.0, 0.2, 0.8)
IDLE_STATE = RingState((0, 0, 255), 3000, 6000, 0.05, 1000.0, 0.1, 0.9)

class Ring:
    def __init__(self, state: RingState):
        """
        :param color: Base color for the ring.
        :param lifetime: Lifetime in ms (default 3000ms).
        :param speed: Expansion speed in pixels per ms. (Final radius = speed * lifetime)
        :param max_thickness: Maximum thickness in pixels reached at the end of lifetime.
        :param fade_in: Fraction of lifetime used to ramp up opacity.
        :param fade_out: Fraction of lifetime used to ramp down opacity.
        """
        self.state = state
        self.creation_time = QDateTime.currentMSecsSinceEpoch()

    def progress(self) -> float:
        """Return normalized progress (0 to 1) of the ring's lifetime."""
        current_time = QDateTime.currentMSecsSinceEpoch()
        t = (current_time - self.creation_time) / self.state.lifetime
        return min(max(t, 0.0), 1.0)

    def radius(self) -> float:
        """Constant speed expansion: radius increases linearly with time."""
        final_radius = self.state.speed * self.state.lifetime  # final radius after lifetime
        return self.progress() * final_radius

    def thickness(self) -> float:
        """Linearly grow thickness from 0 to max_thickness over lifetime."""
        return self.progress() * self.state.max_thickness

    def fade_factor(self) -> float:
        """Compute an opacity factor that ramps up at the beginning and down at the end."""
        t = self.progress()
        if t < self.state.fade_in:
            return t / self.state.fade_in
        elif t > 1 - self.state.fade_out:
            return (1 - t) / self.state.fade_out
        else:
            return 1.0

class RingWidget(QWidget):
    def __init__(self, init_config):
        super().__init__()

        # Set up the widget
        self.setStyleSheet("background-color: black;")
        self.update_state(init_config)
        
        self.rings = []  # List of active rings
        
        # Create the first ring immediately
        self.createNewRing()
        
        # Timer to update the animation (~60 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(33)
        self.anim_timer.timeout.connect(self.updateAnimation)
        self.anim_timer.start()
        
        # Timer to create new rings at the specified frequency
        self.new_ring_timer = QTimer(self)
        self.new_ring_timer.timeout.connect(self.createNewRing)
        self.new_ring_timer.start(self.state.frequency)
        

    
    def createNewRing(self):
        """Create a new ring with the current parameters."""
        new_ring = Ring(self.state)
        self.rings.append(new_ring)
    
    def updateAnimation(self):
        """Update rings and remove those that have completed their lifetime."""
        self.rings = [ring for ring in self.rings if ring.progress() < 1.0]
        self.update()  # Trigger a repaint
    
    def paintEvent(self, event):
        """Paint the rings."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = QPointF(self.width() / 2, self.height() / 2)
        
        for ring in self.rings:
            R = ring.radius()
            T = ring.thickness()
            if T < 1.0:
                continue  # Skip drawing if the ring is too thin
            
            fade = ring.fade_factor()
            base_color = QColor(*ring.state.color)
            base_color.setAlpha(int(base_color.alpha() * fade))
            
            inner_radius = max(0, R - T / 2)
            outer_radius = R + T / 2
            
            # Create a radial gradient
            gradient = QRadialGradient(center, outer_radius)
            inner_stop = inner_radius / outer_radius if outer_radius > 0 else 0
            mid_stop = R / outer_radius if outer_radius > 0 else 0
            gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
            gradient.setColorAt(inner_stop, QColor(0, 0, 0, 0))
            gradient.setColorAt(mid_stop, base_color)
            gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
            
            brush = QBrush(gradient)
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)
            
            rect = QRectF(center.x() - outer_radius, center.y() - outer_radius,
                         2 * outer_radius, 2 * outer_radius)
            painter.drawEllipse(rect) 

    def update_state(self, message):
        state = message.get("state")

        match State(state):
            case State.NORMAL:
                self.state = NORMAL_STATE
            case State.REDUCED_SPEED | State.WARNING:
                self.state = WARNING_STATE
            case State.STOPPED | State.ERROR:
                self.state = ERROR_STATE
            case State.IDLE | State.TASK_FINISHED | _:
                self.state = IDLE_STATE
       
        if hasattr(self, "new_ring_timer"):
            self.new_ring_timer.stop()
            self.new_ring_timer.start(self.state.frequency)
            self.anim_timer.stop()
            self.anim_timer.start()
