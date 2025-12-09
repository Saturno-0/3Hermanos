import flet as ft
from modals.modal_crud_producto import show_modal_editar_producto
from modals.modal_corte import show_modal_corte
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
        
        # Variables de estado
        self.txt_oro_10k = None
        self.txt_oro_14k = None
        self.txt_italiano = None
        self.lista = None
        self.filter_text = None
        
        # --- LÓGICA CÓDIGO 2: Estructura de carrito basada en lista de diccionarios ---
        # [{'product': db_tuple, 'price': float, 'qty': int}, ...]
        self.carrito = [] 
        
        self.sidebar_content = ft.Column(
            controls=[],
            scroll="auto",
            expand=True
        )

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
        )
        
        self._construir_interfaz()

        self._reconstruir_sidebar_visual()
        self.actualizar_lista_productos()

    # --- LÓGICA DE PRECIOS (Código 2) ---

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
        """Calcula el precio sugerido basado en peso * cotización"""
        try:
            peso = float(producto[3]) 
            kilataje = producto[4]
            precio_gramo = self._obtener_precio_gramo(kilataje)
            return peso * precio_gramo
        except (ValueError, TypeError):
            return 0.0

    # --- TILES VISUALES (Lista Principal) ---
    # Mantiene el diseño del Codigo 1, pero usa la lógica de stock del Codigo 2

    def _crear_producto_tile(self, producto, on_agregar):
        # Indices: [0]id, [1]key, [2]name, [3]weight, [4]karat, [5]category, [6]qty
        cantidad_stock = producto[6] if len(producto) > 6 else 1
        
        # --- LÓGICA CÓDIGO 2: Calcular stock visual disponible ---
        en_carrito = 0
        for item in self.carrito:
            if item['product'][0] == producto[0]: # Comparar por ID
                en_carrito = item['qty']
                break
        
        disponible_visual = cantidad_stock - en_carrito

        nombre = producto[2]
        peso_str = producto[3]
        kilataje = producto[4]
        categoria = producto[5]
        clave = producto[1]
        
        # Etiquetas de stock (Diseño Código 1)
        texto_stock = ""
        color_stock = ft.Colors.BLACK
        
        if cantidad_stock > 1:
            texto_stock = f"Stock: {disponible_visual}" # Muestra el disponible real
            color_stock = ft.Colors.BLUE_GREY
        else:
            texto_stock = "Pieza Única"
            color_stock = ft.Colors.ORANGE_400
        
        precio_num = self._calcular_precio_numerico(producto)
        texto_precio = f"${precio_num:,.2f}"
        
        return ft.Container(
            padding=ft.padding.all(10),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            # --- COLUMNA IZQUIERDA (Info) ---
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        f"{nombre} | {peso_str} gr. | {kilataje}", 
                                        weight=ft.FontWeight.BOLD, 
                                        color='Black', 
                                        size=20 
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
                                        height=35,
                                        # Lógica Código 2: Pasamos el producto entero
                                        on_click=lambda e: on_agregar(producto)
                                    )
                                ]
                            )
                        ]
                    ),
                    ft.Container(height=10),
                    ft.Divider(height=1, color=ft.Colors.GREY_300)
                ]
            )
        )

    # --- TILES VISUALES (Sidebar / Carrito Editable) ---
    # Lógica del Código 2 (Inputs editables) con Estética similar al Código 1


    def _accion_nuevo_producto_sidebar(self):
        """
        Abre el modal para crear producto. 
        Al guardar, detecta el último producto creado y lo agrega al carrito.
        """
        def al_guardar_producto():
            # 1. Actualizamos la lista principal (obligatorio)
            self.actualizar_lista_productos()
            
            # 2. Buscamos el producto más nuevo (el que tiene el ID más alto)
            try:
                todos_los_productos = obtener_productos()
                if todos_los_productos:
                    # Asumiendo que la tupla es (id, clave, nombre...), el ID es el índice 0
                    # La función max busca el ID mayor
                    ultimo_producto = max(todos_los_productos, key=lambda p: p[0])
                    
                    # 3. Lo agregamos al carrito automáticamente
                    self._agregar_a_sidebar(ultimo_producto)
                    
                    # 4. Feedback visual
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"¡{ultimo_producto[2]} creado y agregado!"), 
                        bgcolor="green",
                        duration=2000
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
            except Exception as e:
                logging.error(f"Error en auto-agregar: {e}")

        # Abrimos el modal pasándole nuestro callback especial
        show_modal_editar_producto(self.page, al_guardar_producto)

    def _crear_sidebar_tile(self, item_carrito):
        """
        item_carrito es dict: {'product': p, 'price': float, 'qty': int}
        Creamos inputs para editar precio y cantidad (Lógica Cod 2)
        """
        producto = item_carrito['product']
        max_stock = producto[6] if len(producto) > 6 else 1

        # Input de Cantidad (Lógica Cod 2)
        txt_cantidad = ft.TextField(
            value=str(item_carrito['qty']),
            width=50,
            height=30,
            text_size=13,
            content_padding=5,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.CENTER,
            dense=True,
            # Estilo minimalista para que encaje
            border_color=ft.Colors.GREY_400,
            on_change=lambda e: self._actualizar_cantidad_item(item_carrito, e.control.value, max_stock)
        )

        # Input de Precio (Lógica Cod 2 - Editable)
        txt_precio = ft.TextField(
            value=f"{item_carrito['price']:.2f}",
            prefix_text="$",
            width=90,
            height=30,
            text_size=13,
            content_padding=5,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
            dense=True,
            border_color=ft.Colors.GREY_400,
            on_change=lambda e: self._actualizar_precio_item(item_carrito, e.control.value)
        )

        # Contenedor visual (Diseño Cod 1)
        tile_en_sidebar = ft.Container(
            padding=ft.padding.symmetric(vertical=5, horizontal=5),
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY_300)),
            content=ft.Column([
                # Fila Superior: Nombre y Botón Eliminar
                ft.Row([
                    ft.Text(
                        f"{producto[2]}", 
                        weight=ft.FontWeight.BOLD, 
                        size=13, 
                        max_lines=2, 
                        overflow=ft.TextOverflow.ELLIPSIS, 
                        expand=True
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        icon_size=20,
                        tooltip="Quitar del carrito",
                        on_click=lambda e: self._remover_de_sidebar(item_carrito)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Fila Inferior: Detalles y Controles de Edición
                ft.Row([
                    ft.Text(f"Cod: {producto[1]}", size=10, color=ft.Colors.GREY_500),
                    ft.Container(expand=True), # Espaciador
                    ft.Text("Cant:", size=11, color="grey"),
                    txt_cantidad,
                    ft.Container(width=5),
                    txt_precio
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ])
        )
        return tile_en_sidebar

    # --- LÓGICA DE CARRITO Y EDICIÓN (Código 2) ---

    def _actualizar_cantidad_item(self, item, valor_str, max_stock):
        try:
            if not valor_str: return
            nueva_cant = int(valor_str)
            
            if nueva_cant < 1: 
                nueva_cant = 1
            
            if nueva_cant > max_stock:
                nueva_cant = max_stock
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Stock máximo es {max_stock}"), bgcolor="red")
                self.page.snack_bar.open = True
                self.page.update()
            
            item['qty'] = nueva_cant
        except ValueError:
            pass 
        
        # Recalcular totales y refrescar lista principal (el stock visual cambia)
        self._actualizar_subtotal()
        self.actualizar_lista_productos() 

    def _actualizar_precio_item(self, item, valor_str):
        try:
            if not valor_str: return
            nuevo_precio = float(valor_str)
            item['price'] = nuevo_precio
        except ValueError:
            pass
        self._actualizar_subtotal()

    def _actualizar_subtotal(self):
        # Total es suma de (precio * cantidad) para cada item
        total = sum(item['price'] * item['qty'] for item in self.carrito)
        self.txt_subtotal.value = f"${total:,.2f}"
        
        self.btn_continuar.disabled = (total == 0)
        self.btn_continuar.on_click = lambda e: self._abrir_modal_pago(total)
        
        self.txt_subtotal.update()
        self.btn_continuar.update()

    def _agregar_a_sidebar(self, producto):
        # 1. Checar si ya existe en el carrito (Lógica Cod 2)
        item_existente = next((i for i in self.carrito if i['product'][0] == producto[0]), None)
        
        max_stock = producto[6] if len(producto) > 6 else 1

        if item_existente:
            if item_existente['qty'] < max_stock:
                item_existente['qty'] += 1
            else:
                self.page.snack_bar = ft.SnackBar(ft.Text("No hay más stock disponible"), bgcolor="red")
                self.page.snack_bar.open = True
                self.page.update()
                return 
        else:
            # Nuevo item en carrito
            precio_inicial = self._calcular_precio_numerico(producto)
            nuevo_item = {
                'product': producto,
                'price': precio_inicial,
                'qty': 1
            }
            self.carrito.append(nuevo_item)

        self._reconstruir_sidebar_visual()
        self._actualizar_subtotal()
        self.actualizar_lista_productos()

    def _remover_de_sidebar(self, item_a_borrar):
        if item_a_borrar in self.carrito:
            self.carrito.remove(item_a_borrar)
        
        self._reconstruir_sidebar_visual()
        self._actualizar_subtotal()
        self.actualizar_lista_productos()

    def _reconstruir_sidebar_visual(self):
        """Reconstruye TODA la sidebar (Cabecera + Items)"""
        
        # --- 1. Crear la Cabecera con el Botón "+" ---
        cabecera = ft.Column(
            spacing=0,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Carrito de Compras", size=14, weight="bold"),
                        # BOTÓN NUEVO AQUÍ
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_color="green",
                            tooltip="Crear y agregar producto rápido",
                            icon_size=24,
                            on_click=lambda e: self._accion_nuevo_producto_sidebar()
                        )
                    ]
                ),
                ft.Text("Precio y cantidad editables", size=10, color="grey"),
                ft.Divider(height=1, color=ft.Colors.GREY_300)
            ]
        )
        
        # --- 2. Crear los tiles de productos ---
        nuevos_tiles = []
        for item in self.carrito:
            nuevos_tiles.append(self._crear_sidebar_tile(item))
            
        # --- 3. Juntar todo ---
        # La lista de controles es: [Cabecera] + [Lista de Productos]
        self.sidebar_content.controls = [cabecera] + nuevos_tiles

        if self.sidebar_content.page:
            self.sidebar_content.update()

    def _abrir_modal_pago(self, total):
        empleado_id = self.page.session.get('empleado_id')
        if not empleado_id: 
            print("Error: No empleado ID")
            return

        # ### ADAPTADOR DE DATOS ###
        # El manager espera una lista de tuplas [(producto, precio)].
        # Como ahora tenemos cantidades, debemos "aplanar" la lista.
        
        lista_para_manager = []
        for item in self.carrito:
            prod = item['product']
            precio = item['price']
            qty = item['qty']
            
            # Añadir el producto N veces a la lista final
            for _ in range(qty):
                lista_para_manager.append((prod, precio))

        show_modal_pago(
            self.page, 
            lista_para_manager, # Enviamos la lista aplanada
            total, 
            empleado_id, 
            self._limpiar_despues_venta 
        )

    def _limpiar_despues_venta(self):
        self.carrito = [] 
        self._reconstruir_sidebar_visual()
        self._actualizar_subtotal()
        self.actualizar_lista_productos()

    # --- FILTRADO Y ACTUALIZACIÓN (Misma lógica, variables adaptadas) ---

    def filtrar_productos(self, texto_busqueda="", criterio_orden="nombre"):
        productos = obtener_productos()
        
        # 1. Filtro de Texto
        if texto_busqueda:
            texto_busqueda = texto_busqueda.lower()
            productos = [
                p for p in productos 
                if (texto_busqueda in str(p[2]).lower() or
                    texto_busqueda in str(p[4]).lower() or
                    texto_busqueda in str(p[5]).lower())
            ]
        
        # 2. Ordenamiento
        try:
            if criterio_orden == "nombre":
                productos.sort(key=lambda x: str(x[2]).lower())
            elif criterio_orden == "kilataje":
                productos.sort(key=lambda x: str(x[4]).lower())
            elif criterio_orden == "categoria":
                productos.sort(key=lambda x: str(x[5]).lower())
        except Exception as e:
            logging.error(f"Error al ordenar: {e}")
            
        # 3. Filtro de Disponibilidad (Lógica Cod 2)
        # Solo mostramos productos que tengan stock visual > 0
        productos_finales = []
        for p in productos:
            en_carrito = 0
            for item in self.carrito:
                if item['product'][0] == p[0]:
                    en_carrito = item['qty']
                    break
            
            stock_bd = p[6] if len(p) > 6 else 1
            
            if (stock_bd - en_carrito) > 0:
                productos_finales.append(p)
                
        return productos_finales

    def actualizar_lista_productos(self, texto_busqueda="", criterio_orden="nombre"):
        if not self.lista:
            return

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
        # Guardar precios en DB
        try:
            p_10k = float(self.txt_oro_10k.value) if self.txt_oro_10k.value else 0.0
            p_14k = float(self.txt_oro_14k.value) if self.txt_oro_14k.value else 0.0
            p_ita = float(self.txt_italiano.value) if self.txt_italiano.value else 0.0
            
            actualizar_precio_oro(p_10k, p_14k, p_ita)
            
        except ValueError:
            pass

        # Solo actualizamos la lista principal (sugeridos)
        # NO sobreescribimos los precios del carrito para respetar ediciones manuales
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

    # --- INTERFAZ UI (Estructura visual exacta del Código 1) ---

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
                                on_click=lambda e: show_modal_corte(self.page)
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