
# from PyQt6.QtWidgets import QWidget
# from PyQt6.QtSvg import QSvgRenderer
# from PyQt6.QtGui import QPainter, QFont, QFontMetricsF, QFontMetrics, QTextDocument, QTextOption
# from PyQt6.QtCore import Qt, QRectF, QTimer, QTime, QPropertyAnimation, pyqtProperty, QEasingCurve
# from utils.enums import State

# class Screen1(QWidget):
#     def __init__(self, init_config, parent=None):
#         super().__init__(parent)
#         self.ring_svg_path = "assets/green_ring.svg"
#         self.central_warning_svg_path = "assets/central_warning.svg"
#         self.central_error_svg_path = "assets/central_error.svg"
#         self.central_done_svg_path = "assets/central_done.svg"
        
#         # Use QSvgRenderer to load the SVG (instead of QSvgWidget)
#         self.ring_svg_renderer = QSvgRenderer(self.ring_svg_path)
#         self.central_svg_renderer = QSvgRenderer()
        
#         # Two labels: title and subtitle
#         self.title_text = "Max. Productivity"
#         self.subtitle_text = "Keep distance"
#         self.rotation_angle = 0  # Rotation angle for labels
        
#         # Initialize sizes
#         self.resizeEvent(None)
        
#         self._opacity = 0.0
#         self._scale = 0.5  # Start small

#         # Create opacity animation
#         self.opacity_anim = QPropertyAnimation(self, b"opacity")
#         self.opacity_anim.setDuration(1500)
#         self.opacity_anim.setStartValue(0.0)
#         self.opacity_anim.setEndValue(1.0)
#         self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

#         # Create scale animation
#         self.scale_anim = QPropertyAnimation(self, b"scale")
#         self.scale_anim.setDuration(500)
#         self.scale_anim.setStartValue(1.05)
#         self.scale_anim.setEndValue(1.0)
#         self.scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
#         self.update_state(init_config)

#     # Property for opacity
#     def get_opacity(self):
#         return self._opacity

#     def set_opacity(self, value):
#         self._opacity = value
#         self.update()  # Repaint with new opacity

#     opacity = pyqtProperty(float, get_opacity, set_opacity)

#     # Property for scale
#     def get_scale(self):
#         return self._scale

#     def set_scale(self, value):
#         self._scale = value
#         self.update()  # Repaint with new scale

#     scale = pyqtProperty(float, get_scale, set_scale)


#     def rotate(self, angle):
#         """Rotate the labels for demonstration purposes."""
#         self.rotation_angle = (self.rotation_angle + 1)
#         self.update()

#     # def resizeEvent(self, event):
#     #     """Resize the SVG rendering area relative to the screen height."""
#     #     self.update()

#     def paintEvent(self, event):
#         """Draw the title and subtitle, then render the SVG."""

#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         painter.setOpacity(self._opacity)  # Apply smooth fade-in

#         # Calculate SVG size
#         screen_size = min(self.width(), self.height())
#         ring_svg_size = int(screen_size * 0.94 * self._scale)  # Apply scaling
#         # central_svg_size = int(screen_size * 0.90 * self._scale)

#         ring_svg_rect = QRectF(
#             (self.width() - ring_svg_size) // 2,
#             (self.height() - ring_svg_size) // 2,
#             ring_svg_size,
#             ring_svg_size
#         )

#         # Render SVGs with smooth animation
#         self.ring_svg_renderer.render(painter, ring_svg_rect)

#         # # Draw the labels first
#         self.draw_labels(painter, ring_svg_rect)
        
#         # Debugging Borders (optional)
#         # painter.setPen(Qt.GlobalColor.red)
#         # painter.drawRect(svg_rect)  # Border around the SVG
        

#     def draw_labels(self, painter: QPainter, svg_rect):
#         """Draw the title and subtitle dynamically inside the SVG with proper wrapping and layout adjustment."""

#         # Base font sizes relative to the SVG height
#         title_font_size = int(svg_rect.height() * 0.07)
#         subtitle_font_size = int(svg_rect.height() * 0.06)

#         # Define the max label group height
#         label_group_height = svg_rect.height() * 0.3  
#         label_group_rect = QRectF(
#             svg_rect.left(),
#             svg_rect.center().y() - label_group_height / 2,
#             svg_rect.width(),
#             label_group_height
#         )

#         # Reset transformation & prepare painter
#         painter.save()
#         painter.translate(label_group_rect.center())  
#         painter.rotate(self.rotation_angle)  
#         painter.translate(-label_group_rect.center())

#         # DRAW TITLE (WITH WRAPPING)
#         title_font = QFont("DM Sans", title_font_size, QFont.Weight.Bold)
#         title_doc = QTextDocument()
#         title_doc.setDefaultFont(title_font)
#         title_doc.setTextWidth(label_group_rect.width())  # Max width for wrapping
#         title_doc.setHtml(f"<p align='center' style='color:white'>{self.title_text}</p>")  

#         # Calculate adjusted height
#         title_height = title_doc.size().height()
#         title_rect = QRectF(
#             label_group_rect.left(), label_group_rect.top(),  
#             label_group_rect.width(), title_height
#         )
        
#         # Render wrapped title
#         painter.translate(title_rect.topLeft())  
#         title_doc.drawContents(painter)
#         painter.translate(-title_rect.topLeft())  # Reset position

#         # DRAW SUBTITLE (WITH WRAPPING)
#         subtitle_font = QFont("DM Sans", subtitle_font_size)
#         subtitle_doc = QTextDocument()
#         subtitle_doc.setDefaultFont(subtitle_font)
#         subtitle_doc.setTextWidth(label_group_rect.width())  
#         subtitle_doc.setHtml(f"<p align='center' style='color:white'>{self.subtitle_text}</p>")

#         # Calculate subtitle height and place it correctly below title
#         subtitle_height = subtitle_doc.size().height()
#         subtitle_rect = QRectF(
#             label_group_rect.left(), title_rect.bottom(),  
#             label_group_rect.width(), subtitle_height
#         )

#         # Render wrapped subtitle
#         painter.translate(subtitle_rect.topLeft())  
#         subtitle_doc.drawContents(painter)
#         painter.translate(-subtitle_rect.topLeft())  # Reset position

#         # Restore painter state
#         painter.restore()



#     def update_state(self, message):
#         """Update the state of the screen based on the received message."""
#         state = message.get("state")

#         match State(state):
#             case State.NORMAL:
#                 self.ring_svg_renderer.load("assets/green_ring.svg")
#                 self.title_text = "Max. Productivity"
#                 self.subtitle_text = "Keep distance"
#             case State.REDUCED_SPEED | State.WARNING:
#                 self.ring_svg_renderer.load("assets/yellow_ring_warning.svg")
#                 self.title_text = "Reduced Speed"
#                 self.subtitle_text = "SSM reduced speed"
#             case State.STOPPED | State.ERROR:
#                 self.ring_svg_renderer.load("assets/red_ring_error.svg")
#                 self.title_text = "Stopped"
#                 self.subtitle_text = "Safety-Rated Monitored Stop"
#             case State.TASK_FINISHED:
#                 self.ring_svg_renderer.load("assets/blue_ring_done.svg")
#                 self.title_text = "Done"
#                 self.subtitle_text = "Waiting for new task..."
#             case State.IDLE | _:
#                 self.ring_svg_renderer.load("assets/blue_ring.svg")
#                 self.title_text = "Idle"
#                 self.subtitle_text = "Waiting for new task..."

#         self.opacity_anim.start()
#         self.scale_anim.start()
#         self.update()

from PyQt6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QLabel, QApplication
from PyQt6.QtSvgWidgets import QGraphicsSvgItem  # Note: from QtSvgWidgets in PyQt6
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSize, pyqtSlot
from utils.enums import State

