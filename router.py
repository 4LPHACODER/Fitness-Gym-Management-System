import flet as ft
from pages.authentication.login import Login
from pages.authentication.signup import Signup
from pages.dashboard.dashboard import Dashboard
from pages.dashboard.add_client import AddClientView
from pages.dashboard.clients_view import get_clients_view
from pages.dashboard.records_view import get_records_view
from pages.dashboard.edit_client import EditClientView
from pages.dashboard.events_in_gym import AddEventView  # <-- import AddEventView here
from flet_core import colors


def views_handler(page: ft.Page):
    return {
        "/login": ft.View(
            route="/login",
            controls=[Login(page)],
        ),
        "/signup": ft.View(
            route="/signup",
            controls=[Signup(page)],
        ),
        "/dashboard": ft.View(
            route="/dashboard",
            controls=[Dashboard(page)],
        ),
        "/add_client": ft.View(
            route="/add_client",
            controls=[AddClientView(page)],
            scroll=ft.ScrollMode.AUTO,
            appbar=ft.AppBar(title=ft.Text("Add Client"), bgcolor=colors.SURFACE_VARIANT)
        ),
        "/edit_client": ft.View(
            route="/edit_client",
            controls=[EditClientView(page)],
            scroll=ft.ScrollMode.AUTO,
            appbar=ft.AppBar(title=ft.Text("Edit Client"), bgcolor=colors.SURFACE_VARIANT)
        ),
        "/add_event": ft.View(
            route="/add_event",
            controls=[AddEventView(page)],
            scroll=ft.ScrollMode.AUTO,
            appbar=ft.AppBar(title=ft.Text("Add Event"), bgcolor=colors.SURFACE_VARIANT)
        ),
    }
