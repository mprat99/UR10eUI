# from PyQt6.QtWidgets import QWidget
# from PyQt6.QtSvgWidgets import QSvgWidget
# from PyQt6.QtGui import QPainter, QFont
# from PyQt6.QtCore import Qt, QRectF

# class Screen1(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         svg_path = "assets/green_ring.svg"
#         # Create a fixed SVG widget
#         self.svg_widget = QSvgWidget(svg_path, self)
#         # Two labels: title and subtitle
#         self.title_text = "Max. Productivity"
#         self.subtitle_text = "Keep distance"
#         self.resizeEvent(None)  # Initialize sizes
        
#     def resizeEvent(self, event):
#         """Resize the SVG widget relative to the screen height."""
#         screen_height = self.height()
#         svg_size = int(0.98 * screen_height)  # SVG size is 40% of widget height
#         self.svg_widget.setGeometry(
#             (self.width() - svg_size) // 2,
#             (self.height() - svg_size) // 2,
#             svg_size,
#             svg_size
#         )
#         self.update()
        
#     def paintEvent(self, event):
#         """Draw the title and subtitle on top of the static SVG."""
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
#         # Get the geometry of the SVG widget
#         svg_rect = self.svg_widget.geometry()
        
#         # Calculate font sizes relative to the SVG size
#         title_font_size = int(svg_rect.height() * 0.08)
#         subtitle_font_size = int(svg_rect.height() * 0.07)
        
#         label_group_height = svg_rect.height() * 0.3  # for instance, the label_group takes 50% of the SVG height
#         label_group_rect = QRectF(
#             svg_rect.left(),
#             svg_rect.center().y() - label_group_height / 2,
#             svg_rect.width(),
#             label_group_height
#         )

#         # Draw the title text (centered in the upper half of the SVG area)
#         title_font = QFont("DM Sans", title_font_size, QFont.Weight.Bold)
#         painter.setFont(title_font)
#         painter.setPen(Qt.GlobalColor.white)
#         title_rect = QRectF(label_group_rect.left(), label_group_rect.top(), label_group_rect.width(), label_group_rect.height() / 2)
#         subtitle_rect = QRectF(label_group_rect.left(), label_group_rect.top() + label_group_rect.height() / 2, label_group_rect.width(), label_group_rect.height() / 2)

#         painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, self.title_text)
        
#         # Draw the subtitle text (centered in the lower half of the SVG area)
#         subtitle_font = QFont("DM Sans", subtitle_font_size)
#         painter.setFont(subtitle_font)
#         painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, self.subtitle_text)

#         # Set a debug pen (e.g., red color with 1px width)
#         painter.setPen(Qt.GlobalColor.red)
#         painter.drawRect(svg_rect)      # Draw border around the SVG area
#         painter.drawRect(title_rect)    # Draw border around the title area
#         painter.drawRect(subtitle_rect) # Draw border around the subtitle area

from PyQt6.QtWidgets import QWidget
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtCore import Qt, QRectF, QTimer
from config.settings import GREEN_COLOR, YELLOW_COLOR, RED_COLOR, BLUE_COLOR


class Screen1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        svg_path = "assets/green_ring.svg"
        
        # Use QSvgRenderer to load the SVG (instead of QSvgWidget)
        self.svg_renderer = QSvgRenderer(svg_path)
        
        # Two labels: title and subtitle
        self.title_text = "Max. Productivity"
        self.subtitle_text = "Keep distance"
        self.rotation_angle = 0  # Rotation angle for labels
        
        # Initialize sizes
        self.resizeEvent(None)
        
        # Optional: Add a timer to demonstrate rotation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_labels)
        self.timer.start(16)  # Rotate every 100ms

    # def set_rotation(self, angle):
    #     """Set the rotation angle for the labels."""
    #     self.rotation_angle = angle
    #     self.update()  # Trigger a repaint

    def rotate_labels(self):
        """Rotate the labels for demonstration purposes."""
        self.rotation_angle = (self.rotation_angle + 1) % 360
        self.update()

    def resizeEvent(self, event):
        """Resize the SVG rendering area relative to the screen height."""
        self.update()

    def paintEvent(self, event):
        """Draw the title and subtitle, then render the SVG."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate SVG size relative to the screen dimensions
        screen_height = self.height()
        screen_width = self.width()
        svg_size = int(min(screen_height, screen_width) * 0.98)  # SVG size is 98% of the minimum dimension      
        svg_rect = QRectF(
            (self.width() - svg_size) // 2,
            (self.height() - svg_size) // 2,
            svg_size,
            svg_size
        )
        # Render the SVG after the labels
        self.svg_renderer.render(painter, svg_rect)
        # Draw the labels first
        self.draw_labels(painter, svg_rect)
        
        # Debugging Borders (optional)
        painter.setPen(Qt.GlobalColor.red)
        # painter.drawRect(svg_rect)  # Border around the SVG
        

    def draw_labels(self, painter: QPainter, svg_rect):
        """Draw the title and subtitle on top of the static SVG."""
        # Calculate font sizes relative to the SVG size
        title_font_size = int(svg_rect.height() * 0.07)
        subtitle_font_size = int(svg_rect.height() * 0.06)

        
        # Define the area for the labels (centered within the SVG widget)
        label_group_height = svg_rect.height() * 0.3  # Group takes 30% of the SVG height
        label_group_rect = QRectF(
            svg_rect.left(),
            svg_rect.center().y() - label_group_height / 2,
            svg_rect.width(),
            label_group_height
        )

        # Apply transformation for rotation around the center of the labels
        painter.save()  # Save the current painter state
        painter.translate(label_group_rect.center())  # Move to the center of the label group
        painter.rotate(self.rotation_angle)  # Rotate
        painter.translate(-label_group_rect.center())  # Move back

        # Draw the title text (centered in the upper half of the label group)
        title_font = QFont("DM Sans", title_font_size, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.setPen(Qt.GlobalColor.white)
        title_rect = QRectF(
            label_group_rect.left(),
            label_group_rect.top(),
            label_group_rect.width(),
            label_group_rect.height() / 2
        )
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, self.title_text)
        
        # Draw the subtitle text (centered in the lower half of the label group)
        subtitle_font = QFont("DM Sans", subtitle_font_size)
        painter.setFont(subtitle_font)
        subtitle_rect = QRectF(
            label_group_rect.left(),
            label_group_rect.top() + label_group_rect.height() / 2,
            label_group_rect.width(),
            label_group_rect.height() / 2
        )
        painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, self.subtitle_text)
        # painter.drawRect(label_group_rect)
        # Restore the painter state (undo rotation)
        painter.restore()