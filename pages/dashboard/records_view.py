import flet as ft
import mysql.connector
import os
from datetime import datetime, timedelta
from components.nav_button import nav_button_custom_bg
from components.fields import CustomInputField
from utils.colors import customPrimary_color, customText_color

PROGRAM_SCHEDULE = ["Push Day", "Pull Day", "Leg Day", "Shoulder & Arms", "Rest", "Rest"]

def get_program_for_date(activation_date: datetime, today: datetime):
    days_diff = (today - activation_date).days
    return PROGRAM_SCHEDULE[days_diff % len(PROGRAM_SCHEDULE)]

def get_records_view(page: ft.Page) -> ft.Container:
    # Get user_id from session
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return ft.Container()

    search_input = CustomInputField(hint_text="Search by name or ID")
    search_control = search_input.get_control()
    search_control.width = 600
    search_control.height = 50

    client_list_view = ft.ListView(
        controls=[],
        spacing=10,
        height=600,
        expand=True,
    )

    def fetch_clients():
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="H4ckm3!_",
                database="fitness_app"
            )
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clients WHERE user_id = %s", (user_id,))
            clients = cursor.fetchall()
            cursor.close()
            connection.close()
            return clients
        except mysql.connector.Error as err:
            print(f"DB Error: {err}")
            return []

    def display_clients(clients):
        client_list_view.controls.clear()
        today = datetime.now()

        # Header with wider Name and right aligned Days Left
        client_list_view.controls.append(
            ft.Container(
                bgcolor=customPrimary_color,
                padding=ft.padding.all(10),
                content=ft.Row([
                    ft.Text("Photo", width=200, weight=ft.FontWeight.BOLD, color="black", size=18),
                    ft.Text("Name", width=160, weight=ft.FontWeight.BOLD, color="black", size=18),
                    ft.Text("Program", width=160, weight=ft.FontWeight.BOLD, color="black", size=18),
                    ft.Text("Activation Date", width=160, weight=ft.FontWeight.BOLD, color="black", size=18),
                    ft.Text("Expiration Date", width=160, weight=ft.FontWeight.BOLD, color="black", size=18),
                    ft.Container(
                        width=120,
                        alignment=ft.alignment.center_right,
                        content=ft.Text("Days Left", weight=ft.FontWeight.BOLD, color="black", size=18),
                    ),
                ])
            )
        )

        for client in clients:
            img_src = client['profile_picture_path'] if client['profile_picture_path'] and os.path.exists(client['profile_picture_path']) else "assets/imgs/profile.png"
            try:
                activation_date = datetime.strptime(str(client['activation_date']), "%Y-%m-%d")
            except Exception:
                activation_date = today

            expiration_date = activation_date + timedelta(days=30)
            days_left = max((expiration_date - today).days, 0)
            program = get_program_for_date(activation_date, today)

            client_list_view.controls.append(
                ft.Container(
                    padding=ft.padding.symmetric(vertical=10, horizontal=15),
                    border=ft.border.all(1, "#cccccc"),
                    border_radius=5,
                    content=ft.Row([
                        ft.Image(
                            src=img_src,
                            width=150,
                            height=150,
                            fit=ft.ImageFit.COVER,
                            border_radius=ft.border_radius.all(10)
                        ),
                        ft.Text(f"{client['first_name']} {client['last_name']}", width=200, size=16),
                        ft.Text(program, width=160, size=16),
                        ft.Text(activation_date.strftime("%Y-%m-%d"), width=160, size=16),
                        ft.Text(expiration_date.strftime("%Y-%m-%d"), width=160, size=16),
                        ft.Container(
                            width=120,
                            alignment=ft.alignment.center_right,
                            content=ft.Text(f"{days_left} days", size=16),
                        ),
                    ])
                )
            )
        page.update()

    def filter_clients(_):
        search_term = search_control.value.lower().strip()
        all_clients = fetch_clients()
        filtered = [
            c for c in all_clients
            if search_term in str(c['id']).lower()
            or search_term in f"{c['first_name']} {c['last_name']}".lower()
        ]
        display_clients(filtered)

    # Initial load
    all_clients = fetch_clients()
    display_clients(all_clients)

    # Attach filter on typing
    search_control.on_change = filter_clients

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Clients Record", size=30, weight=ft.FontWeight.BOLD, color=customPrimary_color),
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=search_control,
                            alignment=ft.alignment.center,
                            height=70
                        ),
                        nav_button_custom_bg(
                            page,
                            "assets/imgs/search_clients.png",
                            "/search_clients",
                            customPrimary_color
                        ),
                        nav_button_custom_bg(
                            page,
                            "assets/imgs/filter_clients.png",
                            "/filter_clients",
                            customPrimary_color
                        ),
                    ],
                    spacing=20,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Container(
                    content=client_list_view,
                    height=600
                )
            ],
            spacing=15,
        ),
        expand=True,
    )
