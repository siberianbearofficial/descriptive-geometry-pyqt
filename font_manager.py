from PyQt5.QtGui import QFont


class FontManager:
    def __init__(self, medium_family="Alegreya Sans SC Medium", bold_family="Alegreya Sans SC ExtraBold"):

        self.default_medium_size = 9
        self.default_bold_size = 11

        self.default_medium = self.font(family=medium_family, size=self.default_medium_size)
        self.default_bold = self.font(family=bold_family, size=self.default_bold_size)

        self.fonts = dict()

    def bold(self, size=None):
        return FontManager.font(font=self.default_bold, size=size)

    def medium(self, size=None):
        return FontManager.font(font=self.default_medium, size=size)

    @staticmethod
    def font(family=None, size=None, font=None):
        if not font:
            font = QFont()
        if family:
            font.setFamily(family)
        if size:
            font.setPointSize(size)
        return font
