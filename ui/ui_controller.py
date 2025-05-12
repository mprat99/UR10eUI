from PyQt6.QtCore import QTimer
from utils.enums import MessageType
from utils.enums import State
from ui.screens.screen0 import Screen0
from ui.screens.screen2 import Screen2
from utils.utils import format_time_sec
from config.settings import INTERNAL_TIME_COUNTER


class UIController:
    def __init__(self, ring_widget, screen_windows):
        self.ring_widget = ring_widget
        self.screen_windows = screen_windows
        self.target_rotation = 0

        if INTERNAL_TIME_COUNTER:
            self.state_timer = StateTimerManager()
            self.stats_update_timer = QTimer()
            self.stats_update_timer.timeout.connect(self.update_tracked_stats)
            self.stats_update_timer.start(1000)

    def handle_message(self, message):
        """Central message handler for incoming client data."""
        message_type = message.get("type")

        try:
            match MessageType(message_type):
                case MessageType.STATE:
                    self.update_state(message)
                case MessageType.ROTATION:
                    self.update_rotation(message)
                case MessageType.LIVE_STATS:
                    self.update_live_stats(message)
                case MessageType.GLOBAL_STATS:
                    self.update_global_stats(message)
                case _:
                    print(f"[UIController] Unknown message type: {message_type}")
        except ValueError as e:
            print(f"[UIController] Invalid message type: {e}")

    def update_state(self, message):
        """Update the UI and ring for a new robot state."""
        try:
            state = State(message.get("state"))  # validate
            self.ring_widget.update_state(message)

            # Delay screen updates to sync with ring animation
            def delayed_update():
                for screen in self.screen_windows:
                    if hasattr(screen, "update_robot_state"):
                        screen.update_robot_state(message.get("state"))

                    # Update all widgets, not just the visible one
                    if screen.num_screens == 2 and screen.screen_index == 1:
                        screen.screen0_widget.update_state(message)
                        screen.screen2_widget.update_state(message)
                    else:
                        screen.get_active_content_widget().update_state(message)

            QTimer.singleShot(1000, delayed_update)

            if INTERNAL_TIME_COUNTER:
                mapped_state = None
                if state == State.NORMAL:
                    mapped_state = "normal"
                elif state in {State.REDUCED_SPEED, State.WARNING}:
                    mapped_state = "warning"
                elif state in {State.STOPPED, State.ERROR}:
                    mapped_state = "error"
                else:
                    self.state_timer.set_state("")

                if mapped_state:
                    self.state_timer.set_state(mapped_state)

        except (ValueError, KeyError) as e:
            print(f"[UIController] Invalid or missing state: {e}")

    def update_rotation(self, message):
        """Apply rotation to all relevant widgets, visible or not."""
        rotation = message.get("rotation")
        if isinstance(rotation, (int, float)) and abs(rotation - self.target_rotation) > 0.1:
            self.target_rotation = rotation
            for screen in self.screen_windows:
                # Special case for alternating screen (index 1 with 2 screens)
                if screen.num_screens == 2 and screen.screen_index == 1:
                    screen.screen0_widget.rotate(rotation)
                    screen.screen2_widget.rotate(rotation)
                else:
                    screen.get_active_content_widget().rotate(rotation)

    def update_live_stats(self, message):
        """Send live stats to Screen0."""
        for screen in self.screen_windows:
            for attr in ["screen0_widget", "screen1_widget", "screen2_widget"]:
                widget = getattr(screen, attr, None)
                if isinstance(widget, Screen0):
                    widget.update_live_stats(message)

    def update_global_stats(self, message):
        """Send global stats to Screen2."""
        for screen in self.screen_windows:
            for attr in ["screen0_widget", "screen1_widget", "screen2_widget"]:
                widget = getattr(screen, attr, None)
                if isinstance(widget, Screen2):
                    widget.update_global_stats(message)

    def handle_rotation(self, rotation):
        message = {"rotation": rotation}
        self.update_rotation(message)


    def update_tracked_stats(self):
        data = self.state_timer.get_bar_data()
        for screen in self.screen_windows:
            for attr in ["screen0_widget", "screen1_widget", "screen2_widget"]:
                widget = getattr(screen, attr, None)
                if isinstance(widget, Screen2):
                    if hasattr(widget, "chart_view"):
                        widget.chart_view.receive_data(data)


class StateTimerManager:
    def __init__(self):
        self.state_durations = {
            "normal": 1,
            "warning": 0,
            "error": 0
        }
        self.current_state = "normal"
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)

    def set_state(self, state: str):
        if state != self.current_state:
            self.current_state = state

    def _tick(self):
        if self.current_state == "normal":
            self.state_durations["normal"] += 1
        elif self.current_state == "warning":
            self.state_durations["warning"] += 1
        elif self.current_state == "error":
            self.state_durations["error"] += 1

    def get_bar_data(self):
        total_sec = sum(self.state_durations.values())
        return {
            "chart": {
                "units": "sec",
                "bars": [
                    {"label": "Max. Speed", "value": self.state_durations["normal"]},
                    {"label": "Reduced Speed", "value": self.state_durations["warning"]},
                    {"label": "Stopped", "value": self.state_durations["error"]},
                ]
            },
            "statMetric": "Total Time",
            "statValue": format_time_sec(total_sec), 
            "statUnits": ""
        }
