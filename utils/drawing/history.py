class HistoryManager:
    def __init__(self, plot):
        self.plot = plot
        self.records = []
        self.max_count = 20

    def add_record(self, action_type, *action_info):
        self.records.append(Record(action_type, action_info))
        if len(self.records) > self.max_count:
            self.records.pop(0)
        # print(*self.records, sep='\n', end='\n------------------\n')

    def undo(self):
        if len(self.records) == 0:
            return
        record = self.records[-1]
        if record.action_type == 'add_object':
            self.plot.layers[self.plot.current_layer].delete_object(-1, history_record=False)
        elif record.action_type == 'delete_object':
            self.plot.layers[self.plot.current_layer].add_object(*record.action_info, history_record=False)
            self.plot.full_update()
        elif record.action_type == 'change_layer':
            self.plot.current_layer = record.action_info[0]
            self.plot.screen.menu.update_layer_list()
        elif record.action_type == 'hide_layer':
            self.plot.layers[record.action_info[0]].hidden = not record.action_info[1]
            self.plot.screen.menu.update_layer_list()
        elif record.action_type == 'add_several_objects':
            for _ in range(record.action_info[0]):
                self.plot.layers[self.plot.current_layer].delete_object(-1, history_record=False)
        self.records.pop()


class Record:
    def __init__(self, action_type, action_info):
        self.action_type = action_type
        self.action_info = action_info

    def __str__(self):
        return f'{self.action_type} - {self.action_info}'
