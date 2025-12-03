import flet as ft
import csv
import io
from datetime import datetime
from database.manager import (
    obtener_ventas_por_empleado_hoy,
    obtener_total_ventas_hoy,
    obtener_productos, 
    obtener_detalle_ventas_hoy, # <--- NUEVA FUNCIÓN
    exportar_ventas_csv,
    exportar_inventario_csv
)
from utils.printer import imprimir_corte_caja, imprimir_inventario # <--- NUEVAS FUNCIONES

def show_modal_corte(page):
    
    # 1. Obtener datos frescos
    ventas_por_empleado = obtener_ventas_por_empleado_hoy()
    total_ventas = obtener_total_ventas_hoy()
    inventario = obtener_productos()
    detalle_vendidos = obtener_detalle_ventas_hoy() # Datos para tabla detallada
    
    # 2. Configurar FilePicker
    file_picker = ft.FilePicker()
    if file_picker not in page.overlay:
        page.overlay.append(file_picker)
    page.update()
    
    csv_temp_data = {"contenido": "", "nombre": ""}
    
    def on_save_result(e: ft.FilePickerResultEvent):
        if e.path:
            try:
                with open(e.path, "w", newline='', encoding='utf-8') as f:
                    f.write(csv_temp_data["contenido"])
                page.snack_bar = ft.SnackBar(ft.Text("Archivo guardado"), bgcolor="green")
                page.snack_bar.open = True
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
    
    file_picker.on_result = on_save_result
    
    def handle_download(e, tipo_reporte):
        # ... (Tu lógica de CSV se mantiene igual, llamará al nuevo exportar_ventas_csv del manager) ...
        try:
            fecha = datetime.now().strftime("%d_%m_%Y")
            if tipo_reporte == "ventas":
                datos = exportar_ventas_csv() # Ahora trae detalle
                nombre_archivo = f"Corte_Detallado_{fecha}.csv"
            else:
                datos = exportar_inventario_csv()
                nombre_archivo = f"Inventario_Total_{fecha}.csv"
            
            output = io.StringIO()
            writer = csv.writer(output)
            for fila in datos: writer.writerow(fila)
            
            csv_temp_data["contenido"] = output.getvalue()
            csv_temp_data["nombre"] = nombre_archivo
            
            file_picker.save_file(dialog_title=f"Guardar {tipo_reporte}", file_name=nombre_archivo, allowed_extensions=["csv"])
        except Exception as ex:
            print(ex)

    # --- ACCIONES DE IMPRESIÓN ---
    def accion_imprimir_corte(e):
        page.snack_bar = ft.SnackBar(ft.Text("Imprimiendo Corte..."), bgcolor="blue")
        page.snack_bar.open = True
        page.update()
        imprimir_corte_caja(ventas_por_empleado, total_ventas, detalle_vendidos)

    def accion_imprimir_inventario(e):
        page.snack_bar = ft.SnackBar(ft.Text("Imprimiendo Inventario..."), bgcolor="blue")
        page.snack_bar.open = True
        page.update()
        imprimir_inventario(inventario)

    # --- TABLAS VISUALES ---
    
    # --- TABLAS VISUALES (Optimizadas con STRETCH) ---
    
    def crear_tabla_resumen_empleados():
        tabla = ft.DataTable(
            # width=float("inf"),  <-- YA NO ES NECESARIO
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_200),
            border_radius=10,
            columns=[
                ft.DataColumn(ft.Text("Vendedor", weight="bold")), 
                ft.DataColumn(ft.Text("Total", weight="bold"), numeric=True)
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(e)), 
                    ft.DataCell(ft.Text(f"${t:,.2f}", weight="bold"))
                ]) for e, t in ventas_por_empleado
            ]
        )
        # Aplicamos STRETCH aquí en el contenedor padre
        return ft.Column(
            [tabla], 
            scroll=ft.ScrollMode.AUTO, 
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH 
        )

    def crear_tabla_detalle_productos():
        tabla = ft.DataTable(
            heading_row_color=ft.Colors.GREY_100,
            columns=[
                ft.DataColumn(ft.Text("Folio")),
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Peso")),
                ft.DataColumn(ft.Text("Precio"), numeric=True),
            ],
            rows=[]
        )
        
        for item in detalle_vendidos:
            tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(item[0]))),
                    ft.DataCell(ft.Container(content=ft.Text(item[2], size=12), width=180)),
                    ft.DataCell(ft.Text(f"{item[3]}g")),
                    ft.DataCell(ft.Text(f"${item[4]:,.2f}")),
                ])
            )
            
        # Aplicamos STRETCH aquí
        return ft.Column(
            [tabla], 
            scroll=ft.ScrollMode.AUTO, 
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        )

    def crear_tabla_inventario_visual():
        tabla = ft.DataTable(
            heading_row_color=ft.Colors.GREY_100,
            columns=[
                ft.DataColumn(ft.Text("Clave")),
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Stock"), numeric=True),
            ],
            rows=[]
        )
        
        for p in inventario:
            stock = p[6] if len(p) > 6 else 1
            color = ft.Colors.RED if stock < 3 else None
            
            tabla.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(p[1], color=color)),
                ft.DataCell(ft.Container(content=ft.Text(p[2], size=12), width=250)),
                ft.DataCell(ft.Text(str(stock), color=color, weight="bold")),
            ]))
            
        # Aplicamos STRETCH aquí
        return ft.Column(
            [tabla], 
            scroll=ft.ScrollMode.AUTO, 
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        )

    # --- PESTAÑAS ---
    
    # 1. Pestaña CORTE
    tab_ventas = ft.Container(
        padding=20,
        content=ft.Column([
            ft.Row([
                ft.Text("Resumen del Día", size=20, weight="bold", color="#C39D88"),
                ft.Text(datetime.now().strftime("%d/%m/%Y"), size=16)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            # Resumen Empleados
            ft.Container(content=crear_tabla_resumen_empleados(), height=100), # Altura fija pequeña
            
            ft.Divider(),
            ft.Text("Detalle de Productos Vendidos:", weight="bold"),
            
            # Lista detallada (ocupa el espacio central)
            ft.Container(content=crear_tabla_detalle_productos(), expand=True, bgcolor=ft.Colors.GREY_50, border_radius=5),
            
            ft.Divider(),
            
            # Totales y Botones
            ft.Row([
                ft.Text("Total Caja:", size=18),
                ft.Text(f"${total_ventas:,.2f}", size=24, weight="bold", color="#506C64")
            ], alignment=ft.MainAxisAlignment.END),
            
            ft.Container(height=10),
            
            ft.Row([
                ft.ElevatedButton("Imprimir Corte", icon=ft.Icons.PRINT, bgcolor="#506C64", color="white", on_click=accion_imprimir_corte, expand=True),
                ft.OutlinedButton("Descargar CSV", icon=ft.Icons.DOWNLOAD, on_click=lambda e: handle_download(e, "ventas"), expand=True)
            ], spacing=10)
        ])
    )

    # 2. Pestaña INVENTARIO
    tab_inventario = ft.Container(
        padding=20,
        content=ft.Column([
            ft.Text("Inventario Total", size=20, weight="bold", color="#C39D88"),
            ft.Container(content=crear_tabla_inventario_visual(), expand=True),
            
            ft.Container(height=10),
            
            ft.Row([
                ft.ElevatedButton("Imprimir Lista", icon=ft.Icons.PRINT, bgcolor="#506C64", color="white", on_click=accion_imprimir_inventario, expand=True),
                ft.OutlinedButton("Descargar CSV", icon=ft.Icons.DOWNLOAD, on_click=lambda e: handle_download(e, "inventario"), expand=True)
            ], spacing=10)
        ])
    )

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="Corte de Caja", icon=ft.Icons.POINT_OF_SALE, content=tab_ventas),
            ft.Tab(text="Inventario", icon=ft.Icons.INVENTORY_2, content=tab_inventario),
        ],
        expand=True
    )

    dlg_modal = ft.AlertDialog(
        modal=True,
        content_padding=0,
        content=ft.Container(
            width=750,
            height=650,
            bgcolor="white",
            border_radius=15,
            content=ft.Column([
                ft.Container(
                    padding=10,
                    content=ft.Row([
                        ft.Text("Reportes", size=16, color="grey"),
                        ft.IconButton(ft.Icons.CLOSE, on_click=lambda e: page.close(dlg_modal))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),
                tabs
            ])
        )
    )

    page.open(dlg_modal)