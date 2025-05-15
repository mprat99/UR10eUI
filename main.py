import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from network.tcp_client import TCPClient
from network.uart_client import UARTClient
from config.settings import CLIENT_TYPE, ROTATION_FROM_IMU
from ui.ui_setup import launch_ui
from ui.ui_controller import UIController
from network.serial_reader import SerialReader

def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("QLabel { color: white; }")

    
    # Create the TCP or UART client
    if CLIENT_TYPE == "TCP":
        client = TCPClient()
    else:
        client = UARTClient()

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

    # Create and connect UI controller
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
        
    app.exec()

if __name__ == "__main__":
    main()