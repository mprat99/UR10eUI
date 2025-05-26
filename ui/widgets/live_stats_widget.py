from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtSvg import QSvgRenderer 
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtCore import QRectF, QPointF,QPropertyAnimation, pyqtProperty

class LiveStatsWidget(QWidget):

    def __init__(self, svg_path, value_text, label_text, parent=None):
        super().__init__(parent)
        self.svg_renderer = QSvgRenderer(svg_path)
        self._value_text = value_text
        self._label_text = label_text
        self._rotation = 0  
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.rotate_anim = QPropertyAnimation(self, b"rotation")
        self.update()

    def get_rotation(self):
        return self._rotation

    def set_rotation(self, angle):
        """Set the rotation angle and trigger a repaint."""
        self._rotation = angle
        self.update() 

    rotation = pyqtProperty(float, get_rotation, set_rotation)


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
            self.set_rotation(target_rotation)


    def _on_rotation_animation_finished(self):
        self._rotation = self.rotate_anim.currentValue()

    def _animate_rotation(self, start_angle, end_angle):
        """Helper function to animate the rotation of this widget."""
        self.rotate_anim.setStartValue(start_angle)
        self.rotate_anim.setEndValue(end_angle)
        self.rotate_anim.start()

    def set_value(self, value):
        """Update the numeric value and repaint."""
        self._value_text = str(value) 
        self.update()

    def set_label(self, label):
        """Update the label text and repaint."""
        self._label_text = label
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self._rotation)
        painter.translate(-self.width() / 2, -self.height() / 2)

        widget_width = self.width()
        widget_height = self.height()

        svg_size = self.svg_renderer.defaultSize()
        svg_aspect_ratio = svg_size.width() / svg_size.height()

        if widget_width / widget_height > svg_aspect_ratio:
            svg_height = widget_height * 0.9 
            svg_width = svg_height * svg_aspect_ratio
        else:
            svg_width = widget_width * 0.9
            svg_height = svg_width / svg_aspect_ratio

        svg_x = (widget_width - svg_width) / 2
        svg_y = (widget_height - svg_height) * 0.2 
        svg_rect = QRectF(svg_x, svg_y, svg_width, svg_height)
        self.svg_renderer.render(painter, svg_rect)

        value_font_size = svg_height * 0.15
        value_font = QFont()
        value_font.setFamily("DM Sans")
        value_font.setPointSizeF(value_font_size)
        painter.setFont(value_font)
        painter.setPen(Qt.GlobalColor.white)

        value_bounds = QRectF(svg_rect)
        value_bounds.moveCenter(QPointF(svg_rect.center().x(), svg_rect.center().y() + svg_height * 0.09))
        painter.drawText(value_bounds, Qt.AlignmentFlag.AlignCenter, self._value_text)

        label_font_size = svg_height * 0.1
        label_font = QFont()
        label_font.setFamily("DM Sans")
        label_font.setPointSizeF(label_font_size)
        painter.setFont(label_font)

        label_bounds = QRectF(svg_rect)
        label_bounds = label_bounds.adjusted(0, svg_height * 0.23, 0, svg_height * 0.58) 
        painter.drawText(label_bounds, Qt.AlignmentFlag.AlignCenter, self._label_text)
