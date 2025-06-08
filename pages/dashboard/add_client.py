import os
import shutil
import flet as ft
from datetime import date
from components.fields import CustomInputField
from components.dropdown import CustomDropdown
from components.checkbox import CustomCheckbox
from utils.colors import *
import mysql.connector

class AddClientView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        self.expand = True
        self.alignment = ft.alignment.center

        # Get user_id from session
        self.user_id = page.session.get("user_id")
        if not self.user_id:
            self.page.go("/login")
            return

        # Folder to store client photos
        photos_folder = os.path.expanduser("~/SysProjects/FGMS/client_photos")
        os.makedirs(photos_folder, exist_ok=True)  # create if not exists

        def add_client_to_db(
            first_name, last_name, birthday, gender,
            health_condition, fitness_goal, activation_date,
            profile_picture_path
        ):
            try:
                connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='H4ckm3!_',  # replace with your actual password
                    database='fitness_app'
                )
                cursor = connection.cursor()

                # Create table if it doesn't exist
                create_table_query = """
                    CREATE TABLE IF NOT EXISTS clients (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        first_name VARCHAR(50) NOT NULL,
                        last_name VARCHAR(50) NOT NULL,
                        birthday DATE,
                        gender VARCHAR(10),
                        health_condition VARCHAR(50),
                        fitness_goal VARCHAR(50),
                        activation_date DATE,
                        profile_picture_path VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                cursor.execute(create_table_query)

                # Insert the new client
                query = """
                    INSERT INTO clients (
                        user_id,
                        first_name, last_name, birthday, gender,
                        health_condition, fitness_goal,
                        activation_date, profile_picture_path
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(query, (
                    self.user_id,
                    first_name, last_name, birthday, gender,
                    health_condition, fitness_goal,
                    activation_date, profile_picture_path
                ))

                connection.commit()
                cursor.close()
                connection.close()

            except mysql.connector.Error as err:
                print(f"Database error: {err}")

        def on_file_result(e: ft.FilePickerResultEvent):
            if e.files:
                src_path = e.files[0].path
                filename = os.path.basename(src_path)
                dest_path = os.path.join(photos_folder, filename)

                # If file with same name exists, add suffix to avoid overwrite
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    filename = f"{base}_{counter}{ext}"
                    dest_path = os.path.join(photos_folder, filename)
                    counter += 1

                try:
                    shutil.copy(src_path, dest_path)
                    img_display.src = dest_path
                    img_display.update()
                except Exception as ex:
                    print(f"Error copying file: {ex}")

        def on_done_click(e):
            first_name = first_name_field.value
            last_name = last_name_field.value

            month_names = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            try:
                month_index = month_names.index(bday_month_dropdown.value) + 1
                birthday_str = f"{bday_year_dropdown.value}-{month_index:02d}-{int(bday_day_dropdown.value):02d}"
            except Exception:
                birthday_str = None

            gender = gender_group.value
            health = health_conditions.value
            goal = fitness_goal.value
            act_date = act_field.value
            profile_pic = img_display.src  # this will be the copied file path

            add_client_to_db(
                first_name, last_name, birthday_str, gender,
                health, goal, act_date, profile_pic
            )

            self.page.snack_bar = ft.SnackBar(ft.Text("Client added successfully!"))
            self.page.snack_bar.open = True
            self.page.update()
            self.page.go("/dashboard")

        # UI Elements
        img_display = ft.Image(
            src="assets/imgs/profile.png",
            width=150,
            height=150,
            fit=ft.ImageFit.COVER
        )

        file_picker = ft.FilePicker(on_result=on_file_result)
        self.page.overlay.append(file_picker)

        upload_btn = ft.ElevatedButton(
            "Upload Picture",
            on_click=lambda e: file_picker.pick_files(allow_multiple=False)
        )

        first_name_field = CustomInputField(hint_text="First Name").get_control()
        last_name_field = CustomInputField(hint_text="Last Name").get_control()
        first_name_field.width = 295
        last_name_field.width = 295

        bday_month_dropdown = CustomDropdown(
            label="Month",
            options=["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]
        ).get_control()

        bday_day_dropdown = CustomDropdown(
            label="Day",
            options=[str(i) for i in range(1, 32)]
        ).get_control()

        bday_year_dropdown = CustomDropdown(
            label="Year",
            options=[str(year) for year in range(1960, 2025)]
        ).get_control()

        gender_group = ft.RadioGroup(
            value="Male",
            content=ft.Row([
                ft.Radio(value="Male", label="Male"),
                ft.Radio(value="Female", label="Female")
            ])
        )

        health_conditions = CustomDropdown(
            label="Health Condition",
            options=["None", "Asthma", "Diabetes", "Heart Disease"]
        ).get_control()
        health_conditions.width = 400

        fitness_goal = CustomDropdown(
            label="Fitness Goal",
            options=["Weight Loss", "Muscle Gain", "Endurance", "Flexibility"]
        ).get_control()
        fitness_goal.width = 400

        act_field = ft.TextField(
            label="Activation Date",
            read_only=True,
            value=date.today().strftime("%Y-%m-%d")
        )

        act_picker = ft.DatePicker(
            on_change=lambda e: act_field.update(
                value=act_picker.value.strftime("%Y-%m-%d") if act_picker.value else ""
            )
        )
        self.page.overlay.append(act_picker)
        act_field.on_focus = lambda e: act_picker.pick_date()

        done_btn = ft.ElevatedButton("Done", on_click=on_done_click)

        form_container = ft.Column(
            controls=[
                ft.Text("Add New Client", size=35, weight=ft.FontWeight.BOLD, color=customText_color),
                ft.Row([img_display, upload_btn], spacing=20),
                ft.Row([first_name_field, last_name_field], spacing=20),
                ft.Text("Birthday"),
                ft.Row([bday_month_dropdown, bday_day_dropdown, bday_year_dropdown], spacing=12),
                ft.Text("Gender"),
                gender_group,
                health_conditions,
                fitness_goal,
                act_field,
                act_picker,
                done_btn
            ],
            spacing=12,
            scroll=ft.ScrollMode.AUTO
        )

        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=2,
                    padding=20,
                    content=ft.Container(
                        content=ft.Image(src="assets/imgs/Transparent_logo.png", fit=ft.ImageFit.COVER),
                        border_radius=20,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                ),
                ft.Container(
                    expand=3,
                    padding=ft.padding.all(40),
                    content=form_container
                ),
            ],
        )
