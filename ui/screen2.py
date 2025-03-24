from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QSizePolicy, QGraphicsProxyWidget
)
from PyQt6.QtGui import (
    QFont, QColor, QLinearGradient, QBrush, QPen, QPainter, QTransform
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, pyqtProperty, QObject, QPointF, QEasingCurve
)


# ----------------- Bar Chart & Animation -----------------
class AnimatedBar(QObject):
    def __init__(self, rect_item):
        super().__init__()
        self._value = 0
        self.rect_item = rect_item

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value
        rect = self.rect_item.rect()
        self.rect_item.setRect(rect.x(), rect.y(), value, rect.height())

    value = pyqtProperty(float, getValue, setValue)

    def getCurrentWidth(self):
        return self.rect_item.rect().width()


class AnimatedTextItem(QObject):
    def __init__(self, text_item):
        super().__init__()
        self.text_item = text_item

    def getPos(self):
        return self.text_item.pos()

    def setPos(self, pos):
        self.text_item.setPos(pos)

    pos = pyqtProperty(QPointF, getPos, setPos)


class BarChartView(QGraphicsView):
    def __init__(self):
        super().__init__()
        # Allow the layout to expand this widget.
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background: transparent; border: 0px;")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Use a fixed design canvas (300x300) for laying out items.
        self.design_size = 300
        self.scene.setSceneRect(0, 0, self.design_size, self.design_size)

        self._create_title()

        # Layout parameters relative to design_size.
        self.bar_max_width = self.design_size * 0.6
        self.bar_height = 20
        self.bar_x_offset = self.design_size / 2 - self.bar_max_width / 2 - 20
        self.y_start = self.design_size / 2 - 50
        self.spacing = 50

        self.data = [
            ("Max. Speed", QColor("#00ff00"), 100, "1h 20 min"),
            ("Reduced Speed", QColor("#ffff00"), 100, "15 min"),
            ("Stopped", QColor("#ff0000"), 1, "5 min"),
        ]
        self.animated_bars = []
        self._create_bars()

        # Start animation after a short delay.
        QTimer.singleShot(200, self.animate_bars)

    def _create_title(self):
        title_text = "Avg. Speed"
        subtitle_text = "35 pick/min"

        title_item = self.scene.addText(title_text, QFont("DM Sans", 18, QFont.Weight.Bold))
        title_item.setDefaultTextColor(Qt.GlobalColor.white)
        title_rect = title_item.boundingRect()
        title_item.setPos(self.design_size / 2 - title_rect.width() / 2, 20)

        subtitle_item = self.scene.addText(subtitle_text, QFont("DM Sans", 18, QFont.Weight.Normal))
        subtitle_item.setDefaultTextColor(Qt.GlobalColor.white)
        subtitle_rect = subtitle_item.boundingRect()
        subtitle_item.setPos(self.design_size / 2 - subtitle_rect.width() / 2, 50)

    def _create_bars(self):
        for i, (label_text, base_color, value, time_text) in enumerate(self.data):
            y = self.y_start + 20 + i * self.spacing

            gradient = QLinearGradient(0, 0, self.bar_max_width, 0)
            darker_color = base_color.darker(200)
            gradient.setColorAt(0, darker_color)
            gradient.setColorAt(1, base_color)

            bar_item = QGraphicsRectItem(self.bar_x_offset, y, 0, self.bar_height)
            bar_item.setBrush(QBrush(gradient))
            bar_item.setPen(Qt.GlobalColor.transparent)
            self.scene.addItem(bar_item)

            label_item = self.scene.addText(label_text, QFont("DM Sans", 12))
            label_item.setDefaultTextColor(Qt.GlobalColor.white)
            label_item.setPos(self.bar_x_offset - 4, y - 25)

            time_item = self.scene.addText(time_text, QFont("DM Sans", 10))
            time_item.setDefaultTextColor(Qt.GlobalColor.white)

            animated_bar = AnimatedBar(bar_item)
            self.animated_bars.append((animated_bar, value, label_item, time_item))

        # For demonstration, update the data after 5 seconds.
        self.data = [
            ("Max. Speed", QColor("#00ff00"), 50, "1h"),
            ("Reduced Speed", QColor("#ffff00"), 5, "315 min"),
            ("Stopped", QColor("#ff0000"), 1, "25 min"),
        ]
        QTimer.singleShot(5000, self.animate_bars)

    def animate_bars(self):
        if not self.animated_bars:
            return
        max_value = max(value for _, value, _, _ in self.animated_bars)
        for i, (animated_bar, value, label_item, time_item) in enumerate(self.animated_bars):
            y = self.y_start + 20 + i * self.spacing
            target_width = (value / max_value) * self.bar_max_width

            anim = QPropertyAnimation(animated_bar, b"value")
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setDuration(1000)
            anim.setStartValue(0)
            anim.setEndValue(target_width)
            anim.start()

            animated_time_item = AnimatedTextItem(time_item)
            anim_time_item = QPropertyAnimation(animated_time_item, b"pos")
            anim_time_item.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim_time_item.setDuration(1000)
            start_pos = QPointF(self.bar_x_offset, y - self.bar_height / 8)
            end_pos = QPointF(self.bar_x_offset + target_width + 5, y - self.bar_height / 8)
            anim_time_item.setStartValue(start_pos)
            anim_time_item.setEndValue(end_pos)
            anim_time_item.start()

            # Keep references to avoid garbage collection.
            animated_bar.animation = anim
            animated_time_item.animation = anim_time_item

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Scale the fixed design canvas (300x300) to fill the available space.
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


