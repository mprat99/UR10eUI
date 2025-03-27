from enum import Enum

class MessageType(Enum):
    STATE = "state"
    ROTATION = "rotation"
    LIVE_STATS = "liveStats"
    GLOBAL_STATS = "globalStats"

class State(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    ERROR = "error"
    REDUCED_SPEED = "reduced_speed"
    STOPPED = "stopped"
    IDLE = "idle"
    TASK_FINISHED = "task_finished"