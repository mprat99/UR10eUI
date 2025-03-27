
from PyQt6.QtWidgets import QWidget
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter, QFont, QFontMetricsF, QFontMetrics, QTextDocument, QTextOption
from PyQt6.QtCore import Qt, QRectF, QTimer, QTime, QPropertyAnimation, pyqtProperty, QEasingCurve
from utils.enums import State

class Screen1(QWidget):
    def __init__(self, init_config, parent=None):
        super().__init__(parent)
        self.ring_svg_path = "assets/green_ring.svg"
        self.central_warning_svg_path = "assets/central_warning.svg"
        self.central_error_svg_path = "assets/central_error.svg"
        self.central_done_svg_path = "assets/central_done.svg"
        
        # Use QSvgRenderer to load the SVG (instead of QSvgWidget)
        self.ring_svg_renderer = QSvgRenderer(self.ring_svg_path)
        self.central_svg_renderer = QSvgRenderer()
        
        # Two labels: title and subtitle
        self.title_text = "Max. Productivity"
        self.subtitle_text = "Keep distance"
        self.rotation_angle = 0  # Rotation angle for labels
        
        # Initialize sizes
        self.resizeEvent(None)
        
        self._opacity = 0.0
        self._scale = 0.5  # Start small

        # Create opacity animation
        self.opacity_anim = QPropertyAnimation(self, b"opacity")
        self.opacity_anim.setDuration(1500)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Create scale animation
        self.scale_anim = QPropertyAnimation(self, b"scale")
        self.scale_anim.setDuration(500)
        self.scale_anim.setStartValue(1.05)
        self.scale_anim.setEndValue(1.0)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.update_state(init_config)

    # Property for opacity
    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value
        self.update()  # Repaint with new opacity

    opacity = pyqtProperty(float, get_opacity, set_opacity)

    # Property for scale
    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value
        self.update()  # Repaint with new scale

    scale = pyqtProperty(float, get_scale, set_scale)


    def rotate(self, angle):
        """Rotate the labels for demonstration purposes."""
        self.rotation_angle = (self.rotation_angle + 1)
        self.update()

    # def resizeEvent(self, event):
    #     """Resize the SVG rendering area relative to the screen height."""
    #     self.update()

    def paintEvent(self, event):
        """Draw the title and subtitle, then render the SVG."""

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._opacity)  # Apply smooth fade-in

        # Calculate SVG size
        screen_size = min(self.width(), self.height())
        ring_svg_size = int(screen_size * 0.94 * self._scale)  # Apply scaling
        # central_svg_size = int(screen_size * 0.90 * self._scale)

        ring_svg_rect = QRectF(
            (self.width() - ring_svg_size) // 2,
            (self.height() - ring_svg_size) // 2,
            ring_svg_size,
            ring_svg_size
        )

        # Render SVGs with smooth animation
        self.ring_svg_renderer.render(painter, ring_svg_rect)

        # # Draw the labels first
        self.draw_labels(painter, ring_svg_rect)
        
        # Debugging Borders (optional)
        # painter.setPen(Qt.GlobalColor.red)
        # painter.drawRect(svg_rect)  # Border around the SVG
        

    def draw_labels(self, painter: QPainter, svg_rect):
        """Draw the title and subtitle dynamically inside the SVG with proper wrapping and layout adjustment."""

        # Base font sizes relative to the SVG height
        title_font_size = int(svg_rect.height() * 0.07)
        subtitle_font_size = int(svg_rect.height() * 0.06)

        # Define the max label group height
        label_group_height = svg_rect.height() * 0.3  
        label_group_rect = QRectF(
            svg_rect.left(),
            svg_rect.center().y() - label_group_height / 2,
            svg_rect.width(),
            label_group_height
        )

        # Reset transformation & prepare painter
        painter.save()
        painter.translate(label_group_rect.center())  
        painter.rotate(self.rotation_angle)  
        painter.translate(-label_group_rect.center())

        # DRAW TITLE (WITH WRAPPING)
        title_font = QFont("DM Sans", title_font_size, QFont.Weight.Bold)
        title_doc = QTextDocument()
        title_doc.setDefaultFont(title_font)
        title_doc.setTextWidth(label_group_rect.width())  # Max width for wrapping
        title_doc.setHtml(f"<p align='center' style='color:white'>{self.title_text}</p>")  

        # Calculate adjusted height
        title_height = title_doc.size().height()
        title_rect = QRectF(
            label_group_rect.left(), label_group_rect.top(),  
            label_group_rect.width(), title_height
        )
        
        # Render wrapped title
        painter.translate(title_rect.topLeft())  
        title_doc.drawContents(painter)
        painter.translate(-title_rect.topLeft())  # Reset position

        # DRAW SUBTITLE (WITH WRAPPING)
        subtitle_font = QFont("DM Sans", subtitle_font_size)
        subtitle_doc = QTextDocument()
        subtitle_doc.setDefaultFont(subtitle_font)
        subtitle_doc.setTextWidth(label_group_rect.width())  
        subtitle_doc.setHtml(f"<p align='center' style='color:white'>{self.subtitle_text}</p>")

        # Calculate subtitle height and place it correctly below title
        subtitle_height = subtitle_doc.size().height()
        subtitle_rect = QRectF(
            label_group_rect.left(), title_rect.bottom(),  
            label_group_rect.width(), subtitle_height
        )

        # Render wrapped subtitle
        painter.translate(subtitle_rect.topLeft())  
        subtitle_doc.drawContents(painter)
        painter.translate(-subtitle_rect.topLeft())  # Reset position

        # Restore painter state
        painter.restore()



    def update_state(self, message):
        """Update the state of the screen based on the received message."""
        state = message.get("state")

        match State(state):
            case State.NORMAL:
                self.ring_svg_renderer.load("assets/green_ring.svg")
                self.title_text = "Max. Productivity"
                self.subtitle_text = "Keep distance"
            case State.REDUCED_SPEED | State.WARNING:
                self.ring_svg_renderer.load("assets/yellow_ring_warning.svg")
                self.title_text = "Reduced Speed"
                self.subtitle_text = "SSM reduced speed"
            case State.STOPPED | State.ERROR:
                self.ring_svg_renderer.load("assets/red_ring_error.svg")
                self.title_text = "Stopped"
                self.subtitle_text = "Safety-Rated Monitored Stop"
            case State.TASK_FINISHED:
                self.ring_svg_renderer.load("assets/blue_ring_done.svg")
                self.title_text = "Done"
                self.subtitle_text = "Waiting for new task..."
            case State.IDLE | _:
                self.ring_svg_renderer.load("assets/blue_ring.svg")
                self.title_text = "Idle"
                self.subtitle_text = "Waiting for new task..."

        self.opacity_anim.start()
        self.scale_anim.start()
        self.update()
            

