class Thickness:
    LIGHT_THICKNESS = 1
    MEDIUM_THICKNESS = 2
    BOLD_THICKNESS = 4

    @staticmethod
    def fix(thickness):
        def nearest(value, a, b):
            return a if abs(value - a) <= abs(value - b) else b

        try:
            thickness = int(thickness)
            if thickness < Thickness.LIGHT_THICKNESS:
                thickness = Thickness.LIGHT_THICKNESS
            elif thickness < Thickness.MEDIUM_THICKNESS:
                thickness = nearest(thickness, Thickness.LIGHT_THICKNESS, Thickness.MEDIUM_THICKNESS)
            elif thickness < Thickness.BOLD_THICKNESS:
                thickness = nearest(thickness, Thickness.MEDIUM_THICKNESS, Thickness.BOLD_THICKNESS)
            else:
                thickness = Thickness.BOLD_THICKNESS
        except ValueError:
            thickness = Thickness.MEDIUM_THICKNESS

        return thickness
