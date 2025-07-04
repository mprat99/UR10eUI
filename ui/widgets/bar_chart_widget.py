from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QSizePolicy
)
from PyQt6.QtGui import (
    QFont, QColor, QLinearGradient, QBrush
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, pyqtProperty, QObject, QPointF, QEasingCurve
)
from config.settings import GREEN_COLOR, YELLOW_COLOR, RED_COLOR
import random
import utils.utils as utils

class BarData:
    def __init__(self, label: str, value: float, formatted: str, color: QColor):
        self.label = label
        self.value = value
        self.formatted = formatted
        self.color = color


class AnimatedBar(QObject):
    """
    This class wraps a QGraphicsRectItem and exposes a property 'value' that, when updated,
    adjusts the width of the rectangle.
    """
    def __init__(self, rect_item: QGraphicsRectItem):
        super().__init__()
        self._value = 0
        self.rect_item = rect_item

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value
        rect = self.rect_item.rect()
        self.rect_item.setRect(rect.x(), rect.y(), value, rect.height())

    value = pyqtProperty(float, get_value, set_value)

    def get_current_width(self):
        return self.rect_item.rect().width()


class AnimatedTextItem(QObject):
    """
    Wraps a QGraphicsTextItem to animate its position.
    """
    def __init__(self, text_item):
        super().__init__()
        self.text_item = text_item

    def get_pos(self):
        return self.text_item.pos()

    def set_pos(self, pos):
        self.text_item.setPos(pos)

    pos = pyqtProperty(QPointF, get_pos, set_pos)


