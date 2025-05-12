# ui/ui_controller.py

from PyQt6.QtCore import QTimer
from utils.enums import MessageType
from utils.enums import State

class UIController:
    def __init__(self, ring_widget, screen_windows):
        self.ring_widget = ring_widget
        self.screen_windows = screen_windows
        self.target_rotation = 0

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
            QTimer.singleShot(1000, lambda: [
                self._safe_call(screen.get_active_content_widget(), "update_state", message)
                for screen in self.screen_windows
            ])
        except (ValueError, KeyError) as e:
            print(f"[UIController] Invalid or missing state: {e}")

    def update_rotation(self, message):
        """Apply rotation to all relevant widgets, visible or not."""
        rotation = message.get("rotation")
        if isinstance(rotation, (int, float)):
            self.target_rotation = rotation
            for screen in self.screen_windows:
                # Special case for alternating screen (index 1 with 2 screens)
                if screen.num_screens == 2 and screen.screen_index == 1:
                    for widget in [screen.screen0_widget, screen.screen2_widget]:
                        self._safe_call(widget, "rotate", rotation)
                else:
                    widget = screen.get_active_content_widget()
                    self._safe_call(widget, "rotate", rotation)

    def update_live_stats(self, message):
        """Send live stats to the relevant screen (assumed screen0)."""
        for screen in self.screen_windows:
            if screen.screen_index == 0:
                self._safe_call(screen.get_active_content_widget(), "update_live_stats", message)

    def update_global_stats(self, message):
        """Send global stats to the relevant screen (assumed screen2)."""
        for screen in self.screen_windows:
            if screen.screen_index == 2:
                self._safe_call(screen.get_active_content_widget(), "update_global_stats", message)

    def _safe_call(self, widget, method_name, *args, **kwargs):
        """Safely call a method on a widget if it exists."""
        if widget is not None and hasattr(widget, method_name):
            try:
                getattr(widget, method_name)(*args, **kwargs)
            except Exception as e:

                print(f"[UIController] Error calling {method_name} on {widget}: {e}")
