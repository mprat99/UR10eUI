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

# def get_display_config():
#     """Get combined geometry and center point based on display count"""
#     screens = sorted(QGuiApplication.screens(), key=lambda s: (s.geometry().top(), s.geometry().left()))
    
#     # Calculate combined geometry of all screens
#     combined_rect = QRect()
#     for screen in screens:
#         combined_rect = combined_rect.united(screen.geometry())
    
#     # Determine target screen for ring center
#     if len(screens) == 1:
#         target_screen = screens[0]
#     elif len(screens) == 2:
#         target_screen = screens[0]  # Top display
#     else:  # 3+ displays
#         target_screen = screens[1]  # Middle display
    
#     # Calculate absolute center of target screen
#     target_geo = target_screen.geometry()
#     absolute_center = QPointF(
#         target_geo.left() + target_geo.width()/2,
#         target_geo.top() + target_geo.height()/2
#     )
    
#     # Convert to coordinates relative to combined rect
#     relative_center = absolute_center - QPointF(combined_rect.topLeft())
    
#     return combined_rect, relative_center, screens

def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("QLabel { color: white; }")

    
    # Create the TCP or UART client
    if CLIENT_TYPE == "TCP":
        client = TCPClient()
    else:
        client = UARTClient()

    client.connect_to_robot()

    def handle_escape():
        app.quit()

    
    bg_window, screen_windows, ring_widget = launch_ui(app, client, handle_escape)

    # Create and connect UI controller
    controller = UIController(ring_widget, screen_windows)
    client.message_received.connect(controller.handle_message)

    app.exec()

if __name__ == "__main__":
    main()