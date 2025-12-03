import flet as ft
from datetime import datetime
from database.manager import registrar_venta, registrar_apartado
from utils.printer import imprimir_ticket_venta, imprimir_ticket_apartado

def show_modal_pago(page: ft.Page, productos_con_precio: list, total_venta: float, empleado_id: int, on_venta_exitosa: callable):
    
    # --- ESTILOS ---
    estilo_titulo = ft.TextStyle(size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800)
    color_verde = '#506C64'

    # --- INPUTS DEL CLIENTE (Tu diseño personalizado) ---
    def crear_input_cliente(label, expand=1, teclado=ft.KeyboardType.TEXT, autofocus=False):
        return ft.TextField(
            label=label,
            text_size=17, # Tamaño solicitado
            expand=expand,
            dense=True,           
            content_padding=10,   
            keyboard_type=teclado,
            autofocus=autofocus,
        )

    txt_nombre = crear_input_cliente("Nombre del Cliente", expand=2, autofocus=True)
    txt_telefono = crear_input_cliente("Teléfono", expand=1, teclado=ft.KeyboardType.PHONE)
    txt_direccion = crear_input_cliente("Dirección", expand=2)
    txt_cp = crear_input_cliente("C.P.", expand=1, teclado=ft.KeyboardType.NUMBER)

    contenedor_cliente = ft.Container(
        padding=10,
        bgcolor=ft.Colors.GREY_50,
        border_radius=10,
        border=ft.border.all(1, ft.Colors.GREY_300),
        content=ft.Column([
            ft.Text("Datos del Cliente", style=estilo_titulo),
            ft.Row([txt_nombre, txt_telefono], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([txt_direccion, txt_cp], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=10)
    )

    # ==============================================================================
    # PESTAÑA VENTA DIRECTA
    # ==============================================================================

    radio_metodo_venta = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Efectivo", label="Efectivo"),
            ft.Radio(value="Tarjeta", label="Tarjeta"),
            ft.Radio(value="Transferencia", label="Transferencia"),
        ]),
        value="Efectivo"
    )

    txt_monto_recibido = ft.TextField(
        label="Monto recibido ($)",
        text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.RIGHT,
        border_radius=10,
    )

    lbl_cambio = ft.Text("$0.00", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY)

    # Botón inicial (Antes de cobrar)
    btn_confirmar_venta = ft.ElevatedButton(
        "Cobrar",
        icon=ft.Icons.CHECK_CIRCLE,
        bgcolor=color_verde,
        color="white",
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        disabled=True,
        width=float("inf")
    )

    # --- Lógica Venta ---

    def validar_monto_venta(e):
        try:
            val_str = txt_monto_recibido.value
            if not val_str: val_str = "0"
            monto = float(val_str)
            
            if radio_metodo_venta.value != "Efectivo":
                cambio = 0.0
            else:
                cambio = monto - total_venta
            
            lbl_cambio.value = f"${cambio:,.2f}"
            
            if (radio_metodo_venta.value == "Efectivo" and cambio >= 0) or radio_metodo_venta.value != "Efectivo":
                lbl_cambio.color = ft.Colors.GREEN 
                btn_confirmar_venta.disabled = False
            else:
                lbl_cambio.color = ft.Colors.RED
                btn_confirmar_venta.disabled = True
            
        except ValueError:
            btn_confirmar_venta.disabled = True
        page.update()

    def cambiar_metodo_venta(e):
        if radio_metodo_venta.value != "Efectivo":
            txt_monto_recibido.value = str(total_venta)
            txt_monto_recibido.disabled = True
            validar_monto_venta(None)
        else:
            txt_monto_recibido.value = ""
            txt_monto_recibido.disabled = False
            btn_confirmar_venta.disabled = True
            lbl_cambio.value = "$0.00"
            txt_monto_recibido.focus()
        page.update()

    # --- FUNCIÓN DE TRANSICIÓN A PANTALLA DE ÉXITO ---
    def mostrar_opciones_impresion(folio, datos_cliente, recibido, cambio):
        
        # Función interna para imprimir según el botón presionado
        def imprimir_ticket(e, titulo):
            exito = imprimir_ticket_venta(
                folio=folio,
                fecha=datetime.now().strftime("%d/%m/%y %H:%M"),
                productos=productos_con_precio,
                total=total_venta,
                metodo_pago=radio_metodo_venta.value,
                recibio=recibido,
                cambio=cambio,
                cliente_nombre=datos_cliente['nombre'],
                cliente_numero=datos_cliente['telefono'],
                cliente_direccion=datos_cliente['direccion'],
                titulo_ticket=titulo # Título dinámico (Original/Copia)
            )
            if exito:
                page.snack_bar = ft.SnackBar(ft.Text(f"Imprimiendo {titulo}..."), bgcolor="blue")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error de comunicación con la impresora"), bgcolor="red")
            
            page.snack_bar.open = True
            page.update()

        # Nuevo contenido que reemplazará al formulario
        contenido_exito = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=80),
                ft.Text("¡Venta Registrada!", size=24, weight="bold", color="green"),
                ft.Text(f"Folio: {folio:04d}", size=20, weight="bold"),
                ft.Divider(),
                ft.Text("Opciones de Impresión:", size=16),
                
                # BOTONES DE IMPRESIÓN SEPARADOS
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        ft.ElevatedButton(
                            "Original (Cliente)", 
                            icon=ft.Icons.PRINT, 
                            bgcolor="#C39D88", color="white",
                            height=50,
                            on_click=lambda e: imprimir_ticket(e, "*** ORIGINAL CLIENTE ***")
                        ),
                        ft.ElevatedButton(
                            "Copia (Negocio)", 
                            icon=ft.Icons.PRINT, 
                            bgcolor="#506C64", color="white",
                            height=50,
                            on_click=lambda e: imprimir_ticket(e, "*** COPIA NEGOCIO ***")
                        ),
                    ]
                ),
                ft.Container(height=20),
                ft.OutlinedButton(
                    "Finalizar y Cerrar", 
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: page.close(dlg_modal), 
                    width=200,
                    height=45
                )
            ]
        )
        
        # Reemplazamos el contenido del modal
        dlg_modal.content = ft.Container(
            width=550, height=500, bgcolor="white", border_radius=15, padding=20,
            content=contenido_exito
        )
        # Limpiamos acciones del footer si las hubiera
        dlg_modal.actions = [] 
        dlg_modal.update()

    def accion_confirmar_venta(e):
        # Validar nombre
        if not txt_nombre.value:
            txt_nombre.error_text = "Requerido"
            txt_nombre.update()
            return

        btn_confirmar_venta.disabled = True
        btn_confirmar_venta.text = "Procesando..."
        page.update()

        # Preparar datos
        datos_cliente = {
            "nombre": txt_nombre.value,
            "direccion": txt_direccion.value,
            "cp": txt_cp.value,
            "telefono": txt_telefono.value
        }
        
        monto_recibido = float(txt_monto_recibido.value) if txt_monto_recibido.value else 0.0
        cambio = 0.0
        if radio_metodo_venta.value == "Efectivo":
            cambio = monto_recibido - total_venta
        else:
            monto_recibido = total_venta

        # Guardar en BD
        venta_id, folio = registrar_venta(
            empleado_id=empleado_id,
            productos_vendidos=productos_con_precio,
            total=total_venta,
            metodo_pago=radio_metodo_venta.value,
            cliente_data=datos_cliente
        )

        if venta_id:
            # Si se guardó bien, mostramos la pantalla de impresión
            mostrar_opciones_impresion(folio, datos_cliente, monto_recibido, cambio)
            
            # Ejecutamos callback para limpiar carrito en MainView (en segundo plano)
            on_venta_exitosa()
        else:
            # Error
            page.snack_bar = ft.SnackBar(ft.Text("Error al guardar venta en base de datos"), bgcolor="red")
            page.snack_bar.open = True
            btn_confirmar_venta.disabled = False
            btn_confirmar_venta.text = "Cobrar"
            page.update()

    # Eventos Venta
    txt_monto_recibido.on_change = validar_monto_venta
    txt_monto_recibido.on_submit = lambda e: accion_confirmar_venta(e) if not btn_confirmar_venta.disabled else None
    radio_metodo_venta.on_change = cambiar_metodo_venta
    btn_confirmar_venta.on_click = accion_confirmar_venta

    tab_venta = ft.Container(
        padding=15,
        content=ft.Column([
            ft.Text("Método de Pago", style=estilo_titulo),
            radio_metodo_venta,
            ft.Divider(),
            ft.Row([
                ft.Column([ft.Text("Monto Recibido:"), txt_monto_recibido], expand=True),
                ft.Column([ft.Text("Cambio:", weight="bold"), lbl_cambio], expand=True, horizontal_alignment=ft.CrossAxisAlignment.END),
            ]),
            ft.Container(height=10),
            btn_confirmar_venta
        ])
    )

    # ==============================================================================
    # PESTAÑA APARTADO
    # ==============================================================================

    txt_abono_inicial = ft.TextField(label="Abono Inicial", prefix_text="$", keyboard_type=ft.KeyboardType.NUMBER)
    lbl_restante_apartado = ft.Text(f"${total_venta:,.2f}", size=18, color=ft.Colors.ORANGE)
    
    btn_crear_apartado = ft.ElevatedButton(
        "Crear Apartado", 
        icon=ft.Icons.BOOKMARK, 
        bgcolor=ft.Colors.ORANGE_800, 
        color="white", 
        disabled=True, 
        width=float("inf"),
        height=50
    )

    def validar_apartado(e):
        try:
            val_str = txt_abono_inicial.value
            if not val_str: val_str = "0"
            abono = float(val_str)
            restante = total_venta - abono
            
            # Regla: Abono debe ser mayor a 0 y menor al total (si es total, es venta directa)
            if 0 < abono < total_venta:
                lbl_restante_apartado.value = f"Resta: ${restante:,.2f}"
                lbl_restante_apartado.color = ft.Colors.ORANGE
                btn_crear_apartado.disabled = False
            elif abono >= total_venta:
                lbl_restante_apartado.value = "¡Liquida en Venta Directa!"
                lbl_restante_apartado.color = ft.Colors.BLUE
                btn_crear_apartado.disabled = True
            else:
                lbl_restante_apartado.value = "Monto inválido"
                lbl_restante_apartado.color = ft.Colors.RED
                btn_crear_apartado.disabled = True
        except:
            btn_crear_apartado.disabled = True
        page.update()

    def mostrar_impresion_apartado(folio, datos_cliente, abono, restante):
        # Función interna para imprimir
        def imprimir(e, titulo):
            imprimir_ticket_apartado(
                folio=folio,
                fecha=datetime.now().strftime("%d/%m/%y %H:%M"),
                productos=productos_con_precio,
                total=total_venta,
                abono_inicial=abono,
                restante=restante,
                cliente_nombre=datos_cliente['nombre'],
                titulo_ticket=titulo
            )
            page.snack_bar = ft.SnackBar(ft.Text("Imprimiendo ticket de apartado..."), bgcolor="blue")
            page.snack_bar.open = True
            page.update()

        # Pantalla de éxito para apartado
        contenido_exito = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                ft.Icon(ft.Icons.BOOKMARK_ADDED, color="orange", size=80),
                ft.Text("¡Apartado Creado!", size=24, weight="bold", color="orange"),
                ft.Text(f"Folio: {folio:04d}", size=20, weight="bold"),
                ft.Divider(),
                ft.Text(f"Pendiente de pago: ${restante:,.2f}", size=18, weight="bold"),
                
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.ElevatedButton("Ticket Cliente", icon=ft.Icons.PRINT, on_click=lambda e: imprimir(e, "*** TICKET CLIENTE ***")),
                        ft.ElevatedButton("Ticket Negocio", icon=ft.Icons.PRINT, on_click=lambda e: imprimir(e, "*** CONTROL NEGOCIO ***")),
                    ]
                ),
                ft.Container(height=10),
                ft.OutlinedButton("Finalizar", on_click=lambda e: page.close(dlg_modal))
            ]
        )
        
        dlg_modal.content = ft.Container(
            width=550, height=500, bgcolor="white", border_radius=15, padding=20,
            content=contenido_exito
        )
        dlg_modal.update()

    def accion_apartado(e):
        if not txt_nombre.value:
            txt_nombre.error_text = "Nombre requerido para apartar"
            txt_nombre.update()
            return
        
        btn_crear_apartado.disabled = True
        btn_crear_apartado.text = "Guardando..."
        page.update()

        datos_cliente = {"nombre": txt_nombre.value, "telefono": txt_telefono.value}
        abono = float(txt_abono_inicial.value)
        
        # Llamada a la BD
        apartado_id, folio = registrar_apartado(
            empleado_id, productos_con_precio, total_venta, 
            abono, "Efectivo", datos_cliente # Asumimos efectivo por ahora en abono inicial
        )
        
        if apartado_id:
            restante = total_venta - abono
            mostrar_impresion_apartado(folio, datos_cliente, abono, restante)
            on_venta_exitosa() # Limpiar carrito fondo
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Error al crear apartado"), bgcolor="red")
            page.snack_bar.open = True
            btn_crear_apartado.disabled = False
            page.update()

    txt_abono_inicial.on_change = validar_apartado
    btn_crear_apartado.on_click = accion_apartado

    tab_apartado = ft.Container(
        padding=15,
        content=ft.Column([
            ft.Text("Configuración de Apartado", style=estilo_titulo),
            ft.Text("Ingrese el primer pago para reservar los productos.", size=12, color="grey"),
            ft.Divider(),
            txt_abono_inicial,
            lbl_restante_apartado,
            ft.Container(height=10),
            btn_crear_apartado
        ])
    )

    # ==============================================================================
    # DIÁLOGO PRINCIPAL Y CIERRE
    # ==============================================================================

    def cerrar_y_notificar(id_bd, folio, tipo):
        # Esta función se usa para el APARTADO o errores
        if id_bd:
            page.snack_bar = ft.SnackBar(ft.Text(f"¡{tipo} registrado!"), bgcolor="green")
            on_venta_exitosa()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Error al registrar"), bgcolor="red")
        
        page.snack_bar.open = True
        page.close(dlg_modal)
        page.update()

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Cobrar Venta", icon=ft.Icons.MONEY, content=tab_venta),
            ft.Tab(text="Apartado", icon=ft.Icons.BOOKMARK_BORDER, content=tab_apartado),
        ],
        expand=True
    )

    header = ft.Container(
        padding=20,
        bgcolor="#F9F9F9",
        content=ft.Column([
            ft.Row([
                ft.Text("Finalizar Transacción", size=20, weight="bold"),
                ft.Container(expand=True),
                ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_modal))
            ]),
            ft.Text(f"Total a Pagar: ${total_venta:,.2f}", size=24, color="#C39D88", weight="bold"),
        ])
    )

    dlg_modal = ft.AlertDialog(
        modal=True,
        content_padding=0,
        content=ft.Container(
            width=550,
            height=650, # Altura ajustada para que quepa todo
            bgcolor="white",
            border_radius=15,
            content=ft.Column([
                header,
                contenedor_cliente, 
                ft.Divider(height=1),
                tabs
            ], spacing=0)
        )
    )

    page.open(dlg_modal)