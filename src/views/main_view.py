import flet as ft
from modals.modal_crud_producto import show_modal_editar_producto
from modals.modal_pago import show_modal_pago
from database.manager import obtener_productos, obtener_precios_oro, actualizar_precio_oro
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
        
        # Conjunto para evitar duplicados visuales (guarda las claves 'A001', etc.)
        self.productos_en_sidebar_claves = set()
        
        # Lista para calcular totales y pasar al pago: [(producto_tuple, precio_float), ...]
        self.productos_con_precio_sidebar = []

        self.txt_subtotal = ft.Text(
            "$0.00", 
            size=18, 
            weight=ft.FontWeight.BOLD, 
            text_align=ft.TextAlign.RIGHT
        )
        
        self.btn_continuar = ft.FilledButton(
            "Continuar",
            expand=True,
            height=50,
            color='Black',
            bgcolor='#C39D88',
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=7),
                text_style=ft.TextStyle(size=20, weight=ft.FontWeight.BOLD)
            ),
            disabled=True,
            on_click=self._evento_boton_continuar # Se asigna dinámicamente cuando hay total
        )
        
        self._construir_interfaz()
        self.actualizar_lista_productos()

    # --- LÓGICA DE PRECIOS ---

    def _obtener_precio_gramo(self, kilataje):
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
    
    def _calcular_precio_numerico(self, producto):
        """Retorna el valor decimal (float) puro"""
        try:
            peso = float(producto[3]) 
            kilataje = producto[4]
            precio_gramo = self._obtener_precio_gramo(kilataje)
            return peso * precio_gramo
        except (ValueError, TypeError):
            return 0.0

    # --- CREACIÓN DE TILES (Visuales) ---

    def _crear_producto_tile(self, producto, on_agregar):
        precio_num = self._calcular_precio_numerico(producto)
        texto_precio = f"${precio_num:,.2f}"
        
        nombre = producto[2]
        peso_str = producto[3]
        kilataje = producto[4]
        categoria = producto[5]
        clave = producto[1]
        cantidad_stock = producto[6] if len(producto) > 6 else 1
        
        # Si es más de 1, mostramos etiqueta de stock
        texto_stock = ""
        color_stock = ft.Colors.BLACK
        
        if cantidad_stock > 1:
            texto_stock = f"Stock: {cantidad_stock}"
            color_stock = ft.Colors.BLUE_GREY
        else:
            texto_stock = "Pieza Única"
            color_stock = ft.Colors.ORANGE_400
        
        return ft.Container(
            padding=ft.padding.all(10),
            # Opcional: un color de fondo al pasar el mouse o siempre
            # bgcolor=ft.Colors.WHITE, 
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START, # Alinea todo arriba
                        controls=[
                            # --- COLUMNA IZQUIERDA (Información) ---
                            ft.Column(
                                spacing=2,
                                expand=True, # IMPORTANTE: Ocupa todo el espacio posible
                                controls=[
                                    ft.Text(
                                        f"{nombre} | {peso_str} gr. | {kilataje}", 
                                        weight=ft.FontWeight.BOLD, 
                                        color='Black', 
                                        size=20 # Un poco más chico para que quepa mejor, o 18
                                    ),
                                    ft.Text(
                                        f"Categoría: {categoria} - Clave: {clave}", 
                                        size=15, 
                                        selectable=True,
                                        color=ft.Colors.GREY_700
                                    ),
                                    ft.Text(
                                        texto_stock, 
                                        size=12, 
                                        weight=ft.FontWeight.BOLD, 
                                        color=color_stock
                                    )
                                ]
                            ),
                            
                            # --- COLUMNA DERECHA (Precio y Botón) ---
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=5,
                                controls=[
                                    ft.Text(
                                        f"Precio: {texto_precio}", 
                                        size=15, 
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.ElevatedButton(
                                        "Agregar",
                                        color='Black',
                                        bgcolor='#C39D88',
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                                        height=35, # Botón compacto
                                        on_click=lambda e: on_agregar(producto)
                                    )
                                ]
                            )
                        ]
                    ),
                    # Espacio antes de la línea
                    ft.Container(height=10),
                    # La línea divisoria
                    ft.Divider(height=1, color=ft.Colors.GREY_300)
                ]
            )
        )

    def _crear_sidebar_tile(self, producto, precio_num):
        """
        Crea el elemento visual del carrito usando un Row personalizado
        para evitar que el texto se aplaste verticalmente.
        """
        precio_formateado = f"${precio_num:,.2f}"
        
        # Elemento contenedor del producto
        tile_en_sidebar = ft.Container(
            padding=ft.padding.symmetric(vertical=5, horizontal=5),
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY_300)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # IZQUIERDA: Nombre y Código (Usamos expand=True para que ocupe el espacio disponible)
                    ft.Column(
                        spacing=2,
                        expand=True, 
                        controls=[
                            ft.Text(
                                f"{producto[2]}", # Nombre
                                weight=ft.FontWeight.BOLD, 
                                size=13,
                                max_lines=2, # Si es muy largo, usa 2 lineas maximo
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            ft.Text(
                                f"{producto[3]} gr. | {producto[4]}", # Detalles
                                size=11, 
                                color=ft.Colors.GREY_700
                            ),
                            ft.Text(
                                f"Cod: {producto[1]}", # Codigo
                                size=10, 
                                color=ft.Colors.GREY_500
                            ),
                        ]
                    ),
                    
                    # DERECHA: Precio y Boton Eliminar
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=0,
                        controls=[
                            ft.Text(
                                precio_formateado, 
                                size=14, 
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLACK
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.RED_400,
                                icon_size=20,
                                tooltip="Quitar del carrito",
                                on_click=lambda e: self._remover_de_sidebar(producto)
                            )
                        ]
                    )
                ]
            )
        )
        return tile_en_sidebar
    # --- LÓGICA DE ESTADO (Agregar/Quitar/Subtotal) ---

    def _actualizar_subtotal(self):
        total = sum(item[1] for item in self.productos_con_precio_sidebar)
        self.txt_subtotal.value = f"${total:,.2f}"
        
        # Habilitar botón y asignar acción con el total actual capturado
        self.btn_continuar.disabled = (total == 0)
        self.btn_continuar.on_click = lambda e: self._abrir_modal_pago(total)
        
        self.txt_subtotal.update()
        self.btn_continuar.update()

    def _agregar_a_sidebar(self, producto):
        clave = producto[1]
        if clave in self.productos_en_sidebar_claves:
            return 

        self.productos_en_sidebar_claves.add(clave)
        
        precio_num = self._calcular_precio_numerico(producto)
        self.productos_con_precio_sidebar.append((producto, precio_num))

        nuevo_tile = self._crear_sidebar_tile(producto, precio_num)
        self.sidebar_content.controls.append(nuevo_tile)
        
        self.sidebar_content.update()
        self._actualizar_subtotal()
        self.actualizar_lista_productos() # Para actualizar botones o estado visual si fuera necesario

    # CORRECCIÓN: Faltaba este método
    def _remover_de_sidebar(self, producto_a_borrar):
        clave = producto_a_borrar[1]
        
        # 1. Quitar del set de claves
        if clave in self.productos_en_sidebar_claves:
            self.productos_en_sidebar_claves.remove(clave)
            
        # 2. Quitar de la lista de precios (filtro por clave)
        self.productos_con_precio_sidebar = [
            item for item in self.productos_con_precio_sidebar 
            if item[0][1] != clave
        ]
        
        # 3. Reconstruir visualmente la sidebar 
        # (Es más seguro reconstruirla que buscar el control específico para eliminarlo)
        self._reconstruir_sidebar_visual()
        
        self._actualizar_subtotal()
        self.actualizar_lista_productos()

    def _reconstruir_sidebar_visual(self):
        """Reconstruye los controles del sidebar basándose en la lista actual"""
        controles_base = [
            ft.Text("Los productos que escanees o busques aparecerán aquí", size=12),
            ft.Divider(height=1)
        ]
        
        nuevos_tiles = []
        for prod, precio in self.productos_con_precio_sidebar:
            nuevos_tiles.append(self._crear_sidebar_tile(prod, precio))
            
        self.sidebar_content.controls = controles_base + nuevos_tiles
        self.sidebar_content.update()

    # --- LÓGICA DE PAGO ---

    def _abrir_modal_pago(self, total):
        empleado_id = self.page.session.get('empleado_id')
        if not empleado_id: 
            print("Error: No empleado ID")
            return

        show_modal_pago(
            self.page, 
            self.productos_con_precio_sidebar, 
            total, 
            empleado_id, 
            self._limpiar_despues_venta # CORRECCIÓN: Ahora apunta a una función existente
        )

    def _evento_boton_continuar(self, e):
        """Manejador fijo para el botón continuar"""
        if self.total_actual > 0:
            self._abrir_modal_pago(self.total_actual)
        else:
            # Por seguridad, si el total es 0, no abrimos nada
            print("Error: El total es 0")

    # CORRECCIÓN: Faltaba este método para limpiar tras venta exitosa
    def _limpiar_despues_venta(self):
        self.productos_en_sidebar_claves.clear()
        self.productos_con_precio_sidebar = []
        self._reconstruir_sidebar_visual()
        self._actualizar_subtotal()
        self.actualizar_lista_productos() # Refresca lista principal (ya sin los vendidos)

    # --- FILTRADO Y ACTUALIZACIÓN ---

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
            
        # Filtramos los que ya están en sidebar para que no salgan en la lista principal
        productos_finales = [
            p for p in productos
            if p[1] not in self.productos_en_sidebar_claves
        ]
            
        return productos_finales

    def actualizar_lista_productos(self, texto_busqueda="", criterio_orden="nombre"):
        if not self.lista:
            return

        # Si hay texto en el filtro visual, mantenemos ese criterio
        if self.filter_text:
            if "Kilataje" in self.filter_text.value: criterio_orden = "kilataje"
            elif "Categoria" in self.filter_text.value: criterio_orden = "categoria"

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

        try:
            p_10k = float(self.txt_oro_10k.value) if self.txt_oro_10k.value else 0.0
            p_14k = float(self.txt_oro_14k.value) if self.txt_oro_14k.value else 0.0
            p_ita = float(self.txt_italiano.value) if self.txt_italiano.value else 0.0
            
            actualizar_precio_oro(p_10k, p_14k, p_ita)
            
        except ValueError:
            pass

        lista_actualizada = []
        
        for producto_tuple, _ in self.productos_con_precio_sidebar:
            # Recalculamos precio con los nuevos valores de los inputs
            nuevo_precio = self._calcular_precio_numerico(producto_tuple)
            lista_actualizada.append((producto_tuple, nuevo_precio))
            
        # 2. Reemplazamos la lista oficial
        self.productos_con_precio_sidebar = lista_actualizada
        
        # 3. Actualizamos visualmente el Sidebar
        self._reconstruir_sidebar_visual()
        
        # 4. Actualizamos subtotal
        self._actualizar_subtotal()
        
        # 5. Actualizamos la lista principal (los precios de "Agregar" también cambian)
        self.actualizar_lista_productos()

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

    # --- INTERFAZ UI ---

    def _construir_interfaz(self):
        
        precios = obtener_precios_oro()

        self.txt_oro_10k = ft.TextField(
            value=str(precios[0]),
            label="Oro 10K",
            bgcolor="CCCCCC",
            height=40, width=150, border_radius=7, 
            prefix_text="$", suffix_text="/gr",
            on_blur=self.precios_actualizados
        )
        self.txt_oro_14k = ft.TextField(
            value=str(precios[1]),
            label="Oro 14K",
            bgcolor="CCCCCC",
            height=40, width=150, border_radius=7, 
            prefix_text="$", suffix_text="/gr",
            on_blur=self.precios_actualizados
        )
        self.txt_italiano = ft.TextField(
            value=str(precios[2]),
            label="Oro Italiano",
            bgcolor="CCCCCC",
            height=40, width=150, border_radius=7, 
            prefix_text="$", suffix_text="/gr",
            on_blur=self.precios_actualizados
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
                        spacing=20,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.txt_oro_10k,
                            self.txt_oro_14k,
                            self.txt_italiano,
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
                ft.Row(
                    controls=[
                        ft.Text("Subtotal:", size=18, weight=ft.FontWeight.BOLD),
                        self.txt_subtotal,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(
                    content=self.btn_continuar,
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(top=10)
                )
            ],
            spacing=10,
            tight=True
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
                    self.filter_text,
                    ft.PopupMenuButton(  
                        icon = "FILTER_LIST",
                        icon_color=ft.Colors.BLACK,
                        tooltip="Filtrar",
                        items=[
                            ft.PopupMenuItem(text="Nombre", on_click=self.on_filter_selected),
                            ft.PopupMenuItem(text="Kilataje", on_click=self.on_filter_selected),
                            ft.PopupMenuItem(text="Categoria", on_click=self.on_filter_selected)
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
        self.controls = [main_container,
                        ft.Row(
                            [
                                ft.Text(
                                    f"Iniciaste sesión como: {self.page.session.get('empleado_nombre')}",
                                    size=17,
                                    color=ft.Colors.BLACK,
                                    weight=ft.FontWeight.W_600
                                ),
                                ft.FilledButton(
                                "Cerrar sesion",
                                bgcolor='White',
                                color='Black',
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=7)),
                                    on_click=lambda e: self.page.go("/login")
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )]