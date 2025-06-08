import flet as ft
import mysql.connector
import os
from components.nav_button import nav_button_custom_bg
from components.fields import CustomInputField
from utils.colors import customPrimary_color, customText_color, customPrimaryBG_color


def get_clients_view(page: ft.Page) -> ft.Container:
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
            cursor.execute("SELECT * FROM clients WHERE user_id = %s ORDER BY id", (user_id,))
            clients = cursor.fetchall()
            cursor.close()
            connection.close()
            return clients
        except mysql.connector.Error as err:
            print(f"DB Error: {err}")
            return []

    def display_clients(clients):
        client_list_view.controls.clear()

        for client in clients:
            profile_path = client.get("profile_picture_path") or ""
            img_src = profile_path if os.path.exists(profile_path) else "assets/imgs/profile.png"
            client_id = int(client["id"])

            # capture id in default args
            def on_edit_click(e, cid=client_id):
                page.go(f"/edit_client?id={cid}")

            def on_delete_click(e, cid=client_id):
                # confirm dialog
                def on_confirm_delete(e_confirm):
                    try:
                        conn = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="H4ckm3!_",
                            database="fitness_app"
                        )
                        cursor = conn.cursor()
                        # 1) delete target
                        cursor.execute("DELETE FROM clients WHERE id = %s", (cid,))
                        # 2) resequence remaining
                        cursor.execute(
                            "UPDATE clients SET id = id - 1 WHERE id > %s", (cid,)
                        )
                        # 3) reset auto_increment
                        cursor.execute("SELECT MAX(id) FROM clients")
                        max_id = cursor.fetchone()[0] or 0
                        cursor.execute(
                            "ALTER TABLE clients AUTO_INCREMENT = %s", (max_id + 1,)
                        )
                        conn.commit()
                        cursor.close()
                        conn.close()
                    except mysql.connector.Error as err:
                        print(f"DB Error on Delete/Resequence: {err}")
                    finally:
                        page.dialog.open = False
                        page.update()
                        display_clients(fetch_clients())

                def on_cancel_delete(e_cancel):
                    page.dialog.open = False
                    page.update()

                dialog = ft.AlertDialog(
                    title=ft.Text("Confirm Delete"),
                    content=ft.Text(f"Are you sure you want to delete client ID {cid}?"),
                    actions=[
                        ft.TextButton("Cancel", on_click=on_cancel_delete),
                        ft.TextButton("Delete", on_click=on_confirm_delete),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    modal=True,
                )
                page.dialog = dialog
                if dialog not in page.overlay:
                    page.overlay.append(dialog)
                page.dialog.open = True
                page.update()

            # build UI
            client_list_view.controls.append(
                ft.Container(
                    padding=ft.padding.all(10),
                    border=ft.border.all(1, customPrimary_color),
                    border_radius=5,
                    content=ft.Row(
                        spacing=20,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Image(
                                src=img_src,
                                width=100,
                                height=100,
                                fit=ft.ImageFit.COVER,
                                border_radius=ft.border_radius.all(10)
                            ),
                            ft.Column(
                                spacing=6,
                                expand=True,
                                controls=[
                                    ft.Text(f"ID: {client_id}", size=14, color=customText_color),
                                    ft.Text(
                                        f"Name: {client['first_name']} {client['last_name']}",
                                        weight=ft.FontWeight.BOLD,
                                        size=16
                                    ),
                                    ft.Text(f"Birthday: {client['birthday']}"),
                                    ft.Text(f"Gender: {client['gender']}"),
                                    ft.Text(f"Fitness Goal: {client['fitness_goal']}"),
                                    ft.Text(f"Activation Date: {client['activation_date']}"),
                                ],
                            ),
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.TextButton(
                                        content=ft.Text("Edit", color=customPrimaryBG_color),
                                        tooltip="Edit Client",
                                        on_click=on_edit_click,
                                        style=ft.ButtonStyle(
                                            bgcolor=customPrimary_color,
                                            shape=ft.RoundedRectangleBorder(radius=5),
                                            padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                        )
                                    ),
                                    ft.TextButton(
                                        content=ft.Text("Delete", color=customPrimaryBG_color),
                                        tooltip="Delete Client",
                                        on_click=on_delete_click,
                                        style=ft.ButtonStyle(
                                            bgcolor=customPrimary_color,
                                            shape=ft.RoundedRectangleBorder(radius=5),
                                            padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                        )
                                    ),
                                ]
                            )
                        ]
                    )
                )
            )
        page.update()

    def filter_clients(_):
        term = search_control.value.lower().strip()
        all_clients = fetch_clients()
        filtered = [
            c for c in all_clients
            if term in str(c['id']).lower() or term in f"{c['first_name']} {c['last_name']}".lower()
        ]
        display_clients(filtered)

    def on_add_client_click(e):
        page.go("/add_client")

    # initial load
    display_clients(fetch_clients())
    search_control.on_change = filter_clients

    return ft.Container(
        content=ft.Column([
            ft.Text("Clients List", size=30, weight=ft.FontWeight.BOLD, color=customPrimary_color),
            ft.Divider(),
            ft.Row([
                ft.Container(content=search_control, alignment=ft.alignment.center, height=70),
                nav_button_custom_bg(page, "assets/imgs/search_clients.png", "/search_clients", customPrimary_color),
                nav_button_custom_bg(page, "assets/imgs/filter_clients.png", "/filter_clients", customPrimary_color),
                ft.Container(
                    content=ft.GestureDetector(
                        content=nav_button_custom_bg(page, "assets/imgs/add_clients.png", "/add_client", customPrimary_color),
                        on_tap=on_add_client_click
                    ),
                    width=200,
                    padding=ft.padding.symmetric(horizontal=10)
                ),
            ], spacing=20, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(content=client_list_view, height=600)
        ], spacing=15),
        expand=True
    )
