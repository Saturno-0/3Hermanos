import flet as ft
from database.manager import crear_empleado

def show_modal_nuevo_empleado(page):
    """
    Muestra un modal para agregar un nuevo empleado a la base de datos
    
    Args:
        page: Objeto de página de Flet
    """
    # Campo para el nombre del empleado
    nombre_input = ft.TextField(
        label="Nombre del empleado",
        border_color='#EBEBEB',
        border_radius=7,
        filled=True
    )
    
    # Campo para la contraseña
    password_input = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        border_color='#EBEBEB',
        border_radius=7,
        filled=True
    )
    
    # Campo para confirmar contraseña
    confirm_password_input = ft.TextField(
        label="Confirmar contraseña",
        password=True,
        can_reveal_password=True,
        border_color='#EBEBEB',
        border_radius=7,
        filled=True
    )
    
    # Mensaje de estado (éxito o error)
    mensaje_estado = ft.Text(visible=False, color="red")
    
    # Función para cerrar el modal
    def close_modal(e):
        dialog.open = False
        page.update()
    
    # Función para guardar el nuevo empleado
    def guardar_empleado(e):
        # Validar que todos los campos estén llenos
        if not nombre_input.value or not password_input.value or not confirm_password_input.value:
            mensaje_estado.value = "Todos los campos son obligatorios"
            mensaje_estado.color = "red"
            mensaje_estado.visible = True
            page.update()
            return
        
        # Validar que las contraseñas coincidan
        if password_input.value != confirm_password_input.value:
            mensaje_estado.value = "Las contraseñas no coinciden"
            mensaje_estado.color = "red"
            mensaje_estado.visible = True
            page.update()
            return
        
        # Intentar crear el empleado
        resultado = crear_empleado(
            nombre_input.value,
            password_input.value
        )
        
        if resultado:
            mensaje_estado.value = "Empleado creado exitosamente"
            mensaje_estado.color = "green"
            mensaje_estado.visible = True
            
            # Limpiar campos después de éxito
            nombre_input.value = ""
            password_input.value = ""
            confirm_password_input.value = ""
            
            page.update()
        else:
            mensaje_estado.value = "Error: El usuario ya existe"
            mensaje_estado.color = "red"
            mensaje_estado.visible = True
            page.update()
    
    # Construir el modal
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Registrar nuevo empleado", size=20, weight='bold'),
        content=ft.Container(
            width=400,
            padding=10,
            content=ft.Column(
                [
                    nombre_input,
                    ft.Container(height=5),
                    password_input,
                    ft.Container(height=5),
                    confirm_password_input,
                    ft.Container(height=10),
                    mensaje_estado
                ],
                tight=True
            )
        ),
        actions=[
            ft.ElevatedButton(
                "Registrar",
                bgcolor='#FFCDFA',
                color="black",
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                on_click=guardar_empleado
            ),
            ft.OutlinedButton(
                "Cancelar",
                on_click=close_modal
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    # Mostrar el modal
    page.open(dialog)