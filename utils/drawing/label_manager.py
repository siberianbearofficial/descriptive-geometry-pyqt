import core.angem as ag
from utils.drawing.projections.projection_manager import ScreenPoint

SEP = '-'


class LabelManager:
    def __init__(self, plot):
        self.plot = plot
        self.labels = dict()
        self.pos = [0, 0]
        self.sep = SEP

    def add_label(self, pos, text):
        pos = int(pos[0]), int(pos[1])
        if pos in self.labels:
            self.labels[pos].add_text(text)
        else:
            self.labels[pos] = Label(*pos, text)

    def delete_label(self, pos, text):
        pos = int(pos[0]), int(pos[1])
        if pos in self.labels:
            self.labels[pos].delete_text(text)
            if len(self.labels[pos]) == 0:
                self.labels.pop(pos)

    def draw(self):
        # TODO: Стилизовать
        for pos, label in self.labels.items():
            self.plot.draw_text((pos[0] + self.pos[0] + 10, pos[1] + self.pos[1] - 10), " = ".join(set(label.text)))

    def clear(self):
        self.labels = dict()

    def convert_pos(self, pos):
        return int(pos[0]) - self.pos[0], int(pos[1]) - self.pos[1]

    def move(self, x, y):
        self.pos[0] += x
        self.pos[1] += y

    def add_labels_to_obj(self, obj):
        positions = LabelManager.get_label_pos(obj)
        texts = LabelManager.get_label_text(obj)
        res = []
        for i in range(len(positions)):
            pos = self.convert_pos(positions[i])
            self.add_label(pos, texts[i])
            res.append((pos, texts[i]))
        return res

    def get_name_to_new_obj(self, pos):
        pos = self.convert_pos(pos)
        if pos in self.labels:
            return self.labels[pos].text[0].replace("'", "")
        return None

    @staticmethod
    def get_label_text(obj):
        if isinstance(obj.ag_object, ag.Point):
            return obj.name + "'", obj.name + "''"
        if isinstance(obj.ag_object, ag.Segment):
            if obj.name.count(SEP) == 1:
                name = obj.name.split(SEP)
                return name[0] + "'", name[1] + "'", name[0] + "''", name[1] + "''"
            return obj.name + "'", obj.name + "''"
        if isinstance(obj.ag_object, ag.Plane) and obj.general_object.config.get('draw_3p', False):
            if obj.name.count(SEP) == 2:
                name = obj.name.split(SEP)
                return name[0] + "'", name[1] + "'", name[2] + "'", name[0] + "''", name[1] + "''", name[2] + "''"
            return obj.name + "'", obj.name + "'", obj.name + "'", obj.name + "''", obj.name + "''", obj.name + "''"
        if isinstance(obj.ag_object, ag.Line) or isinstance(obj.ag_object, ag.Plane):
            return obj.name + "'", obj.name + "''"
        return tuple()

    @staticmethod
    def get_label_pos(obj):
        if isinstance(obj.ag_object, ag.Point):
            return obj.xy_projection[0].tuple(), obj.xz_projection[0].tuple()
        elif isinstance(obj.ag_object, ag.Segment):
            if obj.name.count(SEP) == 1:
                return obj.xy_projection[0].p1, obj.xy_projection[0].p2, obj.xz_projection[0].p1, obj.xz_projection[
                    0].p2
            return ((obj.xy_projection[0].p1[0] + obj.xy_projection[0].p2[0]) // 2,
                    (obj.xy_projection[0].p1[1] + obj.xy_projection[0].p2[1]) // 2), \
                   ((obj.xz_projection[0].p1[0] + obj.xz_projection[0].p2[0]) // 2,
                    (obj.xz_projection[0].p1[1] + obj.xz_projection[0].p2[1]) // 2)
        elif isinstance(obj.ag_object, ag.Plane) and obj.general_object.config.get('draw_3p', False):
            return obj.xy_projection[3].tuple(), obj.xy_projection[4].tuple(), obj.xy_projection[5].tuple(), \
                   obj.xz_projection[3].tuple(), obj.xz_projection[4].tuple(), obj.xz_projection[5].tuple()

        if isinstance(obj.ag_object, ag.Line) or isinstance(obj.ag_object, ag.Plane):
            if isinstance(obj.xy_projection[0], ScreenPoint):
                res_p1 = obj.xy_projection[0].tuple()
            elif not obj.xy_projection[0].drawing:
                res_p1 = 0, obj.plot.brp[0] + 10
            else:
                if obj.xy_projection[0].point1[1] > obj.xy_projection[0].point2[1]:
                    p1 = obj.xy_projection[0].point1
                    p1_by_y = obj.xy_projection[0].p1_by_y
                else:
                    p1 = obj.xy_projection[0].point2
                    p1_by_y = obj.xy_projection[0].p2_by_y
                if obj.xy_projection[0].k is None:
                    res_p1 = obj.xy_projection[0].x(obj.plot.brp[1] - 10), obj.plot.brp[1] - 10
                elif p1_by_y:
                    x = obj.plot.brp[0] - 50 if obj.xy_projection[0].k > 0 else obj.plot.tlp[0] + 5
                    res_p1 = x, obj.xy_projection[0].y(x)
                else:
                    res_p1 = obj.xy_projection[0].x(obj.plot.brp[1] - 10), obj.plot.brp[1] - 10
                    # res_p1 = (get_point((obj.xy_projection[0].x(p1[1] - d), p1[1] - d),
                    #                     obj.xy_projection[0].k, DIST1, True, True), obj.xy_projection[0].k > 0)
            if isinstance(obj.xz_projection[0], ScreenPoint):
                res_p2 = obj.xz_projection[0].tuple()
            elif not obj.xz_projection[0].drawing:
                res_p2 = 0, obj.plot.tlp[1] - 10
            else:
                if obj.xz_projection[0].point1[1] < obj.xz_projection[0].point2[1]:
                    p2 = obj.xz_projection[0].point1
                    p2_by_y = obj.xz_projection[0].p1_by_y
                else:
                    p2 = obj.xz_projection[0].point2
                    p2_by_y = obj.xz_projection[0].p2_by_y
                if obj.xz_projection[0].k is None:
                    res_p2 = obj.xz_projection[0].x(obj.plot.tlp[1] + 10), obj.plot.tlp[1] + 10
                elif p2_by_y:
                    x = obj.plot.tlp[0] + 5 if obj.xz_projection[0].k > 0 else obj.plot.brp[0] - 50
                    res_p2 = x, obj.xz_projection[0].y(x)
                else:
                    res_p2 = obj.xz_projection[0].x(obj.plot.tlp[1] + 30), obj.plot.tlp[1] + 30
            return (int(res_p1[0]), int(res_p1[1])), (int(res_p2[0]), int(res_p2[1]))
        return tuple()


class Label:
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text if isinstance(text, list) else [text]
        self.screen_x = x
        self.screen_y = y
        self.width = len(' = '.join(self.text)) * 4
        self.height = 12

    def add_text(self, text):
        self.text.append(text)
        self.width = sum(map(len, self.text)) * 4

    def delete_text(self, text):
        self.text.remove(text)
        self.width = len(' = '.join(self.text)) * 4

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f'({self.x}, {self.y}): {self.text}'
