import flet as ft
from database.manager import agregar_producto, actualizar_producto, obtener_producto_por_clave, eliminar_producto

def show_modal_editar_producto(page, actualizar_lista_callback):
    
    busqueda_clave = ft.Container(
        bgcolor="#CCCCCC",
        height=35,
        alignment=ft.alignment.center_left,
        padding=ft.padding.only(left=10),
        border_radius=20,
        content=ft.TextField(
            content_padding=ft.padding.only(top=0, bottom=12),
            border=ft.InputBorder.NONE,
            icon=ft.Icons.SEARCH,
            hint_style=ft.TextStyle(font_family="Inter", size=12),
            text_style=ft.TextStyle(font_family="Inter", size=12),
            hint_text="Busca el producto por clave",
            on_change=lambda e: buscar_producto(e.control.value, page)
        )
    )

    # Switch para activar modo masivo
    sw_modo_masivo = ft.Switch(label="Ingreso Masivo (Lote)", label_style=ft.TextStyle(font_family="Inter", size=15), value=False)

    # Campos Comunes
    nombre = ft.TextField(label="Nombre del Producto", autofocus=True)
    
    kilataje = ft.Dropdown(
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

    # --- CAMPOS MODO INDIVIDUAL ---
    peso = ft.TextField(label="Peso", keyboard_type="number", suffix_text="gr", expand=True)
    clave = ft.TextField(label="Clave", expand=True)
    cantidad = ft.TextField(label="Cantidad", value="1", keyboard_type="number", width=100) # Por defecto 1
    
    # Contenedor para agrupar controles individuales
    contenedor_individual = ft.Column([
        ft.Row([peso, cantidad], spacing=10),
        clave
    ], spacing=10)

    # --- CAMPOS MODO MASIVO ---
    # Campo grande para escribir muchos pesos
    pesos_masivos = ft.TextField(
        label="Lista de Pesos (Escribe uno y da Enter)",
        multiline=True,
        min_lines=3,
        max_lines=4,
        keyboard_type=ft.KeyboardType.NUMBER,
        hint_text="Ejemplo:\n2.5\n3.1\n2.5",
        visible=False # Oculto al inicio
    )
    
    lbl_instruccion_masiva = ft.Text(
        "Se generará una clave única automática para cada peso ingresado.", 
        size=12, color="grey", visible=False
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

    # --- 2. Lógica de Interfaz ---

    def cambiar_modo(e):
        es_masivo = sw_modo_masivo.value
        
        # Alternar visibilidad
        contenedor_individual.visible = not es_masivo
        pesos_masivos.visible = es_masivo
        lbl_instruccion_masiva.visible = es_masivo
        busqueda_clave.visible = not es_masivo # No buscamos en modo masivo
        
        # El botón de generar clave manual se oculta en masivo
        btn_generar.visible = not es_masivo
        
        # Si activamos masivo, enfocamos el campo de pesos
        if es_masivo:
            pesos_masivos.focus()
        else:
            nombre.focus()
            
        page.update()

    sw_modo_masivo.on_change = cambiar_modo

    # --- 3. Lógica de Negocio (Claves) ---

    def generar_clave_logica(k_val, nom_val, peso_val):
        """Función auxiliar pura para crear la clave string"""
        # A) Kilataje
        k_raw = k_val.lower()
        if "italiano" in k_raw: prefijo = "ITA"
        elif "k" in k_raw: prefijo = k_raw.replace("k", "").strip()
        else: prefijo = k_raw[:2].upper()

        # B) Iniciales
        palabras = nom_val.split()
        iniciales = "".join([p[0].upper() for p in palabras if p])

        # C) Peso
        peso_clean = str(peso_val).replace(".", "").replace(",", "").strip()

        # Base
        base = f"{prefijo}{iniciales}{peso_clean}"
        
        # D) Anti-colisión
        final = base
        contador = 1
        while obtener_producto_por_clave(final):
            final = f"{base}{contador}"
            contador += 1
            
        return final

    def generar_clave_automatica_ui(e):
        """Botón manual para el modo individual"""
        if not (nombre.value and peso.value and kilataje.value):
            error_text.value = "Faltan datos para generar clave."
            error_text.visible = True
            page.update()
            return
        
        try:
            nueva_clave = generar_clave_logica(kilataje.value, nombre.value, peso.value)
            clave.value = nueva_clave
            error_text.visible = False
            page.update()
        except Exception as ex:
            error_text.value = str(ex)
            error_text.visible = True
            page.update()

    def buscar_producto(clave_busqueda, page):
        nonlocal producto_actual
        
        # Si buscan, desactivamos modo masivo forzosamente
        if sw_modo_masivo.value:
            sw_modo_masivo.value = False
            cambiar_modo(None)

        clave.value = clave_busqueda

        if clave_busqueda:
            producto = obtener_producto_por_clave(clave_busqueda)
            if producto:
                producto_actual = producto
                nombre.value = producto[2]
                peso.value = str(producto[3])
                kilataje.value = producto[4]
                categoria.value = producto[5]
                cantidad.value = str(producto[6]) if len(producto) > 6 else "1"
                
                error_text.visible = False
                btn_eliminar.visible = True
            else:
                producto_actual = None
                # Limpiamos para permitir creación
                nombre.value = ""
                peso.value = ""
                kilataje.value = ""
                categoria.value = ""
                cantidad.value = "1"
                btn_eliminar.visible = False
        else:
            producto_actual = None
            btn_eliminar.visible = False
            
        page.update()

    def guardar_producto(e):
        nonlocal producto_actual
        
        # Validaciones comunes
        if not (nombre.value and kilataje.value and categoria.value):
            error_text.value = "Nombre, Kilataje y Categoría son obligatorios."
            error_text.visible = True
            page.update()
            return

        try:
            # --- GUARDADO MASIVO ---
            if sw_modo_masivo.value:
                texto_pesos = pesos_masivos.value.strip()
                if not texto_pesos:
                    error_text.value = "Ingresa al menos un peso."
                    error_text.visible = True
                    page.update()
                    return
                
                # Separar por líneas
                lista_pesos_raw = texto_pesos.split('\n')
                guardados = 0
                
                for p_str in lista_pesos_raw:
                    p_str = p_str.strip()
                    if not p_str: continue # saltar lineas vacias
                    
                    try:
                        peso_float = float(p_str)
                        # 1. Generar clave única para este peso
                        clave_gen = generar_clave_logica(kilataje.value, nombre.value, p_str)
                        
                        # 2. Guardar
                        # Nota: En masivo asumimos cantidad 1 por item, ya que suelen ser piezas únicas con ese peso exacto.
                        # Si quieres usar el campo cantidad, cámbialo aquí.
                        agregar_producto(
                            clave_gen,
                            nombre.value,
                            peso_float,
                            kilataje.value,
                            categoria.value,
                            1 # Cantidad por defecto 1 en masivo
                        )
                        guardados += 1
                    except ValueError:
                        print(f"Saltando valor no numérico: {p_str}")
                
                if guardados > 0:
                    page.close(dialog)
                    actualizar_lista_callback()
                    page.snack_bar = ft.SnackBar(ft.Text(f"¡{guardados} productos agregados!"), bgcolor="green")
                    page.snack_bar.open = True
                    page.update()
                else:
                    error_text.value = "No se pudo guardar ningún peso válido."
                    error_text.visible = True
                    page.update()

            # --- GUARDADO INDIVIDUAL (Tu lógica original) ---
            else:
                if not (clave.value and peso.value):
                    error_text.value = "Clave y Peso son obligatorios."
                    error_text.visible = True
                    page.update()
                    return

                qty_val = int(cantidad.value) if cantidad.value else 1
                
                if producto_actual:
                    success = actualizar_producto(
                        producto_actual[0], clave.value, nombre.value,
                        float(peso.value), kilataje.value, categoria.value, qty_val
                    )
                else:
                    success = agregar_producto(
                        clave.value, nombre.value,
                        float(peso.value), kilataje.value, categoria.value, qty_val
                    )
                
                if success:
                    page.close(dialog)
                    actualizar_lista_callback()
                    page.snack_bar = ft.SnackBar(ft.Text("Producto guardado"), bgcolor="green")
                    page.snack_bar.open = True
                    page.update()
                else:
                    error_text.value = "Error: Clave duplicada."
                    error_text.visible = True
                    page.update()

        except Exception as ex:
            error_text.value = f"Error: {ex}"
            error_text.visible = True
            page.update()

    # --- Eliminar (Igual) ---
    def confirmar_eliminar(e):
        page.open(confirm_dialog)

    def eliminar_producto_handler(e):
        if producto_actual and eliminar_producto(producto_actual[0]):
            page.close(confirm_dialog)
            try: page.close(dialog) 
            except: pass
            actualizar_lista_callback()
        else:
            error_text.value = "Error al eliminar"
            page.update()

    btn_eliminar.on_click = confirmar_eliminar

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirmar eliminación"),
        content=ft.Text(f"¿Borrar este producto?"),
        actions=[
            ft.TextButton("Sí", on_click=eliminar_producto_handler, style=ft.ButtonStyle(color="red")),
            ft.TextButton("Cancelar", on_click=lambda e: page.close(confirm_dialog)),
        ],
    )

    btn_generar = ft.TextButton(
        "Generar Clave Auto", 
        icon=ft.Icons.AUTORENEW, 
        style=ft.ButtonStyle(color=ft.Colors.BLUE_GREY),
        on_click=generar_clave_automatica_ui
    )

    # --- Estructura del Modal ---
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Column([
            ft.Text("Gestión de Productos", weight=ft.FontWeight.BOLD),
            busqueda_clave, # Solo visible en individual
            sw_modo_masivo, # EL SWITCH NUEVO
            ft.Divider(height=10, thickness=1)
        ], spacing=10),
        
        content=ft.Column(
            controls=[
                nombre,
                ft.Row([
                    ft.Column([
                        categoria,
                        kilataje,
                        # Cantidad solo visible en individual (en masivo se asume 1)
                        # O puedes moverlo fuera si quieres definir cantidad masiva
                    ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                    
                    ft.Column([
                        # Aquí alternamos entre el contenedor individual y el campo masivo
                        contenedor_individual,
                        pesos_masivos,
                        lbl_instruccion_masiva,
                        
                        ft.Container(content=btn_generar, alignment=ft.alignment.center_right)
                    ], expand=True),
                ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
                
                error_text,
                
                ft.Container(
                    content=btn_eliminar,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=10)
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True 
        ),
        actions=[
            ft.ElevatedButton("Guardar", on_click=guardar_producto, bgcolor="black", color="white"),
            ft.OutlinedButton("Cancelar", on_click=lambda e: page.close(dialog))
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        scrollable=True,
        content_padding=ft.padding.symmetric(horizontal=24, vertical=10),
    )
    
    def on_dialog_open(e):
        if producto_actual:
            nombre.focus()
        else:
            busqueda_clave.content.focus()
    
    dialog.on_open = on_dialog_open
    page.open(dialog)