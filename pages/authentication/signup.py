import flet as ft
import mysql.connector
from components.fields import CustomInputField
from components.dropdown import CustomDropdown
from components.checkbox import CustomCheckbox
from utils.colors import *
from flet_core import colors
from utils.validation import Validation

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='H4ckm3!_',
    database='fitness_app'
)
cursor = conn.cursor()

class Signup(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()

        # Database connection setup
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="H4ckm3!_",  # change this
            database="fitness_app"
        )
        self.cursor = self.db.cursor()

        def goto_login(e):
            page.go("/login")

        self.expand = True
        self.alignment = ft.alignment.center

        # Input fields
        first_name_field = CustomInputField(hint_text="First Name").get_control()
        last_name_field = CustomInputField(hint_text="Last Name").get_control()
        username_field = CustomInputField(hint_text="Username").get_control()
        password_field = CustomInputField(hint_text="Password", password=True).get_control()
        retype_password_field = CustomInputField(hint_text="Re-type Password", password=True).get_control()

        # Field widths
        for field in [first_name_field, last_name_field]:
            field.width = 295
        for field in [username_field, password_field, retype_password_field]:
            field.width = 600

        # Dropdowns
        month_dropdown = CustomDropdown("Month", [str(i).zfill(2) for i in range(1, 13)]).get_control()
        day_dropdown = CustomDropdown("Day", [str(i).zfill(2) for i in range(1, 32)]).get_control()
        year_dropdown = CustomDropdown("Year", [str(y) for y in range(1960, 2025)]).get_control()
        for dd in [month_dropdown, day_dropdown, year_dropdown]:
            dd.width = 177

        # Gender
        male_cb = CustomCheckbox("Male").get_control()
        female_cb = CustomCheckbox("Female").get_control()
        custom_cb = CustomCheckbox("Custom").get_control()

        # Error text
        self.error_text = ft.Text("", visible=False, color=colors.RED, size=14, weight=ft.FontWeight.BOLD)

        # Signup handler
        def validate_signup(e):
            fname = first_name_field.value.strip()
            lname = last_name_field.value.strip()
            uname = username_field.value.strip()
            pwd = password_field.value.strip()
            re_pwd = retype_password_field.value.strip()

            month, day, year = month_dropdown.value, day_dropdown.value, year_dropdown.value
            gender = "Unspecified"
            if male_cb.value:
                gender = "Male"
            elif female_cb.value:
                gender = "Female"
            elif custom_cb.value:
                gender = "Custom"

            # Basic validation
            if not all([fname, lname, uname, pwd, re_pwd, month, day, year]):
                self.error_text.value = "Please fill out all fields."
                self.error_text.visible = True
                page.update()
                return

            if pwd != re_pwd:
                self.error_text.value = "Passwords do not match!"
                self.error_text.visible = True
                page.update()
                return

            birthday = f"{year}-{month}-{day}"  # MySQL DATE format

            try:
                # Check if username already exists
                self.cursor.execute("SELECT username FROM users WHERE username = %s", (uname,))
                if self.cursor.fetchone():
                    self.error_text.value = "Username already exists."
                    self.error_text.visible = True
                    page.update()
                    return

                # Insert new user
                query = """
                INSERT INTO users (first_name, last_name, birthday, gender, username, password)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(query, (fname, lname, birthday, gender, uname, pwd))
                self.db.commit()

                # Get the new user's ID
                self.cursor.execute("SELECT id FROM users WHERE username = %s", (uname,))
                user_id = self.cursor.fetchone()[0]

                # Store user ID in session
                page.session.set("user_id", user_id)
                page.go("/dashboard")

            except mysql.connector.Error as err:
                self.error_text.value = f"Database error: {err}"
                self.error_text.visible = True
                page.update()

        # Sign Up button
        sign_up_btn = ft.ElevatedButton(
            content=ft.Text("SIGN UP", weight=ft.FontWeight.BOLD, color=customPrimaryBG_color, size=22),
            style=ft.ButtonStyle(bgcolor=customPrimary_color, shape=ft.RoundedRectangleBorder(radius=5)),
            width=600,
            height=45,
            on_click=validate_signup,
        )

        already_btn = ft.TextButton(
            "Already have an account?",
            on_click=goto_login,
            style=ft.ButtonStyle(color=customText_color, text_style=ft.TextStyle(size=18))
        )

        form_container = ft.Column([
            ft.Text("Create a new account", size=35, weight=ft.FontWeight.BOLD, color=customText_color),
            ft.Text("It's always you versus you", size=18, color=customText_color),
            ft.Row([first_name_field, last_name_field]),
            ft.Text("Birthday", size=14, weight=ft.FontWeight.BOLD, color=customText_color),
            ft.Row([month_dropdown, day_dropdown, year_dropdown]),
            ft.Text("Gender", size=14, weight=ft.FontWeight.BOLD, color=customText_color),
            ft.Row([male_cb, female_cb, custom_cb]),
            username_field,
            password_field,
            retype_password_field,
            self.error_text,
            sign_up_btn,
            already_btn,
        ], spacing=12)

        self.content = ft.Row([
            ft.Container(expand=2, padding=20, content=ft.Image(src="assets/imgs/Transparent_logo.png")),
            ft.Container(expand=3, padding=40, content=form_container)
        ])
