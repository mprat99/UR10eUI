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
        """Send live stats to screen0"""
        for screen in self.screen_windows:
            if screen.screen_index == 0:
                screen.get_active_content_widget().update_live_stats(message)

    def update_global_stats(self, message):
        """Send global stats to screen2."""
        for screen in self.screen_windows:
            if screen.screen_index == 2:
                screen.get_active_content_widget().update_global_stats(message)

    def handle_rotation(self, rotation):
        message = {"rotation": rotation}
        self.update_rotation(message)
