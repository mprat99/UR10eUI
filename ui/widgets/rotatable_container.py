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