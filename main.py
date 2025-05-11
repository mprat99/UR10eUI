"""Main entry point for the UR10e UI application."""
import os
os.environ["QT_OPENGL"] = "software"  # or "software" if desktop lags more

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.main_window import MainWindow
from network.tcp_client import TCPClient
from network.uart_client import UARTClient
from config.settings import CLIENT_TYPE
from ui.widgets.ring_widget import RingWidget
from ui.ring_overlay_window import RingOverlayWindow


def main():
    # Create the application
    app = QApplication(sys.argv)
    app.setStyleSheet("QLabel { color: white; }")
    init_config = {"state": "normal"}
    # Create the TCP or UART client
    if CLIENT_TYPE == "TCP":
        client = TCPClient()
    else:
        client = UARTClient()

    client.connect_to_robot()

    # Create and show the main window
    window = MainWindow(client)
    # Ensure geometry is up-to-date
    app.processEvents()
    target_geometry = window.geometry()

    ring_widget = RingWidget({"state": "normal"})
    overlay = RingOverlayWindow(ring_widget, target_geometry)
    window.setWindowIcon(QIcon("assets/UR10e.webp"))
    window.show()
    window.raise_()  # Bring to front
    # window.activateWindow()

    # Start the application event loop
    exit_code = app.exec()
    
    # Clean up
    #client.disconnect()
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 