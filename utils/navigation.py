import flet as ft

def navigate_to_signup(page: ft.Page):
    from pages.authentication.signup import Signup
    page.views.clear()
    page.views.append(ft.View(route="/signup", controls=[Signup(page)]))
    page.update()

def navigate_to_login(page: ft.Page):
    from pages.authentication.login import Login
    page.views.clear()
    page.views.append(ft.View(route="/login", controls=[Login(page)]))
    page.update() 