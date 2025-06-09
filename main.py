import flet as ft
from router import views_handler

def main(page: ft.Page):
    page.title = "SAIYAN MECCA GYM"
    page.theme_mode = ft.ThemeMode.DARK  # Set dark mode
    
    # Track the last route to prevent loops
    last_route = None

    def route_change(route):
        nonlocal last_route
        
        # Extract base route without query parameters
        base_route = route.route.split('?')[0]
        
        # Prevent routing loops
        if base_route == last_route:
            return
            
        print(f"Route changed to: {base_route}")
        last_route = base_route

        # Get the view handlers
        views = views_handler(page)

        # Clear existing views
        page.views.clear()

        # Check if the route exists in our views
        if base_route in views:
            print(f"Adding view for route: {base_route}")
            page.views.append(views[base_route])
        else:
            print(f"Route {base_route} not found, defaulting to /login")
            page.views.append(views["/login"])

        # Force update the page
        page.update()

    # Set up route change handler
    page.on_route_change = route_change
    
    # Initialize with login view
    page.go("/login")

ft.app(target=main, assets_dir="assets")
