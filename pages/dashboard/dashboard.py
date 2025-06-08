import flet as ft
from flet_core import colors

from components.nav_button import nav_button_transparent
from utils.colors import customPrimary_color, customPrimaryBG_color
from pages.dashboard.clients_view import get_clients_view
from pages.dashboard.records_view import get_records_view  
from pages.dashboard.home import get_home_view
from pages.dashboard.settings import get_settings_view
from pages.dashboard.chatbot import get_chatbot_view


class Dashboard(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        page.title = "Dashboard"
        page.theme_mode = ft.ThemeMode.DARK

        # Check if user is logged in
        if not page.session.get("user_id"):
            page.go("/login")
            return

        self.expand = True
        self.bgcolor = colors.TRANSPARENT

        # Title Container
        title_container = ft.Container(
            content=ft.Text(
                "FITNESS GYM MANAGEMENT SYSTEM",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=colors.BLACK,
                font_family="Arial"
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor=customPrimary_color,
            border=ft.border.all(2, colors.BLACK),
            border_radius=ft.border_radius.all(8),
            margin=ft.margin.only(top=10),
        )

        self.right_content_column = ft.Column(
            controls=[],
            alignment=ft.MainAxisAlignment.START
        )

        # Left Sidebar
        left_container = ft.Container(
            width=100,
            bgcolor=customPrimaryBG_color,
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Image(
                            src="assets/imgs/Transparent_logo.png",
                            width=100,
                            height=100,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        padding=ft.padding.all(10),
                        alignment=ft.alignment.center
                    ),
                    nav_button_transparent(page, "assets/imgs/btn_imgs_def/home_icon.png", "/home", custom_click=self.on_home_click),
                    nav_button_transparent(page, "assets/imgs/btn_imgs_def/clients_icon.png", "/clients", custom_click=self.on_clients_click),
                    nav_button_transparent(page, "assets/imgs/btn_imgs_def/record_icon.png", "/records", custom_click=self.on_records_click),
                    nav_button_transparent(page, "assets/imgs/btn_imgs_def/robot_icon.png", "/robot", custom_click=self.on_robot_click),
                    nav_button_transparent(page, "assets/imgs/btn_imgs_def/settings_icon.png", "/settings", custom_click=self.on_settings_click),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=25,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )

        # Right Top Buttons
        right_nav_btns = ft.Row(
            controls=[
                nav_button_transparent(page, "assets/imgs/btn_imgs_def/email.png", "/email"),
                nav_button_transparent(page, "assets/imgs/btn_imgs_def/notification.png", "/notification"),
                nav_button_transparent(page, "assets/imgs/btn_imgs_def/menu.png", "/menu"),
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=20,
        )

        # Right Side
        right_container = ft.Container(
            expand=True,
            bgcolor=colors.TRANSPARENT,
            padding=ft.padding.all(20),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[title_container, right_nav_btns],
                        alignment=ft.MainAxisAlignment.START,
                        spacing=1050,
                    ),
                    self.right_content_column
                ],
                alignment=ft.MainAxisAlignment.START,
            )
        )

        # Page Layout
        self.content = ft.Row(
            controls=[left_container, right_container],
            expand=True
        )

        # Load home_view by default
        self.right_content_column.controls.append(get_home_view(self.page))

    def on_home_click(self, e):
        self.right_content_column.controls.clear()
        self.right_content_column.controls.append(get_home_view(self.page))
        self.update()

    def on_clients_click(self, e):
        self.right_content_column.controls.clear()
        self.right_content_column.controls.append(get_clients_view(self.page))
        self.update()

    def on_records_click(self, e):
        self.right_content_column.controls.clear()
        self.right_content_column.controls.append(get_records_view(self.page))
        self.update()

    def on_robot_click(self, e):
        self.right_content_column.controls.clear()
        self.right_content_column.controls.append(get_chatbot_view(self.page))
        self.update()

    def on_settings_click(self, e):
        self.right_content_column.controls.clear()
        self.right_content_column.controls.append(get_settings_view(self.page))
        self.update()
