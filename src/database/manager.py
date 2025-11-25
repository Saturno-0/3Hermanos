import sqlite3
from datetime import datetime
import logging

def crear_tablas():
    """Crea las tablas de productos y empleados si no existen"""
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()

    # Tabla productos (Fuente de verdad)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clave TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        peso REAL NOT NULL,
        kilataje TEXT NOT NULL,
        categoria TEXT NOT NULL
    )
    ''')

    # Tabla empleados (Fuente de verdad)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Nueva tabla para registrar ventas maestras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        total REAL NOT NULL,
        metodo_pago TEXT NOT NULL DEFAULT 'Efectivo',
        empleado_id INTEGER NOT NULL,
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    )
    ''')
    
    # Nueva tabla para registrar los detalles de cada venta
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalles_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER NOT NULL,
        producto_id_original INTEGER, 
        nombre TEXT NOT NULL,
        peso REAL NOT NULL,
        kilataje TEXT NOT NULL,
        categoria TEXT NOT NULL,
        precio_venta REAL NOT NULL,
        FOREIGN KEY (venta_id) REFERENCES ventas(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS apartados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_inicio TEXT NOT NULL,
        empleado_id INTEGER NOT NULL,
        total_venta REAL NOT NULL,
        total_abonado REAL NOT NULL,
        total_pendiente REAL NOT NULL, 
        estado TEXT NOT NULL, -- "Pendiente", "Liquidado", "Cancelado"
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalles_apartado (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apartado_id INTEGER NOT NULL,
        producto_id_original INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        peso REAL NOT NULL,
        kilataje TEXT NOT NULL,
        precio_unitario REAL NOT NULL,
        FOREIGN KEY (apartado_id) REFERENCES apartados(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS abonos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        apartado_id INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        monto_abonado REAL NOT NULL,
        metodo_pago TEXT NOT NULL,
        empleado_id INTEGER NOT NULL,
        FOREIGN KEY (apartado_id) REFERENCES apartados(id),
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    )
    ''')

    conexion.commit()
    conexion.close()
    
def crear_empleado(nombre, password):
    """
    Crea un nuevo empleado.
    Se eliminó 'codigo_identificador' para coincidir con la tabla.
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO empleados (nombre, password)
            VALUES (?, ?)
        ''', (nombre, password))
        
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        # Podría fallar si 'nombre' se define como UNIQUE
        return False
    finally:
        conexion.close()
    

def validar_empleado(nombre: str, password: str):
    """
    Valida las credenciales de un empleado por nombre y password.
    Cambiado de 'codigo_identificador' a 'nombre'.
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre FROM empleados WHERE nombre = ? AND password = ?",
        (nombre, password)
    )
    resultado = cursor.fetchone()
    conexion.close()
    return resultado if resultado else None

def obtener_productos():
    """Obtiene todos los productos de la base de datos"""
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    
    conexion.close()
    return productos

def obtener_producto_por_clave(clave):
    """
    Obtiene un producto por su clave.
    Cambiado de 'obtener_producto_por_barcode' a 'obtener_producto_por_clave'.
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos WHERE clave = ?", (clave,))
    producto = cursor.fetchone()
    conexion.close()
    return producto

def agregar_producto(clave, nombre, peso, kilataje, categoria):
    
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    try:
        cursor.execute('''
            INSERT INTO productos (clave, nombre, peso, kilataje, categoria)
            VALUES (?, ?, ?, ?, ?)
        ''', (clave, nombre, peso, kilataje, categoria))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()

def actualizar_producto(id_producto, clave, nombre, peso, kilataje, categoria):
    """
    Actualiza un producto existente.
    Las columnas 'marca', 'precio', 'cantidad' y 'codigo_barras' 
    fueron reemplazadas por 'peso' y 'kilataje' para coincidir con la tabla.
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    try:
        cursor.execute('''
            UPDATE productos 
            SET clave=? nombre=?, peso=?, kilataje=?, categoria=?
            WHERE id=?
        ''', (clave, nombre, peso, kilataje, categoria, id_producto))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()

def obtener_inventario_actual():
    """
    Obtiene el inventario actual de productos.
    Se ajustaron las columnas a 'peso' y 'kilataje'.
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        SELECT id, clave, nombre, peso, kilataje, categoria
        FROM productos 
        ORDER BY nombre
    ''')
    
    inventario = cursor.fetchall()
    conexion.close()
    return inventario

def eliminar_producto(id_producto):
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conexion.commit()
        return cursor.rowcount > 0  # Retorna True si se eliminó algún registro
    except sqlite3.Error:
        return False
    finally:
        conexion.close()
        
def registrar_venta(empleado_id, productos_vendidos, total, metodo_pago):
    """
    Implementa la lógica Opción B:
    1. Crea la venta.
    2. Copia los datos del producto a detalles_venta.
    3. BORRA el producto de la tabla productos.
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # 1. Registrar Venta Maestra
        cursor.execute('''
            INSERT INTO ventas (fecha, total, empleado_id, metodo_pago)
            VALUES (?, ?, ?, ?)
        ''', (fecha_actual, total, empleado_id, metodo_pago))
        
        venta_id = cursor.lastrowid
        
        # 2. Procesar cada producto
        for producto_tuple, precio_final in productos_vendidos:
            # Desempaquetamos la tupla original de la BD
            # (id, clave, nombre, peso, kilataje, categoria)
            p_id = producto_tuple[0]
            p_nombre = producto_tuple[2]
            p_peso = producto_tuple[3]
            p_kilataje = producto_tuple[4]
            p_categoria = producto_tuple[5]
            
            # A) Guardamos la "FOTO" en el historial (Detalle)
            cursor.execute('''
                INSERT INTO detalles_venta 
                (venta_id, producto_id_original, nombre, peso, kilataje, categoria, precio_venta)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (venta_id, p_id, p_nombre, p_peso, p_kilataje, p_categoria, precio_final))
            
            # B) BORRAMOS el producto del inventario actual
            cursor.execute("DELETE FROM productos WHERE id = ?", (p_id,))
        
        conexion.commit()
        return venta_id
    
    except sqlite3.Error as e:
        conexion.rollback()
        logging.error(f"Error fatal en venta (Rollback realizado): {e}")
        return None
    finally:
        conexion.close()

