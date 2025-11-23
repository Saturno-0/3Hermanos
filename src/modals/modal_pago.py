import flet as ft
from database.manager import registrar_venta, registrar_apartado
import logging

def show_modal_pago(page: ft.Page, productos_con_precio: list, total_venta: float, empleado_id: int, on_venta_exitosa: callable):
    """
    Muestra un modal para procesar el pago (Venta o Apartado).
    
    Args:
        page: Instancia de la página de Flet
        productos_con_precio: Lista de tuplas [(producto_tuple, precio_float), ...]
        total_venta: El total calculado
        empleado_id: ID del empleado logueado
        on_venta_exitosa: Función callback para limpiar la sidebar
    """
    
    # --- Controles de la Pestaña "Venta" ---
    
    metodo_pago_venta = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="Efectivo", label="Efectivo"),
                ft.Radio(value="Tarjeta Débito", label="Tarjeta Débito"),
                ft.Radio(value="Tarjeta Crédito", label="Tarjeta Crédito"),
            ],
            spacing=5
        ),
        value="Efectivo" # Valor por defecto
    )
    
    monto_recibido_efectivo = ft.TextField(
        label="Monto recibido:",
        prefix_text="$",
        input_filter=ft.NumbersOnlyInputFilter(),
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.RIGHT,
    )
    
    cambio_efectivo = ft.Text(
        "$0.00", 
        size=22, 
        weight=ft.FontWeight.BOLD, 
        color=ft.colors.GREEN_600
    )
    
    # Contenedor para "Monto Recibido" y "Cambio"
    cont_efectivo = ft.Column(
        [
            monto_recibido_efectivo,
            ft.Row([ft.Text("Cambio:", size=18), cambio_efectivo], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ],
        visible=True # Visible porque "Efectivo" es el default
    )
    
    # --- Controles de la Pestaña "Apartado" ---
    
    monto_abono_inicial = ft.TextField(
        label="Abono Inicial:",
        prefix_text="$",
        input_filter=ft.NumbersOnlyInputFilter(),
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.RIGHT,
        autofocus=True
    )
    
    restan_apartado = ft.Text(
        f"Restan: ${total_venta:,.2f}", 
        size=22, 
        weight=ft.FontWeight.BOLD, 
        color=ft.colors.ORANGE_800
    )

    metodo_pago_abono = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="Efectivo", label="Efectivo"),
                ft.Radio(value="Tarjeta Débito", label="Tarjeta Débito"),
                ft.Radio(value="Tarjeta Crédito", label="Tarjeta Crédito"),
            ],
            spacing=5
        ),
        value="Efectivo" # Valor por defecto
    )
    
    # --- Botones de Acción ---
    
    btn_confirmar_venta = ft.ElevatedButton(
        "Confirmar Venta",
        icon=ft.icons.CHECK_CIRCLE,
        color="white",
        bgcolor=ft.colors.GREEN_700,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
        disabled=True # Se habilita al seleccionar método o pagar
    )
    
    btn_confirmar_apartado = ft.ElevatedButton(
        "Confirmar Apartado",
        icon=ft.icons.BOOKMARK_ADD,
        color="white",
        bgcolor=ft.colors.ORANGE_800,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
        disabled=True # Se habilita al poner un abono válido
    )
    
    # --- Pestañas ---
    
    tabs_pago = ft.Tabs(
        selected_index=0,
        expand=1,
        tabs=[
            ft.Tab(
                text="Venta Directa",
                icon=ft.icons.POINT_OF_SALE,
                content=ft.Column(
                    [
                        ft.Text("Método de Pago:", weight=ft.FontWeight.BOLD),
                        metodo_pago_venta,
                        ft.Divider(height=5),
                        cont_efectivo, # Contenedor de efectivo (monto/cambio)
                        ft.Container(height=10),
                        btn_confirmar_venta
                    ],
                    spacing=10
                ),
            ),
            ft.Tab(
                text="Apartado",
                icon=ft.icons.BOOKMARK,
                content=ft.Column(
                    [
                        monto_abono_inicial,
                        restan_apartado,
                        ft.Divider(height=5),
                        ft.Text("Método de Pago (Abono):", weight=ft.FontWeight.BOLD),
                        metodo_pago_abono,
                        ft.Container(height=10),
                        btn_confirmar_apartado
                    ],
                    spacing=10
                )
            ),
        ]
    )
    
    # --- Diálogo Principal ---
    
    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(ft.icons.PAYMENT),
                ft.Text("Finalizar Venta", weight="bold", size=24)
            ],
            alignment=ft.MainAxisAlignment.START
        ),
        content=ft.Container(
            width=500,
            height=400,
            content=ft.Column(
                [
                    ft.Text(f"Total a pagar: ${total_venta:,.2f}", size=22, weight="bold"),
                    ft.Divider(height=10),
                    tabs_pago
                ],
                tight=True,
                spacing=5
            ),
            padding=5
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.START
    )

    # --- Lógica de la UI del Modal ---
    
    def toggle_venta_button(e=None):
        """Habilita el botón de venta"""
        metodo = metodo_pago_venta.value
        if metodo != "Efectivo":
            btn_confirmar_venta.disabled = False
        else:
            try:
                monto = float(monto_recibido_efectivo.value)
                btn_confirmar_venta.disabled = monto < total_venta
            except (ValueError, TypeError):
                btn_confirmar_venta.disabled = True
        
        cont_efectivo.visible = (metodo == "Efectivo")
        dlg_modal.update()
        
    def calcular_cambio(e):
        try:
            monto = float(e.control.value)
            cambio = monto - total_venta
            cambio_efectivo.value = f"${cambio:,.2f}"
            cambio_efectivo.color = ft.colors.RED_600 if cambio < 0 else ft.colors.GREEN_600
        except (ValueError, TypeError):
            cambio_efectivo.value = "$0.00"
            cambio_efectivo.color = ft.colors.RED_600
        toggle_venta_button()

    def calcular_restante_apartado(e):
        try:
            abono = float(e.control.value)
            if abono <= 0 or abono > total_venta:
                restan_apartado.value = f"Abono inválido"
                restan_apartado.color = ft.colors.RED_600
                btn_confirmar_apartado.disabled = True
            else:
                restante = total_venta - abono
                restan_apartado.value = f"Restan: ${restante:,.2f}"
                restan_apartado.color = ft.colors.ORANGE_800
                btn_confirmar_apartado.disabled = False
        except (ValueError, TypeError):
            restan_apartado.value = f"Restan: ${total_venta:,.2f}"
            restan_apartado.color = ft.colors.ORANGE_800
            btn_confirmar_apartado.disabled = True
        dlg_modal.update()
    
    # Asignar eventos
    metodo_pago_venta.on_change = toggle_venta_button
    monto_recibido_efectivo.on_change = calcular_cambio
    monto_abono_inicial.on_change = calcular_restante_apartado

    # --- Lógica de Confirmación (BD) ---
    
    def confirmar_venta_accion(e):
        btn_confirmar_venta.disabled = True
        btn_confirmar_venta.text = "Procesando..."
        dlg_modal.update()

        metodo = metodo_pago_venta.value
        
        # 1. Preparar datos para la BD
        lista_para_db = []
        for producto_tuple, precio in productos_con_precio:
            # (producto_id, kilataje, precio_unitario)
            lista_para_db.append(
                (producto_tuple[0], producto_tuple[4], precio)
            )
            
        # 2. Llamar al manager
        venta_id = registrar_venta(
            empleado_id=empleado_id,
            productos_vendidos=lista_para_db,
            total=total_venta,
            metodo_pago=metodo
        )
        
        # 3. Mostrar resultado
        page.close(dlg_modal)
        if venta_id:
            on_venta_exitosa() # Limpia la sidebar
            page.snack_bar = ft.SnackBar(ft.Text(f"¡Venta {venta_id} registrada con éxito!"), bgcolor=ft.colors.GREEN_700)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Error al registrar la venta"), bgcolor=ft.colors.RED_700)
        
        page.snack_bar.open = True
        page.update()

    def confirmar_apartado_accion(e):
        btn_confirmar_apartado.disabled = True
        btn_confirmar_apartado.text = "Procesando..."
        dlg_modal.update()

        try:
            abono = float(monto_abono_inicial.value)
        except (ValueError, TypeError):
            abono = 0.0

        metodo_abono = metodo_pago_abono.value

        # 1. Preparar datos
        lista_para_db = []
        for producto_tuple, precio in productos_con_precio:
            # (producto_id, kilataje, precio_unitario)
            lista_para_db.append(
                (producto_tuple[0], producto_tuple[4], precio)
            )
            
        # 2. Llamar al manager
        apartado_id = registrar_apartado(
            empleado_id=empleado_id,
            productos_apartados=lista_para_db,
            total_venta=total_venta,
            abono_inicial=abono,
            metodo_pago_abono=metodo_abono
        )

        # 3. Mostrar resultado
        page.close(dlg_modal)
        if apartado_id:
            on_venta_exitosa() # Limpia la sidebar
            page.snack_bar = ft.SnackBar(ft.Text(f"¡Apartado {apartado_id} registrado con éxito!"), bgcolor=ft.colors.GREEN_700)
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Error al registrar el apartado"), bgcolor=ft.colors.RED_700)
        
        page.snack_bar.open = True
        page.update()

    # Asignar acciones de confirmación
    btn_confirmar_venta.on_click = confirmar_venta_accion
    btn_confirmar_apartado.on_click = confirmar_apartado_accion

    # Habilitar botón de venta si no es efectivo
    toggle_venta_button()
    
    # Mostrar el diálogo
    page.open(dlg_modal)