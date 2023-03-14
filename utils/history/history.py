class HistoryManager:
    def __init__(self, plot):
        self.plot = plot
        self.records = []
        self.redo_records = []
        self.max_count = 20

    def add_record(self, action_type, *action_info, clear_redo=True):
        if clear_redo:
            self.redo_records = []
        self.records.append(Record(action_type, action_info))
        if len(self.records) > self.max_count:
            self.records.pop(0)

    def add_redo_record(self, action_type, *action_info, clear_redo=False):
        if clear_redo:
            self.redo_records = []
        self.redo_records.append(Record(action_type, action_info))
        if len(self.redo_records) > self.max_count:
            self.redo_records.pop(0)

    def undo(self, redo=False):
        if redo:
            if len(self.redo_records) == 0:
                return
            record = self.redo_records[-1]
            add_action = self.add_record
        else:
            if len(self.records) == 0:
                return
            record = self.records[-1]
            add_action = self.add_redo_record
        if record.action_type == 'add_object':
            add_action('delete_object', self.plot.layers[self.plot.current_layer].objects[-1].to_dict(),
                       clear_redo=False)
            self.plot.layers[self.plot.current_layer].delete_object(-1, history_record=False)
            self.plot.selected_object = None
            self.plot.update()
        elif record.action_type == 'delete_object':
            add_action('add_object', -1, clear_redo=False)
            self.plot.layers[self.plot.current_layer].add_object_from_dict(*record.action_info)
            self.plot.update()
        elif record.action_type == 'object_modified':
            obj = record.action_info[0]
            attribute = record.action_info[1]
            if attribute == 'name':
                add_action('object_modified', obj, 'name', obj.name, clear_redo=False)
                self.plot.save_object_properties(obj, name=record.action_info[2], history_record=False)
        elif record.action_type == 'change_layer':
            add_action('change_layer', self.plot.current_layer, clear_redo=False)
            self.plot.set_current_layer(record.action_info[0], history_record=False)
            self.plot.update_layer_list()
        elif record.action_type == 'add_layer':
            self.add_redo_record('delete_layer', self.plot.layers[record.action_info[0]].to_dict(),
                                 record.action_info[1], clear_redo=False)
            self.plot.delete_layer(record.action_info[0], history_record=False)
            self.plot.update_layer_list()
            self.plot.update()
        elif record.action_type == 'delete_layer':
            add_action('add_layer', record.action_info[1], clear_redo=False)
            self.plot.insert_layer_from_dict(record.action_info[0], record.action_info[1])
            self.plot.update_layer_list()
            self.plot.update()
        elif record.action_type == 'hide_layer':
            add_action('hide_layer', record.action_info[1], clear_redo=False)
            self.plot.layers[record.action_info[0]].hidden = not record.action_info[1]
            self.plot.update_layer_list()
            self.plot.update()
        else:
            print('unknown history record type')
        if redo:
            self.redo_records.pop()
        else:
            self.records.pop()


class Record:
    def __init__(self, action_type, action_info):
        self.action_type = action_type
        self.action_info = action_info

    def __str__(self):
        return f'({self.action_type} - {self.action_info})'
