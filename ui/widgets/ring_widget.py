"""Ring animation widget for the background of the UR10e UI."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QBrush
from PyQt6.QtCore import QTimer, QRectF, QPointF, Qt, QDateTime

from config.settings import (
    RING_COLOR, RING_FREQUENCY, RING_LIFETIME, RING_SPEED,
    RING_MAX_THICKNESS, RING_FADE_IN, RING_FADE_OUT
)

class Ring:
    def __init__(self, color: QColor, lifetime: int, speed: float, max_thickness: float,
                 fade_in: float = 0.1, fade_out: float = 0.2):
        """
        :param color: Base color for the ring.
        :param lifetime: Lifetime in ms (default 3000ms).
        :param speed: Expansion speed in pixels per ms. (Final radius = speed * lifetime)
        :param max_thickness: Maximum thickness in pixels reached at the end of lifetime.
        :param fade_in: Fraction of lifetime used to ramp up opacity.
        :param fade_out: Fraction of lifetime used to ramp down opacity.
        """
        self.color = color
        self.lifetime = lifetime      # in ms (e.g., 3000ms)
        self.speed = speed            # pixels per ms
        self.max_thickness = max_thickness
        self.fade_in = fade_in        # fraction of lifetime for fade in
        self.fade_out = fade_out      # fraction of lifetime for fade out
        self.creation_time = QDateTime.currentMSecsSinceEpoch()

    def progress(self) -> float:
        """Return normalized progress (0 to 1) of the ring's lifetime."""
        current_time = QDateTime.currentMSecsSinceEpoch()
        t = (current_time - self.creation_time) / self.lifetime
        return min(max(t, 0.0), 1.0)

    def radius(self) -> float:
        """Constant speed expansion: radius increases linearly with time."""
        final_radius = self.speed * self.lifetime  # final radius after lifetime
        return self.progress() * final_radius

    def thickness(self) -> float:
        """Linearly grow thickness from 0 to max_thickness over lifetime."""
        return self.progress() * self.max_thickness

    def fade_factor(self) -> float:
        """Compute an opacity factor that ramps up at the beginning and down at the end."""
        t = self.progress()
        if t < self.fade_in:
            return t / self.fade_in
        elif t > 1 - self.fade_out:
            return (1 - t) / self.fade_out
        else:
            return 1.0

class RingWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set up the widget
        self.setStyleSheet("background-color: black;")
        
        # Animation parameters from settings
        self.ring_frequency = RING_FREQUENCY
        self.ring_color = QColor(*RING_COLOR)
        self.lifetime = RING_LIFETIME
        self.speed = RING_SPEED
        self.max_thickness = RING_MAX_THICKNESS
        self.fade_in = RING_FADE_IN
        self.fade_out = RING_FADE_OUT
        
        self.rings = []  # List of active rings
        
        # Create the first ring immediately
        self.createNewRing()
        
        # Timer to update the animation (~60 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16)
        self.anim_timer.timeout.connect(self.updateAnimation)
        self.anim_timer.start()
        
        # Timer to create new rings at the specified frequency
        self.new_ring_timer = QTimer(self)
        self.new_ring_timer.timeout.connect(self.createNewRing)
        self.new_ring_timer.start(self.ring_frequency)
    
    def createNewRing(self):
        """Create a new ring with the current parameters."""
        new_ring = Ring(color=self.ring_color, lifetime=self.lifetime,
                       speed=self.speed, max_thickness=self.max_thickness,
                       fade_in=self.fade_in, fade_out=self.fade_out)
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
            base_color = QColor(ring.color)
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