def registrar_apartado(empleado_id, productos_apartados, total_venta, abono_inicial, metodo_pago_abono):
    """
    Registra un nuevo apartado, el primer abono, y elimina los productos del inventario.
    
    Args:
        empleado_id: ID del empleado
        productos_apartados: Lista de tuplas (producto, precio_calculado)
        total_venta: El costo total de los productos
        abono_inicial: El primer pago
        metodo_pago_abono: Método de pago del primer abono
    
    Returns:
        ID del apartado registrado o None si hay error
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # 1. Registrar el apartado maestro
        total_pendiente = total_venta - abono_inicial
        cursor.execute('''
            INSERT INTO apartados (fecha_inicio, empleado_id, total_venta, total_abonado, total_pendiente, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (fecha_actual, empleado_id, total_venta, abono_inicial, total_pendiente, "Pendiente"))
        
        apartado_id = cursor.lastrowid
        
        # 2. Registrar el primer abono
        cursor.execute('''
            INSERT INTO abonos (apartado_id, fecha, monto_abonado, metodo_pago, empleado_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (apartado_id, fecha_actual, abono_inicial, metodo_pago_abono, empleado_id))
        
        # 3. Registrar detalles y ELIMINAR productos
        for producto, precio_unitario in productos_apartados:
            # producto = (id[0], clave[1], nombre[2], peso[3], kilataje[4], categoria[5])
            
            # Registrar detalle del apartado
            cursor.execute('''
                INSERT INTO detalles_apartado (apartado_id, producto_id_original, nombre, peso, kilataje, precio_unitario)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (apartado_id, producto[0], producto[2], producto[3], producto[4], precio_unitario))
            
            # 4. ELIMINAR producto del inventario
            cursor.execute("DELETE FROM productos WHERE id = ?", (producto[0],))
        
        conexion.commit()
        return apartado_id
    
    except sqlite3.Error as e:
        conexion.rollback()
        logging.error(f"Error al registrar apartado: {e}")
        return None
    
    finally:
        conexion.close()

def obtener_ventas_del_dia():
    """
    Obtiene todas las ventas del día actual
    
    Returns:
        Lista de tuplas con los datos de las ventas
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT v.id, v.total, e.nombre
        FROM ventas v
        JOIN empleados e ON v.empleado_id = e.id
        WHERE v.fecha = ?
        ORDER BY v.fecha
    ''', (fecha_actual,))
    
    ventas = cursor.fetchall()
    conexion.close()
    return ventas

def obtener_detalle_venta(venta_id):
    """
    Obtiene los detalles de una venta específica.
    Se cambió 'p.marca' por 'p.kilataje'.
    
    Args:
        venta_id: ID de la venta
        
    Returns:
        Lista de tuplas con los detalles de la venta
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        SELECT p.nombre, p.kilataje, dv.cantidad, dv.precio_unitario, (dv.cantidad * dv.precio_unitario) as subtotal
        FROM detalles_venta dv
        JOIN productos p ON dv.producto_id = p.id
        WHERE dv.venta_id = ?
    ''', (venta_id,))
    
    detalles = cursor.fetchall()
    conexion.close()
    return detalles

