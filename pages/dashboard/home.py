import flet as ft
import mysql.connector
from collections import Counter
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils.colors import customPrimary_color
from components.nav_button import nav_button_custom_bg
from datetime import datetime
import os


def generate_base64_pie_chart(data, title, colors_map):
    labels = list(data.keys())
    sizes = list(data.values())
    colors = [colors_map.get(label, 'gray') for label in labels]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    ax.set_title(title)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def generate_base64_bar_chart(data, title, colors):
    labels = list(data.keys())
    values = list(data.values())

    fig, ax = plt.subplots()
    ax.bar(labels, values, color=[colors[i % len(colors)] for i in range(len(labels))])
    ax.set_title(title)
    ax.set_ylabel("Number of Clients")
    plt.xticks(rotation=15)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="H4ckm3!_",
        database="fitness_app"
    )


def fetch_client_data(page: ft.Page):
    # Get user_id from session
    user_id = page.session.get("user_id")
    if not user_id:
        page.go("/login")
        return []

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT gender, fitness_goal FROM clients WHERE user_id = %s", (user_id,))
        clients = cursor.fetchall()
        cursor.close()
        connection.close()
        return clients
    except mysql.connector.Error as err:
        print(f"DB Error: {err}")
        return []


def fetch_events():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM events ORDER BY event_date DESC")
        events = cursor.fetchall()
        cursor.close()
        connection.close()
        return events
    except mysql.connector.Error as err:
        print(f"DB Error: {err}")
        return []


def get_home_view(page: ft.Page) -> ft.Container:
    clients = fetch_client_data(page)
    total_clients = len(clients)

    gender_counter = Counter(c['gender'] for c in clients if c.get('gender'))
    fitness_goal_counter = Counter(c['fitness_goal'] for c in clients if c.get('fitness_goal'))

    gender_colors = {"Male": "blue", "Female": "pink", "Other": "gray"}
    bar_colors = ["#4CAF50", "#FF9800", "#2196F3", "#9C27B0", "#E91E63"]

    pie_base64 = generate_base64_pie_chart(gender_counter, "Sex Distribution", gender_colors)
    bar_base64 = generate_base64_bar_chart(fitness_goal_counter, "Program Distribution", bar_colors)

    event_search = ft.TextField(hint_text="Search Events by name", width=400)
    event_list_view = ft.ListView(spacing=10, height=300)

    def display_events(events):
        event_list_view.controls.clear()
        event_list_view.controls.append(
            ft.Container(
                bgcolor=customPrimary_color,
                padding=10,
                content=ft.Row([
                    ft.Text("Photo", width=150, weight=ft.FontWeight.BOLD, color="black", size=18),
                    ft.Text("Event Name", width=200, weight=ft.FontWeight.BOLD, color="black", size=18),
                    ft.Text("Date", width=140, weight=ft.FontWeight.BOLD, color="black", size=18),
                    ft.Text("Description", expand=True, weight=ft.FontWeight.BOLD, color="black", size=18),
                    ft.Text("Actions", width=120, weight=ft.FontWeight.BOLD, color="black", size=18),
                ])
            )
        )

        for event in events:
            event_date = event.get('event_date')
            event_date_str = event_date.strftime("%Y-%m-%d") if isinstance(event_date, datetime) else str(event_date)
            photo_filename = event.get('photo_path')
            if photo_filename:
                photo_path = os.path.join("event_photos", photo_filename)
                photo_src = photo_path if os.path.isfile(photo_path) else "assets/default_event_photo.png"
            else:
                photo_src = "assets/default_event_photo.png"

            event_id = int(event.get("id"))

            def on_edit_click(e, eid=event_id):
                page.go(f"/edit_event?id={eid}")

            def on_delete_click(e, eid=event_id):
                def confirm_delete(ev):
                    try:
                        connection = get_db_connection()
                        cursor = connection.cursor()
                        cursor.execute("DELETE FROM events WHERE id = %s", (eid,))
                        connection.commit()
                        cursor.close()
                        connection.close()
                    except mysql.connector.Error as err:
                        print(f"DB Error on Delete: {err}")
                    finally:
                        page.dialog.open = False
                        page.update()
                        display_events(fetch_events())

                def cancel_delete(ev):
                    page.dialog.open = False
                    page.update()

                dialog = ft.AlertDialog(
                    title=ft.Text("Confirm Delete"),
                    content=ft.Text(f"Are you sure you want to delete event ID {eid}?"),
                    actions=[
                        ft.TextButton("Cancel", on_click=cancel_delete),
                        ft.TextButton("Delete", on_click=confirm_delete),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    modal=True,
                )

                page.dialog = dialog
                if dialog not in page.overlay:
                    page.overlay.append(dialog)
                page.dialog.open = True
                page.update()

            actions = ft.Row([
                ft.ElevatedButton("Edit", on_click=lambda e, eid=event_id: on_edit_click(e, eid), bgcolor="#4CAF50", color="white"),
                ft.ElevatedButton("Delete", on_click=lambda e, eid=event_id: on_delete_click(e, eid), bgcolor="#2196F3", color="white"),
            ], spacing=5)

            event_list_view.controls.append(
                ft.Container(
                    padding=10,
                    border=ft.border.all(1, "#ddd"),
                    border_radius=5,
                    content=ft.Row([
                        ft.Image(
                            src=photo_src,
                            width=150,
                            height=150,
                            fit=ft.ImageFit.COVER,
                            border_radius=ft.border_radius.all(10)
                        ),
                        ft.Text(event.get('event_name', 'N/A'), width=200, size=16),
                        ft.Text(event_date_str, width=140, size=16),
                        ft.Text(event.get('description', ''), expand=True, size=16),
                        ft.Container(actions, width=120),
                    ])
                )
            )
        page.update()

    def filter_events(e):
        term = event_search.value.lower().strip()
        all_events = fetch_events()
        filtered = [ev for ev in all_events if term in ev.get('event_name', '').lower() or term in ev.get('location', '').lower()]
        display_events(filtered)

    all_events = fetch_events()
    display_events(all_events)
    event_search.on_change = filter_events

    return ft.Container(
        padding=20,
        expand=True,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text(
                    f"Number of Clients: {total_clients}",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                    color=customPrimary_color,
                    text_align=ft.TextAlign.CENTER,
                    expand=True,
                ),
                ft.Divider(height=2),
                ft.Row(
                    expand=True,
                    spacing=20,
                    controls=[
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Sex Distribution", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Image(src_base64=pie_base64, width=300, height=300),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text("Program Distribution", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Image(src_base64=bar_base64, width=400, height=300),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            expand=True,
                        ),
                    ]
                ),
                ft.Divider(height=2),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Events in Gym", size=22, weight=ft.FontWeight.BOLD),
                        nav_button_custom_bg(
                            page,
                            "assets/imgs/btn_imgs_wt/add_icon.png",
                            "/add_event",
                            customPrimary_color,
                        ),
                    ],
                ),
                event_search,
                event_list_view,
            ]
        ),
    )
