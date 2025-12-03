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
        folio INTEGER NOT NULL,
        fecha TEXT NOT NULL,
        total REAL NOT NULL,
        metodo_pago TEXT NOT NULL DEFAULT 'Efectivo',
        empleado_id INTEGER NOT NULL,
        cliente_nombre TEXT,
        cliente_direccion TEXT,
        cliente_cp TEXT,
        cliente_telefono TEXT,
        FOREIGN KEY (empleado_id) REFERENCES empleados(id)
    )
    ''')
    
    # Nueva tabla para registrar los detalles de cada venta
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalles_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER NOT NULL,
        producto_id_original INTEGER NOT NULL, 
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
        folio INTEGER NOT NULL,
        fecha_inicio TEXT NOT NULL,
        empleado_id INTEGER NOT NULL,
        total_venta REAL NOT NULL,
        total_abonado REAL NOT NULL,
        total_pendiente REAL NOT NULL, 
        estado TEXT NOT NULL, 
        cliente_nombre TEXT,
        cliente_telefono TEXT,
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
        
def registrar_venta(empleado_id, productos_vendidos, total, metodo_pago, cliente_data):
    """
    cliente_data: Diccionario con {nombre, direccion, cp, telefono}
    """
    conexion = sqlite3.connect("inventario_joyeria.db")
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # --- LÓGICA DEL FOLIO CÍCLICO (1 - 10000) ---
        # Obtenemos el último folio registrado (ordenado por ID descendente)
        cursor.execute("SELECT folio FROM ventas ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()
        
        nuevo_folio = 1
        if resultado:
            ultimo_folio = resultado[0]
            if ultimo_folio >= 10000:
                nuevo_folio = 1 # Reiniciamos el ciclo
            else:
                nuevo_folio = ultimo_folio + 1
        
        # 1. Registrar Venta con los datos del cliente y el nuevo folio
        cursor.execute('''
            INSERT INTO ventas (
                folio, fecha, total, empleado_id, metodo_pago, 
                cliente_nombre, cliente_direccion, cliente_cp, cliente_telefono
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nuevo_folio, 
            fecha_actual, 
            total, 
            empleado_id, 
            metodo_pago,
            cliente_data.get('nombre', 'Público General'),
            cliente_data.get('direccion', ''),
            cliente_data.get('cp', ''),
            cliente_data.get('telefono', '')
        ))
        
        venta_id = cursor.lastrowid # Este es el ID único interno de la BD
        
        # 2. Procesar productos (Igual que antes)
        for producto_tuple, precio_final in productos_vendidos:
            p_id = producto_tuple[0]
            
            cursor.execute('''
                INSERT INTO detalles_venta 
                (venta_id, producto_id_original, nombre, peso, kilataje, categoria, precio_venta)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (venta_id, p_id, producto_tuple[2], producto_tuple[3], producto_tuple[4], producto_tuple[5], precio_final))
            
            # Lógica de inventario híbrido
            cursor.execute("SELECT cantidad FROM productos WHERE id = ?", (p_id,))
            res_stock = cursor.fetchone()
            if res_stock:
                stock_actual = res_stock[0]
                if stock_actual > 1:
                    cursor.execute("UPDATE productos SET cantidad = cantidad - 1 WHERE id = ?", (p_id,))
                else:
                    cursor.execute("DELETE FROM productos WHERE id = ?", (p_id,))
        
        conexion.commit()
        return venta_id, nuevo_folio # Retornamos ambos para mostrar el folio al usuario
    
    except sqlite3.Error as e:
        conexion.rollback()
        logging.error(f"Error fatal en venta: {e}")
        return None, None
    finally:
        conexion.close()

def registrar_apartado(empleado_id, productos_apartados, total_venta, abono_inicial, metodo_pago_abono, cliente_data):
    conexion = sqlite3.connect("inventario_joyeria.db")
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # 1. Generar Folio Cíclico para Apartados
        cursor.execute("SELECT folio FROM apartados ORDER BY id DESC LIMIT 1")
        resultado = cursor.fetchone()
        nuevo_folio = 1
        if resultado:
            nuevo_folio = 1 if resultado[0] >= 10000 else resultado[0] + 1

        total_pendiente = total_venta - abono_inicial
        
        # 2. Registrar el Apartado Maestro
        cursor.execute('''
            INSERT INTO apartados (
                folio, fecha_inicio, empleado_id, total_venta, total_abonado, 
                total_pendiente, estado, cliente_nombre, cliente_telefono
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nuevo_folio, fecha_actual, empleado_id, total_venta, abono_inicial, 
            total_pendiente, "Pendiente", 
            cliente_data.get('nombre', 'Cliente Apartado'),
            cliente_data.get('telefono', '')
        ))
        
        apartado_id = cursor.lastrowid
        
        # 3. Registrar el primer abono
        cursor.execute('''
            INSERT INTO abonos (apartado_id, fecha, monto_abonado, metodo_pago, empleado_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (apartado_id, fecha_actual, abono_inicial, metodo_pago_abono, empleado_id))
        
        # 4. Registrar detalles y descontar stock
        for producto_dicc in productos_apartados:
            # NOTA: Recibimos lista de tuplas [(prod, precio)] ya aplanada desde el modal
            producto = producto_dicc[0] # Tupla DB
            precio_unitario = producto_dicc[1] # Precio
            
            cursor.execute('''
                INSERT INTO detalles_apartado (apartado_id, producto_id_original, nombre, peso, kilataje, precio_unitario)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (apartado_id, producto[0], producto[2], producto[3], producto[4], precio_unitario))
            
            # Descontar inventario (Lógica Híbrida)
            cursor.execute("SELECT cantidad FROM productos WHERE id = ?", (producto[0],))
            res = cursor.fetchone()
            if res:
                if res[0] > 1:
                    cursor.execute("UPDATE productos SET cantidad = cantidad - 1 WHERE id = ?", (producto[0],))
                else:
                    cursor.execute("DELETE FROM productos WHERE id = ?", (producto[0],))
        
        conexion.commit()
        return apartado_id, nuevo_folio
    
    except sqlite3.Error as e:
        conexion.rollback()
        logging.error(f"Error al registrar apartado: {e}")
        return None, None
    finally:
        conexion.close()

