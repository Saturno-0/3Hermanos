# views/login_view.py
import flet as ft
# Usamos la lógica real de la base de datos
from database.manager import validar_empleado
from modals.modal_registro import show_modal_nuevo_empleado

class LoginView(ft.View):
    def __init__(self, page: ft.Page):
        # 1. Configuración de la vista
        super().__init__(
            route="/login",
            padding=0
        )
        self.page = page

        # 2. Controles interactivos
        self.nombre_input = ft.TextField(
            autofocus=True,
            hint_text="Nombre",
            width=300,
            height=40,
            border_color="#C4A484",
            border_radius=30,
            border_width=1.5,
            focused_border_color="#A47C5A",
            hint_style=ft.TextStyle(font_family="Inter", color="#C4A484")
        )
        self.password_input = ft.TextField(
            hint_text="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            height=40,
            border_color="#C4A484",
            border_radius=30,
            border_width=1.5,
            focused_border_color="#A47C5A",
            hint_style=ft.TextStyle(font_family="Inter", color="#C4A484")
        )
        self.error_text = ft.Text(color="red", visible=False)
        
        # 3. Lógica de inicio de sesión (REAL)
        def on_login(e):
            
            # Usamos la función real de la base de datos
            empleado = validar_empleado(self.nombre_input.value, self.password_input.value)
            
            if empleado:
                
                self.page.session.set("empleado_id", empleado[0]) 
                
                self.page.session.set("empleado_nombre", empleado[1]) 
                
                self.page.go("/main") 
            else:
                self.error_text.value = "Credenciales incorrectas"
                self.error_text.visible = True
                self.page.update()
        
        cover = ft.Container(
            expand=True, 
            content=ft.Image(
                src="bg.png",
                fit=ft.ImageFit.COVER, 
            )
        )
        
        form = ft.Container(
            bgcolor='#FFFFFF',
            content = ft.Column(
                spacing=0,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Image(src="logo.png", width=300),
                    ft.Text(
                        "Joyería 3 Hermanos", 
                        size=58, 
                        font_family="Poppins",
                        color="#8D8D8D"
                    ),
                    ft.Text(
                        "Bienvenido.",
                        size=58, 
                        font_family="Figtree Medium",
                        color="#BC9475"
                    ),
                    ft.Text(
                        "Por favor, inicia sesión o regístrate\ncomo empleado para continuar",
                        size=15,
                        font_family="Poppins Medium",
                        color="#C4A484", 
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=5),
                    self.nombre_input,
                    self.password_input,
                    self.error_text,
                    ft.Container(height=5),
                    ft.FilledButton(
                        "Iniciar Sesión",
                        width=300,
                        height=40,
                        on_click=on_login,
                        style=ft.ButtonStyle(
                            bgcolor="#C4A484", 
                            shape=ft.RoundedRectangleBorder(radius=30),
                            color="white"
                        )
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text("¿Aun no tienes una cuenta?",font_family="Inter", size=12, color=ft.Colors.GREY),
                            ft.TextButton(
                                "Regístrate aqui", 
                                style=ft.ButtonStyle(
                                    padding=ft.padding.only(left=5),   
                                    color="#C4A484",
                                ),
                                on_click= lambda e: show_modal_nuevo_empleado(page)
                            )
                        ]
                    )
                ]
            ),
            expand=True,
            padding=30,
        ) 
        
        self.controls.append(
            ft.Row([cover, form], expand=True, spacing=0)
        )