class Screen1(QWidget):
    def __init__(self, init_config, parent=None):
        super().__init__(parent)
        
        # Store the SVG paths for each state.
        self.ring_svg_paths = {
            State.NORMAL: "assets/green_ring.svg",
            State.REDUCED_SPEED: "assets/yellow_ring_warning.svg",
            State.WARNING: "assets/yellow_ring_warning.svg",
            State.STOPPED: "assets/red_ring_error.svg",
            State.ERROR: "assets/red_ring_error.svg",
            State.TASK_FINISHED: "assets/blue_ring_done.svg",
            State.IDLE: "assets/blue_ring.svg",
        }
        
        # Default texts for state NORMAL.
        self.default_title = "Max. Productivity"
        self.default_subtitle = "Keep distance"

        # Setup QGraphicsView and Scene.
        self.view = QGraphicsView(self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        
        # Create the ring background as a QGraphicsSvgItem.
        self.ring_item = QGraphicsSvgItem(self.ring_svg_paths[State.NORMAL])
        self.ring_item.setZValue(0)
        self.scene.addItem(self.ring_item)
        
        # Create a container widget for the labels.
        self.label_container = QWidget()
        self.label_container.setStyleSheet("background: transparent")
        layout = QVBoxLayout(self.label_container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.title_label = QLabel(self.default_title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Only set properties like color, font-family, and weight via stylesheet.
        self.title_label.setStyleSheet("color: white; font-family: 'DM Sans'; font-weight: bold;")
        
        self.subtitle_label = QLabel(self.default_subtitle)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("color: white; font-family: 'DM Sans';")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)
        
        # Wrap the container widget in a QGraphicsProxyWidget.
        self.proxy = self.scene.addWidget(self.label_container)
        self.proxy.setZValue(1)  # Ensure labels appear above the SVG.

        # Create animations for the proxy: opacity, scale, and rotation.
        self.opacity_anim = QPropertyAnimation(self.proxy, b"opacity")
        self.opacity_anim.setDuration(1500)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.scale_anim = QPropertyAnimation(self.proxy, b"scale")
        self.scale_anim.setDuration(500)
        self.scale_anim.setStartValue(1.05)
        self.scale_anim.setEndValue(1.0)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        self.rotation_anim = QPropertyAnimation(self.proxy, b"rotation")
        self.rotation_anim.setDuration(500)
        self.rotation_anim.setStartValue(0)  # starting rotation angle
        self.rotation_anim.setEndValue(360)  # rotate full circle (adjust as needed)
        self.rotation_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Group animations to start them together.
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.opacity_anim)
        self.anim_group.addAnimation(self.scale_anim)
        self.anim_group.addAnimation(self.rotation_anim)
        
        self.update_state(init_config)
    
    def resizeEvent(self, event):
        # Update view and scene geometry.
        self.view.setGeometry(self.rect())
        self.scene.setSceneRect(QRectF(self.view.rect()))
        
        side = min(self.width(), self.height())
        desired_ring_size = side * 0.94
        
        # Get the original size of the SVG from its renderer.
        renderer: QSvgRenderer = self.ring_item.renderer()
        original_size = renderer.defaultSize()
        if original_size.isEmpty():
            original_size = QSize(100, 100)  # Fallback size
        
        # Compute scale factor for the ring.
        factor = desired_ring_size / min(original_size.width(), original_size.height())
        self.ring_item.setScale(factor)
        
        # Center the ring item.
        ring_width = original_size.width() * factor
        ring_height = original_size.height() * factor
        ring_x = (self.width() - ring_width) / 2
        ring_y = (self.height() - ring_height) / 2
        self.ring_item.setPos(ring_x, ring_y)
        
        # Dynamically adjust the font sizes relative to the window size.
        title_font_size = max(10, int(side * 0.08))
        subtitle_font_size = max(8, int(side * 0.06))
        
        # Update the fonts for the title and subtitle labels.
        title_font = self.title_label.font()
        title_font.setPointSize(title_font_size)
        self.title_label.setFont(title_font)
        
        subtitle_font = self.subtitle_label.font()
        subtitle_font.setPointSize(subtitle_font_size)
        self.subtitle_label.setFont(subtitle_font)
        
        # Let the proxy widget (labels) adjust size and center it.
        self.label_container.adjustSize()
        proxy_rect = self.proxy.boundingRect()
        self.proxy.setPos((self.width() - proxy_rect.width()) / 2,
                          (self.height() - proxy_rect.height()) / 2)
        
        super().resizeEvent(event)
    
    @pyqtSlot(dict)
    def update_state(self, message: dict):
        state = message.get("state", State.NORMAL)
        
        # Use match-case to update state.
        match state:
            case State.NORMAL:
                self.ring_item.setSharedRenderer(QSvgRenderer(self.ring_svg_paths[State.NORMAL]))
                self.title_label.setText("Max. Productivity")
                self.subtitle_label.setText("Keep distance")
            case State.REDUCED_SPEED | State.WARNING:
                self.ring_item.setSharedRenderer(QSvgRenderer(self.ring_svg_paths[State.REDUCED_SPEED]))
                self.title_label.setText("Reduced Speed")
                self.subtitle_label.setText("SSM reduced speed")
            case State.STOPPED | State.ERROR:
                self.ring_item.setSharedRenderer(QSvgRenderer(self.ring_svg_paths[State.STOPPED]))
                self.title_label.setText("Stopped")
                self.subtitle_label.setText("Safety-Rated Monitored Stop")
            case State.TASK_FINISHED:
                self.ring_item.setSharedRenderer(QSvgRenderer(self.ring_svg_paths[State.TASK_FINISHED]))
                self.title_label.setText("Done")
                self.subtitle_label.setText("Waiting for new task...")
            case State.IDLE | _:
                self.ring_item.setSharedRenderer(QSvgRenderer(self.ring_svg_paths[State.IDLE]))
                self.title_label.setText("Idle")
                self.subtitle_label.setText("Waiting for new task...")
        
        # Restart animations.
        self.opacity_anim.stop()
        self.scale_anim.stop()
        self.rotation_anim.stop()
        
        self.proxy.setOpacity(0.0)
        self.proxy.setScale(1.05)
        self.proxy.setRotation(0)
        
        self.opacity_anim.start()
        self.scale_anim.start()
        self.rotation_anim.start()