def obtener_ventas_por_empleado_hoy():
    """Retorna [(Nombre Empleado, Total Vendido), ...] del día actual"""
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT e.nombre, SUM(v.total) 
        FROM ventas v
        JOIN empleados e ON v.empleado_id = e.id
        WHERE date(v.fecha) = ?
        GROUP BY e.nombre
    ''', (fecha_hoy,))
    
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def obtener_total_ventas_hoy():
    """Retorna el monto total de dinero ingresado hoy"""
    conexion = sqlite3.connect('inventario_joyeria.db')
    cursor = conexion.cursor()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute("SELECT SUM(total) FROM ventas WHERE date(fecha) = ?", (fecha_hoy,))
    resultado = cursor.fetchone()
    conexion.close()
    return resultado[0] if resultado and resultado[0] else 0.0

def obtener_detalle_ventas_hoy():
    """
    Retorna los productos individuales vendidos hoy.
    Devuelve: [(Folio, Clave, Nombre, Peso, PrecioVenta, Vendedor), ...]
    """
    conexion = sqlite3.connect("inventario_joyeria.db")
    cursor = conexion.cursor()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
        SELECT v.folio, p.clave, dv.nombre, dv.peso, dv.precio_venta, e.nombre
        FROM ventas v
        JOIN detalles_venta dv ON v.id = dv.venta_id
        LEFT JOIN productos p ON dv.producto_id_original = p.id -- Ojo: Si se borró de productos, la clave podría no estar, pero el nombre sí en dv
        JOIN empleados e ON v.empleado_id = e.id
        WHERE date(v.fecha) = ?
        ORDER BY v.folio DESC
    ''', (fecha_hoy,))
    
    resultados = cursor.fetchall()
    conexion.close()
    return resultados

def exportar_ventas_csv():
    """
    MODIFICADO: Ahora genera un reporte detallado ITEM POR ITEM.
    """
    conexion = sqlite3.connect("inventario_joyeria.db")
    cursor = conexion.cursor()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    # Consulta detallada plana
    cursor.execute('''
        SELECT v.folio, time(v.fecha), e.nombre, v.cliente_nombre, 
        dv.nombre, dv.kilataje, dv.peso, dv.precio_venta
        FROM ventas v
        JOIN detalles_venta dv ON v.id = dv.venta_id
        JOIN empleados e ON v.empleado_id = e.id
        WHERE date(v.fecha) = ?
        ORDER BY v.folio ASC
    ''', (fecha_hoy,))
    
    filas = cursor.fetchall()
    conexion.close()
    
    # Cabeceras
    datos = [["Folio", "Hora", "Vendedor", "Cliente", "Producto", "Kilataje", "Peso", "Precio Venta"]]
    for f in filas:
        datos.append([
            str(f[0]), f[1], f[2], f[3] or "Publico", 
            f[4], f[5], str(f[6]), f"${f[7]:.2f}"
        ])
        
    return datos

def exportar_inventario_csv():
    """Genera inventario completo para CSV"""
    productos = obtener_productos() # Reutilizamos la funcion principal
    
    datos = [["Clave", "Nombre", "Peso (gr)", "Kilataje", "Categoria", "Stock"]]
    for p in productos:
        # p: (id, clave, nombre, peso, kilataje, categoria, cantidad)
        stock = p[6] if len(p) > 6 else 1
        datos.append([p[1], p[2], str(p[3]), p[4], p[5], str(stock)])
        
    return datos

# Crear tablas al importar este módulo
crear_tablas()