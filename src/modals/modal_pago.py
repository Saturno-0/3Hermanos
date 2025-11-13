import flet as ft
from datetime import datetime

def show_modal_pago(page, sale, empleado_id, nuevo_pedido, actualizar_sidebar):
    """
    Muestra un modal para procesar el pago.
    
    Args:
        page: Instancia de la página de Flet
        sale: Objeto Sale con la información de la venta actual
        empleado_id: ID del empleado que realiza la venta
        nuevo_pedido: Función para limpiar el carrito después de la venta
        actualizar_sidebar: Función para actualizar el sidebar después de la venta
    """
    from database.manager import registrar_venta
    
    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Finalizar Venta", weight="bold", size=24),
        content=ft.Container(
            width=500,
            height=350,
            content=ft.Column(
                controls=[
                    ft.Text(f"Total a pagar: ${sale.total:.2f}", size=22, weight="bold"),
                    ft.Divider(),
                    ft.Text("Monto recibido:", size=18),
                    ft.TextField(
                        label="Monto recibido:",
                        prefix_text="$",
                        input_filter=ft.NumbersOnlyInputFilter(),
                        keyboard_type=ft.KeyboardType.NUMBER,
                        autofocus=True,
                        text_align=ft.TextAlign.RIGHT,
                        on_change=lambda e: calcular_cambio(e.control.value)
                    ),
                    
                    ft.Text("Cambio a entregar:", size=18),
                    ft.Text("$0.00", size=25, weight="bold", color=ft.Colors.GREEN),
                    
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Cancelar",
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.RED_100,
                                    color=ft.Colors.BLACK,
                                    shape=ft.RoundedRectangleBorder(radius=7)
                                ),
                                on_click=lambda e: page.close(dlg_modal)
                            ),
                            ft.ElevatedButton(
                                "Confirmar venta",
                                style=ft.ButtonStyle(
                                    bgcolor='#FFCDFA',
                                    color=ft.Colors.BLACK,
                                    shape=ft.RoundedRectangleBorder(radius=7)
                                ),
                                on_click=lambda e: confirmar_venta()
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                ],
                spacing=10
            ),
            padding=20
        )
    )
    
    # Acceder a los controles para actualizar dinámicamente
    monto_recibido = dlg_modal.content.content.controls[3]
    texto_cambio = dlg_modal.content.content.controls[5]
    boton_confirmar = dlg_modal.content.content.controls[6].controls[1]
    
    def calcular_cambio(valor):
        try:
        
            monto = float(valor)
            
            cambio = monto - sale.total
            
            texto_cambio.value = f"${cambio}"
            boton_confirmar.disabled = monto < sale.total
            
            # Si el cambio es negativo, mostrar en rojo
            texto_cambio.color = ft.Colors.RED if cambio < 0 else ft.Colors.GREEN
            
            page.update()
        
        except ValueError:
            # Si hay un error al convertir el valor, no hacemos nada
            pass
    
    def confirmar_venta():
        # Registrar la venta en la base de datos
        venta_id = registrar_venta(
            empleado_id=empleado_id,
            productos_vendidos=sale.productos,
            total=sale.total
        )
        
        if venta_id:
            # Mostrar mensaje de éxito
            page.close(dlg_modal)
            page.open(ft.SnackBar(
                content=ft.Text("¡Venta registrada con éxito!"),
                bgcolor=ft.Colors.GREEN
            ))
            
            # Limpiar el carrito
            nuevo_pedido(None)
            actualizar_sidebar()
        else:
            # Mostrar mensaje de error
            page.close(dlg_modal)
            page.open(ft.SnackBar(
                content=ft.Text("Error al registrar la venta"),
                bgcolor=ft.Colors.RED
            ))
            page.snack_bar.open = True  
        
        page.update()
    
    # Mostrar el diálogo
    page.open(dlg_modal)