from utils.drawing.real_point import RealPoint as RP


class RealSegment:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    @staticmethod
    def from_segment(segment, axis, plane):
        return RealSegment(RP.from_point(segment.p1, axis, plane),
                           RP.from_point(segment.p2, axis, plane))
