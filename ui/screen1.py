import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QStackedLayout,
    QGraphicsScene, QGraphicsView, QGraphicsItem  
)
from PyQt6.QtCore import Qt, QSize, QPointF, QTimer
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QPainter

class Screen1(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        
        # Main layout: center the graphics view.
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- Build the square container with stacked content ---
        self.square_container = QFrame()
        self.square_container.setStyleSheet("background: transparent; border: 0px solid red;")
        
        # Use a QStackedLayout to overlay the labels on the SVG.
        stacked_layout = QStackedLayout(self.square_container)
        stacked_layout.setContentsMargins(0, 0, 0, 0)
        stacked_layout.setSpacing(0)
        # Ensure both widgets are visible.
        stacked_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        
        # Top layer: Container for labels
        labels_container = QWidget()
        labels_container.setStyleSheet("background: transparent;")
        labels_layout = QVBoxLayout(labels_container)
        labels_layout.setContentsMargins(0, 0, 0, 0)
        labels_layout.setSpacing(0)
        
        self.title_label = QLabel("Max. Productivity")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font: DM Sans; font-weight: bold; background: transparent;")
        
        self.subtitle_label = QLabel("Keep distance")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("font: DM Sans; background: transparent;")
        
        labels_layout.addStretch(1)
        labels_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        labels_layout.addWidget(self.subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
        labels_layout.addStretch(1)
        stacked_layout.addWidget(labels_container)
        
        # Base layer: SVG widget
        self.svg_widget = QSvgWidget("assets/green_ring.svg")
        self.svg_widget.setStyleSheet("background: transparent;")
        stacked_layout.addWidget(self.svg_widget)
        
        # --- Set up QGraphicsScene / QGraphicsView for rotation ---
        self.graphics_scene = QGraphicsScene()
        self.graphics_proxy = self.graphics_scene.addWidget(self.square_container)
        self.graphics_proxy.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

        self.graphics_view = QGraphicsView(self.graphics_scene)
        self.graphics_view.setStyleSheet("background: transparent; border: 0px solid red;")
        self.graphics_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graphics_view.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_layout.addWidget(self.graphics_view, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # --- Rotation timer ---
        # self.rotation_timer = QTimer(self)
        # self.rotation_timer.timeout.connect(self.increment_rotation)
        # self.rotation_timer.start(16)  # ~60 FPS
    
    def increment_rotation(self):
        """Rotate the proxy widget by 1 degree."""
        self.graphics_proxy.setRotation(self.graphics_proxy.rotation() + 1)
        self.graphics_scene.update()  # <-- Force scene repaint
        print(self.graphics_proxy.rotation())
    
    def resizeEvent(self, event):
        """Keep the container square and update scene settings, applying scaling if needed."""
        super().resizeEvent(event)
        # Use the smaller of the widget's dimensions for a square container.
        size = min(self.width(), self.height())
        if size <= 0:
            return
        
        # Update font sizes relative to container height
        title_font_size = int(size * 0.1)  # 10% of container height
        subtitle_font_size = round(size * 0.09)  # 9% of container height
        
        self.title_label.setStyleSheet(f"font: DM Sans; font-weight: bold; background: transparent; font-size: {title_font_size}px;")
        self.subtitle_label.setStyleSheet(f"font: DM Sans; background: transparent; font-size: {subtitle_font_size}px;")
        
        self.square_container.setFixedSize(QSize(size, size))
        self.svg_widget.setFixedSize(QSize(size, size))
        
        # Compute the diagonal to ensure the rotated widget isn't clipped.
        diagonal = size * math.sqrt(2)
        # Set scene rect once for rotation
        self.graphics_scene.setSceneRect(-diagonal/2, -diagonal/2, diagonal, diagonal)
        
        # Center the proxy widget in the scene.
        self.graphics_proxy.setPos(-size/2, -size/2)
        self.graphics_proxy.setTransformOriginPoint(QPointF(size/2, size/2))

        # Ensure the view matches the ring size exactly
        self.graphics_view.setFixedSize(QSize(size, size))
        
        # Reset any previous scaling
        self.graphics_view.resetTransform()
        
        # Center the view on the proxy widget
        self.graphics_view.centerOn(self.graphics_proxy)
# import math
# from PyQt6.QtWidgets import (
#     QWidget, QVBoxLayout, QLabel, QFrame, QStackedLayout,
#     QGraphicsScene, QGraphicsView
# )
# from PyQt6.QtCore import Qt, QSize, QPointF, QTimer
# from PyQt6.QtSvgWidgets import QSvgWidget
# from PyQt6.QtGui import QPainter

# class Screen1(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setStyleSheet("background: transparent;")
        
#         # Main layout: centers the QGraphicsView.
#         main_layout = QVBoxLayout(self)
#         main_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.setSpacing(0)
#         main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
#         # --- Build the square container with stacked content ---
#         self.square_container = QFrame()
#         # The red border is for debugging; remove it if desired.
#         self.square_container.setStyleSheet("background: transparent; border: 1px solid red;")
        
#         # Use a QStackedLayout to overlay the labels on top of the SVG.
#         stacked_layout = QStackedLayout(self.square_container)
#         stacked_layout.setContentsMargins(0, 0, 0, 0)
#         stacked_layout.setSpacing(0)
#         stacked_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        
#         # --- Top layer: Container for labels ---
#         labels_container = QWidget()
#         labels_container.setStyleSheet("background: transparent;")
#         labels_layout = QVBoxLayout(labels_container)
#         labels_layout.setContentsMargins(0, 0, 0, 0)
#         labels_layout.setSpacing(0)
        
#         self.title_label = QLabel("Max. Productivity")
#         self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.title_label.setStyleSheet("font: DM Sans; font-weight: bold; background: transparent;")
        
#         self.subtitle_label = QLabel("Keep distance")
#         self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.subtitle_label.setStyleSheet("font: DM Sans; background: transparent;")
        
#         labels_layout.addStretch(1)
#         labels_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)
#         labels_layout.addWidget(self.subtitle_label, alignment=Qt.AlignmentFlag.AlignCenter)
#         labels_layout.addStretch(1)
#         stacked_layout.addWidget(labels_container)
        
#         # --- Base layer: SVG widget ---
#         self.svg_widget = QSvgWidget("assets/green_ring.svg")
#         self.svg_widget.setStyleSheet("background: transparent;")
#         stacked_layout.addWidget(self.svg_widget)
        
#         # --- Set up QGraphicsScene / QGraphicsView for rotation ---
#         self.graphics_scene = QGraphicsScene()
#         # Add the square container (with its stacked layout) to the scene.
#         self.graphics_proxy = self.graphics_scene.addWidget(self.square_container)
#         self.graphics_view = QGraphicsView(self.graphics_scene)
#         self.graphics_view.setStyleSheet("background: transparent; border: 1px solid red;")
#         self.graphics_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.graphics_view.setRenderHints(
#             QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
#         )
#         self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#         self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
#         main_layout.addWidget(self.graphics_view, alignment=Qt.AlignmentFlag.AlignCenter)
        
#         # --- Rotation timer (using built-in proxy rotation) ---
#         self.rotation_timer = QTimer(self)
#         self.rotation_timer.timeout.connect(self.increment_rotation)
#         self.rotation_timer.start(100)  # Approximately 10 FPS
    
#     def increment_rotation(self):
#         """Rotate the proxy widget by 1 degree using its setRotation() method."""
#         new_angle = (self.graphics_proxy.rotation() + 1) % 360
#         self.graphics_proxy.setRotation(new_angle)
#         self.graphics_scene.update()
#         print(f"Rotation: {new_angle}")
    
#     def resizeEvent(self, event):
#         """Update sizes and center the scene; used during development for responsiveness."""
#         super().resizeEvent(event)
#         size = min(self.width(), self.height())
#         if size <= 0:
#             return
        
#         # Update container and SVG widget sizes.
#         self.square_container.setFixedSize(QSize(size, size))
#         self.svg_widget.setFixedSize(QSize(size, size))
        
#         # Compute the diagonal to allow the rotated widget to be fully visible.
#         diagonal = size * math.sqrt(2)
#         self.graphics_scene.setSceneRect(-diagonal/2, -diagonal/2, diagonal, diagonal)
        
#         # Center the proxy widget in the scene.
#         self.graphics_proxy.setPos(-size/2, -size/2)
#         self.graphics_proxy.setTransformOriginPoint(QPointF(size/2, size/2))
        
#         # Ensure the QGraphicsView exactly matches the container size.
#         self.graphics_view.setFixedSize(QSize(size, size))
#         self.graphics_view.resetTransform()
#         self.graphics_view.centerOn(self.graphics_proxy)

