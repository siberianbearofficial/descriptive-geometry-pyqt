from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView


class SvgWidget(QGraphicsView):
    def __init__(self):
        super().__init__()

        svg_renderer = QSvgRenderer(r"C:\Users\sergi\PycharmProjects\DescriptiveGeometry\utils\ui\widgets\Group 1.svg")

        scene = QGraphicsScene()
        scene.addItem(svg_renderer)

        self.setScene(scene)
