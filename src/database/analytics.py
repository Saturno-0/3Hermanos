import sqlite3
from datetime import datetime
from database.manager import obtener_productos, obtener_ventas_del_dia

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
    inventario = obtener_productos() # (id, nombre, peso, kilataje, categoria)
    
    # Cabecera para el CSV (ajustada)
    datos_csv = [["ID", "Clave", "Nombre", "Peso", "Kilataje", "Categoría"]]
    
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

