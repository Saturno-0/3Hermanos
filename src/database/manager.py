import sqlite3
from datetime import datetime

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
        kilataje INTEGER NOT NULL,
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
        
def registrar_venta(empleado_id, productos_vendidos, total):
    """
    Registra una venta completa y sus detalles.
    
    NOTA: La actualización de inventario (restar cantidad) se eliminó
    porque la tabla 'productos' no tiene una columna 'cantidad'.
    
    Args:
        empleado_id: ID del empleado que realizó la venta
        productos_vendidos: Lista de tuplas (producto_id, cantidad, precio_unitario)
        total: Total de la venta después de descuentos
    
    Returns:
        ID de la venta registrada o None si hay error
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
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
        
        # Registrar detalles de la venta
        # La estructura de productos_vendidos se asumió como (producto_id, cantidad, precio_unitario)
        # para que 'precio_unitario' esté disponible.
        for producto_id, cantidad, precio_unitario in productos_vendidos:
            
            # Registrar detalle
            cursor.execute('''
                INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario)
                VALUES (?, ?, ?, ?)
            ''', (venta_id, producto_id, cantidad, precio_unitario))
            
            # --- SECCIÓN ELIMINADA ---
            # La siguiente sección fue eliminada porque la tabla 'productos'
            # no tiene una columna 'cantidad' según tu función crear_tablas().
            #
            # cursor.execute('''
            #     UPDATE productos
            #     SET cantidad = cantidad - ?
            #     WHERE id = ?
            # ''', (cantidad, producto_id))
            # -------------------------
        
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