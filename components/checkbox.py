import flet as ft

class CustomCheckbox:
    def __init__(self, label):
        self.label = label

    def get_control(self):
        return ft.Checkbox(
            label=self.label,
        )
