import flet as ft
from database.manager import agregar_producto, actualizar_producto, obtener_producto_por_clave, eliminar_producto


def show_modal_editar_producto(page, actualizar_lista_callback):
    # Campos del formulario
    busqueda_clave = ft.Container(
        bgcolor="#CCCCCC",
        height=35,
        alignment=ft.alignment.center_left, # Alinea el contenido del contenedor
        padding=ft.padding.only(left=10),
        border_radius=20,
        content=ft.TextField(
            content_padding=ft.padding.only(top=0, bottom=12),
            border=ft.InputBorder.NONE,
            icon  = ft.Icons.SEARCH,
            hint_style=ft.TextStyle(font_family="Inter", size=12),
            text_style=ft.TextStyle(font_family="Inter", size=12),
            hint_text="Busca el producto por clave",
            on_change=lambda e: buscar_producto(e.control.value, page)
        )
    )

    cantidad = ft.TextField(
        label="Cantidad (opcional)", 
        value="1",  # Por defecto 1 (Pieza única)
        keyboard_type="number"
    )

    clave = ft.TextField(hint_text="Clave", label="Clave")
    nombre = ft.TextField(hint_text="Nombre", label="Nombre del Producto", autofocus=True)
    peso = ft.TextField(hint_text="Peso", label="Peso", keyboard_type="number", suffix_text="gr")
    
    kilataje = ft.Dropdown(
        hint_text="Kilataje",
        label="Kilataje",
        options=[
            ft.dropdown.Option("10k"),
            ft.dropdown.Option("14k"),
            ft.dropdown.Option("Italiano"),
        ],
    )

    categoria = ft.Dropdown(
        label="Categoría",
        menu_height=200,
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

    error_text = ft.Text(color="red", visible=False, size=12)
    
    btn_eliminar = ft.ElevatedButton(
        "Eliminar Producto",
        icon=ft.Icons.DELETE,
        icon_color="white",
        color="white",
        bgcolor="red",
        visible=False
    )

    producto_actual = None

    # --- 2. Lógica de Negocio ---

    def generar_clave_automatica(e):
        """Genera la clave basada en Kilataje + Iniciales + Peso + (Contador si existe)"""
        # Validar campos necesarios
        if not (nombre.value and peso.value and kilataje.value):
            error_text.value = "Llena Nombre, Peso y Kilataje primero."
            error_text.visible = True
            page.update()
            return

        try:
            # A) Procesar Kilataje (10k -> 10, Italiano -> ITA)
            k_raw = kilataje.value.lower()
            if "k" in k_raw:
                prefijo_k = k_raw.replace("k", "").strip()
            elif "italiano" in k_raw:
                prefijo_k = "ITA"
            else:
                prefijo_k = k_raw[:2].upper()

            # B) Procesar Nombre (Iniciales)
            palabras = nombre.value.split()
            # Toma la primera letra de cada palabra, mayúscula
            iniciales = "".join([p[0].upper() for p in palabras if p])

            # C) Procesar Peso (Sin puntos)
            peso_clean = peso.value.replace(".", "").replace(",", "").strip()

            # Construir clave base
            clave_base = f"{prefijo_k}{iniciales}{peso_clean}"
            
            # D) Verificar existencia y agregar contador
            clave_final = clave_base
            contador = 1
            
            # Loop infinito hasta encontrar una clave libre
            while obtener_producto_por_clave(clave_final):
                clave_final = f"{clave_base}{contador}"
                contador += 1
            
            # Asignar valor
            clave.value = clave_final
            error_text.visible = False
            clave.focus()
            page.update()

        except Exception as ex:
            error_text.value = f"Error generando clave: {ex}"
            error_text.visible = True
            page.update()


    def buscar_producto(clave_busqueda, page):
        nonlocal producto_actual
        
        # Sincronización: Lo que escribas en el buscador se pone en el campo clave
        # esto ayuda a crear productos rápido si no existen.
        clave.value = clave_busqueda

        if clave_busqueda:
            producto = obtener_producto_por_clave(clave_busqueda)
            if producto:
                # [0]id, [1]clave, [2]nombre, [3]peso, [4]kilataje, [5]categoria (Ajustar índices según tu DB real)
                producto_actual = producto
                # Nota: No sobreescribimos clave.value aquí porque ya lo hicimos arriba con lo que busca el usuario
                nombre.value = producto[2]
                peso.value = str(producto[3])
                kilataje.value = producto[4]
                categoria.value = producto[5]

                if len(producto) > 6: 
                    cantidad.value = str(producto[6]) 
                else:
                    cantidad.value = "1"
                
                error_text.visible = False
                btn_eliminar.visible = True
            else:
                # Si no existe, limpiamos para permitir creación, pero MANTENEMOS la clave
                producto_actual = None
                nombre.value = ""
                peso.value = ""
                kilataje.value = ""
                categoria.value = ""
                cantidad.value = "1"
                btn_eliminar.visible = False
        else:
            # Si borran la búsqueda, limpiamos todo
            producto_actual = None
            clave.value = ""
            nombre.value = ""
            peso.value = ""
            kilataje.value = ""
            categoria.value = ""
            btn_eliminar.visible = False
            
        page.update()

    def guardar_producto(e):
        nonlocal producto_actual
        
        if not all([clave.value, nombre.value, peso.value, kilataje.value, categoria.value]):
            error_text.value = "Todos los campos son obligatorios"
            error_text.visible = True
            page.update()
            return

        qty_val = int(cantidad.value) if cantidad.value else 1
        # Intentar guardar/actualizar
        if producto_actual:
            success = actualizar_producto(
                producto_actual[0], # ID
                clave.value,
                nombre.value,
                peso.value,
                kilataje.value,
                categoria.value,
                qty_val
            )
        else:
            success = agregar_producto(
                clave.value,
                nombre.value,
                peso.value,
                kilataje.value,
                categoria.value,
                qty_val
            )
        
        if success:
            page.close(dialog)
            actualizar_lista_callback()
            # Verificación segura de método opcional
            if hasattr(page, 'nuevo_pedido') and callable(page.nuevo_pedido):
                page.nuevo_pedido(None)
        else:
            # Si falla (probablemente duplicado que se escapó a la validación UI)
            error_text.value = "Error: No se pudo guardar (¿Clave duplicada?)"
            error_text.visible = True
            page.update()

    def confirmar_eliminar(e):
        page.open(confirm_dialog)

    def eliminar_producto_handler(e):
        if producto_actual and eliminar_producto(producto_actual[0]):
            page.close(confirm_dialog)
            # Cierre de seguridad de diálogos superpuestos
            if len(page.views) > 0: 
                # Intentar cerrar el dialogo principal si sigue abierto
                try: page.close(dialog) 
                except: pass

            actualizar_lista_callback()
        else:
            error_text.value = "Error al eliminar el producto"
            error_text.visible = True
            page.update()

    btn_eliminar.on_click = confirmar_eliminar

    # --- 3. Diálogos ---

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar eliminación"),
        content=ft.Text(f"¿Estás seguro de eliminar este producto?"),
        actions=[
            ft.TextButton("Sí, eliminar", on_click=eliminar_producto_handler, style=ft.ButtonStyle(color="red")),
            ft.TextButton("Cancelar", on_click=lambda e: page.close(confirm_dialog)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Botón para generar clave
    btn_generar = ft.TextButton(
        "Generar Clave Automática", 
        icon=ft.Icons.AUTORENEW, 
        style=ft.ButtonStyle(color=ft.Colors.BLUE_GREY),
        on_click=generar_clave_automatica
    )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Column([
            ft.Text("Crear/Editar Producto", weight=ft.FontWeight.BOLD),
            busqueda_clave,
            ft.Divider(height=10, thickness=1)
        ], spacing=10),
        content=ft.Column(
            controls=[
                nombre,
                ft.Row([
                    ft.Column([
                        categoria,
                        kilataje,
                        cantidad
                    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                    
                    ft.Column([
                        peso,
                        clave,
                        # Aquí insertamos el botón justo debajo de la clave
                        ft.Container(content=btn_generar, alignment=ft.alignment.center_right)
                    ], expand=True),
                ], expand=True),
                
                error_text,
                
                ft.Container(
                    content=btn_eliminar,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=10)
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            # Importante: expand=True en el contenido ayuda a que el scroll funcione bien en pantallas chicas
            expand=True 
        ),
        actions=[
            ft.ElevatedButton("Guardar", on_click=guardar_producto, bgcolor="black", color="white"),
            ft.OutlinedButton("Cancelar", on_click=lambda e: page.close(dialog))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        scrollable=True,
        # Ajuste de padding del modal general
        content_padding=ft.padding.symmetric(horizontal=24, vertical=10),
    )
    
    def on_dialog_open(e):
        # Enfocar el nombre o la búsqueda al abrir
        if producto_actual:
            nombre.focus()
        else:
            # Acceso al textfield dentro del container para autofocus (truco de Flet)
            busqueda_clave.content.focus()
    
    dialog.on_open = on_dialog_open
    page.open(dialog)