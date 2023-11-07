from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, pyqtProperty
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget, QLineEdit, QApplication
from PyQt6.QtGui import QPixmap, QMouseEvent, QTransform

from utils.ui.widgets.line_edit_widget import LineEditWidget
from utils.color import *


class PropertiesBarObject(QWidget):
    ARROW_SIZE = 20
    ARROW_PIXMAP = None

    def __init__(self, struct=None, parent=None, font_manager=None, name=None, on_editing_finished=None, path=None):
        super().__init__()

        if not PropertiesBarObject.ARROW_PIXMAP:
            PropertiesBarObject.ARROW_PIXMAP = QPixmap(":/img/img/inspector_bar_object_icon.png")

        self.path = path if path else list()
        self.font_manager = font_manager
        self.name = name
        self.on_editing_finished = on_editing_finished

        # Layout
        self.layout = QVBoxLayout()
        self.set_margin(15)
        self.layout.setSpacing(5)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.container = QHBoxLayout()
        self.container.setContentsMargins(0, 0, 0, 0)
        self.container.setSpacing(0)

        self.layout.addLayout(self.container)

        # Arrow
        self.container.addWidget(Arrow(self))

        # Label
        label = QLabel(self)
        label.setStyleSheet(f"color: {ACCENT_COLOR};")
        if font_manager:
            label.setFont(font_manager.bold())
        if name:
            label.setText(name)
        self.container.addWidget(label)

        # Objects
        self.objects_widget = None
        self.unpack_objects_struct(struct)

    def unpack_objects_struct(self, struct):
        if isinstance(struct, dict):
            self.objects_widget = QWidget()
            objects_layout = QVBoxLayout(self.objects_widget)
            objects_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            objects_layout.setContentsMargins(0, 0, 0, 0)
            objects_layout.setSpacing(5)
            for key, item in struct.items():
                if key != 'class':
                    wdg = PropertiesBarObject(struct=item,
                                              path=self.path + [key],
                                              font_manager=self.font_manager,
                                              name=key,
                                              on_editing_finished=self.on_editing_finished)
                    objects_layout.addWidget(wdg)
            self.layout.addWidget(self.objects_widget)
            self.clicked()
        elif isinstance(struct, (int, float)):
            # self.layout.addWidget(QLabel(str(struct)))    # test line
            self.clear_container()
            self.container.addWidget(
                FloatInputWidget(self.name, str(struct),
                                 editing_finished=lambda val: self.on_editing_finished(self.path, val),
                                 font_manager=self.font_manager))

    def clear_container(self):
        for i in range(self.container.count() - 1, -1, -1):
            self.container.itemAt(i).widget().deleteLater()

    def clicked(self):
        if self.objects_widget:
            self.objects_widget.show() if self.objects_widget.isHidden() else self.objects_widget.hide()

    def set_margin(self, margin):
        self.layout.setContentsMargins(margin, 0, 0, 0)
        return self


class Arrow(QLabel):
    ANIMATION_DURATION = 100

    pixmapAngleChanged = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.opened = True

        self._pixmap_angle = 0
        self.setPixmap(PropertiesBarObject.ARROW_PIXMAP)
        self.pixmapAngleChanged.connect(self.pixmap_angle_changed)

        self.angle_change_anim = QPropertyAnimation(self, b"pixmap_angle")
        self.angle_change_anim.setDuration(Arrow.ANIMATION_DURATION)

        self.setFixedSize(PropertiesBarObject.ARROW_SIZE, PropertiesBarObject.ARROW_SIZE)

        self.setScaledContents(True)

        if parent.clicked:
            self.clicked = parent.clicked
        else:
            self.clicked = lambda: print('Nothing is here...')

    @pyqtProperty(int)
    def pixmap_angle(self):
        return self._pixmap_angle

    @pixmap_angle.setter
    def pixmap_angle(self, angle):
        if self._pixmap_angle != angle:
            self._pixmap_angle = angle
            self.pixmapAngleChanged.emit(angle)

    def pixmap_angle_changed(self, angle):
        self.setPixmap(PropertiesBarObject.ARROW_PIXMAP.transformed(QTransform().rotate(angle)))

    def mousePressEvent(self, ev):
        if ev.button() == 1:
            if self.clicked:
                self.opened = not self.opened
                if self.opened:
                    self.angle_change_anim.setStartValue(90)
                    self.angle_change_anim.setEndValue(0)
                else:
                    self.angle_change_anim.setStartValue(0)
                    self.angle_change_anim.setEndValue(90)
                self.angle_change_anim.start()
                self.clicked()

    def set_on_click_listener(self, func):
        self.clicked = func
        return self


class FloatInputWidget(QWidget):
    def __init__(self, name, value, editing_finished=None, font_manager=None):
        super().__init__()

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Name
        name_widget = QLabel()
        name_widget.setText(name)
        name_widget.setStyleSheet(f'color: {ACCENT_COLOR};')
        layout.addWidget(name_widget)

        # Value
        self.value_widget = LineEditWidget()
        self.value_widget.setText(value)
        self.value_widget.textChanged.connect(self.text_changed)
        self.value_widget.setStyleSheet(f"color: {ACCENT_COLOR};\n"
                                        f"background-color: {LIGHT_COLOR};\n"
                                        f"border: 2px solid {ACCENT_COLOR};")
        self.value_widget.setFixedHeight(30)
        if editing_finished:
            self.value_widget.editingFinished.connect(lambda: editing_finished(float(self.value_widget.text())))
        layout.addWidget(self.value_widget)

        # Font
        if font_manager:
            name_widget.setFont(font_manager.bold())
            self.value_widget.setFont(font_manager.medium())

    def text_changed(self):
        modified_text = list()
        cursor_pos = self.value_widget.cursorPosition()
        text = self.value_widget.text()
        if text and text[0] == '-':
            FloatInputWidget.positive_float_filter(text[1:], modified_text)
            modified_text.insert(0, '-')
        else:
            FloatInputWidget.positive_float_filter(text, modified_text)
        modified_text_str = ''.join(modified_text)
        self.value_widget.setText(modified_text_str)
        self.value_widget.setCursorPosition(cursor_pos - len(text) + len(modified_text_str))

    @staticmethod
    def positive_float_filter(text, output):
        num_start = True
        can_place_zero = True
        can_place_dot = True
        for sym in text:
            if sym == '0' and can_place_zero:
                output.append(sym)
                if num_start:
                    can_place_zero = False
            elif sym in '.,' and can_place_dot:
                if not output:
                    output.append('0')
                output.append('.')
                can_place_zero = True
                can_place_dot = False
            elif sym.isdigit() and sym != '0':
                if not can_place_zero:
                    output.pop(0)
                output.append(sym)
                can_place_zero = True
            num_start = False


if __name__ == '__main__':
    app = QApplication([])
    widget = PropertiesBarObject({
        'Point': {
            'x': 100.0,
            'y': 750.2,
            'z': 83.17,
        }
    }, name='TestName').set_margin(0)
    widget.setFixedSize(720, 480)
    widget.show()
    app.exec_()

    # import resources_rc
