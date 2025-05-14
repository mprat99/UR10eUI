from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene,
    QGraphicsWidget, QVBoxLayout, QSizePolicy
)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, pyqtProperty, QEasingCurve, QTimer
)
from PyQt6.QtGui import (
    QColor, QFont, QPainter, QTextOption
)
from utils.enums import State

class RingScreen(QWidget):

    def __init__(self, init_config, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Fixed design size parameters
        self.design_size = 300
        self.title_font_size = 23
        self.subtitle_font_size = 18

        # Main graphics view setup
        self.view = QGraphicsView()
        self.view.setStyleSheet("background: transparent; border: none;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Scene setup with fixed design size
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.design_size, self.design_size)
        self.scene.setBackgroundBrush(QColor(0, 0, 0, 0))
        self.view.setScene(self.scene)

        # Central container for transformations
        self.container = QGraphicsWidget()
        self.scene.addItem(self.container)
        self.container.setPos(self.design_size/2, self.design_size/2)  # Center in scene

        # SVG setup
        self.svg_item = QSvgWidget()
        self.svg_item.setStyleSheet("background: transparent")
        self.svg_item.setFixedSize(self.design_size, self.design_size)
        self.svg_proxy = self.scene.addWidget(self.svg_item)
        self.svg_proxy.setParentItem(self.container)
        self.svg_proxy.setPos(-self.design_size/2, -self.design_size/2)  # Center in container

        # Text items
        self.title_item = self.scene.addText("", QFont("DM Sans", self.title_font_size, QFont.Weight.Bold))
        self.subtitle_item = self.scene.addText("", QFont("DM Sans", self.subtitle_font_size))
        self.title_item.setDefaultTextColor(QColor(255, 255, 255))
        self.subtitle_item.setDefaultTextColor(QColor(255, 255, 255))
        self.title_item.setParentItem(self.container)
        self.subtitle_item.setParentItem(self.container)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.view)

        # Animation properties
        self._opacity = 1.0
        self._scale = 1.05
        self._rotation = 0.0

        # Animations setup
        self.opacity_anim = QPropertyAnimation(self, b"opacity")
        self.opacity_anim.setDuration(1500)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.scale_anim = QPropertyAnimation(self, b"scale")
        self.scale_anim.setDuration(500)
        self.scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.rotate_anim = QPropertyAnimation(self, b"rotation")
        self.rotate_anim.setDuration(1000)
        self.rotate_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        # Set transform origin to center (0,0) of container
        self.container.setTransformOriginPoint(0, 0)

        # Initial update with delayed scaling
        self.update_state(init_config)
        QTimer.singleShot(50, self._initial_fit_view)

    def _initial_fit_view(self):
        """Handle initial view fitting after first render"""
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _update_text_positions(self):
        """Position text with smart wrapping and debug borders"""
        # Calculate available width (90% of design size)
        available_width = self.design_size * 0.9

        def setup_item(item):
            # Measure natural width
            item.document().setTextWidth(-1)
            natural_width = item.boundingRect().width()
            
            # Configure wrapping only if needed
            should_wrap = natural_width > available_width
            option = QTextOption()
            option.setAlignment(Qt.AlignmentFlag.AlignCenter)
            option.setWrapMode(QTextOption.WrapMode.WordWrap if should_wrap else QTextOption.WrapMode.NoWrap)
            item.document().setDefaultTextOption(option)
            item.setTextWidth(available_width if should_wrap else -1)
            item.adjustSize()
        

        # Setup both items
        setup_item(self.title_item)
        setup_item(self.subtitle_item)

        # Calculate vertical positions
        spacing = -2
        total_height = self.title_item.boundingRect().height() + \
                    self.subtitle_item.boundingRect().height() + spacing
        start_y = -total_height / 2

        # Position items
        self.title_item.setPos(-self.title_item.boundingRect().width()/2, start_y)
        self.subtitle_item.setPos(-self.subtitle_item.boundingRect().width()/2,
                                start_y + self.title_item.boundingRect().height() + spacing)

    def resizeEvent(self, event):
        """Handle window resizing"""
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        super().resizeEvent(event)

    # Animation properties
    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value
        self.container.setOpacity(value)

    opacity = pyqtProperty(float, get_opacity, set_opacity)

    def get_scale(self):
        return self._scale

    def set_scale(self, value):
        self._scale = value
        self.container.setScale(value)

    scale = pyqtProperty(float, get_scale, set_scale)

    def get_rotation(self):
        return self._rotation

    def set_rotation(self, value):
        self._rotation = value % 360
        self.container.setRotation(value)

    rotation = pyqtProperty(float, get_rotation, set_rotation)

    def update_state(self, message):

        try:
            state = State(message.get("state", State.IDLE))
            
            svg_map = {
                State.NORMAL: "assets/green_ring.svg",
                State.REDUCED_SPEED: "assets/yellow_ring_warning.svg",
                State.WARNING: "assets/yellow_ring_warning.svg",
                State.STOPPED: "assets/red_ring_error.svg",
                State.ERROR: "assets/red_ring_error.svg",
                State.TASK_FINISHED: "assets/blue_ring_done.svg",
                State.IDLE: "assets/blue_ring.svg"
            }
            
            text_map = {
                State.NORMAL: ("Max. Productivity", "Keep distance"),
                State.REDUCED_SPEED: ("Reduced Speed", "SSM reduced speed"),
                State.WARNING: ("Reduced Speed", "SSM reduced speed"),
                State.STOPPED: ("Stopped", "Safety-Rated Monitored Stop"),
                State.ERROR: ("Stopped", "Safety-Rated Monitored Stop"),
                State.TASK_FINISHED: ("Done", "Waiting for new task..."),
                State.IDLE: ("Idle", "Waiting for new task...")
            }

            # Update SVG
            self.svg_item.load(svg_map[state])
            
            # Update text content
            self.title_item.setPlainText(text_map[state][0])
            self.subtitle_item.setPlainText(text_map[state][1])
            
            if (title := message.get("screen1Text0")) is not None:
                self.title_item.setPlainText(title)
            if (subtitle := message.get("screen1Text1")) is not None:
                self.subtitle_item.setPlainText(subtitle)   

            self._update_text_positions()

            # Reset and start animations
            self.opacity_anim.setStartValue(0.0)
            self.opacity_anim.setEndValue(1.0)
            self.scale_anim.setStartValue(1.05)
            self.scale_anim.setEndValue(1.0)
            self.rotate_anim.setStartValue(0)
            self.rotate_anim.setEndValue(360)
            
            self.opacity_anim.start()
            self.scale_anim.start()

        except (ValueError, KeyError) as e:
            print("Invalid State")

    def rotate(self, target_rotation):

        difference = int(abs(self._rotation - target_rotation))
        if self.rotate_anim.state() == QPropertyAnimation.State.Running:
            self._rotation = self.rotate_anim.currentValue()
            self.rotate_anim.stop()

        if difference > 10:
            self.rotate_anim.setStartValue(self._rotation)
            self.rotate_anim.setEndValue(target_rotation)
            self.rotate_anim.setDuration(min(300, 10 * difference))
            self.rotate_anim.finished.connect(self._on_rotation_animation_finished)
            self.rotate_anim.start()
        else:
            self.container.setRotation(target_rotation)
            self._rotation = target_rotation


    def _on_rotation_animation_finished(self):
        self._rotation = self.rotate_anim.currentValue()
