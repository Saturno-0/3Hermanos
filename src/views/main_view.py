# main_view.py
import flet as ft
from functools import partial

# Debes definir o importar estas funciones
# from utils import obtener_productos, obtener_producto_por_barcode 
# from modals import show_modal_editar_producto, show_modal_corte, show_modal_descuento, show_modal_pago 

# NOTA: Simulaciones de funciones que DEBES implementar o importar
def obtener_productos():
    # Simulación de datos: (id, nombre, marca, precio, código, categoría)
    return [
        (1, "Labial Velvet", "ColorPop", 150.00, "750100000001", "Maquillaje"),
        (2, "Esmalte Rojo", "NailsArt", 85.50, "750100000002", "Uñas"),
    ]

def obtener_producto_por_barcode(codigo_barras):
    # Lógica de búsqueda real
    if codigo_barras == "12345":
        return (3, "Crema Facial", "DermCare", 220.00, "12345", "Cuidado Personal")
    return None

def show_modal_editar_producto(page, callback):
    page.snack_bar = ft.SnackBar(ft.Text("Modal editar producto simulado"))
    page.snack_bar.open = True
    page.update()

def show_modal_corte(page):
    page.snack_bar = ft.SnackBar(ft.Text("Modal Corte simulado"))
    page.snack_bar.open = True
    page.update()

def show_modal_descuento(page, sale, callback):
    page.snack_bar = ft.SnackBar(ft.Text("Modal Descuento simulado"))
    page.snack_bar.open = True
    page.update()

def show_modal_pago(page, sale, empleado_id, nuevo_pedido_callback, actualizar_sidebar_callback):
    page.snack_bar = ft.SnackBar(ft.Text("Modal Pago simulado"))
    page.snack_bar.open = True
    page.update()

# --- Clase de Lógica de Negocio (Se mantiene) ---
class Sale: 
    def __init__(self):
        self.productos = []
        self.subtotal = 0.0
        self.descuento_porcentaje = 0.0
        self.descuento = 0.0
        self.total = 0.0
        
    def _calcular_totales(self):
        """Calcula subtotal, descuento y total final"""
        # (p[3] es el precio)
        self.subtotal = sum(p[3] * cantidad for p, cantidad in self.productos)
        self.descuento = self.subtotal * (self.descuento_porcentaje / 100)
        self.total = max(0, self.subtotal - self.descuento)

    def aplicar_descuento(self, porcentaje):
        self.descuento_porcentaje = max(0, min(100, float(porcentaje)))
        self._calcular_totales()
        
    def agregar_producto(self, producto):
        for i, (p, cantidad) in enumerate(self.productos):
            if p[0] == producto[0]:
                self.productos[i] = (p, cantidad + 1)
                self._calcular_totales() # Corregido de _calcular_total
                return
        self.productos.append((producto, 1))
        self._calcular_totales() # Corregido de _calcular_total

    def actualizar_cantidad(self, producto_id, nueva_cantidad):
        for i, (p, cantidad) in enumerate(self.productos):
            if p[0] == producto_id:
                if nueva_cantidad <= 0:
                    del self.productos[i]
                else:
                    self.productos[i] = (p, nueva_cantidad)
                self._calcular_totales() # Corregido de _calcular_total
                break

    # NOTA: Tu código original usaba un método llamado _calcular_total que era redundante o incompleto, 
    # se usa el corregido _calcular_totales en toda la clase para consistencia.
    
    def agregar_producto_por_codigo(self, codigo_barras):
        # Asegúrate de que esta función esté implementada o importada
        producto = obtener_producto_por_barcode(codigo_barras) 
        if producto:
            self.agregar_producto(producto)
            return True
        return False

