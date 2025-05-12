import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QRect, QPointF
from PyQt6.QtGui import QGuiApplication
from ui.screen_window import ScreenWindow
from ui.widgets.ring_widget import RingWidget
from network.tcp_client import TCPClient
from network.uart_client import UARTClient
from config.settings import CLIENT_TYPE
from ui.main_ui import launch_ui
from ui.ui_controller import UIController
from network.imu_serial_reader import IMUSerialReader

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
        serial_reader = IMUSerialReader()
    except Exception as e:
        print(f"Error initializing SerialReader: {e}")


    def handle_escape():
        app.quit()

    def closeEvent(self, event):
        self.serial_reader.stop()
        super().closeEvent(event)
    
    bg_window, screen_windows, ring_widget = launch_ui(app, client, handle_escape)

    # Create and connect UI controller
    controller = UIController(ring_widget, screen_windows)
    client.message_received.connect(controller.handle_message)
    serial_reader.rotation_received.connect(controller.handle_rotation)
    serial_reader.start()
    app.exec()

if __name__ == "__main__":
    main()