def obtener_ventas_por_empleado_hoy():
    """
    Obtiene el total de ventas por empleado para el día actual
    
    Returns:
        Lista de tuplas (nombre_empleado, total_ventas)
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT e.nombre, SUM(v.total) as total_ventas
        FROM ventas v
        JOIN empleados e ON v.empleado_id = e.id
        WHERE v.fecha = ?
        GROUP BY v.empleado_id
        ORDER BY total_ventas DESC
    ''', (fecha_actual,))
    
    ventas_por_empleado = cursor.fetchall()
    conexion.close()
    return ventas_por_empleado

def obtener_total_ventas_hoy():
    """
    Obtiene el total de todas las ventas del día
    
    Returns:
        Valor total de ventas
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT SUM(total) as total_ventas
        FROM ventas
        WHERE fecha = ?
    ''', (fecha_actual,))
    
    resultado = cursor.fetchone()
    conexion.close()
    
    return resultado[0] if resultado and resultado[0] else 0.0

def exportar_ventas_csv():
    """
    Genera los datos para exportar las ventas del día a CSV
    
    Returns:
        Datos de ventas formateados para CSV
    """
    # Primero obtenemos la lista de ventas del día
    ventas = obtener_ventas_del_dia()
    
    # Cabecera para el CSV
    datos_csv = [["ID Venta", "Total", "Empleado"]]
    
    # Añadimos cada venta
    for venta in ventas:
        datos_csv.append([str(venta[0]), str(venta[1]), venta[2]])
    
    return datos_csv

def exportar_inventario_csv():
    """
    Genera los datos para exportar el inventario actual a CSV.
    Se ajustaron las cabeceras y los datos a las columnas de la tabla.
    
    Returns:
        Datos de inventario formateados para CSV
    """
    # Obtenemos el inventario actual
    inventario = obtener_inventario_actual() # (id, nombre, peso, kilataje, categoria)
    
    # Cabecera para el CSV (ajustada)
    datos_csv = [["ID", "Producto", "Peso", "Kilataje", "Categoría"]]
    
    # Añadimos cada producto (ajustado)
    for producto in inventario:
        datos_csv.append([
            str(producto[0]),   # ID
            producto[1],        # Producto (nombre)
            str(producto[2]),   # Peso
            str(producto[3]),   # Kilataje
            producto[4]         # Categoría
        ])
    
    return datos_csv

# Crear tablas al importar este módulo
crear_tablas()