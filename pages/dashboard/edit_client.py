import os
import shutil
import flet as ft
from urllib.parse import parse_qs, urlparse
from components.fields import CustomInputField
from components.dropdown import CustomDropdown
from utils.colors import *
import mysql.connector


class EditClientView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        self.expand = True
        self.alignment = ft.alignment.center
        self.client_id = None
        self.client_data = None

        # Get user_id from session
        self.user_id = page.session.get("user_id")
        if not self.user_id:
            self.page.go("/login")
            return

        photos_folder = os.path.expanduser("~/SysProjects/FGMS/client_photos")
        os.makedirs(photos_folder, exist_ok=True)

        self.img_display = ft.Image(src="assets/imgs/profile.png", width=150, height=150, fit=ft.ImageFit.COVER)

        self.first_name_field = CustomInputField(hint_text="First Name").get_control()
        self.last_name_field = CustomInputField(hint_text="Last Name").get_control()

        self.bday_month_dropdown = CustomDropdown("Month", options=[
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]).get_control()
        self.bday_day_dropdown = CustomDropdown("Day", options=[str(i) for i in range(1, 32)]).get_control()
        self.bday_year_dropdown = CustomDropdown("Year", options=[str(y) for y in range(1960, 2025)]).get_control()

        self.gender_group = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="Male", label="Male"),
            ft.Radio(value="Female", label="Female")
        ]))

        self.health_conditions_dropdown = CustomDropdown("Health Condition", options=[
            "None", "Asthma", "Diabetes", "Heart Disease"
        ]).get_control()

        self.fitness_goal_dropdown = CustomDropdown("Fitness Goal", options=[
            "Weight Loss", "Muscle Gain", "Endurance", "Flexibility"
        ]).get_control()

        self.act_field = CustomInputField(hint_text="Activation Date (YYYY-MM-DD)").get_control()

        file_picker = ft.FilePicker(on_result=self.on_file_result)
        page.overlay.append(file_picker)

        upload_btn = ft.ElevatedButton("Upload Picture", on_click=lambda e: file_picker.pick_files(allow_multiple=False))
        save_btn = ft.ElevatedButton("Save Changes", on_click=self.on_save_click)

        # LEFT PANEL - Logo
        left_panel = ft.Container(
            content=ft.Image(
                src="assets/imgs/Transparent_logo.png",
                fit=ft.ImageFit.CONTAIN,
                expand=True
            ),
            expand=2,
            alignment=ft.alignment.center,
            padding=20
        )

        # RIGHT PANEL - Form Fields
        right_panel = ft.Container(
            content=ft.Column([
                self.img_display,
                upload_btn,
                ft.Row([self.first_name_field]),
                ft.Row([self.last_name_field]),
                ft.Row([self.bday_month_dropdown, self.bday_day_dropdown, self.bday_year_dropdown]),
                self.gender_group,
                self.health_conditions_dropdown,
                self.fitness_goal_dropdown,
                self.act_field,
                save_btn
            ], spacing=10),
            expand=2,
            padding=20,
            alignment=ft.alignment.top_center
        )

        # Combine panels in Row layout
        self.content = ft.Row(
            controls=[left_panel, right_panel],
            expand=True
        )

        self.controls = [self.content]

    def on_file_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            src = e.files[0].path
            filename = os.path.basename(src)
            photos_folder = os.path.expanduser("~/SysProjects/FGMS/client_photos")
            dest = os.path.join(photos_folder, filename)

            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest):
                filename = f"{base}_{counter}{ext}"
                dest = os.path.join(photos_folder, filename)
                counter += 1

            shutil.copy(src, dest)
            self.img_display.src = dest
            self.img_display.update()

    def on_save_click(self, e):
        try:
            month_index = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ].index(self.bday_month_dropdown.value) + 1

            birthday = f"{self.bday_year_dropdown.value}-{month_index:02d}-{int(self.bday_day_dropdown.value):02d}"
        except Exception:
            birthday = None

        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='H4ckm3!_', database='fitness_app')
            cursor = conn.cursor()

            # First check if the client belongs to the current user
            cursor.execute("SELECT user_id FROM clients WHERE id = %s", (self.client_id,))
            result = cursor.fetchone()
            if not result or result[0] != self.user_id:
                self.page.snack_bar = ft.SnackBar(ft.Text("Unauthorized access!"), open=True)
                self.page.update()
                return

            query = """
                UPDATE clients SET first_name=%s, last_name=%s, birthday=%s, gender=%s,
                health_condition=%s, fitness_goal=%s, activation_date=%s, profile_picture_path=%s
                WHERE id=%s AND user_id=%s
            """

            cursor.execute(query, (
                self.first_name_field.value,
                self.last_name_field.value,
                birthday,
                self.gender_group.value,
                self.health_conditions_dropdown.value,
                self.fitness_goal_dropdown.value,
                self.act_field.value,
                self.img_display.src if self.img_display.src != "assets/imgs/profile.png" else None,
                self.client_id,
                self.user_id
            ))

            conn.commit()
            cursor.close()
            conn.close()

            self.page.snack_bar = ft.SnackBar(ft.Text("Client updated successfully!"), open=True)
            self.page.update()

        except mysql.connector.Error as err:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Database error: {err}"), open=True)
            self.page.update()

        self.page.go("/dashboard")

    def did_mount(self):
        query_params = parse_qs(urlparse(self.page.route).query)
        self.client_id = query_params.get("id", [None])[0]

        if self.client_id:
            try:
                conn = mysql.connector.connect(host="localhost", user="root", password="H4ckm3!_", database="fitness_app")
                cursor = conn.cursor(dictionary=True)
                # Check if client belongs to current user
                cursor.execute("SELECT * FROM clients WHERE id = %s AND user_id = %s", (self.client_id, self.user_id))
                self.client_data = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if not self.client_data:
                    self.page.snack_bar = ft.SnackBar(ft.Text("Unauthorized access!"), open=True)
                    self.page.update()
                    self.page.go("/dashboard")
                    return
                    
                self.load_client_data()
            except mysql.connector.Error as err:
                print(f"Error loading client: {err}")

    def load_client_data(self):
        if not self.client_data:
            return

        self.first_name_field.value = self.client_data["first_name"]
        self.last_name_field.value = self.client_data["last_name"]

        birthday = self.client_data.get("birthday")
        if birthday:
            self.bday_year_dropdown.value = str(birthday.year)
            self.bday_month_dropdown.value = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ][birthday.month - 1]
            self.bday_day_dropdown.value = str(birthday.day)
        else:
            self.bday_year_dropdown.value = None
            self.bday_month_dropdown.value = None
            self.bday_day_dropdown.value = None

        self.gender_group.value = self.client_data["gender"]
        self.health_conditions_dropdown.value = self.client_data.get("health_condition") or "None"
        self.fitness_goal_dropdown.value = self.client_data.get("fitness_goal") or "Weight Loss"
        self.act_field.value = self.client_data["activation_date"]
        self.img_display.src = self.client_data["profile_picture_path"] or "assets/imgs/profile.png"
        self.update()
