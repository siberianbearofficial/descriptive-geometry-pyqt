class HistoryManager:
    def __init__(self, object_manager):
        self.object_manager = object_manager
        self.records = []
        self.redo_records = []
        self.max_count = 20

    def add_record(self, action_type, clear_redo=True, **action_info):
        if clear_redo:
            self.redo_records = []
        self.records.append(Record(action_type, action_info))
        if len(self.records) > self.max_count:
            self.records.pop(0)

    def add_redo_record(self, action_type, clear_redo=False, **action_info):
        if clear_redo:
            self.redo_records = []
        self.redo_records.append(Record(action_type, action_info))
        if len(self.redo_records) > self.max_count:
            self.redo_records.pop(0)

    def redo(self):
        self.undo(redo=True)

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
        print(record.action_type, record.action_info)
        if record.action_type == 'add_object':
            add_action('delete_object', clear_redo=False, dict=self.object_manager.layers[
                record.action_info['index'][0]].objects[record.action_info['index'][1]].to_dict(),
                       index=record.action_info['index'])
            self.object_manager.delete_object(record.action_info['index'][0], record.action_info['index'][1],
                                              history_record=False)
        elif record.action_type == 'delete_object':
            add_action('add_object', clear_redo=False, index=record.action_info['index'])
            self.object_manager.add_object_from_dict(record.action_info['dict'], history_record=False)
        elif record.action_type == 'set_obj_name':
            add_action('set_obj_name', clear_redo=False, name=self.object_manager[record.action_info['index']].name,
                       index=record.action_info['index'])
            self.object_manager.set_object_name(record.action_info['name'], record.action_info['index'],
                                                history_record=False)
        elif record.action_type == 'set_obj_color':
            add_action('set_obj_color', clear_redo=False, color=self.object_manager[record.action_info['index']].color,
                       index=record.action_info['index'])
            self.object_manager.set_object_color(record.action_info['color'], record.action_info['index'],
                                                 history_record=False)
        elif record.action_type == 'set_obj_thickness':
            add_action('set_obj_thickness', clear_redo=False, thickness=self.object_manager[
                record.action_info['index']].thickness, index=record.action_info['index'])
            self.object_manager.set_object_thickness(record.action_info['thickness'], record.action_info['index'],
                                                     history_record=False)
        elif record.action_type == 'set_obj_layer':
            add_action('set_obj_layer', clear_redo=False, layer=record.action_info['index'][0], index=(
                record.action_info['layer'], len(self.object_manager[record.action_info['layer']].objects)))
            self.object_manager.set_object_layer(record.action_info['layer'], record.action_info['index'],
                                                 history_record=False)
        elif record.action_type == 'set_obj_ag_obj':
            add_action('set_obj_ag_obj', clear_redo=False, dct=self.object_manager[
                record.action_info['index']].to_dict(), index=record.action_info['index'])
            self.object_manager.set_object_ag_object(record.action_info['dct'], record.action_info['index'],
                                                     history_record=False)
        elif record.action_type == 'set_obj_config':
            add_action('set_obj_config', clear_redo=False, config=self.object_manager[
                record.action_info['index']].config, index=record.action_info['index'])
            self.object_manager.set_object_config(record.action_info['config'], record.action_info['index'],
                                                  history_record=False)
        elif record.action_type == 'select_layer':
            add_action('select_layer', clear_redo=False, layer=self.object_manager.current_layer)
            self.object_manager.select_layer(record.action_info['layer'], history_record=False)
        elif record.action_type == 'add_layer':
            self.add_redo_record('delete_layer', clear_redo=False,
                                 dict=self.object_manager[record.action_info['index']].to_dict(),
                                 index=record.action_info['index'])
            self.object_manager.delete_layer(record.action_info['index'], history_record=False)
        elif record.action_type == 'delete_layer':
            add_action('add_layer', clear_redo=False, index=record.action_info['index'])
            self.object_manager.add_layer(index=record.action_info['index'], dct=record.action_info['dict'],
                                          history_record=False)
        elif record.action_type == 'layer_name':
            add_action('layer_name', clear_redo=False, name=self.object_manager[record.action_info['index']].name,
                       index=record.action_info['index'])
            self.object_manager.set_layer_attr('name', record.action_info['name'], record.action_info['index'])
        elif record.action_type == 'layer_color':
            add_action('layer_color', clear_redo=False, color=self.object_manager[record.action_info['index']].color,
                       index=record.action_info['index'])
            self.object_manager.set_layer_attr('color', record.action_info['color'], record.action_info['index'])
        elif record.action_type == 'layer_thickness':
            add_action('layer_thickness', clear_redo=False, thickness=self.object_manager[record.action_info['index']].thickness,
                       index=record.action_info['index'])
            self.object_manager.set_layer_attr('thickness', record.action_info['thickness'], record.action_info['index'])
        elif record.action_type == 'layer_hidden':
            add_action('layer_hidden', clear_redo=False, hidden=self.object_manager[record.action_info['index']].hidden,
                       index=record.action_info['index'])
            self.object_manager.set_layer_hidden(record.action_info['hidden'], record.action_info['index'])
        else:
            print(f'unknown history record type: {record.action_type}')
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
