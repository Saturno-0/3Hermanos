# views/main_view.py
import flet as ft
from modals.modal_crud_producto import show_modal_editar_producto
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
        # 0=id, 2=nombre, 3=peso, 4=descripcion, 5=categoria
        return ft.Column(
            controls=[
                ft.ListTile(
                    content_padding=ft.padding.all(15),
                    leading=ft.Column([
                        # <--- CORRECCIÓN 2: producto[2] es 'nombre'
                        ft.Text(f"{producto[2]} | {producto[3]} gr. | {producto[4]}",  weight=ft.FontWeight.BOLD, color='Black', size=20),
                        # <--- CORRECCIÓN 3: producto[5] es 'categoria' (más útil que 'marca')
                        ft.Text(f"Categoría: {producto[5]}      Clave: {producto[1]}", weight=ft.FontWeight.NORMAL, size=15, selectable=True),    
                    ]),
                    title=ft.Container(
                        ft.Text(f"Precio: ???", size=15, weight=ft.FontWeight.BOLD), 
                        alignment=ft.alignment.center_right,
                    ),
                    trailing=ft.ElevatedButton(
                        "Agregar",
                        color='Black',
                        bgcolor='#C39D88',
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
            
            actions=[
                ft.Container(

                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Oro 10k:", font_family="Poppins Medium", size=12),
                            ft.TextField(height=20, width=150, border_radius=7, prefix_text="$", suffix_text="/gr"),
                            ft.Text("Oro 14k:", font_family="Poppins Medium", size=12),
                            ft.TextField( width=150, border_radius=7, label=" ", prefix_text="$", suffix_text="/gr"),
                            ft.Text("Italiano:",font_family="Poppins Medium", size=12),
                            ft.TextField( width=150, border_radius=7, label=" ", prefix_text="$", suffix_text="/gr"),
                        ]
                    )
                ),
                ft.Container(
                    padding=10,
                    content=ft.Row(
                        controls=[      
                            ft.ElevatedButton(
                                'Crear/Editar articulo', 
                                color="#F2F2F2",
                                bgcolor="#506C64",
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                                on_click=lambda e: show_modal_editar_producto(self.page, lambda: actualizar_lista_productos())
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
        
        def filtrar_productos(texto_busqueda="", criterio_orden="nombre"):
            productos = obtener_productos()  # Obtenemos todos los productos
            
            # Filtrado
            if texto_busqueda:
                texto_busqueda = texto_busqueda.lower()
                productos = [
                    p for p in productos 
                    if (texto_busqueda in p[1].lower() or  # Nombre
                        texto_busqueda in p[2].lower() or  # Marca
                        texto_busqueda in p[5].lower())    # Categoría
                ]
            
            # Ordenamiento
            if criterio_orden == "nombre":
                productos.sort(key=lambda x: x[1].lower())  # Índice 1 es nombre
            elif criterio_orden == "kilataje":
                productos.sort(key=lambda x: x[2].lower())  # Índice 2 es marca
            elif criterio_orden == "categoria":
                productos.sort(key=lambda x: x[5].lower())  # Índice 5 es categoría
            
            return productos

        def actualizar_lista_productos(texto_busqueda="", criterio_orden="nombre"):

            productos = filtrar_productos(texto_busqueda, criterio_orden)
            lista.content.controls = [
                self._crear_producto_tile(
                    producto, 
                    on_agregar=None  # Aquí debes pasar la función real para agregar el producto
                )
                for producto in productos  
            ]
            lista.update()

        # Define la lista (sin simulación)
        lista = ft.Container(
            border_radius=10,
            expand=7,
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

        filter_text = ft.Text('Filtrar por: Nombre', size=16, weight=ft.FontWeight.W_600)
        def on_filter_selected(e):
            # Actualiza el texto del filtro
            filter_text.value = f"Filtrar por: {e.control.text}"
            
            # Determina el criterio de ordenamiento
            criterio = "nombre"  # Por defecto
            if e.control.text == "Kilataje":
                criterio = "kilataje"
            elif e.control.text == "Categoria":
                criterio = "categoria"
            
            # Actualiza la lista con el nuevo orden
            actualizar_lista_productos(criterio_orden=criterio)
            self.update()

        filtro=ft.Container( 
            content=ft.Row( 
                controls=[
                    ft.Text('Listado de Productos', weight=ft.FontWeight.BOLD, size=20),
                    ft.Container(expand=True),
                    filter_text,
                    ft.PopupMenuButton(  
                        icon = "FILTER_LIST",
                        icon_color=ft.Colors.BLACK,
                        tooltip="Filtrar",
                        items=[
                            ft.PopupMenuItem(text="Nombre", on_click=on_filter_selected),
                            ft.PopupMenuItem(text="Kilataje", on_click=on_filter_selected),
                            ft.PopupMenuItem(text="Categoria", on_click=on_filter_selected)
                        ],
                    )
                ]
                )
            )

        search_bar=ft.Container(
                bgcolor=ft.Colors.WHITE,
                alignment=ft.alignment.center,
                height=50,
                border_radius=15,
                content=ft.Row(
                    controls=[
                        ft.Container(width=5),
                        ft.Icon(ft.Icons.SEARCH),  
                        ft.TextField(
                            hint_text="Buscar...",
                            border=ft.InputBorder.NONE,
                            expand=True,
                            on_change=lambda e: actualizar_lista_productos(e.control.value)
                        )
                    ]
                )
            )
        
        product_container = ft.Column(
            controls=[
                search_bar,
                filtro,
                lista
            ],
            expand=7
        )

        main_container = ft.Row(
            controls=[
                product_container,
                ft.VerticalDivider(),
                sidebar
            ],
            spacing=40,
            expand=True
        )

        self.appbar = appbar
        self.controls = [main_container]
        