# views/main_view.py
import flet as ft
from database.manager import obtener_productos
from functools import partial
from datetime import datetime

class MainView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/main",
            padding=ft.padding.only(left=40, top=40, right=40, bottom=10)
        )
        self.page = page
        
        self._construir_interfaz()

    def _crear_producto_tile(self, producto, on_agregar):

        # 0=id, 1=nombre, 2=peso, 3=descripcion, 4=categoria
        
        return ft.Column(
            controls=[
                ft.ListTile(
                    content_padding=ft.padding.all(15),
                    leading=ft.Column([
                        # <--- CORRECCIÓN 2: producto[1] es 'nombre'
                        ft.Text(producto[1], weight=ft.FontWeight.BOLD, color='Black', size=20),
                        # <--- CORRECCIÓN 3: producto[4] es 'categoria' (más útil que 'marca')
                        ft.Text(f"Categoría: {producto[4]}", weight=ft.FontWeight.NORMAL, size=15),    
                    ]),
                    title=ft.Container(
                        ft.Text(f"Peso: {producto[2]}", size=15, weight=ft.FontWeight.BOLD), 
                        alignment=ft.alignment.center_right,

                    ),
                    trailing=ft.ElevatedButton(
                        "Agregar",
                        color='Black',
                        bgcolor='#FFCDFA',
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                        on_click=on_agregar
                    )
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_400)
            ]
        )

    def _construir_interfaz(self):
        # Define el AppBar
        appbar = ft.AppBar(
            # ... (Tu código de AppBar está bien, lo omito por brevedad) ...
            shadow_color=ft.Colors.BLACK87,
            elevation=15,
            bgcolor="#F2F2F2",
            leading=ft.Container(
                padding=10,
                content=ft.Row(
                    controls=[
                        ft.Text("Joyería 3 Hermanos", font_family="Poppins Medium", size=25, color="#C39D88"),
                    ],
                ),
            ),
            title=ft.Container(
                alignment=ft.alignment.center,
                content=ft.Row(
                    controls=[
                        ft.Text("Oro 10k:"),
                        ft.TextField(label="$100.00/gr"),
                        ft.Text("Oro 14k:"),
                        ft.TextField(label="$140.00/gr"),
                    ]
                )
            ),
            actions=[
                ft.Container(
                    padding=10,
                    content=ft.Row(
                        controls=[      
                            ft.ElevatedButton(
                                'Crear/Editar articulo', 
                                color="#F2F2F2",
                                bgcolor="#506C64",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                            ),
                            ft.ElevatedButton(
                                'Corte',
                                color='Black',
                                width=90,
                                bgcolor="#FCBF49",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                            )
                        ]
                    ),
                )
            ]
        )
        
        # Define la lista (sin simulación)
        lista = ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            expand=True,
            content=ft.ListView(
                controls=[
                    # <--- CORRECCIÓN 5: Pasa el argumento 'on_agregar'
                    #    (Usamos None por ahora, aquí debe ir tu función)
                    self._crear_producto_tile(
                        producto, 
                        on_agregar=None 
                    )
                    # Llama directamente a la función real de la DB
                    for producto in obtener_productos()
                ]
            )
        )

        # Define la barra lateral
        sidebar = ft.Container(
            alignment=ft.alignment.top_center,
            expand=3,
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            content=ft.Column(
                controls=[
                    ft.Text("Los productos que escanees o busques aparecerán aquí", size=12),
                    ft.Divider(height=1)
                ],
                scroll="auto",
                expand=True
            )
        )

        main_container = ft.Row(
            controls=[
                lista,
                sidebar
            ],
            spacing=40,
            expand=True
        )

        self.appbar = appbar
        self.controls = [main_container]
        