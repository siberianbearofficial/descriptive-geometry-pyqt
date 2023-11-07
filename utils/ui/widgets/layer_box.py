from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QPushButton, QMenu, QVBoxLayout, QHBoxLayout

from utils.objects.layer import Layer
from utils.ui.widgets.button import Button


class LayerBox(QPushButton):
    def __init__(self, tm, object_manager):
        super().__init__()
        self.tm = tm
        self.object_manager = object_manager
        self.setMinimumSize(180, 24)

        self.clicked.connect(self._on_clicked)

        self.object_manager.layerSelected.connect(self._on_layer_changed)
        self.object_manager.layerNameChanged.connect(self._on_layer_changed)
        self._on_layer_changed()

    def _on_layer_changed(self):
        self.setText(self.object_manager.layers[self.object_manager.current_layer].name)

    def _on_clicked(self):
        menu = LayersMenu(self.tm, self.object_manager)
        menu.move(self.mapToGlobal(QPoint(0, self.height() + 5)))
        menu.exec()

    def set_styles(self):
        self.tm.auto_css(self)


class LayersMenu(QMenu):
    def __init__(self, tm, object_manager):
        super().__init__()
        self.tm = tm
        self.object_manager = object_manager

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(3, 3, 3, 3)
        self.setLayout(main_layout)

        self.items = dict()

        for el in self.object_manager.layers.values():
            item = LayerItem(self.tm, self.object_manager, el)
            item.clicked.connect(self.close)
            self.items[el.id] = item
            main_layout.addWidget(item)

    def showEvent(self, a0) -> None:
        super().showEvent(a0)
        self.set_styles()

    def set_styles(self):
        self.tm.auto_css(self, palette='Menu')
        for el in self.items.values():
            el.set_styles()


class LayerItem(QPushButton):
    def __init__(self, tm, object_manager, layer):
        super().__init__()
        self.tm = tm
        self.object_manager = object_manager
        self.layer = layer
        self.setFixedSize(200, 26)
        self.setText(layer.name)

        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(main_layout)

        self._button_hide = Button(self.tm, 'hide', css='Menu')
        self._button_hide.setFixedSize(22, 22)
        self._button_hide.clicked.connect(self._on_hide)
        main_layout.addWidget(self._button_hide)

        self._button_show = Button(self.tm, 'show', css='Menu')
        self._button_show.setFixedSize(22, 22)
        self._button_show.clicked.connect(self._on_show)
        main_layout.addWidget(self._button_show)

        self.clicked.connect(lambda: self.object_manager.select_layer(self.layer.id))

        if self.layer.hidden:
            self._button_hide.hide()
        else:
            self._button_show.hide()

    def _on_hide(self):
        self._button_hide.hide()
        self._button_show.show()
        self.object_manager.set_layer_hidden(self.layer.id, True)

    def _on_show(self):
        self._button_show.hide()
        self._button_hide.show()
        self.object_manager.set_layer_hidden(self.layer.id, False)

    def set_styles(self):
        self.tm.auto_css(self, palette='Menu', border=False, alignment='left', padding=True)
        self._button_show.set_styles()
        self._button_hide.set_styles()
