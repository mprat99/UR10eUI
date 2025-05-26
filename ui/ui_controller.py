from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget
from utils.enums import MessageType, State
from ui.screens.live_stats_screen import LiveStatsScreen
from ui.screens.bar_chart_info_screen import BarChartInfoScreen
from ui.widgets.dual_screen_widget import DualScreenWidget
from utils.utils import format_time_sec
from config.settings import INTERNAL_TIME_COUNTER, ROTATION_THRESHOLD, LIVE_STATS_AVAILABLE, SWITCH_SCREEN_INTERVAL

class UIController:
    def __init__(self, ring_manager, screen_windows):
        self.ring_manager = ring_manager
        self.screen_windows = screen_windows
        self.current_rotation = 0
        self.current_state = State.NORMAL

        if INTERNAL_TIME_COUNTER:
            self.state_timer = StateTimerManager()
            self.stats_update_timer = QTimer()
            self.stats_update_timer.timeout.connect(self._tick_and_update)
            self.stats_update_timer.start(1000)

        if LIVE_STATS_AVAILABLE and len(self.screen_windows) == 2:
            self._screen_switch_timer = QTimer()
            self._screen_switch_timer.timeout.connect(self._switch_bottom_screen)
            self._screen_switch_timer.start(SWITCH_SCREEN_INTERVAL)

    def _tick_and_update(self):
        self.state_timer._tick()
        self.update_tracked_stats()

    def handle_message(self, message):
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
            
            if len(message)==2 and state == self.current_state:
                return
            
            self.ring_manager.update_state(message.get("state"))

            for screen in self.screen_windows:
                if hasattr(screen, "update_robot_state"):
                    screen.update_robot_state(message.get("state"))

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
            self.current_state = state  

            if LIVE_STATS_AVAILABLE and len(self.screen_windows) == 2:
                if state not in {State.NORMAL, State.IDLE}:
                    self._screen_switch_timer.stop()

                    for screen in self.screen_windows:
                        for widget in self._get_all_screen_widgets(screen):
                            if isinstance(widget, DualScreenWidget):
                                # Determine which subwidget is a BarChartInfoScreen and force show it
                                if isinstance(widget.widget_0, BarChartInfoScreen):
                                    widget.layout.setCurrentWidget(widget.widget_0)
                                    widget.widget_0.update_state({"state": state})
                                elif isinstance(widget.widget_1, BarChartInfoScreen):
                                    widget.layout.setCurrentWidget(widget.widget_1)
                                    widget.widget_1.update_state({"state": state})
                else:
                    if not self._screen_switch_timer.isActive():
                        self._screen_switch_timer.start(SWITCH_SCREEN_INTERVAL)

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
                for live_Stats_widget in self._find_class_widgets(widget, LiveStatsScreen):
                    live_Stats_widget.update_live_stats(message)

    def update_global_stats(self, message):
        for screen in self.screen_windows:
            for widget in self._get_all_screen_widgets(screen):
                for barchart_widget in self._find_class_widgets(widget, BarChartInfoScreen):
                    if hasattr(barchart_widget, "chart_view"):
                        widget.update_global_stats(message)

    def update_tracked_stats(self):
        data = self.state_timer.get_bar_data()
        for screen in self.screen_windows:
            for widget in self._get_all_screen_widgets(screen):
                for barchart_widget in self._find_class_widgets(widget, BarChartInfoScreen):
                    if hasattr(barchart_widget, "chart_view"):
                        barchart_widget.chart_view.receive_data(data)

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
        widgets = []
        if hasattr(screen, "alt_widget_0"):
            widgets.append(screen.alt_widget_0)
        if hasattr(screen, "alt_widget_1"):
            widgets.append(screen.alt_widget_1)
        elif hasattr(screen, "content_widget"):
            widgets.append(screen.content_widget)
        return widgets
    
    def _find_class_widgets(self, widget, widget_class):
        found = []
        if isinstance(widget, widget_class):
            found.append(widget)
        elif hasattr(widget, 'findChildren'):
            children = widget.findChildren(QWidget)
            for child in children:
                found.extend(self._find_class_widgets(child, widget_class))
        return found

    def _switch_bottom_screen(self):
        if len(self.screen_windows) < 2:
            return

        bottom_screen = self.screen_windows[1]

        for widget in self._get_all_screen_widgets(bottom_screen):
            if isinstance(widget, DualScreenWidget):
                widget.show_next()



class StateTimerManager:
    def __init__(self):
        self.state_durations = {
            "normal": 1,
            "warning": 0,
            "error": 0
        }
        self.current_state = "normal"

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
