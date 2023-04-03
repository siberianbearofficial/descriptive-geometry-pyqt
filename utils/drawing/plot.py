from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtCore import Qt, pyqtSignal

from utils.drawing.projections.projection_manager import ScreenPoint, ThinScreenPoint
from utils.drawing.projections.projection_manager import ScreenSegment
from utils.drawing.projections.projection_manager import ScreenCircle

from utils.drawing.axis import Axis
from utils.drawing.projections.projection_manager import ProjectionManager
from utils.drawing.label_manager import LabelManager
import utils.drawing.snap as snap
from utils.objects.layer import Layer
from utils.objects.general_object import GeneralObject
import utils.drawing.drawing_on_plot as drw
import utils.drawing.names as names

from random import randint
from utils.drawing.projections.plot_object import PlotObject

drawing_functions = {
    'point': drw.create_point, 'segment': drw.create_segment, 'line': drw.create_line, 'plane': drw.create_plane,
    'perpendicular_segment': drw.create_perpendicular_segment, 'parallel_segment': drw.create_parallel_segment,
    'perpendicular_line': drw.create_perpendicular_line, 'parallel_line': drw.create_parallel_line,
    'plane_3p': drw.create_plane_3p, 'parallel_plane': drw.create_parallel_plane,
    'horizontal': drw.create_horizontal, 'frontal': drw.create_frontal,
    'distance': drw.get_distance, 'angle': drw.get_angle, 'circle': drw.create_circle, 'sphere': drw.create_sphere,
    'cylinder': drw.create_cylinder, 'cone': drw.create_cone, 'tor': drw.create_point, 'spline': drw.create_spline,
    'rotation_surface': drw.create_rotation_surface, 'intersection': drw.get_intersection}


