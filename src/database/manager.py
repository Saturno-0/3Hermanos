import sqlite3
from datetime import datetime

def crear_tablas():
    """Crea las tablas de productos y empleados si no existen"""
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()

    # Tabla productos (exactamente como en tu original)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        marca TEXT NOT NULL,
        precio REAL NOT NULL,
        cantidad INTEGER NOT NULL,
        categoria TEXT NOT NULL,
        codigo_barras TEXT UNIQUE
    )
    ''')

    # Tabla empleados (exactamente como en tu original)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS empleados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo_identificador TEXT UNIQUE,
        password TEXT NOT NULL
    )
    ''')
    
    # Nueva tabla para registrar ventas maestras
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        total REAL NOT NULL,
        empleado_id INTEGER NOT NULL,
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    )
    ''')
    
    # Nueva tabla para registrar los detalles de cada venta
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalles_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        FOREIGN KEY (venta_id) REFERENCES ventas(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )
    ''')

    conexion.commit()
    conexion.close()
    
def crear_empleado(nombre, codigo_identificador, password):
    
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO empleados (nombre, codigo_identificador, password)
            VALUES (?, ?, ?)
        ''', (nombre, codigo_identificador, password))
        
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        # Error por duplicación de código identificador
        return False
    finally:
        conexion.close()
    
def obtener_id_empleado(codigo: str) -> int:
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM empleados WHERE codigo_identificador = ?", (codigo,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado else None

def validar_empleado(codigo: str, password: str):
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT id, nombre FROM empleados WHERE codigo_identificador = ? AND password = ?",
        (codigo, password)
    )
    resultado = cursor.fetchone()
    conexion.close()
    return resultado if resultado else None

def obtener_productos():
    """Obtiene todos los productos de la base de datos"""
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    
    conexion.close()
    return productos

def agregar_producto(nombre, marca, precio, cantidad, categoria, codigo_barras):
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    try:
        cursor.execute('''
            INSERT INTO productos (nombre, marca, precio, cantidad, categoria, codigo_barras)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, marca, precio, cantidad, categoria, codigo_barras))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()

def actualizar_producto(id_producto, nombre, marca, precio, cantidad, categoria, codigo_barras):
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    try:
        cursor.execute('''
            UPDATE productos 
            SET nombre=?, marca=?, precio=?, cantidad=?, categoria=?, codigo_barras=?
            WHERE id=?
        ''', (nombre, marca, precio, cantidad, categoria, codigo_barras, id_producto))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()

def obtener_producto_por_barcode(codigo_barras):
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos WHERE codigo_barras = ?", (codigo_barras,))
    producto = cursor.fetchone()
    conexion.close()
    return producto


def obtener_inventario_actual():
    """Obtiene el inventario actual de productos"""
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        SELECT id, nombre, marca, cantidad, precio, categoria
        FROM productos 
        ORDER BY nombre
    ''')
    
    inventario = cursor.fetchall()
    conexion.close()
    return inventario

def eliminar_producto(id_producto):
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        conexion.commit()
        return cursor.rowcount > 0  # Retorna True si se eliminó algún registro
    except sqlite3.Error:
        return False
    finally:
        conexion.close()
        
def registrar_venta(empleado_id, productos_vendidos, total):
    """
    Registra una venta completa y sus detalles, actualiza el inventario
    
    Args:
        empleado_id: ID del empleado que realizó la venta
        productos_vendidos: Lista de tuplas (producto, cantidad) donde producto es una tupla con los datos
        total: Total de la venta después de descuentos
    
    Returns:
        ID de la venta registrada o None si hay error
    """
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    
    # Obtener fecha y hora actuales
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    
    
    try:
        # Registrar la venta maestra
        cursor.execute('''
            INSERT INTO ventas (fecha, total, empleado_id)
            VALUES (?, ?, ?)
        ''', (fecha_actual, total, empleado_id))
        
        venta_id = cursor.lastrowid
        
        # Registrar detalles de la venta y actualizar inventario
        for producto, cantidad in productos_vendidos:
            producto_id = producto[0]
            precio_unitario = producto[3]
            
            # Registrar detalle
            cursor.execute('''
                INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            ''', (venta_id, producto_id, cantidad, precio_unitario))
            
            # Actualizar inventario
            cursor.execute('''
                UPDATE productos
                SET cantidad = cantidad - ?
                WHERE id = ?
            ''', (cantidad, producto_id))
        
        conexion.commit()
        return venta_id
    
    except sqlite3.Error as e:
        conexion.rollback()
        print(f"Error al registrar venta: {e}")
        return None
    
    finally:
        conexion.close()

def obtener_ventas_del_dia():
    """
    Obtiene todas las ventas del día actual
    
    Returns:
        Lista de tuplas con los datos de las ventas
    """
    conexion = sqlite3.connect('inventario_dulceria.db')
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
    Obtiene los detalles de una venta específica
    
    Args:
        venta_id: ID de la venta
        
    Returns:
        Lista de tuplas con los detalles de la venta
    """
    conexion = sqlite3.connect('inventario_dulceria.db')
    cursor = conexion.cursor()
    
    cursor.execute('''
        SELECT p.nombre, p.marca, dv.cantidad, dv.precio_unitario, (dv.cantidad * dv.precio_unitario) as subtotal
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
    conexion = sqlite3.connect('inventario_dulceria.db')
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
    conexion = sqlite3.connect('inventario_dulceria.db')
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
    Genera los datos para exportar el inventario actual a CSV
    
    Returns:
        Datos de inventario formateados para CSV
    """
    # Obtenemos el inventario actual
    inventario = obtener_inventario_actual()
    
    # Cabecera para el CSV
    datos_csv = [["ID", "Producto", "Marca", "Cantidad", "Precio", "Categoría"]]
    
    # Añadimos cada producto
    for producto in inventario:
        datos_csv.append([str(producto[0]), producto[1], producto[2],
        str(producto[3]), str(producto[4]), producto[5]])
    
    return datos_csv
# Crear tablas al importar este módulo
crear_tablas()