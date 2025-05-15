"""Configuration settings for the UR10e UI application."""


CLIENT_TYPE = "TCP"
# Network settings
TCP_HOST = "192.168.0.66"
TCP_PORT = 30003
TCP_MESSAGE_DELIMITER = b'\n'
INTERNAL_TIME_COUNTER = True

#UART settings
UART_PORT = "COM10"
UART_BAUDRATE = 115200
UART_RECONNECT_INTERVAL = 5000
UART_READ_INTERVAL = 10

# IMU Settings
ROTATION_FROM_IMU = True
AXIS_SIGN = -1
ROTATION_OFFSET = -1.7
ROTATION_THRESHOLD = 0.5
IMU_SERIAL_PORT = "COM7"
IMU_SERIAL_BAUDRATE = 115200

# UI settings
WINDOW_TITLE = "UR10e Interface"
BACKGROUND_COLOR = "#000000"
GREEN_COLOR = "#00FF00"
YELLOW_COLOR = "#FFFF00"
RED_COLOR = "#FF0000"
BLUE_COLOR = "#0000FF"

# Window settings
UI_SCREEN_INDICES = [0]

WINDOW_ASPECT_RATIO = 9/4 
SECTION_ASPECT_RATIO = 3/4
SECTION_MARGIN = 0        

# Layout config
SCREEN_CLASSES_BY_INDEX = {
    1: ["RingScreen"],

    2: [
        "RingScreen",
        ["BarChartInfoScreen", "LiveStatsScreen"]
    ],

    3: [
        "LiveStatsScreen",
        "RingScreen",
        "BarChartInfoScreen"
    ]
}
LIVE_STATS_AVAILABLE = False