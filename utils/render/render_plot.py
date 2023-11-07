from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QFont

from utils.drawing.plot import Plot
from utils.render.render_label import RenderLabel
from utils.drawing.projections.plot_object import PlotObject

from utils.color import *


class RenderPlot(Plot):
    def __init__(self, width, height, parent=None):
        super(RenderPlot, self).__init__(parent)
        self.main_color = Color(120, 90, 80)
        self.setFixedSize(width, height)
        self.draw_mode = 0
        self.zoom = 3
        self.pm.zoom = 3
        self.mode = 1
        self.labels = []

    def draw_point(self, point, color=Color(0, 0, 0), thickness=1):
        self.set_pen(color, thickness * self.scale2)
        if self.mode == 0:
            super(RenderPlot, self).draw_point(point, color=self.main_color, thickness=thickness)
        else:
            self.set_pen(self.main_color, thickness * self.scale2)
            brush = self.painter.brush()
            self.painter.setBrush(self.main_color)
            self.painter.drawEllipse(
                int(point[0] * self.scale1 - 3 * self.scale2), int(point[1] * self.scale1 - 3 * self.scale2),
                6 * self.scale2, 6 * self.scale2)
            self.painter.setBrush(brush)
        
    def draw_point2(self, point, color=Color(0, 0, 0), thickness=1):
        super(RenderPlot, self).draw_point2(point, self.main_color, thickness)
        
    def draw_segment(self, p1, p2, color=Color(0, 0, 0), thickness=1, line_type=1):
        super(RenderPlot, self).draw_segment(p1, p2, self.main_color, thickness, line_type)
        
    def draw_circle(self, center, radius, color=Color(0, 0, 0), thickness=2):
        super(RenderPlot, self).draw_circle(center, radius, self.main_color, thickness)

    def paintEvent(self, e):
        self.painter.begin(self)

        self.axis.draw()
        for obj in self.objects:
            obj.draw()
        for obj in self.extra_objects:
            if isinstance(obj, PlotObject):
                obj.draw(selected=self.selected_mode)
            else:
                obj.draw()
        if self.selected_object_index:
            self.selected_object.draw(selected=1)

        self.set_pen(Color(0, 0, 0), 4)
        for label in self.labels:
            label.draw()
        self.painter.end()

    def update_plot_objects(self, object_list):
        super(RenderPlot, self).update_plot_objects(object_list)
        self.labels = [RenderLabel(self, label.text, [label.x + self.lm.pos[0], label.y + self.lm.pos[1]])
                       for label in self.lm.labels.values()]

    def set_zoom(self, zoom, pos=None):
        super(RenderPlot, self).set_zoom(zoom, pos)

    def reset_labels(self):
        self.labels = [RenderLabel(self, label.text, [label.x + self.lm.pos[0], label.y + self.lm.pos[1]])
                       for label in self.lm.labels.values()]
        self.update()


class ChooseAreaPlot(RenderPlot):
    def wheelEvent(self, a0) -> None:
        pass

    def move_camera(self, x, y, update=True):
        for label in self.labels:
            label.move(x, y)
        super(RenderPlot, self).move_camera(x, y, update)


class FinalEditPlot(RenderPlot):
    def move_camera(self, x, y, update=True):
        pass

    def save_image(self, path, scale1, scale2):
        image = QImage(int(self.width() * scale1), int(self.height() * scale1), QImage.Format_RGB32)
        image.fill(Qt.white)
        self.scale1 = scale1
        self.scale2 = scale2
        self.painter.begin(image)
        self.painter.setRenderHint(QPainter.Antialiasing)
        self.axis.draw()
        for obj in self.objects:
            obj.draw()
        font = QFont('Arial', int(14 * scale2))    # TODO: connect font manager + ISOCPEUR font
        self.painter.setFont(font)
        for label in self.labels:
            label.draw()
        self.painter.end()
        self.scale1 = 1
        self.scale2 = 1
        image.save(path, 'PNG')
