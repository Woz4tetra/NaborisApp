
class Button:
    def __init__(self, labels, command, button_id, group, current_label=0):
        self.labels = labels
        self.command = command
        self.button_id = button_id
        self.group = group
        if type(labels) == str:
            self.current_label = self.labels
        else:
            self.current_label = self.labels[current_label]

    def switch_label(self, index):
        if type(self.labels) == str:
            return self.current_label
        else:
            self.current_label = self.labels[index]
            return self.current_label


class ButtonCollection:
    def __init__(self, *buttons):
        self.buttons = buttons

        self.dict_buttons = {}
        for button in self.buttons:
            self.dict_buttons[button.command] = button

        self.grouped_buttons = {}
        for button in self.buttons:
            if button.group not in self.grouped_buttons:
                self.grouped_buttons[button.group] = [button]
            else:
                self.grouped_buttons[button.group].append(button)

    def get_group(self, group):
        for button in self.grouped_buttons[group]:
            yield button.current_label, button.command, button.button_id, button.group

    def __getitem__(self, item):
        return self.dict_buttons[item]
