import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
from network.tcp_client import TCPClient
from config.settings import TCP_ENABLED, ROTATION_FROM_IMU
from ui.ui_setup import launch_ui
from ui.ui_controller import UIController
from network.serial_reader import SerialReader
import time

now = time.time()

def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("QLabel { color: white; }")

    client = TCPClient()

    if TCP_ENABLED:
        client.connect_to_robot()

    try:
        serial_reader = SerialReader()
    except Exception as e:
        print(f"Error initializing SerialReader: {e}")


    def handle_escape():
        app.quit()

    def closeEvent(self, event):
        serial_reader.stop()
        super().closeEvent(event)
    
    bg_window, screen_windows, ring_widget = launch_ui(app, client, handle_escape)

    controller = UIController(ring_widget, screen_windows)
    client.message_received.connect(
                controller.handle_message,
                type=Qt.ConnectionType.QueuedConnection
            )

    if ROTATION_FROM_IMU:
        serial_reader.rotation_received.connect(
            controller.handle_rotation_serial,
            type=Qt.ConnectionType.QueuedConnection
        )

        serial_reader.state_received.connect(
            controller.handle_state_serial,
            type=Qt.ConnectionType.QueuedConnection
        )
        serial_reader.start()
    heartbeat_timer = QTimer()
    heartbeat_timer.setInterval(1000)
    heartbeat_timer.timeout.connect(print_time)
    # heartbeat_timer.start()
        
    app.exec()


def print_time():
    elapsed_time = time.time() - now
    if (elapsed_time > 60):
        print(f"Elapsed time: {elapsed_time // 60} minutes")
    else:
        print(f"Elapsed time: {elapsed_time} seconds")

if __name__ == "__main__":
    main()
