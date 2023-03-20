from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPainter

from utils.drawing.plot import Plot


class RenderPlot(Plot):
    def __init__(self, width, height, parent=None):
        super(RenderPlot, self).__init__(parent)
        self.main_color = (120, 90, 80)
        self.setFixedSize(width, height)
        self.draw_mode = 0
        self.image = QImage(width * 5, height * 5, QImage.Format_RGB32)
        self.zoom = 3
        self.pm.zoom = 3

    def draw_point(self, point, color=(0, 0, 0), thickness=1):
        super(RenderPlot, self).draw_point(point, self.main_color, thickness)
        
    def draw_point2(self, point, color=(0, 0, 0), thickness=1):
        super(RenderPlot, self).draw_point2(point, self.main_color, thickness)
        
    def draw_segment(self, p1, p2, color=(0, 0, 0), thickness=1, line_type=1):
        super(RenderPlot, self).draw_segment(p1, p2, self.main_color, thickness, line_type)
        
    def draw_circle(self, center, radius, color=(0, 0, 0), thickness=2):
        super(RenderPlot, self).draw_circle(center, radius, self.main_color, thickness)

    def wheelEvent(self, a0) -> None:
        pass

    def set_zoom(self, zoom):
        print(zoom)
        self.zoom = zoom
        self.pm.zoom = zoom
        self.camera_pos = [0, 0]
        self.axis.update(self)
        for obj in self.objects:
            obj.update_projections()
        self.update()

    def save_image(self, path):
        self.image.fill(Qt.white)
        self.scale = 5
        self.painter.begin(self.image)
        self.painter.setRenderHint(QPainter.Antialiasing)
        self.axis.draw()
        for obj in self.objects:
            obj.draw()
        self.painter.end()
        self.scale = 1
        self.image.save(path, 'PNG')

