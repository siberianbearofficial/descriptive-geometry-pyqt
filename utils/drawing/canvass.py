from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QWidget

from core.config import CANVASS_Y, CANVASS_X
from utils.color import Color
from utils.drawing import snap
from utils.drawing.drawing_on_plot import Drawer
from utils.drawing.projections.movable_point import ObjectMoveManager
from utils.drawing.projections.screen_point import ScreenPoint
from utils.drawing.projections.screen_segment import ScreenSegment
from utils.objects.general_object import GeneralObject
from utils.objects.object_manager import ObjectManager


class Canvass(QWidget):
    def __init__(self, theme_manager, object_manager: ObjectManager):
        super().__init__()
        self.theme_manager = theme_manager
        self.object_manager = object_manager
        self.painter = QPainter()
        self.drawer = None
        self.object_mover = None

        self.bg_color = ''
        self.default_color = ''
        self.draw_color = ''
        self.cl_color = ''

        self.scale = 1
        self.thickness_scale = 1
        self.set_scale()

        self.axis = [ScreenSegment(ScreenPoint(0, CANVASS_Y // 2),
                                   ScreenPoint(CANVASS_X, CANVASS_Y // 2)),
                     ScreenSegment(ScreenPoint(CANVASS_X // 2, CANVASS_Y // 2 - 10),
                                   ScreenPoint(CANVASS_X // 2, CANVASS_Y // 2 + 10))]
        self.temp_objects = []
        self.hover_objects = []

        self.object_manager.objectAdded.connect(self.full_update)
        self.object_manager.objectSelected.connect(self._on_object_selected)
        self.object_manager.objectDeleted.connect(self.full_update)
        self.object_manager.objectColorChanged.connect(self.full_update)
        self.object_manager.layerDeleted.connect(self.full_update)
        self.object_manager.layerColorChanged.connect(self.full_update)
        self.object_manager.layerHiddenChanged.connect(self.full_update)
        self.object_manager.objectAgChanged.connect(self.full_update)
        
    def set_scale(self, scale=1):
        self.scale = scale
        self.setFixedSize(int(CANVASS_X * scale), int(CANVASS_Y * scale))
        self.update()

    def draw_segment(self, p1, p2, color=None, thickness=1, line_type=Qt.PenStyle.SolidLine):
        if color is None:
            color = self.default_color
        self.set_pen(color, thickness * self.thickness_scale, line_type)
        self.painter.drawLine(int(p1.x * self.scale), int(p1.y * self.scale),
                              int(p2.x * self.scale), int(p2.y * self.scale))

    def draw_text(self, pos, text):
        self.painter.drawText(int(pos[0] * self.scale), int(pos[1] * self.scale), text)

    def draw_point(self, point, color=None, thickness=1):
        if color is None:
            color = self.default_color
        thickness *= self.thickness_scale
        self.set_pen(color, thickness)
        brush = self.painter.brush()
        self.painter.setBrush(Color(self.bg_color))
        self.painter.drawEllipse(
            int(point[0] * self.scale - 1 * thickness), int(point[1] * self.scale - 1 * thickness),
            int(2 * thickness), int(2 * thickness))
        self.painter.setBrush(brush)

    def draw_object(self, obj, hover=False, selected=False, color=None):
        if isinstance(obj, ScreenPoint):
            self.draw_point((obj.x, obj.y), obj.color if color is None else color, obj.thickness + (2 if hover or selected else 0))
        elif isinstance(obj, ScreenSegment):
            self.draw_segment(obj.p1, obj.p2, obj.color if color is None else color,
                              obj.thickness + (2 if hover or selected else 0), obj.line_type)
        else:
            if not isinstance(obj, GeneralObject):
                obj = GeneralObject(obj, None)
                color = self.draw_color
            else:
                color = self.object_manager.get_object_color(obj.id)
            for el in obj.xy_projections:
                self.draw_object(el, color=color, hover=hover, selected=selected)
            for el in obj.xz_projections:
                self.draw_object(el, color=color, hover=hover, selected=selected)
            for el in obj.connection_lines:
                self.draw_object(el, hover=False, selected=False, color=self.cl_color)
            
    def paintEvent(self, a0) -> None:
        self.painter.begin(self)

        for el in self.axis:
            self.draw_object(el)
        for el in self.object_manager.get_all_objects():
            self.draw_object(el)
        for el in self.temp_objects:
            self.draw_object(el)
        for el in self.hover_objects:
            self.draw_object(el, hover=True)
        # if self.object_manager.selected_object is not None:
        #     self.draw_object(self.object_manager.get_object(self.object_manager.selected_object), selected=True)
        if self.object_mover is not None:
            for point in self.object_mover.points:
                self.draw_object(point.point)

        # self.set_pen(BLACK_COLOR, 4)
        # self.lm.draw()
        self.painter.end()

    def set_pen(self, color, thickness, line_type=Qt.PenStyle.SolidLine):
        pen = QPen()
        pen.setColor(QColor(color))
        pen.setWidth(thickness)
        pen.setStyle(line_type)
        self.painter.setPen(pen)

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Escape:
            if self.drawer:
                self.drawer.esc()
        elif a0.key() == Qt.Key.Key_Return:
            if self.drawer:
                self.drawer.enter()

    def mousePressEvent(self, a0) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            if self.drawer:
                self.drawer.mouse_left(a0.pos() / self.scale)
            elif self.object_mover and self.object_mover.mouse_left(a0.pos() / self.scale, self.scale):
                pass
            else:
                obj = self.object_by_pos((a0.pos().x() / self.scale, a0.pos().y() / self.scale))
                self.object_manager.select_object(None if obj is None else obj.id)
        elif a0.button() == Qt.MouseButton.RightButton:
            if self.drawer:
                self.drawer.mouse_right(a0.pos() / self.scale)
            super().mousePressEvent(a0)
        else:
            super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0) -> None:
        if self.drawer:
            self.drawer.mouse_move(a0.pos() / self.scale)
        elif self.object_mover:
            self.object_mover.mouse_move(a0.pos() / self.scale)
        super().mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0) -> None:
        if self.object_mover:
            self.object_mover.mouse_left_release()
        super().mouseReleaseEvent(a0)

    def start_drawing(self, object_type):
        self.setMouseTracking(True)
        self.drawer = Drawer(self, object_type)
        self.drawer.finished.connect(self.end_drawing)
        self.drawer.start()

    def end_drawing(self):
        if isinstance(self.drawer, Drawer):
            if self.drawer.result is not None:
                self.object_manager.new_object(self.drawer.result)
            else:
                self.set_temp_objects()
        self.drawer = None
        self.setMouseTracking(False)
        self.update()

    def object_by_pos(self, pos):
        pos = ScreenPoint(*pos)
        for obj in self.object_manager.get_all_objects():
            for el in obj.xy_projections + obj.xz_projections:
                if isinstance(el, ScreenPoint) and el.distance(pos) <= 7 / self.scale:
                    return obj
                if isinstance(el, ScreenSegment) and el.distance(pos) <= 3 / self.scale:
                    return obj
        return None

    def _on_object_selected(self, obj_id):
        if obj_id is None:
            self.object_mover = None
        else:
            self.object_mover = ObjectMoveManager(self, self.object_manager.get_object(obj_id))
        self.full_update()

    def full_update(self):
        self.temp_objects = tuple()
        self.hover_objects = tuple()
        self.update()

    def set_temp_objects(self, *objects):
        self.hover_objects = tuple()
        self.temp_objects = objects
        self.update()

    def set_hover_objects(self, *objects):
        self.temp_objects = tuple()
        self.hover_objects = objects
        self.update()
        
    def set_styles(self):
        self.bg_color = self.theme_manager['BgColor']
        self.default_color = self.theme_manager['TextColor']
        self.draw_color = Color(self.theme_manager['DrawColor'])
        self.cl_color = Color(self.theme_manager['CLColor'])
        self.update()

