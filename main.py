"""Main entry point for the UR10e UI application."""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ui.main_window import MainWindow
from network.tcp_client import TCPClient
from network.uart_client import UARTClient
from config.settings import CLIENT_TYPE


def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Create the TCP or UART client
    if CLIENT_TYPE == "TCP":
        client = TCPClient()
    else:
        client = UARTClient()

    client.connect_to_robot()

    # Create and show the main window
    window = MainWindow(client)
    window.setWindowIcon(QIcon("assets/UR10e.webp"))
    window.show()
    
    # Start the application event loop
    exit_code = app.exec()
    
    # Clean up
    #client.disconnect()
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 