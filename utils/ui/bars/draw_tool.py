from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QHoverEvent
from utils.ui.widgets.widget import Widget


class DrawTool(Widget):
    hovered_tool = None

    def __init__(self, name, parent, font_manager):
        super().__init__(parent)

        self.clicked = None
        self.name = name

        self.setStyleSheet("QWidget::hover {}")

        # LAYOUT
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.icon = QLabel(self.central_widget)
        self.icon.setMaximumSize(30, 30)
        self.icon.setStyleSheet("border: 2px solid #00ABB3;\n"
                                "border-radius: 10px;\n"
                                "background-color: #ffffff;")
        self.icon.setPixmap(QPixmap(":/img/img/point.png"))
        self.icon.setScaledContents(True)
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setWordWrap(False)
        self.layout.addWidget(self.icon)

        self.label = QLabel(self.central_widget)

        self.label.setFont(font_manager.bold())
        self.label.setText(name)
        self.label.setStyleSheet('color: #00ABB3;')

        self.layout.addWidget(self.label)

    def mousePressEvent(self, a0) -> None:
        if a0.button() == 1:
            if self.clicked:
                self.clicked()

    def eventFilter(self, a0, a1) -> bool:
        super().eventFilter(a0, a1)
        if isinstance(a1, QHoverEvent):
            DrawTool.tool_hovered(self)
        return False

    def set_text(self, text):
        self.label.setText(text)

    def set_on_click_listener(self, func):
        self.clicked = func
        return self

    def hover(self):
        print('Hover:', self.label.text())
        self.label.setStyleSheet('color: #3C4048;')

    def unhover(self):
        print('Unhover:', self.label.text())
        self.label.setStyleSheet('color: #00ABB3;')

    @staticmethod
    def tool_hovered(tool):
        if DrawTool.hovered_tool and DrawTool.hovered_tool != tool:
            DrawTool.hovered_tool.unhover()
        if DrawTool.hovered_tool != tool and tool:
            tool.hover()
        DrawTool.hovered_tool = tool