# ----------------- Circle Container -----------------
class CircleContainer(QWidget):
    """
    A container that reserves a circular area with diameter = min(width, height),
    centers its single child widget in that circle, and draws a debug circular border.
    """
    def __init__(self, child_widget: QWidget, debug_border_color=QColor("red")):
        super().__init__()
        self.setStyleSheet("background: transparent; border: 0px;")
        self.child = child_widget
        self.debug_border_color = debug_border_color
        self.child.setParent(self)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.child)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        diameter = min(self.width(), self.height())
        self.child.setFixedSize(diameter, diameter)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        diameter = min(self.width(), self.height())
        painter = QPainter(self)
        pen = QPen(self.debug_border_color)
        pen.setWidth(2)
        painter.setPen(pen)
        # Center the circle in the container.
        x = int((self.width() - diameter) / 2)
        y = int((self.height() - diameter) / 2)
        painter.drawEllipse(x, y, int(diameter), int(diameter))


# ----------------- Rotatable Container -----------------
class RotatableContainer(QGraphicsView):
    """
    A container that wraps a widget in a QGraphicsProxyWidget so it can be rotated.
    Rotation is controlled via a QTimer.
    """
    def __init__(self, widget: QWidget, rotation: float = 0):
        super().__init__()
        self.setStyleSheet("background: transparent; border: 0px;")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.proxy = QGraphicsProxyWidget()
        self.proxy.setWidget(widget)
        # Set the transform origin to the center of the proxy.
        self.proxy.setTransformOriginPoint(self.proxy.boundingRect().center())
        self.proxy.setRotation(rotation)
        self.scene.addItem(self.proxy)

    def rotate(self, angle: float):
        self.proxy.setRotation(angle)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Disable scroll bars so that the view does not introduce them.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Calculate the new square size from the available width and height.
        size = min(self.width(), self.height())
        
        # Define your fixed design canvas size (e.g., 300, as used in BarChartView)
        design_size = 300
        
        # Compute the scale factor.
        scale_factor = size / design_size
        
        # Reset any previous transformation.
        self.resetTransform()
        # Apply the new scaling.
        self.scale(scale_factor, scale_factor)
        
        # Update the scene rect so that it matches the fixed design size.
        self.setSceneRect(0, 0, design_size, design_size)




# ----------------- Screen -----------------
class Screen2(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create the bar chart view.
        self.chart_view = BarChartView()
        # Wrap the bar chart view in a circle container.
        self.circle_container = CircleContainer(self.chart_view)
        # Wrap the circle container in a rotatable container.
        self.rot_container = RotatableContainer(self.circle_container)

        layout.addWidget(self.rot_container)

        # Use a QTimer to rotate the container continuously.
        self.rotation_angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rotation)
        self.timer.start(50)  # Adjust the speed (ms).

    def update_rotation(self):
        self.rotation_angle = (self.rotation_angle + 2) % 360
        self.rot_container.rotate(self.rotation_angle)
