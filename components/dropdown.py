import flet as ft

class CustomDropdown:
    def __init__(self, label, options, width=150):
        self.label = label
        self.options = options
        self.width = width

    def get_control(self):
        return ft.Dropdown(
            label=self.label,
            options=[ft.dropdown.Option(option) for option in self.options],
            width=self.width,
        )
