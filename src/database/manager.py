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
        categoria TEXT NOT NULL,
        cantidad INTEGER NOT NULL
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
        producto_id INTEGER NOT NULL, 
        nombre TEXT NOT NULL,
        peso REAL NOT NULL,
        kilataje TEXT NOT NULL,
        categoria TEXT NOT NULL,
        precio_venta REAL NOT NULL,
        FOREIGN KEY (venta_id) REFERENCES ventas(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kilatajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diez REAL NOT NULL,
        catorce REAL NOT NULL,
        italiano REAL NOT NULL
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
        estado TEXT NOT NULL, 
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

def obtener_precios_oro():
    """
    Obtiene los precios actuales. Si no existen, inicializa en 0.
    Retorna una tupla: (diez, catorce, italiano)
    """
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    
    # Intentamos obtener la primera fila (configuración única)
    cursor.execute("SELECT diez, catorce, italiano FROM kilatajes WHERE id = 1")
    resultado = cursor.fetchone()
    
    if resultado:
        conexion.close()
        return resultado
    else:
        # Si no existe configuración, creamos la fila inicial en 0
        cursor.execute("INSERT INTO kilatajes (id, diez, catorce, italiano) VALUES (1, 0.0, 0.0, 0.0)")
        conexion.commit()
        conexion.close()
        return (0.0, 0.0, 0.0)

def actualizar_precio_oro(diez, catorce, italiano):
    """Actualiza los valores en la base de datos"""
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    try:
        # Usamos UPDATE asegurando que solo tocamos la fila con id=1
        cursor.execute('''
            UPDATE kilatajes 
            SET diez = ?, catorce = ?, italiano = ? 
            WHERE id = 1
        ''', (diez, catorce, italiano))
        conexion.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"Error actualizando precios oro: {e}")
        return False
    finally:
        conexion.close()

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

def agregar_producto(clave, nombre, peso, kilataje, categoria, cantidad):
    
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    try:
        cursor.execute('''
            INSERT INTO productos (clave, nombre, peso, kilataje, categoria, cantidad)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (clave, nombre, peso, kilataje, categoria, cantidad))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()

def actualizar_producto(id_producto, clave, nombre, peso, kilataje, categoria, cantidad):
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
            SET clave=?, nombre=?, peso=?, kilataje=?, categoria=?, cantidad=?
            WHERE id=?
        ''', (clave, nombre, peso, kilataje, categoria, cantidad, id_producto))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conexion.close()


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
    conexion = sqlite3.connect("inventario_joyeria.db")
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # 1. Registrar Venta Maestra (Igual)
        cursor.execute('''
            INSERT INTO ventas (fecha, total, empleado_id, metodo_pago)
            VALUES (?, ?, ?, ?)
        ''', (fecha_actual, total, empleado_id, metodo_pago))
        venta_id = cursor.lastrowid
        
        # 2. Procesar cada producto
        for producto_tuple, precio_final in productos_vendidos:
            # producto_tuple: (0:id, 1:clave, 2:nombre, 3:peso, 4:kilataje, 5:categoria, 6:cantidad)
            p_id = producto_tuple[0]
            
            # A) Guardar historial (Igual)
            cursor.execute('''
                INSERT INTO detalles_venta 
                (venta_id, producto_id_original, nombre, peso, kilataje, categoria, precio_venta)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (venta_id, p_id, producto_tuple[2], producto_tuple[3], producto_tuple[4], producto_tuple[5], precio_final))
            
            # B) LÓGICA HÍBRIDA: RESTAR O ELIMINAR
            # Primero verificamos la cantidad actual en la base de datos (por si se vendió otro mientras tanto)
            cursor.execute("SELECT cantidad FROM productos WHERE id = ?", (p_id,))
            resultado = cursor.fetchone()
            
            if resultado:
                stock_actual = resultado[0]
                if stock_actual > 1:
                    # Si hay muchos, restamos 1
                    cursor.execute("UPDATE productos SET cantidad = cantidad - 1 WHERE id = ?", (p_id,))
                else:
                    # Si queda 1 (o menos), lo borramos del inventario
                    cursor.execute("DELETE FROM productos WHERE id = ?", (p_id,))
        
        conexion.commit()
        return venta_id
    
    except sqlite3.Error as e:
        conexion.rollback()
        logging.error(f"Error fatal en venta: {e}")
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

# Crear tablas al importar este módulo
crear_tablas()