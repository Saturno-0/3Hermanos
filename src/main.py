# src/main.py
import flet as ft
# Importa las vistas desde la subcarpeta
from views.login_view import LoginView
from views.main_view import MainView

def main(page: ft.Page):
    # --- Configuración Inicial de la Página ---
    page.window.alignment = ft.alignment.center
    page.window.maximized = True
    page.window.icon = "Icon.ico"
    page.title = "Sistema de Punto de Venta"
    page.theme_mode = ft.ThemeMode.LIGHT

    page.fonts = {
        "Poppins": "Poppins/Poppins-Regular.ttf",
        "Poppins Medium": "Poppins/Poppins-Medium.ttf",
        "Poppins Bold": "Poppins/Poppins-Bold.ttf",
        "Figtree Medium": "Figtree/static/Figtree-Medium.ttf",
        "Inter" : "Inter/static/Inter_18pt-Regular.ttf"
    }

    # --- Diálogo de Confirmación de Cierre de Ventana ---
    def no_click(e):
        page.close(confirm_dialog)

    def yes_click(e):
        page.close(confirm_dialog)
        page.window.destroy()

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Favor de confirmar"),
        content=ft.Text("¿Está seguro de que desea salir?"),
        actions=[
            ft.ElevatedButton("Si", on_click=yes_click),
            ft.OutlinedButton("No", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def handle_window_event(e):
        if e.data == "close":
            page.open(confirm_dialog)

    page.window.prevent_close = True
    page.window.on_event = handle_window_event
    
    # --- Lógica de Enrutamiento (Router) ---
    def route_change(e):
        page.views.clear()

        # Ruta /login
        if page.route == "/login":
            page.views.append(LoginView(page))
        
        # Ruta /main
        elif page.route == "/main":
            if not page.session.get("empleado_id"):
                page.go("/login")
                return
            page.views.append(MainView(page))
        
        page.update()

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    # Configuración inicial
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/login")

# Inicia la aplicación. Asegúrate de que el path a assets_dir sea correcto si lo ejecutas desde afuera de src.
ft.app(target=main, assets_dir="assets")