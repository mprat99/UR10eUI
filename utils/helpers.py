"""Helper functions for the UR10e UI application."""

from typing import Tuple
import math

def calculate_section_size(window_width: int, window_height: int,
                         aspect_ratio: float = 4/3) -> Tuple[int, int]:
    """Calculate the size for a section widget based on window size and aspect ratio.
    
    :param window_width: Total window width
    :param window_height: Total window height
    :param aspect_ratio: Desired width to height ratio (default 4:3)
    :return: Tuple of (width, height)
    """
    # Section height is 30% of window height
    section_height = int(window_height * 0.3)
    # Section width is calculated to maintain aspect ratio
    section_width = int(section_height * aspect_ratio)
    return section_width, section_height

def format_joint_angles(angles: list) -> list:
    """Format joint angles for display.
    
    :param angles: List of joint angles in radians
    :return: List of formatted angle strings in degrees
    """
    return [f"{math.degrees(angle):.2f}°" for angle in angles]

def format_position(position: list) -> list:
    """Format TCP position for display.
    
    :param position: List of position values [x, y, z] in meters
    :return: List of formatted position strings in millimeters
    """
    return [f"{pos * 1000:.1f}mm" for pos in position]

def format_speed(speed: float) -> str:
    """Format speed value for display.
    
    :param speed: Speed value in m/s
    :return: Formatted speed string
    """
    return f"{speed * 1000:.0f} mm/s"

def parse_program_state(state_code: int) -> str:
    """Convert program state code to human-readable string.
    
    :param state_code: Program state code from robot
    :return: Human-readable state description
    """
    states = {
        1: "RUNNING",
        2: "STOPPED",
        3: "PAUSED",
        4: "ERROR"
    }
    return states.get(state_code, "UNKNOWN") 