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
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


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

    # Machine Learning Analysis Section
    ml_container = ft.Container(
        padding=20,
        border=ft.border.all(1, customPrimary_color),
        border_radius=10,
        bgcolor="#1a1a1a",
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=375,
            spacing=20,
            controls=[
            ft.Container(
                    padding=15,
                    bgcolor=customPrimary_color,
                    border_radius=10,
                    content=ft.Column([
                        ft.Text("Machine Learning Insights", size=24, weight=ft.FontWeight.BOLD, color="black"),
                        ft.Text("Advanced Analytics Dashboard", size=16, color="black", weight=ft.FontWeight.BOLD),
                    ])
                ),
                ft.Container(
                    padding=15,
                    border=ft.border.all(1, customPrimary_color),
                    border_radius=10,
                    bgcolor="#2d2d2d",
                    content=ft.Column([
                        ft.Text("Client Demographics", size=20, weight=ft.FontWeight.BOLD, color=customPrimary_color),
                        ft.Text(f"Total Clients: {total_clients}", size=16, color="white"),
                        ft.ListView(
                            height=100,
                            spacing=10,
                            controls=[
                                ft.Container(
                                    padding=10,
                                    border=ft.border.all(1, customPrimary_color),
                                    border_radius=5,
                                    bgcolor="#363636",
                                    content=ft.Column([
                                        ft.Text(f"{gender}", size=14, weight=ft.FontWeight.BOLD, color=customPrimary_color),
                                        ft.Text(f"{count} clients ({count/total_clients*100:.1f}%)", size=14, color="white"),
                                        ft.ProgressBar(
                                            value=count/total_clients,
                                            color=customPrimary_color,
                                            bgcolor="#1a1a1a",
                                        )
                                    ])
                                )
                                for gender, count in gender_counter.most_common()
                            ]
                        ),
                    ])
                ),
                ft.Container(
                    padding=15,
                    border=ft.border.all(1, customPrimary_color),
                    border_radius=10,
                    bgcolor="#2d2d2d",
                    content=ft.Column([
                        ft.Text("Fitness Goals Analysis", size=20, weight=ft.FontWeight.BOLD, color=customPrimary_color),
                        ft.ListView(
                            height=100,
                            spacing=10,
                            controls=[
                                ft.Container(
                                    padding=10,
                                    border=ft.border.all(1, customPrimary_color),
                                    border_radius=5,
                                    bgcolor="#363636",
                                    content=ft.Column([
                                        ft.Text(f"{goal}", size=14, weight=ft.FontWeight.BOLD, color=customPrimary_color),
                                        ft.Text(f"{count} clients ({count/total_clients*100:.1f}%)", size=14, color="white"),
                                        ft.ProgressBar(
                                            value=count/total_clients,
                                            color=customPrimary_color,
                                            bgcolor="#1a1a1a",
                                        )
                                    ])
                                )
                                for goal, count in fitness_goal_counter.most_common()
                            ]
                        ),
                    ])
                ),
                ft.Container(
                    padding=15,
                    border=ft.border.all(1, customPrimary_color),
                    border_radius=10,
                    bgcolor="#2d2d2d",
                    content=ft.Column([
                        ft.Text("Strategic Recommendations", size=20, weight=ft.FontWeight.BOLD, color=customPrimary_color),
                        ft.ListView(
                            height=300,
                            spacing=10,
                            controls=[
                                ft.Container(
                                    padding=10,
                                    border=ft.border.all(1, customPrimary_color),
                                    border_radius=5,
                                    bgcolor="#363636",
                                    content=ft.Column([
                                        ft.Text("Client Acquisition", size=16, weight=ft.FontWeight.BOLD, color=customPrimary_color),
                                        ft.Text("• Target " + 
                                            ("Female" if gender_counter["Female"] < gender_counter["Male"] else "Male") + 
                                            " clients through specialized marketing", size=14, color="white"),
                                        ft.Text("• Develop programs for " + 
                                            (fitness_goal_counter.most_common(2)[1][0] if len(fitness_goal_counter.most_common(2)) > 1 
                                             else fitness_goal_counter.most_common(1)[0][0]) + 
                                            " programs", size=14, color="white"),
                                    ])
                                ),
                ft.Container(
                    padding=10,
                                    border=ft.border.all(1, customPrimary_color),
                    border_radius=5,
                                    bgcolor="#363636",
                                    content=ft.Column([
                                        ft.Text("Program Development", size=16, weight=ft.FontWeight.BOLD, color=customPrimary_color),
                                        ft.Text("• Create specialized programs for underrepresented goals", size=14, color="white"),
                                        ft.Text("• Develop gender-specific training modules", size=14, color="white"),
                                        ft.Text("• Implement progress tracking systems", size=14, color="white"),
                                    ])
                                ),
                            ]
                        ),
                    ])
                ),
            ]
        )
    )

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
                ml_container,
            ]
        ),
    )
