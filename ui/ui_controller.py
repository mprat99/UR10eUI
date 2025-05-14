from PyQt6.QtCore import QTimer
from utils.enums import MessageType
from utils.enums import State
from ui.screens.live_stats_screen import LiveStatsScreen
from ui.screens.bar_chart_info_screen import BarChartInfoScreen
from utils.utils import format_time_sec
from config.settings import INTERNAL_TIME_COUNTER, ROTATION_THRESHOLD


class UIController:
    def __init__(self, ring_widget, screen_windows):
        self.ring_widget = ring_widget
        self.screen_windows = screen_windows
        self.current_rotation = 0

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
        try:
            state = State(message.get("state"))
            self.ring_widget.update_state(message)

            for screen in self.screen_windows:
                if hasattr(screen, "update_robot_state"):
                    screen.update_robot_state(message.get("state"))

                # Update all widgets on the screen if alternating
                for widget in self._get_all_screen_widgets(screen):
                    widget.update_state(message)

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
        rotation = message.get("rotation")
        if isinstance(rotation, (int, float)) and abs(rotation - self.current_rotation) > ROTATION_THRESHOLD:
            self.current_rotation = rotation
            for screen in self.screen_windows:
                for widget in self._get_all_screen_widgets(screen):
                    widget.rotate(rotation)

    def update_live_stats(self, message):
        for screen in self.screen_windows:
            for widget in self._get_all_screen_widgets(screen):
                if isinstance(widget, LiveStatsScreen):
                    widget.update_live_stats(message)

    def update_global_stats(self, message):
        for screen in self.screen_windows:
            for widget in self._get_all_screen_widgets(screen):
                if isinstance(widget, BarChartInfoScreen):
                    widget.update_global_stats(message)

    def update_tracked_stats(self):
        data = self.state_timer.get_bar_data()
        for screen in self.screen_windows:
            for widget in self._get_all_screen_widgets(screen):
                if isinstance(widget, BarChartInfoScreen) and hasattr(widget, "chart_view"):
                    widget.chart_view.receive_data(data)

    def handle_rotation_serial(self, rotation):
        self.update_rotation({"rotation": rotation})

    def handle_state_serial(self, state):
        state_map = {
            1: "reduced_speed",
            2: "normal",
            3: "stopped"
        }

        mapped_state = state_map.get(state, 2)
        if mapped_state is not None:
            message = {
                "type": "state",
                "state": mapped_state
            }
            self.update_state(message)
        else:
            print(f"[Warning] Unknown state received from serial: {state}")




    def _get_all_screen_widgets(self, screen):
        """Returns all widgets on a screen — visible and alternate."""
        widgets = []

        # Alternating screen: both widgets exist
        if hasattr(screen, "alt_widget_0"):
            widgets.append(screen.alt_widget_0)
        if hasattr(screen, "alt_widget_1"):
            widgets.append(screen.alt_widget_1)

        # Single widget screen
        elif hasattr(screen, "content_widget"):
            widgets.append(screen.content_widget)

        return widgets



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
