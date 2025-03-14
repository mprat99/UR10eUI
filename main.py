"""Main entry point for the UR10e UI application."""

import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from network.tcp_client import URClient

def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Create the TCP client
    #client = URClient()
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Try to connect to the robot
    #if not client.connect():
    #    print("Warning: Could not connect to robot. Running in offline mode.")
    
    # Start the application event loop
    exit_code = app.exec()
    
    # Clean up
    #client.disconnect()
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 