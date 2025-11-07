import flet as ft
# from modals.modal_crud_producto import show_modal_editar_producto
# from modals.modal_pago import show_modal_pago 
# from modals.modal_apartado import show_modal_apartado
# from modals.modal_corte import show_modal_corte  
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
        return ft.Column(
            controls=[
                ft.ListTile(
                    content_padding=ft.padding.all(15),
                    leading=ft.Column([
                        ft.Text(producto[1], weight=ft.FontWeight.BOLD, color='Black', size=20),
                        ft.Text(f"Marca: {producto[2]}", weight=ft.FontWeight.NORMAL, size=15),    
                    ]),
                    title=ft.Container(
                        alignment=ft.alignment.center_right,
                        content=ft.Text(f"Precio: ${producto[3]}", size=15, weight=ft.FontWeight.BOLD)
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
        appbar = ft.AppBar(
            shadow_color=ft.Colors.BLACK87,
            elevation=15,
            bgcolor=ft.Colors.BLACK,
            leading=ft.Container(
                padding=10,
                content=ft.Row(
                    controls=[
                        ft.Text("Vale's", weight=ft.FontWeight.BOLD, size=25, color='white'),
                        ft.Text('PdV', weight=ft.FontWeight.BOLD, size=25, color='#D013BD'),
                    ],
                ),
            ),
            title=ft.Container(
                alignment=ft.alignment.center,
                content=ft.Image(src="Logo.png", fit=ft.ImageFit.CONTAIN, height=50),
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
        lista = ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            expand=True,
            content=ft.ListView(
                controls=[
                    self._crear_producto_tile(
                        producto, 
                        on_agregar=None  
                    )
                    for producto in obtener_productos()
                ]
            )
        )

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