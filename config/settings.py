"""Configuration settings for the UR10e UI application."""

# Network settings
TCP_ENABLED = True
TCP_HOST = "192.168.1.218"
TCP_PORT = 30003
TCP_MESSAGE_DELIMITER = b'\n'

# IMU Settings
ROTATION_FROM_IMU = False
AXIS_SIGN = 1
ROTATION_OFFSET = -1.7
ROTATION_THRESHOLD = 0.1
IMU_SERIAL_PORT = "COM6"
IMU_SERIAL_BAUDRATE = 115200

# UI settings
GREEN_COLOR = "#00FF00"
YELLOW_COLOR = "#FFFF00"
RED_COLOR = "#FF0000"
BLUE_COLOR = "#0000FF"

# Debug Settings
DEBUG_MODE = True
DEBUG_DISPLAY_INDEX = 0
DEBUG_HEIGHT_RATIO = 0.8   
DEBUG_ASPECT_RATIO = 4 / 3 
DEBUG_NUM_SCREENS = 3
DEBUG_FRAMELESS_WINDOW = False
HIDE_WINDOW_FROM_TASKBAR = False




# Layout config
UI_SCREEN_INDICES = [1, 2]
LIVE_STATS_AVAILABLE = True
INTERNAL_TIME_COUNTER = True
SWITCH_SCREEN_INTERVAL = 5000
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
