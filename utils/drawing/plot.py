from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QPointF
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QApplication, QScrollArea

import utils.drawing.drawing_on_plot as drw
import utils.drawing.names as names
import utils.drawing.snap as snap
from core.config import CANVASS_X, CANVASS_Y
from utils.color import *
from utils.drawing.canvass import Canvass
from utils.drawing.label_manager import LabelManager
from utils.drawing.projections.projection_manager import ScreenPoint, ThinScreenPoint
from utils.drawing.projections.projection_manager import ScreenSegment
from utils.objects.general_object import GeneralObject
from utils.objects.object_manager import ObjectManager

drawing_functions = {
    'point': drw.create_point, 'segment': drw.create_segment, 'line': drw.create_line, 'plane': drw.create_plane,
    'perpendicular_segment': drw.create_perpendicular_segment, 'parallel_segment': drw.create_parallel_segment,
    'perpendicular_line': drw.create_perpendicular_line, 'parallel_line': drw.create_parallel_line,
    'plane_3p': drw.create_plane_3p, 'parallel_plane': drw.create_parallel_plane,
    'horizontal': drw.create_horizontal, 'frontal': drw.create_frontal,
    'distance': drw.get_distance, 'angle': drw.get_angle, 'circle': drw.create_circle, 'sphere': drw.create_sphere,
    'cylinder': drw.create_cylinder, 'cone': drw.create_cone, 'tor': drw.create_point, 'spline': drw.create_spline,
    'rotation_surface': drw.create_rotation_surface, 'intersection': drw.get_intersection}


class Plot(QScrollArea):
    objectSelected = pyqtSignal(object)
    printToCommandLine = pyqtSignal(str)
    layersModified = pyqtSignal(object, int)
    setCmdStatus = pyqtSignal(bool)
    ZOOMS = [0.1, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 3.5, 4, 5]

    def __init__(self, theme_manager, object_manager: ObjectManager):
        super().__init__()
        self.object_manager = object_manager
        self.theme_manager = theme_manager
        self.painter = QPainter()

        self.objects = []
        self.selected_object_index = 0

        self.lm = LabelManager(self)

        self.moving_camera = False
        self.mouse_pos = 0, 0
        self.zoom = 4

        self.cmd_command = None

        self.canvass = Canvass(self.theme_manager, self.object_manager)
        self.setWidget(self.canvass)
        self.setWidgetResizable(True)
        
    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self.move_camera(-(CANVASS_X - self.width()) / 2, -(CANVASS_Y - self.height()) / 2)

    def draw(self, figure):
        self.canvass.start_drawing(figure)

    def move_camera(self, x, y, update=True):
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(x))
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(y))

    def add_object(self, ag_object, name=None, color=None, end=False, **config):
        if color is None:
            color = Color.random()
        # if name is None:
        #     name = names.generate_name(self, ag_object, config)
        self.object_manager.add_object(ag_object, name, color, history_record=True, **config)
        # self.canvass.sm.update_intersections()
        self.update()
        if end:
            self.end()

    def mousePressEvent(self, a0) -> None:
        if a0.button() in (Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton):
            self.mouse_pos = a0.pos().x(), a0.pos().y()
            self.moving_camera = True

    def mouseReleaseEvent(self, a0) -> None:
        if a0.button() in (Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton):
            self.moving_camera = False

    def mouseMoveEvent(self, a0) -> None:
        if self.moving_camera:
            self.move_camera(a0.pos().x() - self.mouse_pos[0], a0.pos().y() - self.mouse_pos[1])
            self.mouse_pos = a0.pos().x(), a0.pos().y()

    def wheelEvent(self, a0) -> None:
        self.set_zoom(self.zoom + a0.angleDelta().y() // 120, a0.position())

    def set_selected_object(self, obj):
        if obj:
            self.selected_object_index = obj.id
            self.selected_object = self.find_by_id(obj.id)
        else:
            self.selected_object_index = 0
            self.selected_object = None
        self.update()

    def find_by_id(self, id):
        for obj in self.objects:
            if obj.id == id:
                return obj
        raise IndexError(f"Object {id} not found")

    def set_zoom(self, zoom, pos=None):
        old_zoom = Plot.ZOOMS[self.zoom]
        self.zoom = max(0, min(len(Plot.ZOOMS) - 1, zoom))
        new_zoom = Plot.ZOOMS[self.zoom]

        if isinstance(pos, QPointF):
            canvass_x = (self.horizontalScrollBar().value() + pos.x()) / old_zoom
            canvass_y = (self.verticalScrollBar().value() + pos.y()) / old_zoom
            self.canvass.set_scale(new_zoom)
            self.horizontalScrollBar().setValue(int(canvass_x * new_zoom - pos.x()))
            self.verticalScrollBar().setValue(int(canvass_y * new_zoom - pos.y()))
        else:
            self.canvass.set_scale(new_zoom)

    def end(self):
        self.setMouseTracking(False)
        self.cmd_command = None
        self.setCmdStatus.emit(False)
        self.update()

    def print(self, s):
        self.printToCommandLine.emit(s)
        print(s)

    def set_styles(self):
        self.theme_manager.auto_css(self, border=False, border_radius=False)
        self.canvass.set_styles()


def main():
    app = QApplication([])
    plot = Plot(None)
    plot.show()
    app.exec()


if __name__ == '__main__':
    main()