# --- Clase de la Vista Principal (Punto de Venta) ---
class MainView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/main",
            padding=ft.padding.only(left=40, top=40, right=40, bottom=10),
            bgcolor=ft.Colors.PINK_100
        )
        self.page = page
        self.sale = Sale()
        self.codigo_barras_buffer = ""
        
        # Inicializa controles que necesitan ser actualizados
        self.filter_text = ft.Text('Filtrar por: Nombre', size=16, weight=ft.FontWeight.W_600)
        # Inicializa los contenedores (se llenarán en las funciones de actualización)
        self.lista = self._crear_lista_productos_vacia() 
        self.sidebar = self._crear_sidebar_vacia() 
        
        # Adjunta el manejador de teclado (solo se activa en /main)
        page.on_keyboard_event = self._on_keyboard
        
        # Construye la interfaz
        self.controls = self._construir_interfaz()
        
        # Inicializa el contenido de los contenedores
        self.actualizar_lista_productos()
        self.actualizar_sidebar()


    # --- Lógica de Eventos/Interacción ---
    
    def _on_keyboard(self, e: ft.KeyboardEvent):
        if e.key == "Enter":
            if self.codigo_barras_buffer:
                if self.sale.agregar_producto_por_codigo(self.codigo_barras_buffer):
                    self.actualizar_sidebar()
                self.codigo_barras_buffer = ""
        elif len(e.key) == 1 and e.key.isalnum():
            self.codigo_barras_buffer += e.key
        elif self.codigo_barras_buffer: 
            self.codigo_barras_buffer = ""
        self.page.update()

    def on_logout(self, e):
        # Lógica de confirmación de cierre de sesión (copiada de main.py)
        def yes_click(e):
            self.page.views.clear()
            self.page.go("/login")

        def no_click(e):
            self.page.close(confirm_logout)
            
        confirm_logout = ft.AlertDialog(
            modal=True,
            title=ft.Text("Esta a punto de cerrar sesion"),
            content=ft.Text("Todo cambio no confirmado sera eliminado, ¿continuar?"),
            actions=[
                ft.ElevatedButton("Si", on_click=yes_click),
                ft.OutlinedButton("No", on_click=no_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(confirm_logout)

    def nuevo_pedido(self, e):
        self.sale = Sale()
        self.actualizar_sidebar()
        
    def _actualizar_cantidad_producto_handler(self, e, producto_id, cambio):
        for p, cantidad in self.sale.productos:
            if p[0] == producto_id:
                self.sale.actualizar_cantidad(producto_id, cantidad + cambio)
                self.actualizar_sidebar()
                break

    def _cambiar_cantidad_producto_handler(self, nueva_cantidad_str, producto_id):
        try:
            nueva_cantidad = int(nueva_cantidad_str) if nueva_cantidad_str else 0
            self.sale.actualizar_cantidad(producto_id, nueva_cantidad)
            self.actualizar_sidebar()
        except ValueError:
             # Si no es número, se ignora
            pass
            
    def _on_filter_selected(self, e):
        criterio = "nombre"
        if e.control.text == "Marca":
            criterio = "marca"
        elif e.control.text == "Categoria":
            criterio = "categoria"
            
        self.filter_text.value = f"Filtrar por: {e.control.text}"
        
        # Obtenemos el valor de la barra de búsqueda (asumiendo que es el primer TextField en el primer contenedor)
        search_value = self.controls[1].controls[0].controls[0].content.controls[3].value
        
        self.actualizar_lista_productos(search_value, criterio)
        self.page.update()


    # --- Lógica de Construcción de UI (Sub-componentes) ---
    
    def _crear_producto_tile(self, producto):
        # Función para agregar un producto al carrito y actualizar la sidebar
        on_agregar = lambda e, p=producto: (
            self.sale.agregar_producto(p), 
            self.actualizar_sidebar()
        )
        
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
                        content=ft.Text(f"Precio: ${producto[3]:.2f}", size=15, weight=ft.FontWeight.BOLD)
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

    def _crear_item_carrito(self, producto, cantidad):
        precio_total = producto[3] * cantidad
        producto_id = producto[0]
        
        # Handlers con partial para pasar el producto ID
        on_aumentar = partial(self._actualizar_cantidad_producto_handler, producto_id=producto_id, cambio=+1)
        on_disminuir = partial(self._actualizar_cantidad_producto_handler, producto_id=producto_id, cambio=-1)
        on_cambio_cantidad = partial(self._cambiar_cantidad_producto_handler, producto_id=producto_id)
        
        cantidad_field = ft.Container(
            bgcolor='#D9D9D9',
            alignment=ft.alignment.center,
            width=50,
            border_radius=5,
            content=ft.TextField(
                value=str(cantidad),
                text_align=ft.TextAlign.CENTER,
                border=ft.InputBorder.NONE,
                on_change=lambda e: on_cambio_cantidad(e.control.value),
                input_filter=ft.NumbersOnlyInputFilter(),
                keyboard_type=ft.KeyboardType.NUMBER,
                on_blur=lambda e: self.actualizar_sidebar() # Forzar la actualización al salir del campo
            )
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text(producto[1], weight=ft.FontWeight.BOLD, size=16),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Text("Cant.", size=15),
                        ft.IconButton(icon=ft.Icons.REMOVE, icon_color=ft.Colors.BLACK, on_click=on_disminuir, tooltip="Reducir cantidad"),
                        cantidad_field,
                        ft.IconButton(icon=ft.Icons.ADD, icon_color=ft.Colors.BLACK, on_click=on_aumentar, tooltip="Aumentar cantidad"),
                        ft.Container(expand=True),
                        ft.Text(f"${precio_total:.2f}", size=20, weight=ft.FontWeight.BOLD)
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ]),
            padding=10,
            margin=5,
            border_radius=10,
            bgcolor="#f0f0f0"
        )
        
    def _crear_lista_productos_vacia(self):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            expand=True,
            content=ft.ListView(controls=[])
        )
    
    def _crear_sidebar_vacia(self):
        return ft.Container(
            alignment=ft.alignment.top_center,
            expand=3,
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            content=ft.Column(
                controls=[],
                spacing=0,
                expand=True
            )
        )
    
    
    # --- Lógica de Filtrado y Actualización ---

    def filtrar_productos(self, texto_busqueda="", criterio_orden="nombre"):
        productos = obtener_productos() # Utiliza tu función real
        
        if texto_busqueda:
            texto_busqueda = texto_busqueda.lower()
            productos = [
                p for p in productos 
                if (texto_busqueda in str(p[1]).lower() or
                    texto_busqueda in str(p[2]).lower() or 
                    texto_busqueda in str(p[5]).lower()) 
            ]
        
        if criterio_orden == "nombre":
            productos.sort(key=lambda x: str(x[1]).lower())
        elif criterio_orden == "marca":
            productos.sort(key=lambda x: str(x[2]).lower())
        elif criterio_orden == "categoria":
            productos.sort(key=lambda x: str(x[5]).lower()) 
        
        return productos

    def actualizar_lista_productos(self, texto_busqueda="", criterio_orden="nombre"):
        productos = self.filtrar_productos(texto_busqueda, criterio_orden)
        
        self.lista.content.controls = [
            self._crear_producto_tile(producto)
            for producto in productos
        ]
        self.lista.update()
        
    def actualizar_sidebar(self):
        items_carrito = [self._crear_item_carrito(p, c) for p, c in self.sale.productos]
        
        self.sale._calcular_totales()
        
        scroll_area = ft.ListView(
            controls=[
                ft.Text("Los productos que escanees o busques aparecerán aquí", size=12),
                ft.Divider(height=1),
                *items_carrito
            ],
            expand=True
        )
        
        total_controls = [
            ft.Row([ft.Text(f"Subtotal: ${self.sale.subtotal:.2f}")], alignment=ft.MainAxisAlignment.CENTER)
        ]
        
        if self.sale.descuento > 0:
            total_controls.append(
                ft.Row(
                    [ft.Text(f"Descuento ({self.sale.descuento_porcentaje}%): -${self.sale.descuento:.2f}", color="red")],
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
            
        total_controls.append(
            ft.Row([ft.Text(f"Total: ${self.sale.total:.2f}", weight=ft.FontWeight.BOLD, size=30)], alignment=ft.MainAxisAlignment.CENTER)
        )
        
        fixed_controls = ft.Column(
            controls=[
                ft.Divider(),
                ft.FilledButton(
                    "Agregar descuento",
                    color='Black',
                    bgcolor='#FFCDFA',
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                    icon=ft.Icons.DISCOUNT,
                    icon_color='black',
                    on_click=lambda e: show_modal_descuento(self.page, self.sale, self.actualizar_sidebar),
                    disabled=len(self.sale.productos) == 0
                ),
                ft.Column(total_controls, spacing=5),
                ft.Container(
                    content=ft.FilledButton(
                        "Continuar",
                        width=700,
                        height=50,
                        color='Black',
                        bgcolor='#FFCDFA',
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=7),
                            text_style=ft.TextStyle(size=30, weight=ft.FontWeight.BOLD)
                        ),
                        on_click=lambda e: show_modal_pago(self.page, self.sale, self.page.session.get("empleado_id"), self.nuevo_pedido, self.actualizar_sidebar),
                        disabled=len(self.sale.productos) == 0
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ],
            spacing=10,
            tight=True
        )
        
        self.sidebar.content.controls = [scroll_area, fixed_controls]
        self.sidebar.update()

    # --- Construcción de la Interfaz Completa ---

    def _construir_interfaz(self):
        # AppBar
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
                            ft.TextButton(
                                text ='Crear/Editar articulo', 
                                style=ft.ButtonStyle(color=ft.Colors.WHITE),
                                on_click=lambda e: show_modal_editar_producto(self.page, lambda: self.actualizar_lista_productos())
                            ),
                            ft.ElevatedButton(
                                'Corte', color='Black', width=90, bgcolor="#D9D9D9",
                                style=ft.ButtonStyle(color=ft.Colors.BLACK, shape=ft.RoundedRectangleBorder(radius=7)),
                                on_click=lambda e: show_modal_corte(self.page)
                            ),
                            ft.Container(width=2),
                            ft.ElevatedButton(
                                'Nuevo Pedido', color='Black', bgcolor='#FFCDFA',
                                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),
                                on_click=self.nuevo_pedido
                            ),
                        ]
                    ),
                )
            ]
        )

        # Search Bar
        search_bar = ft.Container(
            bgcolor=ft.Colors.WHITE, alignment=ft.alignment.center, height=50, border_radius=15,
            content=ft.Row(
                controls=[
                    ft.Container(width=5), ft.Icon(ft.Icons.SEARCH),  
                    ft.TextField(
                        hint_text="Buscar...", border=ft.InputBorder.NONE, expand=True,
                        on_change=lambda e: self.actualizar_lista_productos(e.control.value)
                    )
                ]
            )
        )
        
        # Filter Bar
        filtro = ft.Container( 
            content=ft.Row( 
                controls=[
                    ft.Text('Listado de Productos', weight=ft.FontWeight.BOLD, size=20),
                    ft.Container(expand=True),
                    self.filter_text,
                    ft.PopupMenuButton(  
                        icon = "FILTER_LIST", icon_color=ft.Colors.BLACK, tooltip="Filtrar",
                        items=[
                            ft.PopupMenuItem(text="Nombre", on_click=self._on_filter_selected),
                            ft.PopupMenuItem(text="Categoria", on_click=self._on_filter_selected),
                            ft.PopupMenuItem(text="Marca", on_click=self._on_filter_selected)
                        ],
                    )
                ]
            )
        )

        # Contenedor de productos (Izquierda)
        product_container = ft.Column(
            controls=[search_bar, filtro, self.lista], expand=7
        )

        # Contenedor principal
        main_container = ft.Row(
            controls=[product_container, self.sidebar], spacing=40, expand=True
        ) 

        # Footer
        footer = ft.Row(
            controls=[
                ft.Text(
                    f"Iniciaste sesión como: {self.page.session.get('empleado_nombre')}",
                    size=17, color=ft.Colors.BLACK, weight=ft.FontWeight.W_600
                ),
                ft.FilledButton(
                    "Cerrar sesion", bgcolor='White', color='Black',
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=7)),  
                    on_click=self.on_logout
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        return [appbar, main_container, footer]