import flet as ft
from database.manager import registrar_venta, registrar_apartado

def show_modal_pago(page: ft.Page, productos_con_precio: list, total_venta: float, empleado_id: int, on_venta_exitosa: callable):
    """
    Muestra el modal de cobro con pestañas para Venta Directa y Apartado.
    """
    
    # --- ESTILOS COMPARTIDOS ---
    estilo_input = ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)
    color_primario = '#C39D88'  # Color de tu marca
    color_verde = '#506C64'     # Color secundario/confirmar

    # ==============================================================================
    # PESTAÑA 1: VENTA DIRECTA
    # ==============================================================================
    
    # Selector de método de pago
    radio_metodo_venta = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Efectivo", label="Efectivo"),
            ft.Radio(value="Tarjeta", label="Tarjeta"),
            ft.Radio(value="Transferencia", label="Transferencia"),
        ]),
        value="Efectivo"
    )

    txt_monto_recibido = ft.TextField(
        label="Monto recibido",
        prefix_text="$",
        text_style=estilo_input,
        input_filter=ft.NumbersOnlyInputFilter(),
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.RIGHT,
        border_radius=10,
    )

    lbl_cambio = ft.Text("$0.00", size=25, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY)
    
    btn_confirmar_venta = ft.ElevatedButton(
        "Confirmar Venta",
        icon=ft.Icons.CHECK,
        bgcolor=color_verde,
        color="white",
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        disabled=True, # Se habilita al calcular cambio o cambiar metodo
        width=200
    )

    # Contenedor para inputs de efectivo (se oculta si es tarjeta)
    contenedor_efectivo = ft.Column(
        visible=True,
        controls=[
            ft.Text("Monto Recibido:", size=16),
            txt_monto_recibido,
            ft.Row([
                ft.Text("Cambio:", size=18, weight="bold"),
                lbl_cambio
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ]
    )

    # --- Lógica Venta ---
    def cambiar_metodo_venta(e):
        es_efectivo = (radio_metodo_venta.value == "Efectivo")
        contenedor_efectivo.visible = es_efectivo
        
        # Si no es efectivo, habilitamos el boton directo
        if not es_efectivo:
            btn_confirmar_venta.disabled = False
        else:
            # Si regresamos a efectivo, revalidamos el monto
            validar_monto_venta(None)
            
        page.update()

    def validar_monto_venta(e):
        try:
            monto = float(txt_monto_recibido.value) if txt_monto_recibido.value else 0.0
            cambio = monto - total_venta
            
            lbl_cambio.value = f"${cambio:,.2f}"
            lbl_cambio.color = ft.Colors.GREEN if cambio >= 0 else ft.Colors.RED
            
            # Solo permitir venta si cubre el total
            btn_confirmar_venta.disabled = (monto < total_venta)
            
        except ValueError:
            btn_confirmar_venta.disabled = True
        
        page.update()

    def accion_confirmar_venta(e):
        # Deshabilitar para evitar doble click
        btn_confirmar_venta.disabled = True
        btn_confirmar_venta.text = "Procesando..."
        page.update()

        # Llamar a la BD
        venta_id = registrar_venta(
            empleado_id=empleado_id,
            productos_vendidos=productos_con_precio,
            total=total_venta,
            metodo_pago=radio_metodo_venta.value
        )

        cerrar_y_notificar(venta_id, "Venta")

    # Asignar eventos venta
    radio_metodo_venta.on_change = cambiar_metodo_venta
    txt_monto_recibido.on_change = validar_monto_venta
    btn_confirmar_venta.on_click = accion_confirmar_venta

    tab_venta = ft.Container(
        padding=20,
        content=ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Método de Pago", weight="bold"),
                radio_metodo_venta,
                ft.Divider(),
                contenedor_efectivo,
                ft.Container(expand=True), # Espaciador
                btn_confirmar_venta
            ]
        )
    )

    # ==============================================================================
    # PESTAÑA 2: APARTADO
    # ==============================================================================

    txt_abono_inicial = ft.TextField(
        label="Abono Inicial",
        prefix_text="$",
        text_style=estilo_input,
        input_filter=ft.NumbersOnlyInputFilter(),
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.RIGHT,
        border_radius=10,
    )

    radio_metodo_apartado = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="Efectivo", label="Efectivo"),
            ft.Radio(value="Tarjeta", label="Tarjeta"),
        ]),
        value="Efectivo"
    )

    lbl_restante = ft.Text(f"${total_venta:,.2f}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE)

    btn_confirmar_apartado = ft.ElevatedButton(
        "Crear Apartado",
        icon=ft.Icons.BOOKMARK_ADD,
        bgcolor=ft.Colors.ORANGE_700,
        color="white",
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        disabled=True,
        width=200
    )

    # --- Lógica Apartado ---
    def validar_abono(e):
        try:
            abono = float(txt_abono_inicial.value) if txt_abono_inicial.value else 0.0
            restante = total_venta - abono

            if abono <= 0:
                lbl_restante.value = "Ingresa un abono válido"
                lbl_restante.color = ft.Colors.RED
                btn_confirmar_apartado.disabled = True
            elif abono >= total_venta:
                lbl_restante.value = "¡Liquida en Venta Directa!"
                lbl_restante.color = ft.Colors.BLUE
                btn_confirmar_apartado.disabled = True
            else:
                lbl_restante.value = f"Restan: ${restante:,.2f}"
                lbl_restante.color = ft.Colors.ORANGE
                btn_confirmar_apartado.disabled = False
        except ValueError:
            btn_confirmar_apartado.disabled = True
        
        page.update()

    def accion_confirmar_apartado(e):
        btn_confirmar_apartado.disabled = True
        btn_confirmar_apartado.text = "Guardando..."
        page.update()

        abono = float(txt_abono_inicial.value)
        
        # Llamar a la BD
        apartado_id = registrar_apartado(
            empleado_id=empleado_id,
            productos_apartados=productos_con_precio,
            total_venta=total_venta,
            abono_inicial=abono,
            metodo_pago_abono=radio_metodo_apartado.value
        )
        
        cerrar_y_notificar(apartado_id, "Apartado")

    # Asignar eventos apartado
    txt_abono_inicial.on_change = validar_abono
    btn_confirmar_apartado.on_click = accion_confirmar_apartado

    tab_apartado = ft.Container(
        padding=20,
        content=ft.Column(
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Datos del Primer Abono", weight="bold"),
                txt_abono_inicial,
                ft.Row([
                    ft.Text("Saldo Restante:", size=16),
                    lbl_restante
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Text("Método de Pago (Abono)", weight="bold"),
                radio_metodo_apartado,
                ft.Container(expand=True),
                btn_confirmar_apartado
            ]
        )
    )

    # ==============================================================================
    # DIÁLOGO PRINCIPAL Y UTILIDADES
    # ==============================================================================

    def cerrar_y_notificar(id_resultado, tipo):
        page.close(dlg_modal)
        
        if id_resultado:
            # Éxito
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"¡{tipo} #{id_resultado} registrado con éxito!", weight="bold"),
                bgcolor=ft.Colors.GREEN_700,
                duration=4000
            )
            page.snack_bar.open = True
            on_venta_exitosa() # Limpia el carrito en la vista principal
        else:
            # Error
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al registrar el {tipo}. Intenta de nuevo."),
                bgcolor=ft.Colors.RED_700
            )
            page.snack_bar.open = True
        
        page.update()

    # Pestañas
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Venta Directa", 
                icon=ft.Icons.MONEY,
                content=tab_venta
            ),
            ft.Tab(
                text="Apartado", 
                icon=ft.Icons.BOOKMARK_BORDER,
                content=tab_apartado
            ),
        ],
        expand=True,
    )

    # Cabecera del Modal
    header = ft.Container(
        padding=ft.padding.only(left=20, right=20, top=20),
        content=ft.Column([
            ft.Text("Finalizar Transacción", size=24, weight="bold"),
            ft.Text(f"Total Global: ${total_venta:,.2f}", size=20, color=color_primario, weight="bold"),
        ])
    )

    dlg_modal = ft.AlertDialog(
        modal=True,
        content_padding=0,
        # Usamos un Container con tamaño fijo para que las tabs funcionen bien
        content=ft.Container(
            width=500,
            height=550,
            bgcolor="white",
            border_radius=15,
            content=ft.Column(
                spacing=0,
                controls=[
                    header,
                    ft.Divider(),
                    tabs, # Las tabs ocupan el resto del espacio (expand=True interno)
                    ft.Container( # Botón cancelar discreto al fondo
                        padding=10,
                        alignment=ft.alignment.center_right,
                        content=ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_modal))
                    )
                ]
            )
        )
    )

    page.open(dlg_modal)