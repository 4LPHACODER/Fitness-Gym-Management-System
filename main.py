import flet as ft
from router import views_handler

def main(page: ft.Page):
    page.title = "SAIYAN MECCA GYM"
    page.theme_mode = ft.ThemeMode.DARK  # Set dark mode

    def route_change(route):
        print(f"Route changed to: {route.route}")

        # Extract base route without query parameters
        base_route = route.route.split('?')[0]
        print(f"Base route extracted: {base_route}")

        page.views.clear()  # Clear the current views
        views = views_handler(page)  # Get the view handlers

        if base_route in views:
            print(f"Adding view for route: {base_route}")
            page.views.append(views[base_route])  # Add the corresponding view
        else:
            print("Route not found, defaulting to /login")
            page.views.append(views["/login"])  # Default to /login view if route is not found

        page.update()  # Ensure the page updates after changing views



    page.on_route_change = route_change  # Set the route change handler
    page.go("/login")  # Initially load the login view

ft.app(target=main, assets_dir="assets")
