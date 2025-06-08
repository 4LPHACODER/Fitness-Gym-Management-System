import flet as ft
import mysql.connector
from components.fields import CustomInputField
from utils.colors import *
from flet_core import colors
from utils.validation import Validation

class Login(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()

        # Database connection setup (change credentials as needed)
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="H4ckm3!_",  # change this
            database="fitness_app"
        )
        self.cursor = self.db.cursor()

        # Go to signup
        def goto_signup(e):
            page.go("/signup")

        # Error message container
        self.error_text = ft.Text(
            "",
            color=colors.RED,
            size=14,
            weight=ft.FontWeight.BOLD,
            visible=False
        )

        # Login logic
        def login_user(e):
            username = username_input.value.strip()
            password = password_input.value.strip()

            # Reset error message
            self.error_text.visible = False
            self.error_text.value = ""
            page.update()

            # Validate input
            if not username or not password:
                self.error_text.value = "Please fill all fields"
                self.error_text.visible = True
                page.update()
                return

            try:
                # First check if username exists
                self.cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
                user = self.cursor.fetchone()

                if not user:
                    self.error_text.value = "Username does not exist"
                    self.error_text.visible = True
                    page.update()
                    return

                # Check password
                if user[1] != password:
                    self.error_text.value = "Incorrect password"
                    self.error_text.visible = True
                    page.update()
                    return

                # Login successful
                user_id = user[0]
                page.session.set("user_id", user_id)
                page.go("/dashboard")

            except mysql.connector.Error as err:
                self.error_text.value = f"Database error: {err}"
                self.error_text.visible = True
                page.update()

        # Input Fields
        username_input = CustomInputField(hint_text="Username").get_control()
        password_input = CustomInputField(hint_text="Password", password=True).get_control()

        # UI layout
        self.expand = True
        self.alignment = ft.alignment.center
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                # Left: Image
                ft.Container(
                    expand=2,
                    padding=20,
                    content=ft.Container(
                        content=ft.Image(src="assets/imgs/login_bg.jpg", fit=ft.ImageFit.COVER),
                        border_radius=20,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                ),
                # Right: Login form
                ft.Container(
                    expand=2,
                    padding=ft.padding.all(40),
                    content=ft.Column(
                        spacing=20,
                        controls=[
                            ft.Text(
                                "Welcome Back",
                                color=customText_color,
                                size=40,
                                weight=ft.FontWeight.BOLD,
                            ),
                            username_input,
                            password_input,
                            self.error_text,
                            ft.ElevatedButton(
                                content=ft.Text(
                                    "LOGIN",
                                    weight=ft.FontWeight.BOLD,
                                    color=customPrimaryBG_color,
                                    size=24
                                ),
                                on_click=login_user,
                                style=ft.ButtonStyle(
                                    bgcolor=customPrimary_color,
                                    shape=ft.RoundedRectangleBorder(radius=5),
                                ),
                                width=600,
                                height=45,
                            ),
                            ft.TextButton(
                                "Don't have an account? Sign up",
                                on_click=goto_signup,
                                style=ft.ButtonStyle(
                                    color=customText_color,
                                    text_style=ft.TextStyle(size=18),
                                    bgcolor=None
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )
