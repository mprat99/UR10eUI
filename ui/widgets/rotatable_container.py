from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsProxyWidget
)
from PyQt6.QtGui import (
    QColor,QPen, QPainter
)
from PyQt6.QtCore import (Qt, QPropertyAnimation, pyqtProperty, QEasingCurve)


# ----------------- Rotatable Container -----------------
class RotatableContainer(QGraphicsView):
    """
    A container that wraps a widget in a QGraphicsProxyWidget so it can be rotated.
    Optionally draws a circular border on top of the content for debug purposes.
    """
    def __init__(self, widget: QWidget, rotation: float = 0, draw_border: bool = False, border_color: QColor = QColor("red")):
        super().__init__()
        self.setStyleSheet("background: transparent; border: 0px;")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Unparent the widget if necessary.
        if widget.parent() is not None:
            widget.setParent(None)

        self.proxy = QGraphicsProxyWidget()
        self.proxy.setWidget(widget)
        self.draw_border = draw_border
        self.border_color = border_color

        # Set the transform origin and initial rotation.
        self.proxy.setTransformOriginPoint(self.proxy.boundingRect().center())
        self.proxy.setRotation(rotation)
        self.scene.addItem(self.proxy)

        # Disable scrollbars.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    #     # Animations setup
    #     self.opacity_anim = QPropertyAnimation(self, b"opacity")
    #     self.opacity_anim.setDuration(1500)
    #     self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    #     self.scale_anim = QPropertyAnimation(self, b"scale")
    #     self.scale_anim.setDuration(500)
    #     self.scale_anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    # # Animation properties
    # def get_opacity(self):
    #     return self.proxy.opacity()

    # def set_opacity(self, value):
    #     self.proxy.setOpacity(value)

    # opacity = pyqtProperty(float, get_opacity, set_opacity)

    # def get_scale(self):
    #     return self.proxy.scale()

    # def set_scale(self, value):
    #     self.proxy.setScale(value)

    # scale = pyqtProperty(float, get_scale, set_scale)
    
    # def start_animations(self):
    #     # Reset and start animations
    #     self.opacity_anim.setStartValue(0.0)
    #     self.opacity_anim.setEndValue(1.0)
    #     self.scale_anim.setStartValue(1.05)
    #     self.scale_anim.setEndValue(1.0)

    #     self.opacity_anim.start()
    #     self.scale_anim.start()
        
    def rotate(self, angle: float):
        self.proxy.setRotation(angle)

    def drawForeground(self, painter: QPainter, rect):
        """
        Optionally draw a circle border for debugging purposes.
        """
        if self.draw_border:
            painter.save()
            painter.resetTransform()  # Draw in view coordinates.
            painter.setPen(QPen(self.border_color, 1))
            diameter = int(min(self.width(), self.height()))
            x = int((self.width() - diameter) / 2)
            y = int((self.height() - diameter) / 2)
            painter.drawEllipse(x, y, diameter, diameter)
            painter.drawRect(x, y, diameter, diameter)
            painter.restore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        size = min(self.width(), self.height())
        design_size = 300
        scale_factor = size / design_size
        self.resetTransform()
        self.scale(scale_factor, scale_factor)
        self.setSceneRect(0, 0, design_size, design_size)
        self.proxy.widget().setFixedSize(design_size, design_size)
