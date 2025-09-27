# login_view.py
import flet as ft
from datetime import datetime
# Debes definir o importar estas funciones
# from utils import validar_empleado, show_modal_nuevo_empleado 

# NOTA: Simulaciones de funciones que DEBES implementar o importar
def validar_empleado(codigo, password):
    # Lógica de validación real
    return (1, "Empleado de Ejemplo") if codigo == "test" and password == "123" else None

def show_modal_nuevo_empleado(page):
    # Lógica para mostrar el modal de nuevo empleado
    page.snack_bar = ft.SnackBar(ft.Text("Modal de nuevo empleado simulado"))
    page.snack_bar.open = True
    page.update()


class LoginView(ft.View):
    def __init__(self, page: ft.Page):
        # 1. Configuración de la vista
        super().__init__(
            route="/login",
            padding=0, 
            # El bgcolor se establece en el contenedor 'cover' o 'form' si se desea un color por vista
        )
        self.page = page

        # 2. Controles interactivos (Necesitan ser atributos para acceder a sus valores)
        self.codigo_input = ft.TextField(label="Ingrese su nombre", filled=True, autofocus=True,border_color='#EBEBEB', border_radius=7)
        self.password_input = ft.TextField(label="Ingrese su contraseña", password=True, can_reveal_password=True, filled=True, border_color='#EBEBEB', border_radius=7)
        self.error_text = ft.Text(color="red", visible=False)
        
        # 3. Lógica de inicio de sesión
        def on_login(e):
            empleado = validar_empleado(self.codigo_input.value, self.password_input.value)
            if empleado:
                self.page.session.set("empleado_id", empleado[0])
                self.page.session.set("empleado_nombre", empleado[1]) 
                self.page.go("/main")
            else:
                self.error_text.value = "Credenciales incorrectas"
                self.error_text.visible = True
                self.page.update()

        # 4. Estructura de la interfaz
        cover = ft.Container(
            height=page.height * 2,
            padding=100,
            expand=True,
            bgcolor='#FFF1F4',
            content= ft.Image (src="Logo.png")
        )
        
        form = ft.Container(
            content = ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                controls=[
                    ft.Text("Inicio de sesión", size=32, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [ft.Text(datetime.now().strftime("%d/%m/%y"),size=16, weight=ft.FontWeight.BOLD)],
                    alignment=ft.MainAxisAlignment.END
                    ),
                    ft.Text("Identificador",size=25),
                    self.codigo_input,
                    ft.Text("Contraseña",size=25),
                    self.password_input,
                    self.error_text,
                    ft.Container( 
                        content= ft.FilledButton("Iniciar Sesion",
                            bgcolor='#FFCDFA', 
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=7),
                                text_style=ft.TextStyle(size=20)
                            ),
                            height=50,
                            width=700,
                            color=ft.Colors.BLACK,
                            on_click=on_login
                        ), 
                    ),
                    ft.ElevatedButton(
                        "Nuevo usuario",
                        style=ft.ButtonStyle(
                            bgcolor='#FFCDFA',
                            color=ft.Colors.BLACK,
                            shape=ft.RoundedRectangleBorder(radius=7)
                        ),
                        on_click= lambda e: show_modal_nuevo_empleado(self.page)
                    ),
                    ft.Divider(),
                    ft.Row([ft.Text("ó",size=17)], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([ft.Text("Escanea tu gafete",size=25)], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([ft.Icon(ft.Icons.BARCODE_READER, size=100,color='black')], alignment=ft.MainAxisAlignment.CENTER)
                ], 
            ),
            padding=30,
            expand=True
        ) 
        
        # 5. Asignar los controles a la vista
        self.controls.append(
            ft.Row([cover, form], expand=True)
        )