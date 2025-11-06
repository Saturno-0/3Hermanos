# login_view.py
import flet as ft
from database.manager import validar_empleado

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
            padding=0
        )
        self.page = page

        # 2. Controles interactivos (Necesitan ser atributos para acceder a sus valores)
        self.nombre_input = ft.TextField(
            label="Nombre",
            width=300,
            height=40,
            border_color="#C4A484",
            border_radius=30,
            border_width=1.5,
            focused_border_color="#A47C5A",
            label_style=ft.TextStyle(size=10, color="#C4A484")
        )
        self.password_input = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            width=300,
            height=40,
            border_color="#C4A484",
            border_radius=30,
            border_width=1.5,
            focused_border_color="#A47C5A",
            label_style=ft.TextStyle(color="#C4A484")
        )
        self.error_text = ft.Text(color="red", visible=False)
        
        # 3. Lógica de inicio de sesión
        def on_login(e):
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
            expand=True, # Hace que el contenedor ocupe todo el espacio disponible
            content=ft.Image(
                src="bg.png",
                fit=ft.ImageFit.COVER,  # Ajusta la imagen para cubrir todo el contenedor
            )
        )
        
        form = ft.Container(
            bgcolor='#FFFFFF',
            content = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5, # Espacio vertical entre elementos
                controls=[
                    # Asumiendo que 'logo.png' está en una carpeta 'assets'
                    # Si no, cambia la ruta a solo "logo.png"
                    ft.Image(src="logo.png", width=300),
                    
                    ft.Text(
                        "Joyería 3 Hermanos", 
                        size=58, 
                        font_family="Poppins Bold",
                        color="#8D8D8D" # Un color gris como en la imagen
                    ),
                    ft.Text(
                        "Bienvenido.",
                        size=58, 
                        weight=ft.FontWeight.BOLD,
                        color="#BC9475" # Color café claro
                    ),
                    
                    ft.Text(
                        "Por favor, inicia sesión o regístrate\ncomo empleado para continuar",
                        size=15,
                        color="#C4A484", # Gris más claro
                        text_align=ft.TextAlign.CENTER
                    ),

                    ft.Container(height=5),

                    self.nombre_input,
                    self.password_input,

                    # Espacio antes del botón
                    ft.Container(height=5),

                    # Botón de Iniciar Sesión
                    ft.FilledButton(
                        "Iniciar Sesión",
                        width=300,
                        height=30,
                        on_click=on_login,
                        style=ft.ButtonStyle(
                            bgcolor="#C4A484", # Color café del botón
                            shape=ft.RoundedRectangleBorder(radius=30), # Totalmente redondeado
                            color="white" # Color del texto
                        )
                    ),
                    
                    # Texto para registrarse
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text("¿Aun no tienes una cuenta?", size=12, color=ft.Colors.GREY),
                            # Hacemos que "Regístrate aqui" parezca un enlace
                            ft.TextButton(
                                "Regístrate aqui", 
                                style=ft.ButtonStyle(
                                    padding=ft.padding.only(left=5),
                                ),
                                # Aquí puedes agregar una función on_click para el registro
                                # on_click=lambda e: print("Ir a registro")
                            )
                        ]
                    )
                ]
            ),
            expand=True,
            padding=30,
        ) 
        
        # 5. Asignar los controles a la vista
        self.controls.append(

            ft.Row([cover, form], expand=True, spacing=0)
        )