class BarChartView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background: transparent; border: 0px;")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.design_size = 300
        self.scene.setSceneRect(0, 0, self.design_size, self.design_size)

        self.stat_metric = "Avg. Speed"
        self.stat_value = "0"
        self.stat_units = "pick/min"

        self.chart_units = "min"
        self.default_colors = [QColor(GREEN_COLOR), QColor(YELLOW_COLOR), QColor(RED_COLOR)]

        self.bar_data = []         # Raw data received (list of dicts with keys 'label' and 'value')
        self.bar_display_data = [] # List[BarData]
        self.bar_items = []        # Visual items: tuple(AnimatedBar, target_value, label_item, formatted_value_item)

        self.title_item = None
        self.subtitle_item = None

        self.bar_max_width = self.design_size * 0.55
        self.bar_height = 20
        self.bar_x_offset = self.design_size / 2 - self.bar_max_width / 2 - 20
        self.y_start = self.design_size / 2 - 50
        self.spacing = 50

        sample_data = {
            "chart": {
                "units": "sec",
                "bars": [
                    {"label": "Max. Speed", "value": 1},
                    {"label": "Reduced Speed", "value": 0},
                    {"label": "Stopped", "value": 0}
                ]
            },
            "statMetric": "Total Time",
            "statValue": "1s",
            "statUnits": ""
        }
        self.receive_data(sample_data)
        QTimer.singleShot(200, self._animate_bars)


    def receive_data(self, data: dict):
        """
        Update statistics and bar data from incoming data.
        """
        self.stat_metric = data.get("statMetric", self.stat_metric)
        self.stat_value = data.get("statValue", self.stat_value)
        self.stat_units = data.get("statUnits", self.stat_units)

        if "chart" in data:
            chart = data["chart"]
            self.chart_units = chart.get("units", self.chart_units)
            if "bars" in chart:
                self.bar_data = [{"label": bar.get("label", ""), "value": bar.get("value", 0)} for bar in chart["bars"]]
        self._create_title()
        self._format_bars_data()

    def _create_title(self):
        """
        Create or update title and subtitle based on stat_metric, stat_value, and stat_units.
        """
        title_text = self.stat_metric
        subtitle_text = f"{self.stat_value} {self.stat_units}"

        if not self.title_item:
            self.title_item = self.scene.addText(title_text, QFont("DM Sans", 18, QFont.Weight.Bold))
            self.title_item.setDefaultTextColor(Qt.GlobalColor.white)
        else:
            self.title_item.setPlainText(title_text)
        title_rect = self.title_item.boundingRect()
        self.title_item.setPos(self.design_size / 2 - title_rect.width() / 2, 20)

        if not self.subtitle_item:
            self.subtitle_item = self.scene.addText(subtitle_text, QFont("DM Sans", 16, QFont.Weight.Normal))
            self.subtitle_item.setDefaultTextColor(Qt.GlobalColor.white)
        else:
            self.subtitle_item.setPlainText(subtitle_text)
        subtitle_rect = self.subtitle_item.boundingRect()
        self.subtitle_item.setPos(self.design_size / 2 - subtitle_rect.width() / 2, 50)

    def _format_bars_data(self):
        """
        Process raw bar data into BarData objects with formatted values and assigned colors.
        """
        new_display_data = []
        for i, bar in enumerate(self.bar_data):
            label = bar["label"]
            value = bar["value"]
            if self.chart_units == "min":
                formatted_value = utils.format_time(value)
            elif self.chart_units == "sec":
                formatted_value = utils.format_time_sec(value)
            else:
                formatted_value = f"{value} {self.chart_units}"
            color = self.default_colors[i] if i < len(self.default_colors) else QColor(
                random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            new_display_data.append(BarData(label, value, formatted_value, color))

        if len(new_display_data) != len(self.bar_display_data) or any(
            new_display_data[i].label != self.bar_display_data[i].label for i in range(len(new_display_data))
        ):
            self.bar_display_data = new_display_data
            self._create_bars()
            QTimer.singleShot(50, self._animate_bars)
        else:
            self.bar_display_data = new_display_data
            QTimer.singleShot(50, self._animate_bars)
            for i, (animated_bar, target_value, label_item, formatted_value_item) in enumerate(self.bar_items):
                _, new_value, new_formatted, _ = new_display_data[i].__dict__.values()
                self.bar_items[i] = (animated_bar, new_value, label_item, formatted_value_item)
                formatted_value_item.setPlainText(new_formatted)

    def _create_bars(self):
        """
        Remove old bar items and create new ones based on the processed display data.
        """
        for animated_bar, _, label_item, formatted_value_item in self.bar_items:
            self.scene.removeItem(animated_bar.rect_item)
            self.scene.removeItem(label_item)
            self.scene.removeItem(formatted_value_item)
        self.bar_items.clear()

        for i, bar in enumerate(self.bar_display_data):
            y = self.y_start + 20 + i * self.spacing

            gradient = QLinearGradient(0, 0, self.bar_max_width, 0)
            darker_color = bar.color.darker(200)
            gradient.setColorAt(0, darker_color)
            gradient.setColorAt(1, bar.color)

            rect_item = QGraphicsRectItem(self.bar_x_offset, y, 0, self.bar_height)
            rect_item.setBrush(QBrush(gradient))
            rect_item.setPen(Qt.GlobalColor.transparent)
            self.scene.addItem(rect_item)

            label_item = self.scene.addText(bar.label, QFont("DM Sans", 12))
            label_item.setDefaultTextColor(Qt.GlobalColor.white)
            label_item.setPos(self.bar_x_offset - 4, y - 25)

            formatted_value_item = self.scene.addText(bar.formatted, QFont("DM Sans", 10))
            formatted_value_item.setDefaultTextColor(Qt.GlobalColor.white)
            formatted_value_item.setPos(self.bar_x_offset + 5, y - self.bar_height / 8)

            animated_bar = AnimatedBar(rect_item)
            self.bar_items.append((animated_bar, bar.value, label_item, formatted_value_item))

    def _animate_bars(self):
        """
        Animate each bar's width and reposition the formatted value text accordingly.
        """
        if not self.bar_items:
            return
        max_value = max(value for _, value, _, _ in self.bar_items)
        for i, (animated_bar, value, _, formatted_value_item) in enumerate(self.bar_items):
            y = self.y_start + 20 + i * self.spacing
            target_width = (value / max_value) * self.bar_max_width

            anim = QPropertyAnimation(animated_bar, b"value")
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setDuration(1000)
            anim.setStartValue(animated_bar.get_value())
            anim.setEndValue(target_width)
            anim.start()

            animated_text = AnimatedTextItem(formatted_value_item)
            anim_text = QPropertyAnimation(animated_text, b"pos")
            anim_text.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim_text.setDuration(1000)
            start_pos = animated_text.get_pos()
            end_pos = QPointF(self.bar_x_offset + target_width + 5, y - self.bar_height / 8)
            anim_text.setStartValue(start_pos)
            anim_text.setEndValue(end_pos)
            anim_text.start()

            animated_bar.animation = anim
            animated_text.animation = anim_text

