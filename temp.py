import flet as ft
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def create_pie_chart():
    labels = ["Male", "Female"]
    sizes = [5, 2]
    colors = ["blue", "pink"]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def create_bar_chart():
    labels = ["Muscle Gain", "Weight Loss"]
    values = [4, 3]
    colors = ["green", "orange"]

    fig, ax = plt.subplots()
    ax.bar(labels, values, color=colors)
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

def main(page: ft.Page):
    pie_data = create_pie_chart()
    bar_data = create_bar_chart()

    page.add(
        ft.Text("Number of Clients: 7", size=30, weight=ft.FontWeight.BOLD),
        ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Text("Sex Distribution", size=20, weight=ft.FontWeight.BOLD),
                        ft.Image(src_base64=pie_data, width=300, height=300)
                    ])
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Program Distribution", size=20, weight=ft.FontWeight.BOLD),
                        ft.Image(src_base64=bar_data, width=400, height=300)
                    ])
                )
            ],
            spacing=20
        )
    )

ft.app(target=main)
