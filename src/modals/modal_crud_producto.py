import flet as ft
from database.manager import agregar_producto, actualizar_producto, obtener_producto_por_clave, eliminar_producto


def show_modal_editar_producto(page, actualizar_lista_callback):
    # Campos del formulario
    busqueda_clave = ft.TextField(
        label="Busqueda Por Clave",
        on_blur=lambda e: buscar_producto(e.control.value, page)
    )
    clave = ft.TextField(label="Clave")
    nombre = ft.TextField(label="Nombre", autofocus=True)
    peso = ft.TextField(label="Peso", keyboard_type="number")
    kilataje = ft.Dropdown(
        label="Kilataje",
        options=[
            ft.dropdown.Option("10k"),
            ft.dropdown.Option("14k"),
            ft.dropdown.Option("Italiano"),
        ],
    )
    # Categoría (sigue igual, como string)
    categoria = ft.Dropdown(
        label="Categoría",
        menu_height= 200,
        label_style=ft.TextStyle(size=12),
        options=[
            ft.dropdown.Option("Cadenas"),
            ft.dropdown.Option("Pulseras"),
            ft.dropdown.Option("Dijes"),
            ft.dropdown.Option("Aros"),
            ft.dropdown.Option("Medallas"),
            ft.dropdown.Option("Aretes"),
            ft.dropdown.Option("Arracadas"),
            ft.dropdown.Option("Gargantillas"),
            ft.dropdown.Option("Anillos Caballero"),
            ft.dropdown.Option("Anillos Dama"),
            ft.dropdown.Option("Argolla Boda"),
            ft.dropdown.Option("Anillo de Diamante"), 
            ft.dropdown.Option("Cruces"),
            ft.dropdown.Option("Relojes"),
            ft.dropdown.Option("Semanarios"),
            ft.dropdown.Option("Broqueles"),
            ft.dropdown.Option("Otro."),     
        ],
    )
    error_text = ft.Text(color="red", visible=False)
    btn_eliminar = ft.ElevatedButton(
        "Eliminar Producto",
        icon=ft.Icons.DELETE,
        icon_color="white",
        color="white",
        bgcolor="red",
        visible=False
    )
    producto_actual = None

    def buscar_producto(clave, page):
        nonlocal producto_actual
        if clave:
            producto = obtener_producto_por_clave(clave)
            if producto:
                producto_actual = producto
                nombre.value = producto[2]
                peso.value = str(producto[3])
                kilataje.value = producto[4]
                categoria.value = producto[5]
                error_text.visible = False
                btn_eliminar.visible = True
            else:
                producto_actual = None
                nombre.value = ""
                peso.value = ""
                kilataje.value = ""
                categoria.value = ""
                btn_eliminar.visible = False
            page.update()

    def guardar_producto(e):
        nonlocal producto_actual
        try:
            peso_val = float(peso.value)
        except ValueError:
            error_text.value = "Peso y debe ser un numero válido"
            error_text.visible = True
            page.update()
            return
        
        if not all([clave.value, nombre.value, peso.value, kilataje.value, categoria.value]):
            error_text.value = "Todos los campos son obligatorios"
            error_text.visible = True
            page.update()
            return

        if producto_actual:
            success = actualizar_producto(
                producto_actual[0],
                clave.value,
                nombre.value,
                peso_val,
                kilataje.value,
                categoria.value
            )
        else:
            success = agregar_producto(
                clave.value,
                nombre.value,
                peso_val,
                kilataje.value,
                categoria.value,
            )
        
        if success:
            page.close(dialog)
            actualizar_lista_callback()
            if hasattr(page, 'nuevo_pedido'):
                page.nuevo_pedido(None)
        else:
            error_text.value = "Error: Código de barras ya existe"
            error_text.visible = True
            page.update()

    def confirmar_eliminar(e):
        page.open(confirm_dialog)

    def eliminar_producto_handler(e):
        if eliminar_producto(producto_actual[0]):
            page.close(confirm_dialog)
            # Cerrar también el diálogo de confirmación si está abierto
            if len(page.views) > 1:
                page.close(page.views[-1])
            actualizar_lista_callback()
        else:
            error_text.value = "Error al eliminar el producto"
            error_text.visible = True
            page.update()

    # Asignar el evento de click al botón eliminar
    btn_eliminar.on_click = confirmar_eliminar

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar eliminación"),
        content=ft.Text(f"¿Estás seguro de eliminar el producto {nombre.value}?"),
        actions=[
            ft.TextButton("Sí", on_click=eliminar_producto_handler),
            ft.TextButton("No", on_click=lambda e: page.close(confirm_dialog)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Column([
            ft.Text("Crear/Editar Producto"),
            busqueda_clave
        ]),
        content=ft.Column(
            controls=[
                nombre,
                ft.Row([
                    ft.Column([
                        categoria,
                        kilataje
                    ], expand=True),
                    ft.Column([
                        peso,
                        clave
                    ], expand=True),
                ], expand=True),
                error_text,
                ft.Container(
                    content=btn_eliminar,
                    alignment=ft.alignment.center,
                    padding=10
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        ),
        actions=[
            ft.ElevatedButton("Guardar", on_click=guardar_producto),
            ft.OutlinedButton("Cancelar", on_click=lambda e: page.close(dialog))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        scrollable=True,
        content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
        inset_padding=ft.padding.all(20)  # Aumenta el padding interno
    )
    
    def on_dialog_open(e):
        clave.focus()
    
    dialog.on_open = on_dialog_open
    page.open(dialog)