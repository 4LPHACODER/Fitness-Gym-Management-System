import flet as ft
from utils.colors import customPrimary_color
from flet_core import colors

def nav_button_transparent(page: ft.Page, icon_path: str, route: str, custom_click=None) -> ft.Container:
    """
    Navigation button with transparent background by default.
    """
    def on_click(e):
        if custom_click:
            custom_click(e)
        else:
            page.go(route)

    return ft.Container(
        content=ft.Image(src=icon_path, width=28, height=28),
        padding=ft.padding.all(12),
        bgcolor=colors.TRANSPARENT,
        border_radius=ft.border_radius.all(12),
        border=ft.border.all(1, customPrimary_color),
        on_click=on_click,
        ink=True,
        alignment=ft.alignment.center,
        width=50,
        margin=ft.margin.only(top=10),
    )


def nav_button_custom_bg(page: ft.Page, icon_path: str, route: str, bgcolor: str, custom_click=None) -> ft.Container:
    """
    Navigation button with a customizable background color.
    """
    def on_click(e):
        if custom_click:
            custom_click(e)
        else:
            page.go(route)

    return ft.Container(
        content=ft.Image(src=icon_path, width=15, height=15),
        padding=ft.padding.all(12),
        bgcolor=bgcolor,  # Use the bgcolor passed in the function
        border_radius=ft.border_radius.all(12),
        border=ft.border.all(1, customPrimary_color),
        on_click=on_click,
        ink=True,
        alignment=ft.alignment.center,
        width=70,
        margin=ft.margin.only(top=10),
    )
