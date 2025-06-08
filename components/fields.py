import flet as ft
from utils.colors import *


class CustomInputField:
    def __init__(self, hint_text: str, password: bool = False):
        self.password = password
        self.visible = not password

        # Create text field
        self.text_field = ft.TextField(
            label=hint_text,
            password=self.password,
            bgcolor=customSecondaryBG_color,
            width=600,
            height=60,

            can_reveal_password=False,  # We handle manually
        )

        # If it's a password field, add eye icon
        if self.password:
            self.eye_icon = ft.IconButton(
                content=ft.Image(src="assets/imgs/closed-eyes.png", width=24, height=24),
                on_click=self.toggle_password_visibility,
            )
            self.text_field.suffix = self.eye_icon

    def toggle_password_visibility(self, e):
        self.visible = not self.visible
        self.text_field.password = not self.visible
        self.eye_icon.content = ft.Image(
            src="assets/imgs/open-eyes.png" if self.visible else "assets/imgs/closed-eyes.png",
            width=24,
            height=24,
        )
        self.text_field.update()

    def get_control(self):
        return self.text_field