class Plot(QWidget):
    objectSelected = pyqtSignal(object)
    printToCommandLine = pyqtSignal(str)
    layersModified = pyqtSignal(object, int)
    setCmdStatus = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)

        self.screen = parent
        self.painter = QPainter()

        self.bg_color = (255, 255, 255)

        self.tlp = 0, 0
        self.brp = self.width(), self.height()
        self.zoom = 1
        self.zoom_step = 1.5
        self.camera_pos = (0, 0)
        self.min_zoom = 1/20
        self.max_zoom = 20

        self.objects = []
        self.add_object_func = None
        self.selected_object = None
        self.selected_object_index = 0

        self.axis = Axis(self)
        self.pm = ProjectionManager(self)
        self.sm = snap.SnapManager(self)
        self.lm = LabelManager(self)

        self.clear()
        self.moving_camera = False
        self.mouse_pos = 0, 0
        self.extra_objects = tuple()
        self.selected_mode = 0
        self.i = 0
        self.scale1 = 1
        self.scale2 = 1

        self.mouse_move = None
        self.mouse_left = None
        self.mouse_right = None
        self.enter = None
        self.esc = None
        self.cmd_command = None

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

        self.set_pen((0, 0, 0), 4)
        self.lm.draw()
        self.painter.end()

    def keyPressEvent(self, a0):
        key = a0.key()
        if key == Qt.Key_Escape:
            if self.esc is not None:
                self.esc(a0)
        if key == Qt.Key_Space:
            print('Enter')
            if self.enter is not None:
                self.enter(a0)
        elif key == Qt.Key_C:
            self.draw('cylinder')
        elif key == Qt.Key_P:
            self.draw('point')
        elif key == Qt.Key_S:
            self.draw('segment')
        elif key == Qt.Key_O:
            self.draw('plane')
        elif key == Qt.Key_L:
            self.draw('line')
        elif key == Qt.Key_W:
            self.draw('perpendicular_segment')
        elif key == Qt.Key_E:
            self.draw('parallel_segment')
        elif key == Qt.Key_G:
            self.draw('perpendicular_line')
        elif key == Qt.Key_T:
            self.draw('parallel_line')
        elif key == Qt.Key_I:
            self.draw('plane_3p')
        elif key == Qt.Key_U:
            self.draw('parallel_plane')
        elif key == Qt.Key_H:
            self.draw('horizontal')
        elif key == Qt.Key_F:
            self.draw('frontal')
        elif key == Qt.Key_D:
            self.draw('distance')
        elif key == Qt.Key_A:
            self.draw('angle')
        elif key == Qt.Key_V:
            self.draw('circle')
        elif key == Qt.Key_B:
            self.draw('sphere')
        elif key == Qt.Key_K:
            self.draw('cone')
        elif key == Qt.Key_X:
            self.draw('intersection')
        elif key == Qt.Key_Q:
            self.draw('spline')
        elif key == Qt.Key_R:
            self.draw('rotation_surface')

    def draw_segment(self, p1, p2, color=(0, 0, 0), thickness=1, line_type=1):
        self.set_pen(color, thickness * self.scale2, line_type)
        self.painter.drawLine(int(p1[0] * self.scale1), int(p1[1] * self.scale1),
                              int(p2[0] * self.scale1), int(p2[1] * self.scale1))

    def draw_point(self, point, color=(0, 0, 0), thickness=1):
        self.set_pen(color, thickness * self.scale2)
        brush = self.painter.brush()
        self.painter.setBrush(QColor(*self.bg_color))
        self.painter.drawEllipse(
            int(point[0] * self.scale1 - 5 * self.scale2), int(point[1] * self.scale1 - 5 * self.scale2),
            int(10 * self.scale2), int(10 * self.scale2))
        self.painter.setBrush(brush)

    def draw_point2(self, point, color=(0, 0, 0), thickness=1):
        if self.tlp[0] <= point[0] <= self.brp[0] and self.tlp[1] <= point[1] <= self.brp[1]:
            self.set_pen(color, thickness * self.scale2)
            self.painter.drawPoint(int(point[0] * self.scale1), int(point[1] * self.scale1))

    def draw_circle(self, center, radius, color=(0, 0, 0), thickness=2):
        self.set_pen(color, thickness * self.scale2)
        self.painter.drawEllipse(int((center[0] - radius) * self.scale1), int((center[1] - radius) * self.scale1),
                                 int(radius * 2 * self.scale1), int(radius * 2 * self.scale1))

    def draw_text(self, pos, text):
        self.painter.drawText(int(pos[0] * self.scale1), int(pos[1] * self.scale1), text)

    def draw_text2(self, rect, text, option):
        self.painter.drawText(rect, text, option)

    def set_pen(self, color, thickness, line_type=1):
        self.painter.setPen(QPen(QColor(*color), int(thickness), line_type))

    def clear(self):
        self.objects.clear()
        self.update()

    def draw(self, figure):
        self.setMouseTracking(True)
        drawing_functions[figure](self, 1)

    def update(self, *objects, selected=0) -> None:
        self.extra_objects = objects
        self.selected_mode = selected
        super(Plot, self).update()

    def resizeEvent(self, a0) -> None:
        self.tlp = 0, 0
        self.brp = self.size().width(), self.size().height()
        self.axis.update(self)
        for obj in self.objects:
            obj.update_projections()
        self.update()

    def move_camera(self, x, y, update=True):
        x = int(x)
        y = int(y)
        self.axis.move(0, y)
        self.camera_pos = self.camera_pos[0] + x, self.camera_pos[1] + y
        self.pm.camera_pos = self.camera_pos
        if update:
            for obj in self.objects:
                obj.move(x, y)
            self.lm.move(x, y)
            self.sm.update_intersections()
            self.update()

    def add_object(self, ag_object, name=None, color=None, end=False, **config):
        if color is None:
            color = self.random_color()
        if name is None:
            name = names.generate_name(self, ag_object, config)
        self.add_object_func(ag_object, name, color, history_record=True, **config)
        self.sm.update_intersections()
        self.update()
        if end:
            self.end()

    def modify_plot_object(self, id, general_object):
        if general_object:
            for obj in self.objects:
                if obj.id == id:
                    obj.replace_general_object(general_object)
                    break
            else:
                self.objects.append(PlotObject(self, general_object))
        else:
            self.objects.remove(self.find_by_id(id))
        self.sm.update_intersections()
        self.update()

    def update_plot_objects(self, object_list):
        self.objects.clear()
        for obj in object_list:
            self.objects.append(PlotObject(self, obj))

    def mousePressEvent(self, a0) -> None:
        if a0.button() == 1:
            if self.mouse_left:
                self.mouse_left(a0.pos())
            else:
                self.select_object((a0.x(), a0.y()))
        elif a0.button() == 2:
            if self.mouse_right:
                self.mouse_right(a0.pos())
            else:
                self.mouse_pos = a0.x(), a0.y()
                self.moving_camera = True
        elif a0.button() == Qt.MouseButton.MidButton:
            self.mouse_pos = a0.x(), a0.y()
            self.moving_camera = True

    def mouseReleaseEvent(self, a0) -> None:
        if a0.button() in (2, Qt.MouseButton.MidButton):
            self.moving_camera = False

    def mouseMoveEvent(self, a0) -> None:
        # print('mouse move')
        if self.moving_camera:
            self.move_camera(a0.x() - self.mouse_pos[0], a0.y() - self.mouse_pos[1])
            self.mouse_pos = a0.x(), a0.y()
        if self.mouse_move:
            self.mouse_move(a0.pos())

    def wheelEvent(self, a0) -> None:
        if a0.angleDelta().y() > 0:
            self.set_zoom(self.zoom * self.zoom_step, (a0.x(), a0.y()))
        else:
            self.set_zoom(self.zoom / self.zoom_step, (a0.x(), a0.y()))

    def select_object(self, pos):
        selected_object = None
        for obj in self.objects:
            for el in obj.xy_projection:
                if isinstance(el, ScreenPoint) and snap.distance(pos, el.tuple()) <= 7:
                    selected_object = obj
                    break
                if isinstance(el, ThinScreenPoint) and snap.distance(pos, el.tuple()) <= 3:
                    selected_object = obj
                    break
                if isinstance(el, ScreenSegment) and snap.distance(pos, snap.nearest_point(pos, el)) <= 3:
                    selected_object = obj
                    break
                if isinstance(el, ScreenCircle) and abs(snap.distance(pos, el.center) - el.radius) <= 3:
                    selected_object = obj
                    break
            for el in obj.xz_projection:
                if isinstance(el, ScreenPoint) and snap.distance(pos, el.tuple()) <= 7:
                    selected_object = obj
                    break
                if isinstance(el, ThinScreenPoint) and snap.distance(pos, el.tuple()) <= 2:
                    selected_object = obj
                    break
                if isinstance(el, ScreenSegment) and snap.distance(pos, snap.nearest_point(pos, el)) <= 2:
                    selected_object = obj
                    break
                if isinstance(el, ScreenCircle) and abs(snap.distance(pos, el.center) - el.radius) <= 3:
                    selected_object = obj
                    break
        if selected_object:
            if selected_object.id != self.selected_object_index:
                self.objectSelected.emit(selected_object.id)
        else:
            self.objectSelected.emit(0)

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
        if zoom > self.zoom:
            self.zoom_in(pos, zoom / self.zoom)
        elif zoom < self.zoom:
            self.zoom_out(pos, self.zoom / zoom)

    def zoom_in(self, pos=None, zoom_step=1.5):
        if pos is None:
            pos = (self.tlp[0] + self.brp[0]) // 2, (self.tlp[1] + self.brp[1]) // 2
        self.zoom *= zoom_step
        self.pm.zoom *= zoom_step
        self.move_camera((zoom_step - 1) * ((self.axis.rp[0] - pos[0]) + self.camera_pos[0]),
                         (zoom_step - 1) * (self.axis.rp[1] - pos[1]), update=False)
        for obj in self.objects:
            obj.update_projections()
        self.sm.update_intersections()
        self.update()

    def zoom_out(self, pos=None, zoom_step=1.5):
        if pos is None:
            pos = (self.tlp[0] + self.brp[0]) // 2, (self.tlp[1] + self.brp[1]) // 2
        self.zoom /= zoom_step
        self.pm.zoom /= zoom_step
        new_camera_x = (self.camera_pos[0] + self.axis.rp[0] - pos[0]) / zoom_step - self.axis.rp[0] + pos[0]
        new_axis_y = pos[1] - (pos[1] - self.axis.lp[1]) / zoom_step
        self.move_camera(new_camera_x - self.camera_pos[0], new_axis_y - self.axis.lp[1], update=False)
        for obj in self.objects:
            obj.update_projections()
        self.sm.update_intersections()
        self.update()

    def end(self):
        self.mouse_move = None
        self.mouse_left = None
        self.mouse_right = None
        self.setMouseTracking(False)
        self.cmd_command = None
        self.setCmdStatus.emit(False)
        self.update()

    def print(self, s):
        self.printToCommandLine.emit(s)
        print(s)

    @staticmethod
    def random_color():
        red = randint(20, 240)
        green = randint(20, 240)
        blue = randint(20, min(570 - red - green, 240))
        return red, green, blue
        while True:
            red = randint(20, 240)
            green = randint(20, 240)
            blue = randint(20, 570 - red - green)
            if 300 < red + green + blue < 570:
                return red, green, blue

    def set_current_layer(self, ind, history_record=True):
        if ind == self.current_layer:
            return
        if history_record:
            self.hm.add_record('change_layer', self.current_layer)
        self.current_layer = ind

    def add_layer(self, layer=None, history_record=True):
        if history_record:
            self.hm.add_record('add_layer', len(self.layers) - 1)
        if layer:
            self.layers.append(layer)
        else:
            self.layers.append(Layer(self, ''))

    def insert_layer_from_dict(self, dct, index):
        self.layers.insert(index, Layer.from_dict(dct, self))

    def replace_object(self, dct, layer=None, index=None, history_record=True):
        if layer is None:
            layer, index = self.selected_object_index
        self.layers[layer].replace_object(index, dct)
        self.update()

    def save_object_properties(self, obj: GeneralObject, name=None, layer=None, thickness=None, color=None,
                               ag_obj=None, config=None, history_record=True):
        if obj:
            if name:
                old_name = obj.name
                if obj.set_name(name) and history_record:
                    self.hm.add_record('object_modified', obj, 'name', old_name)
            if thickness:
                old_thickness = obj.thickness
                if obj.set_thickness(thickness) and history_record:
                    self.hm.add_record('object_modified', obj, 'thickness', old_thickness)
            if color:
                old_color = obj.color
                if obj.set_color(color) and history_record:
                    self.hm.add_record('object_modified', obj, 'color', old_color)
        self.update()

    def update_layer_list(self):
        self.layersModified.emit(self.layers, self.current_layer)


def main():
    app = QApplication([])
    plot = Plot(None)
    app.exec_()


if __name__ == '__main__':
    main()
