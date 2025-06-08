import flet as ft
import mysql.connector
from components.fields import CustomInputField
from components.dropdown import CustomDropdown
from utils.colors import customText_color, customPrimary_color
from datetime import datetime

def get_settings_view(page: ft.Page) -> ft.Container:
    # Get user_id from session
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.Container()

    # Initialize fields
    first_name_field = CustomInputField(hint_text="First Name").get_control()
    last_name_field = CustomInputField(hint_text="Last Name").get_control()
    username_field = CustomInputField(hint_text="Username").get_control()
    password_field = CustomInputField(hint_text="New Password", password=True).get_control()
    retype_password_field = CustomInputField(hint_text="Re-type New Password", password=True).get_control()

    # Set field widths
    for field in [first_name_field, last_name_field]:
        field.width = 295
    for field in [username_field, password_field, retype_password_field]:
        field.width = 600

    # Birthday dropdowns
    month_dropdown = CustomDropdown("Month", [str(i).zfill(2) for i in range(1, 13)]).get_control()
    day_dropdown = CustomDropdown("Day", [str(i).zfill(2) for i in range(1, 32)]).get_control()
    year_dropdown = CustomDropdown("Year", [str(y) for y in range(1960, 2025)]).get_control()
    for dd in [month_dropdown, day_dropdown, year_dropdown]:
        dd.width = 177

    # Gender radio group
    gender_group = ft.RadioGroup(
        value="Male",
        content=ft.Row([
            ft.Radio(value="Male", label="Male"),
            ft.Radio(value="Female", label="Female"),
            ft.Radio(value="Custom", label="Custom")
        ])
    )

    # Error/Success message
    message_text = ft.Text("", color=customText_color)

    def load_user_data():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="H4ckm3!_",
                database="fitness_app"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()

            if user_data:
                first_name_field.value = user_data["first_name"]
                last_name_field.value = user_data["last_name"]
                username_field.value = user_data["username"]
                
                # Set birthday
                if user_data["birthday"]:
                    birthday = user_data["birthday"]
                    month_dropdown.value = str(birthday.month).zfill(2)
                    day_dropdown.value = str(birthday.day).zfill(2)
                    year_dropdown.value = str(birthday.year)
                
                # Set gender
                gender_group.value = user_data["gender"] or "Male"

                page.update()
        except mysql.connector.Error as err:
            print(f"Error loading user data: {err}")

    def on_save_click(e):
        try:
            # Get values
            fname = first_name_field.value.strip()
            lname = last_name_field.value.strip()
            uname = username_field.value.strip()
            pwd = password_field.value.strip()
            re_pwd = retype_password_field.value.strip()

            # Validate required fields
            if not all([fname, lname, uname]):
                message_text.value = "Please fill out all required fields."
                message_text.color = "red"
                page.update()
                return

            # Check if passwords match if provided
            if pwd and pwd != re_pwd:
                message_text.value = "Passwords do not match!"
                message_text.color = "red"
                page.update()
                return

            # Format birthday
            birthday = f"{year_dropdown.value}-{month_dropdown.value}-{day_dropdown.value}"

            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="H4ckm3!_",
                database="fitness_app"
            )
            cursor = conn.cursor()

            # Check if username is taken by another user
            cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", (uname, user_id))
            if cursor.fetchone():
                message_text.value = "Username already taken!"
                message_text.color = "red"
                page.update()
                return

            # Update user data
            if pwd:  # If password is provided, update it too
                query = """
                    UPDATE users 
                    SET first_name=%s, last_name=%s, username=%s, password=%s,
                        birthday=%s, gender=%s
                    WHERE id=%s
                """
                cursor.execute(query, (fname, lname, uname, pwd, birthday, gender_group.value, user_id))
            else:  # Update without changing password
                query = """
                    UPDATE users 
                    SET first_name=%s, last_name=%s, username=%s,
                        birthday=%s, gender=%s
                    WHERE id=%s
                """
                cursor.execute(query, (fname, lname, uname, birthday, gender_group.value, user_id))

            conn.commit()
            cursor.close()
            conn.close()

            message_text.value = "Profile updated successfully!"
            message_text.color = "green"
            page.update()

        except mysql.connector.Error as err:
            message_text.value = f"Database error: {err}"
            message_text.color = "red"
            page.update()

    def on_logout_click(e):
        # Clear session
        page.session.clear()
        # Redirect to login
        page.go("/login")

    # Load user data when view is created
    load_user_data()

    # Create the settings form
    settings_form = ft.Column(
        controls=[
            ft.Text("Account Settings", size=35, weight=ft.FontWeight.BOLD, color=customText_color),
            ft.Row([first_name_field, last_name_field], spacing=20),
            username_field,
            ft.Text("Change Password (optional)", size=16, weight=ft.FontWeight.BOLD, color=customText_color),
            password_field,
            retype_password_field,
            ft.Text("Birthday", size=16, weight=ft.FontWeight.BOLD, color=customText_color),
            ft.Row([month_dropdown, day_dropdown, year_dropdown], spacing=12),
            ft.Text("Gender", size=16, weight=ft.FontWeight.BOLD, color=customText_color),
            gender_group,
            message_text,
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        "Save Changes",
                        on_click=on_save_click,
                        style=ft.ButtonStyle(
                            bgcolor=customPrimary_color,
                            color="white"
                        )
                    ),
                    ft.ElevatedButton(
                        "Logout",
                        on_click=on_logout_click,
                        style=ft.ButtonStyle(
                            bgcolor="red",
                            color="white"
                        )
                    )
                ],
                spacing=20
            )
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO
    )

    return ft.Container(
        content=settings_form,
        padding=20
    ) 