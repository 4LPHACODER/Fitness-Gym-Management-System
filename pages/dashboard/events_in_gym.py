import os
import shutil
import flet as ft
from datetime import date
from components.fields import CustomInputField
from utils.colors import *
import mysql.connector

class AddEventView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()

        self.page = page
        self.expand = True
        self.alignment = ft.alignment.center

        photos_folder = os.path.expanduser("~/SysProjects/FGMS/event_photos")
        os.makedirs(photos_folder, exist_ok=True)

        self.ensure_table_exists()

        def add_event_to_db(photo_path, event_name, event_date, description):
            try:
                connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='H4ckm3!_',  
                    database='fitness_app'
                )
                cursor = connection.cursor()

                query = """
                    INSERT INTO events (photo_path, event_name, event_date, description)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (photo_path, event_name, event_date, description))
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
            event_name = event_name_field.value.strip()
            event_date = event_date_field.value
            description = description_field.value.strip()
            photo_path = img_display.src

            if not event_name:
                self.page.snack_bar = ft.SnackBar(ft.Text("Event name is required"))
                self.page.snack_bar.open = True
                self.page.update()
                return

            if not event_date:
                self.page.snack_bar = ft.SnackBar(ft.Text("Event date is required"))
                self.page.snack_bar.open = True
                self.page.update()
                return

            add_event_to_db(photo_path, event_name, event_date, description)

            self.page.snack_bar = ft.SnackBar(ft.Text("Event added successfully!"))
            self.page.snack_bar.open = True
            self.page.update()
            page.go("/dashboard")

        img_display = ft.Image(
            src="assets/imgs/profile.png",  # changed here to profile.png
            width=150,
            height=150,
            fit=ft.ImageFit.COVER
        )

        file_picker = ft.FilePicker(on_result=on_file_result)
        self.page.overlay.append(file_picker)

        upload_btn = ft.ElevatedButton(
            "Upload Event Photo",
            on_click=lambda e: file_picker.pick_files(allow_multiple=False)
        )

        event_name_field = CustomInputField(hint_text="Event Name").get_control()
        event_name_field.width = 400

        event_date_field = ft.TextField(
            label="Event Date",
            read_only=True,
            value=date.today().strftime("%Y-%m-%d")
        )

        date_picker = ft.DatePicker(
            on_change=lambda e: event_date_field.update(
                value=date_picker.value.strftime("%Y-%m-%d") if date_picker.value else ""
            )
        )
        self.page.overlay.append(date_picker)
        event_date_field.on_focus = lambda e: date_picker.pick_date()

        description_field = ft.TextField(
            label="Description",
            multiline=True,
            min_lines=3,
            max_lines=5,
            width=400
        )

        done_btn = ft.ElevatedButton("Done", on_click=on_done_click)

        form_container = ft.Column(
            controls=[
                ft.Text("Add New Event", size=35, weight=ft.FontWeight.BOLD, color=customText_color),
                ft.Row([img_display, upload_btn], spacing=20),
                event_name_field,
                event_date_field,
                description_field,
                done_btn
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO
        )

        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=1,
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

    def ensure_table_exists(self):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='H4ckm3!_',  
                database='fitness_app'
            )
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    photo_path VARCHAR(255),
                    event_name VARCHAR(255),
                    event_date DATE,
                    description TEXT
                )
            """)
            connection.commit()
            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            print(f"Database error during table creation: {err}")
