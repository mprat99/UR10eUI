from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QDateTime, QPointF
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RingState:
    color: tuple
    frequency: int
    lifetime: int
    speed: float
    max_thickness: float
    fade_in: float
    fade_out: float

NORMAL_STATE = RingState((0, 255, 0), 3000, 6000, 0.05, 6000.0, 0.1, 0.9)
WARNING_STATE = RingState((255, 255, 0), 2000, 5000, 0.07, 6000.0, 0.15, 0.85)
ERROR_STATE = RingState((255, 0, 0), 1200, 1000, 0.1, 6000.0, 0.2, 0.8)
IDLE_STATE = RingState((0, 0, 255), 3000, 6000, 0.05, 6000.0, 0.1, 0.9)

class Ring:
    def __init__(self, state: RingState, center: Optional[QPointF] = None):
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

class RingManager(QObject):
    rings_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.state = NORMAL_STATE
        self.rings: List[Ring] = []
        self.center = QPointF(0, 0)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.updateAnimation)
        self.anim_timer.start(33)

        self.new_ring_timer = QTimer(self)
        self.new_ring_timer.timeout.connect(self.createNewRing)
        self.new_ring_timer.start(self.state.frequency)

    def update_state(self, state_str):
        if state_str == "normal":
            self.state = NORMAL_STATE
        elif state_str in ["reduced_speed", "warning"]:
            self.state = WARNING_STATE
        elif state_str in ["stopped", "error"]:
            self.state = ERROR_STATE
        else:
            self.state = IDLE_STATE

        self.rings = self.rings[:-1]  # remove newest ring to sync state
        for ring in self.rings:
            ring.state.speed = self.state.speed
        self.new_ring_timer.stop()
        self.new_ring_timer.setInterval(self.state.frequency)
        self.new_ring_timer.start()

        self.createNewRing()

    def set_center(self, center: QPointF):
        self.center = center


    def createNewRing(self):
        self.rings.append(Ring(self.state, self.center))


    def updateAnimation(self):
        self.rings = [ring for ring in self.rings if ring.progress() < 1.0]
        self.rings_updated.emit()
