import flet as ft
from modals.modal_crud_producto import show_modal_editar_producto
from database.manager import obtener_productos
from functools import partial
from datetime import datetime
import logging

class MainView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/main",
            padding=ft.padding.only(left=40, top=40, right=40, bottom=10)
        )
        self.page = page
        
        self.txt_oro_10k = None
        self.txt_oro_14k = None
        self.txt_italiano = None
        self.lista = None
        self.filter_text = None
        
        self.sidebar_content = ft.Column(
            controls=[
                ft.Text("Los productos que escanees o busques aparecerán aquí", size=12),
                ft.Divider(height=1)
            ],
            scroll="auto",
            expand=True
        )
        self.productos_en_sidebar_claves = set()

        self.txt_subtotal = ft.Text(
            "$0.00", 
            size=18, 
            weight=ft.FontWeight.BOLD, 
            text_align=ft.TextAlign.RIGHT
        )
        self.btn_continuar = ft.FilledButton(
            "Continuar",
            expand=True, # Se expande al ancho de la sidebar
            height=50,
            color='Black',
            bgcolor='#C39D88', # Usamos el color de la app
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=7),
                text_style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)
            ),
            disabled=True # Inicia deshabilitado
        )
        
        self._construir_interfaz()
        
        self.actualizar_lista_productos()

    def _obtener_precio_gramo(self, kilataje):
        """
        Método auxiliar para obtener el precio por gramo desde los TextFields del AppBar.
        Maneja errores si el valor no es un número.
        """
        precio = 0.0
        kilataje_str = str(kilataje).lower()

        try:
            if "10k" in kilataje_str:
                precio = float(self.txt_oro_10k.value)
            elif "14k" in kilataje_str:
                precio = float(self.txt_oro_14k.value)
            elif "ita" in kilataje_str:
                precio = float(self.txt_italiano.value)
        
        except (ValueError, TypeError):
            precio = 0.0
        
        return precio
    
    def _calcular_precio_str(self, producto):
        """
        Calcula y formatea el precio de un producto.
        Índices: [2]=Nombre, [3]=Peso, [4]=Kilataje
        """
        nombre = producto[2]
        peso_str = producto[3]
        kilataje = producto[4]

        precio_gramo = self._obtener_precio_gramo(kilataje)
        precio_total = 0.0
        
        try:
            peso_float = float(peso_str)
            precio_total = peso_float * precio_gramo
        except (ValueError, TypeError) as e:
            logging.error(f"Error al calcular precio para {nombre}: {e}")
            return "$Error"
        
        return f"${precio_total:,.2f}"

    def _crear_producto_tile(self, producto, on_agregar):
        # Índices confirmados: 2=Nombre, 3=Peso, 4=Kilataje, 5=Categoría
        
        nombre = producto[2]
        peso_str = producto[3]
        kilataje = producto[4]
        categoria = producto[5]
        clave = producto[1]

        precio_formateado = self._calcular_precio_str(producto)
        
        if precio_formateado == "$Error":
            peso_str = f"ErrorPeso ({peso_str})"
        
        return ft.Column(
            controls=[
                ft.ListTile(
                    content_padding=ft.padding.all(15),
                    leading=ft.Column([
                        ft.Text(f"{nombre} | {peso_str} gr. | {kilataje}", weight=ft.FontWeight.BOLD, color='Black', size=20),
                        ft.Text(f"Categoría: {categoria}    Clave: {clave}", weight=ft.FontWeight.NORMAL, size=15, selectable=True),  
                    ]),
                    title=ft.Container(
                        ft.Text(f"Precio: {precio_formateado}", size=15, weight=ft.FontWeight.BOLD), 
                        alignment=ft.alignment.center_right,
                    ),
                    trailing=ft.ElevatedButton(
                        "Agregar",
                        color='Black',
                        bgcolor='#C39D88',
                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                        on_click=lambda e: on_agregar(producto)
                    )
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_400)
            ]
        )
    
    def _crear_sidebar_tile(self, producto, precio_formateado):
        """
        Crea el widget para el producto en la sidebar,
        basado en el formato solicitado.
        """
        # Índices: [2]=Nombre, [3]=Peso, [4]=Kilataje, [1]=Clave
        
        tile_en_sidebar = ft.Column(
            spacing=0,
            controls=[
                ft.ListTile(
                    content_padding=ft.padding.only(left=5, right=5, top=2, bottom=2),
                    title=ft.Text(
                        f"{producto[2]} | {producto[3]} gr. | {producto[4]}", 
                        weight=ft.FontWeight.BOLD, size=14
                    ),
                    subtitle=ft.Text(f"Código: {producto[1]}", size=12),
                    trailing=ft.Text(
                        precio_formateado, 
                        size=15, 
                        weight=ft.FontWeight.BOLD
                    ),
                    on_click=lambda e: self._regresar_a_lista(producto, tile_en_sidebar)
                ),
                ft.Divider(height=1)
            ]
        )
        return tile_en_sidebar

    # --- NUEVO ---
    def _actualizar_subtotal(self):
        """
        Calcula el subtotal de los productos en la sidebar y actualiza
        el texto y el estado del botón 'Continuar'.
        """
        total = 0.0
        
        # Creamos un diccionario {clave: producto} para buscar rápido
        try:
            todos_productos = {p[1]: p for p in obtener_productos()}
        except Exception as e:
            logging.error(f"Error al obtener productos para subtotal: {e}")
            todos_productos = {}
        
        for clave in self.productos_en_sidebar_claves:
            if clave in todos_productos:
                producto = todos_productos[clave]
                
                # Lógica de cálculo (simplificada)
                precio_gramo = self._obtener_precio_gramo(producto[4]) # kilataje
                try:
                    peso_float = float(producto[3]) # peso
                    total += peso_float * precio_gramo
                except (ValueError, TypeError):
                    pass # Ignora productos con datos erróneos
        
        # Actualizar el texto
        self.txt_subtotal.value = f"${total:,.2f}"
        
        # Habilitar/deshabilitar botón
        self.btn_continuar.disabled = (total == 0.0)
        
        # Actualizar controles en la UI (si la página ya cargó)
        if self.page:
            self.txt_subtotal.update()
            self.btn_continuar.update()

    # --- MODIFICADO ---
    def _agregar_a_sidebar(self, producto):
        clave_producto = producto[1]
        self.productos_en_sidebar_claves.add(clave_producto)
        precio_str = self._calcular_precio_str(producto)
        nuevo_tile = self._crear_sidebar_tile(producto, precio_str)
        self.sidebar_content.controls.append(nuevo_tile)
        
        if self.sidebar_content.page:
            self.sidebar_content.update()
            
        self.actualizar_lista_productos()
        
        # --- NUEVO ---
        self._actualizar_subtotal() # Actualiza el total

    # --- MODIFICADO ---
    def _regresar_a_lista(self, producto, tile_a_remover):
        clave_producto = producto[1]
        if clave_producto in self.productos_en_sidebar_claves:
            self.productos_en_sidebar_claves.remove(clave_producto)
            
        self.sidebar_content.controls.remove(tile_a_remover)
        
        if self.sidebar_content.page:
            self.sidebar_content.update()
            
        self.actualizar_lista_productos()
        
        # --- NUEVO ---
        self._actualizar_subtotal()


    # --- MODIFICADO ---
    def filtrar_productos(self, texto_busqueda="", criterio_orden="nombre"):
        productos = obtener_productos()
        
        if texto_busqueda:
            texto_busqueda = texto_busqueda.lower()
            productos = [
                p for p in productos 
                if (texto_busqueda in str(p[2]).lower() or
                    texto_busqueda in str(p[4]).lower() or
                    texto_busqueda in str(p[5]).lower())
            ]
        
        try:
            if criterio_orden == "nombre":
                productos.sort(key=lambda x: str(x[2]).lower())
            elif criterio_orden == "kilataje":
                productos.sort(key=lambda x: str(x[4]).lower())
            elif criterio_orden == "categoria":
                productos.sort(key=lambda x: str(x[5]).lower())
        except Exception as e:
            logging.error(f"Error al ordenar: {e}")
            
        productos_finales = [
            p for p in productos
            if p[1] not in self.productos_en_sidebar_claves
        ]
            
        return productos_finales

    def actualizar_lista_productos(self, texto_busqueda="", criterio_orden="nombre"):
        """
        Actualiza la self.lista con los productos filtrados y ordenados.
        Recalcula todos los precios.
        """
        if not self.lista:
            return

        productos = self.filtrar_productos(texto_busqueda, criterio_orden)
        
        self.lista.content.controls = [
            self._crear_producto_tile(
                producto, 
                on_agregar=self._agregar_a_sidebar
            )
            for producto in productos  
        ]
        
        if self.lista.page:
            self.lista.update()

    def precios_actualizados(self, e):
        """
        Refresca ambas listas para recalcular todos los precios.
        """
        criterio_actual = "nombre"
        if self.filter_text:
            if "Kilataje" in self.filter_text.value:
                criterio_actual = "kilataje"
            elif "Categoria" in self.filter_text.value:
                criterio_actual = "categoria"
        
        self.actualizar_lista_productos(criterio_orden=criterio_actual)
        
        productos_en_sidebar = [
            p for p in obtener_productos() 
            if p[1] in self.productos_en_sidebar_claves
        ]
        
        controles_sidebar = [self.sidebar_content.controls[0], self.sidebar_content.controls[1]]
        
        for producto in productos_en_sidebar:
            precio_str = self._calcular_precio_str(producto)
            nuevo_tile = self._crear_sidebar_tile(producto, precio_str)
            controles_sidebar.append(nuevo_tile)
            
        self.sidebar_content.controls = controles_sidebar
        if self.sidebar_content.page:
            self.sidebar_content.update()

        self._actualizar_subtotal()


    def on_filter_selected(self, e):
        self.filter_text.value = f"Filtrar por: {e.control.text}"
        criterio = "nombre"
        if e.control.text == "Kilataje":
            criterio = "kilataje"
        elif e.control.text == "Categoria":
            criterio = "categoria"
        self.actualizar_lista_productos(criterio_orden=criterio)
        if self.page:
            self.update()

    def _construir_interfaz(self):
        
        self.txt_oro_10k = ft.TextField(
            bgcolor="CCCCCC",
            height=40, width=150, border_radius=7, 
            prefix_text="$", suffix_text="/gr",
            on_change=self.precios_actualizados # <--- ACTUALIZA AL CAMBIAR
        )
        self.txt_oro_14k = ft.TextField(
            bgcolor="CCCCCC",
            height=40, width=150, border_radius=7, 
            prefix_text="$", suffix_text="/gr",
            on_change=self.precios_actualizados # <--- ACTUALIZA AL CAMBIAR
        )
        self.txt_italiano = ft.TextField(
            bgcolor="CCCCCC",
            height=40, width=150, border_radius=7, 
            prefix_text="$", suffix_text="/gr",
            on_change=self.precios_actualizados # <--- ACTUALIZA AL CAMBIAR
        )

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
                            self.txt_oro_10k, # <-- Usamos el atributo
                            ft.Text("Oro 14k:", font_family="Poppins Medium", size=12),
                            self.txt_oro_14k, # <-- Usamos el atributo
                            ft.Text("Italiano:",font_family="Poppins Medium", size=12),
                            self.txt_italiano, # <-- Usamos el atributo
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
                                # Usamos el método de la clase
                                on_click=lambda e: show_modal_editar_producto(self.page, lambda: self.actualizar_lista_productos())
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

        self.lista = ft.Container(
            border_radius=10,
            expand=7,
            content=ft.ListView(
                controls=[],
                spacing=0
            )
        )

        fixed_controls = ft.Column(
            controls=[
                ft.Divider(),
                # El Subtotal
                ft.Row(
                    controls=[
                        ft.Text("Subtotal:", size=18, weight=ft.FontWeight.BOLD),
                        self.txt_subtotal, # El texto que actualizaremos
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                # El botón de Continuar
                ft.Container(
                    content=self.btn_continuar, # El botón que actualizaremos
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=10)
                )
            ],
            spacing=10,
            tight=True # Para que no ocupe espacio extra
        )

        sidebar = ft.Container(
            alignment=ft.alignment.top_center,
            expand=3,
            padding=15,
            border_radius=10,
            content=ft.Column(
                controls=[
                    self.sidebar_content,
                    fixed_controls         
                ],
                expand=True
            )
        )

        self.filter_text = ft.Text('Filtrar por: Nombre', size=16, weight=ft.FontWeight.W_600)
        filtro=ft.Container( 
            content=ft.Row( 
                controls=[
                    ft.Text('Listado de Productos', weight=ft.FontWeight.BOLD, size=20),
                    ft.Container(expand=True),
                    self.filter_text, # <-- Usamos el atributo
                    ft.PopupMenuButton(  
                        icon = "FILTER_LIST",
                        icon_color=ft.Colors.BLACK,
                        tooltip="Filtrar",
                        items=[
                            ft.PopupMenuItem(text="Nombre", on_click=self.on_filter_selected), # <-- Usamos el método
                            ft.PopupMenuItem(text="Kilataje", on_click=self.on_filter_selected), # <-- Usamos el método
                            ft.PopupMenuItem(text="Categoria", on_click=self.on_filter_selected) # <-- Usamos el método
                        ],
                    )
                ]
            )
        )
        search_bar=ft.Container(
            bgcolor="#CCCCCC",
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
                        # Usamos el método de la clase
                        on_change=lambda e: self.actualizar_lista_productos(texto_busqueda=e.control.value)
                    )
                ]
            )
        )

        
        product_container = ft.Column(
            controls=[
                search_bar,
                filtro,
                self.lista
            ],
            expand=7,
            spacing=10
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