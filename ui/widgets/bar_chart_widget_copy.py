from PyQt6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QSizePolicy, QGraphicsProxyWidget
)
from PyQt6.QtGui import (
    QFont, QColor, QLinearGradient, QBrush, QPen, QPainter, QTransform
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, pyqtProperty, QObject, QPointF, QEasingCurve
)
from config.settings import GREEN_COLOR, YELLOW_COLOR, RED_COLOR, BLUE_COLOR

import random


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
        self.statMetric = "Avg. Speed"
        self.statValue = "0"
        self.statUnits = "pick/min"
        self.chart_units = "min"
        self.bars = []
        self.data = [
            ("Max. Speed", 100, "1h 20 min", QColor(GREEN_COLOR)),
            ("Reduced Speed", 100, "15 min", QColor(YELLOW_COLOR)),
            ("Stopped", 1, "5 min", QColor(RED_COLOR)),
        ]
        self.animated_bars = []
        self.title_item = None
        self.subtitle_item = None
        self.colors = [QColor(GREEN_COLOR), QColor(YELLOW_COLOR), QColor(RED_COLOR)]  
        # self._create_title()

        # Layout parameters relative to design_size.
        self.bar_max_width = self.design_size * 0.55
        self.bar_height = 20
        self.bar_x_offset = self.design_size / 2 - self.bar_max_width / 2 - 20
        self.y_start = self.design_size / 2 - 50
        self.spacing = 50
        data = {"chart": {"units": "min", "bars": [{"label": "Max. Speed", "value": 99}, {"label": "Reduced Speed", "value": 50}, {"label": "Stopped", "value": 2}]}, "statMetric": "Avg. Speed", "statValue": "45", "statUnits": "pick/min"}
        self.receive_data(data)
        # self._create_bars()
        QTimer.singleShot(200, self._animate_bars)
        data = {"chart": {"units": "min", "bars": [{"label": "Max. Speed", "value": 99}, {"label": "Reduced Speed", "value": 50}, {"label": "Stopped", "value": 2}]}, "statMetric": "Avg. Speed", "statValue": "45", "statUnits": "pick/min"}
        # QTimer.singleShot(15000, lambda: self.receive_data(data))

    def receive_data(self, data):
        self.statMetric = data.get("statMetric", self.statMetric)
        self.statValue = data.get("statValue", self.statValue)
        self.statUnits = data.get("statUnits", self.statUnits)

        if "chart" in data:
            chart = data["chart"]
            self.chart_units = chart.get("units", self.chart_units)

            if "bars" in chart:
                self.bars = [{"label": bar.get("label", ""), "value": bar.get("value", 0)} for bar in chart["bars"]]
        self._create_title()
        self.format_bars_data()
        # QTimer.singleShot(100, self._animate_bars)

    def _create_title(self):
        title_text = self.statMetric
        value = self.statValue
        units = self.statUnits
        subtitle_text = f"{value} {units}"

        # Update title item or create new one if it doesn't exist
        if not self.title_item:
            self.title_item = self.scene.addText(title_text, QFont("DM Sans", 18, QFont.Weight.Bold))
            self.title_item.setDefaultTextColor(Qt.GlobalColor.white)
        else:
            self.title_item.setPlainText(title_text)
        title_rect = self.title_item.boundingRect()
        self.title_item.setPos(self.design_size / 2 - title_rect.width() / 2, 20)
            

        # Update subtitle item or create new one if it doesn't exist
        if not self.subtitle_item:
            self.subtitle_item = self.scene.addText(subtitle_text, QFont("DM Sans", 18, QFont.Weight.Normal))
            self.subtitle_item.setDefaultTextColor(Qt.GlobalColor.white)
        else:
            self.subtitle_item.setPlainText(subtitle_text)
        subtitle_rect = self.subtitle_item.boundingRect()
        self.subtitle_item.setPos(self.design_size / 2 - subtitle_rect.width() / 2, 50)

    def format_bars_data(self):
        new_data = []
        
        for i, bar in enumerate(self.bars):
            label = bar["label"]
            value = bar["value"]
            formatted_value = self.format_time(value) if self.chart_units == "min" else f"{value} {self.chart_units}"
            color = self.colors[i] if i < len(self.colors) else QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            new_data.append((label, value, formatted_value, color))

        # Check if the number of bars and labels are the same as in the existing data
        if len(new_data) != len(self.data) or any(new_data[i][0] != self.data[i][0] for i in range(len(new_data))):
            self.data = new_data
            self._create_bars()
            QTimer.singleShot(50, self._animate_bars)
        else:
            self.data = new_data
            QTimer.singleShot(50, self._animate_bars)
            for i, (animated_bar, value, label_item, formatted_value_item) in enumerate(self.animated_bars):
                _, new_value, new_formatted_value, _ = new_data[i]
                self.animated_bars[i] = (animated_bar, new_value, label_item, formatted_value_item)
                formatted_value_item.setPlainText(new_formatted_value)
            


    def _create_bars(self):
        # Clear existing bars (if any)
        for animated_bar, _,  label_item, formatted_value_item in self.animated_bars:
            self.scene.removeItem(animated_bar.rect_item)  # Remove the bar item from the scene
            self.scene.removeItem(label_item)  # Remove the label item from the scene
            self.scene.removeItem(formatted_value_item)  # Remove the formatted value item from the scene

        # Clear the animated bars list
        self.animated_bars.clear()

        for i, (label_text, value, formatted_value, base_color) in enumerate(self.data):
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

            formatted_value_item = self.scene.addText(formatted_value, QFont("DM Sans", 10))
            formatted_value_item.setDefaultTextColor(Qt.GlobalColor.white)
            formatted_value_item.setPos(self.bar_x_offset + 5, y - self.bar_height / 8)

            animated_bar = AnimatedBar(bar_item)
            self.animated_bars.append((animated_bar, value, label_item, formatted_value_item))

    def _animate_bars(self):
        if not self.animated_bars:
            return
        max_value = max(value for _, value, _, _ in self.animated_bars)
        sum_values = sum(value for _, value, _, _ in self.animated_bars)
        for i, (animated_bar, value, _, formatted_value_item) in enumerate(self.animated_bars):
            y = self.y_start + 20 + i * self.spacing
            target_width = (value / max_value) * self.bar_max_width

            anim = QPropertyAnimation(animated_bar, b"value")
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setDuration(1000)
            anim.setStartValue(animated_bar.getValue())
            anim.setEndValue(target_width)
            anim.start()

            animated_formatted_value_item = AnimatedTextItem(formatted_value_item)
            anim_formatted_value_item = QPropertyAnimation(animated_formatted_value_item, b"pos")
            anim_formatted_value_item.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim_formatted_value_item.setDuration(1000)
            start_pos = animated_formatted_value_item.getPos()
            end_pos = QPointF(self.bar_x_offset + target_width + 5, y - self.bar_height / 8)
            anim_formatted_value_item.setStartValue(start_pos)
            anim_formatted_value_item.setEndValue(end_pos)
            anim_formatted_value_item.start()

            # Keep references to avoid garbage collection.
            animated_bar.animation = anim
            animated_formatted_value_item.animation = anim_formatted_value_item

    def format_time(self, minutes):
        if minutes < 60:
            return f"{minutes} min"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_minutes} min"

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Scale the fixed design canvas (300x300) to fill the available space.
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


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
        
        # Ensure the widget is unparented.
        if widget.parent() is not None:
            widget.setParent(None)

        self.proxy = QGraphicsProxyWidget()
        self.proxy.setWidget(widget)
        # Store border settings.
        self.draw_border = draw_border
        self.border_color = border_color
        
        # Set the transform origin to the center of the proxy.
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
        Override drawForeground to draw an optional circle border.
        This is drawn on top of the scene and isn't affected by the scene's transformation.
        """
        if self.draw_border:
            painter.save()
            # Reset transformations so the border is drawn in view coordinates.
            painter.resetTransform()
            painter.setPen(QPen(self.border_color, 1))
            # Use the current widget dimensions for the circle.
            diameter = int(min(self.width(), self.height()))
            x = int((self.width() - diameter) / 2)
            y = int((self.height() - diameter) / 2)
            painter.drawEllipse(x, y, diameter, diameter)
            painter.drawRect(x, y, diameter, diameter)
            painter.restore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Disable scroll bars.
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Calculate the new square size from the available width and height.
        size = min(self.width(), self.height())
        
        # Define your fixed design canvas size.
        design_size = 300
        
        # Compute the scale factor.
        scale_factor = size / design_size
        
        # Reset previous transformation.
        self.resetTransform()
        # Apply the scaling.
        self.scale(scale_factor, scale_factor)
        
        # Update the scene rect to the design size.
        self.setSceneRect(0, 0, design_size, design_size)
        
        # Force the proxy widget's contained widget to fill the scene.
        self.proxy.widget().setFixedSize(design_size, design_size)
        