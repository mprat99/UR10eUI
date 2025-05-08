"""Configuration settings for the UR10e UI application."""


CLIENT_TYPE = "TCP"
# Network settings
TCP_HOST = "localhost"
TCP_PORT = 30003  # Default UR robot port

#UART settings
UART_PORT = "COM2"
UART_BAUDRATE = 115200
UART_RECONNECT_INTERVAL = 5000
UART_READ_INTERVAL = 50

# UI settings
WINDOW_TITLE = "UR10e Interface"
BACKGROUND_COLOR = "#000000"
GREEN_COLOR = "#00FF00"
YELLOW_COLOR = "#FFFF00"
RED_COLOR = "#FF0000"
BLUE_COLOR = "#0000FF"

# Ring animation settings
RING_COLOR = (0, 255, 0)  # Default green color
RING_FREQUENCY = 3000     # New ring every 3000ms
RING_LIFETIME = 6000      # Ring lifetime in ms
RING_SPEED = 0.05        # Expansion speed in pixels per ms
RING_MAX_THICKNESS = 1000.0  # Maximum thickness in pixels
RING_FADE_IN = 0.1       # Fraction of lifetime to fade in
RING_FADE_OUT = 0.9      # Fraction of lifetime to fade out

# Window settings
WINDOW_ASPECT_RATIO = 9/4  # Height to width ratio (9 times taller than wider)

# Section widget settings
SECTION_ASPECT_RATIO = 3/4  # Height to width ratio for section widgets
SECTION_MARGIN = 0         # Margin between sections in pixels 