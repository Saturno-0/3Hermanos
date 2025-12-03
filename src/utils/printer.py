import win32print
import datetime

# --- CONFIGURACIÓN ---
NOMBRE_IMPRESORA = "POS-58"

def imprimir_ticket_venta(folio, fecha, productos, total, metodo_pago, recibio, cambio, cliente_nombre, cliente_numero, cliente_direccion, titulo_ticket="*** ORIGINAL CLIENTE ***"):
    
    # --- COMANDOS ESC/POS ---
    INIT = b'\x1b@'
    ALIGN_CENTER = b'\x1ba\x01'
    ALIGN_LEFT = b'\x1ba\x00'
    BOLD_ON = b'\x1bE\x01'
    BOLD_OFF = b'\x1bE\x00'
    FEED_N = b'\x1bd\x04' 
    
    SIZE_2X = b'\x1d!\x11'
    SIZE_NORMAL = b'\x1d!\x00'
    
    ANCHO_NORMAL = 32
    
    # --- HELPER: Codificación ---
    def trans(txt):
        try:
            return str(txt).encode('cp437', errors='replace')
        except:
            return str(txt).encode('utf-8', errors='ignore')

    def texto_dos_cols(izq, der):
        str_izq = str(izq)[:20]
        str_der = str(der)[:10]
        espacios = ANCHO_NORMAL - len(str_izq) - len(str_der)
        if espacios < 0: espacios = 0
        linea = str_izq + (" " * espacios) + str_der + "\n"
        return trans(linea)

    def linea_divisoria():
        return b"-" * ANCHO_NORMAL + b"\n"

    # --- LÓGICA DE AGRUPACIÓN ---
    items_agrupados = {}
    for prod, precio in productos:
        p_id = prod[0]
        nombre = prod[2]
        if p_id in items_agrupados:
            items_agrupados[p_id]['cantidad'] += 1
            items_agrupados[p_id]['total_linea'] += precio
        else:
            items_agrupados[p_id] = {'nombre': nombre, 'cantidad': 1, 'total_linea': precio}

    # --- IMPRESIÓN ---
    try:
        hPrinter = win32print.OpenPrinter(NOMBRE_IMPRESORA)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket Venta", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                
                # 1. CABECERA
                win32print.WritePrinter(hPrinter, INIT)
                win32print.WritePrinter(hPrinter, ALIGN_CENTER)
                
                # TITULO DINÁMICO (Original o Copia)
                win32print.WritePrinter(hPrinter, trans(f"{titulo_ticket}\n"))
                win32print.WritePrinter(hPrinter, b"\n")
                
                # Nombre Tienda
                win32print.WritePrinter(hPrinter, SIZE_2X)
                win32print.WritePrinter(hPrinter, BOLD_ON)
                win32print.WritePrinter(hPrinter, trans("JOYERIA\n")) 
                win32print.WritePrinter(hPrinter, trans("3 HERMANOS\n"))
                win32print.WritePrinter(hPrinter, BOLD_OFF)
                win32print.WritePrinter(hPrinter, SIZE_NORMAL) 
                
                win32print.WritePrinter(hPrinter, trans("R.F.C DEPN850420N18\n"))
                win32print.WritePrinter(hPrinter, trans("PLAZA DE LA MUJER LOCAL 118\n"))
                win32print.WritePrinter(hPrinter, trans("443-312-64-14 COL. CENTRO\n"))
                win32print.WritePrinter(hPrinter, trans("C.P. 52800 MORELIA, MICH.\n\n"))
                
                win32print.WritePrinter(hPrinter, BOLD_ON)
                win32print.WritePrinter(hPrinter, trans("Extenso surtido en alhajas de oro de 10 y 14 kilates\n"))
                win32print.WritePrinter(hPrinter, BOLD_OFF)

                # 2. DATOS VENTA
                win32print.WritePrinter(hPrinter, ALIGN_LEFT)
                win32print.WritePrinter(hPrinter, linea_divisoria())
                win32print.WritePrinter(hPrinter, trans(f"Folio: {folio}\n"))
                win32print.WritePrinter(hPrinter, trans(f"Fecha: {fecha}\n"))
                
                cliente_str = cliente_nombre[:22] if cliente_nombre else "Publico General"
                win32print.WritePrinter(hPrinter, trans(f"Cliente: {cliente_str}\n"))
                
                if cliente_numero:
                    win32print.WritePrinter(hPrinter, trans(f"Tel: {cliente_numero}\n"))
                if cliente_direccion:
                    dir_str = cliente_direccion[:32]
                    win32print.WritePrinter(hPrinter, trans(f"Dir: {dir_str}\n"))

                win32print.WritePrinter(hPrinter, linea_divisoria())
                
                # 3. PRODUCTOS
                win32print.WritePrinter(hPrinter, BOLD_ON)
                win32print.WritePrinter(hPrinter, trans("CANT DESCRIPCION       IMPORTE\n"))
                win32print.WritePrinter(hPrinter, BOLD_OFF)
                win32print.WritePrinter(hPrinter, linea_divisoria())
                
                for item in items_agrupados.values():
                    cant = item['cantidad']
                    nombre = item['nombre']
                    importe = item['total_linea']
                    
                    str_cant = f"{cant}".ljust(4)
                    str_nombre = f"{nombre[:18]}".ljust(19)
                    str_importe = f"${importe:,.0f}"
                    
                    linea_final = f"{str_cant}{str_nombre}"
                    espacio = ANCHO_NORMAL - len(linea_final) - len(str_importe)
                    if espacio > 0:
                        linea_final += (" " * espacio) + str_importe + "\n"
                    else:
                        linea_final = f"{str_cant}{nombre[:15]:<16}{str_importe:>6}\n"

                    win32print.WritePrinter(hPrinter, trans(linea_final))
                
                win32print.WritePrinter(hPrinter, linea_divisoria())
                
                # 4. TOTALES
                win32print.WritePrinter(hPrinter, ALIGN_CENTER)
                win32print.WritePrinter(hPrinter, SIZE_2X)
                win32print.WritePrinter(hPrinter, BOLD_ON)
                win32print.WritePrinter(hPrinter, trans("TOTAL:\n"))
                win32print.WritePrinter(hPrinter, trans(f"${total:,.2f}\n"))
                win32print.WritePrinter(hPrinter, BOLD_OFF)
                win32print.WritePrinter(hPrinter, SIZE_NORMAL)
                
                win32print.WritePrinter(hPrinter, ALIGN_LEFT)
                win32print.WritePrinter(hPrinter, b"\n")
                win32print.WritePrinter(hPrinter, texto_dos_cols("Pago:", metodo_pago))
                
                if "Efectivo" in metodo_pago:
                    win32print.WritePrinter(hPrinter, texto_dos_cols("Recibido:", f"${recibio:,.2f}"))
                    win32print.WritePrinter(hPrinter, texto_dos_cols("Cambio:", f"${cambio:,.2f}"))
                
                win32print.WritePrinter(hPrinter, b"\n")
                
                # 5. PIE DE PAGINA
                win32print.WritePrinter(hPrinter, ALIGN_CENTER)
                win32print.WritePrinter(hPrinter, trans("Gracias por su preferencia\n"))
                win32print.WritePrinter(hPrinter, trans("NOTA: LA GARANTIA CONSISTE EN LA CALIDAD DEL ORO, EN DESCOMPOSTURA NO HAY GARANTIA\n"))
                
                win32print.WritePrinter(hPrinter, FEED_N)
                
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
            return True
            
    except Exception as e:
        print(f"Error imprimiendo: {e}")
        return False
    
def imprimir_ticket_apartado(folio, fecha, productos, total, abono_inicial, restante, cliente_nombre, titulo_ticket="*** TICKET APARTADO ***"):
        # --- COMANDOS ESC/POS ---
    INIT = b'\x1b@'
    ALIGN_CENTER = b'\x1ba\x01'
    ALIGN_LEFT = b'\x1ba\x00'
    BOLD_ON = b'\x1bE\x01'
    BOLD_OFF = b'\x1bE\x00'
    FEED_N = b'\x1bd\x04' 
    
    SIZE_2X = b'\x1d!\x11'
    SIZE_NORMAL = b'\x1d!\x00'
    
    ANCHO_NORMAL = 32

    def trans(txt):
        try:
            return str(txt).encode('cp437', errors='replace')
        except:
            return str(txt).encode('utf-8', errors='ignore')

    def linea_divisoria():
        return b"-" * ANCHO_NORMAL + b"\n"

    try:
        hPrinter = win32print.OpenPrinter(NOMBRE_IMPRESORA)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket Apartado", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                
                # 1. CABECERA
                win32print.WritePrinter(hPrinter, INIT)
                win32print.WritePrinter(hPrinter, ALIGN_CENTER)
                win32print.WritePrinter(hPrinter, trans(f"{titulo_ticket}\n\n"))
                
                win32print.WritePrinter(hPrinter, SIZE_2X)
                win32print.WritePrinter(hPrinter, BOLD_ON)
                win32print.WritePrinter(hPrinter, trans("JOYERIA\n3 HERMANOS\n"))
                win32print.WritePrinter(hPrinter, BOLD_OFF)
                win32print.WritePrinter(hPrinter, SIZE_NORMAL)
                
                win32print.WritePrinter(hPrinter, trans("PLAN DE APARTADO\n\n"))

                # 2. DATOS
                win32print.WritePrinter(hPrinter, ALIGN_LEFT)
                win32print.WritePrinter(hPrinter, trans(f"Folio Apartado: {folio}\n"))
                win32print.WritePrinter(hPrinter, trans(f"Fecha: {fecha}\n"))
                win32print.WritePrinter(hPrinter, trans(f"Cliente: {cliente_nombre[:22]}\n"))
                win32print.WritePrinter(hPrinter, linea_divisoria())

                # 3. PRODUCTOS APARTADOS
                win32print.WritePrinter(hPrinter, BOLD_ON)
                win32print.WritePrinter(hPrinter, trans("PRODUCTOS APARTADOS\n"))
                win32print.WritePrinter(hPrinter, BOLD_OFF)
                
                # Agrupar productos (Misma lógica que venta)
                items = {}
                for prod, precio in productos:
                    pid = prod[0]
                    if pid in items: 
                        items[pid]['cant'] += 1
                        items[pid]['total'] += precio
                    else: 
                        items[pid] = {'nom': prod[2], 'cant': 1, 'total': precio}

                for i in items.values():
                    # Formato simple: "1 x Anillo Oro... $1500"
                    linea = f"{i['cant']} x {i['nom'][:15]} ${i['total']:,.0f}\n"
                    win32print.WritePrinter(hPrinter, trans(linea))

                win32print.WritePrinter(hPrinter, linea_divisoria())

                # 4. ESTADO DE CUENTA (LO IMPORTANTE)
                win32print.WritePrinter(hPrinter, ALIGN_CENTER)
                win32print.WritePrinter(hPrinter, BOLD_ON)
                win32print.WritePrinter(hPrinter, trans("VALOR TOTAL:  "))
                win32print.WritePrinter(hPrinter, trans(f"${total:,.2f}\n"))
                win32print.WritePrinter(hPrinter, b"\n")
                
                win32print.WritePrinter(hPrinter, trans("ABONO INICIAL: "))
                win32print.WritePrinter(hPrinter, trans(f"${abono_inicial:,.2f}\n"))
                win32print.WritePrinter(hPrinter, linea_divisoria())
                
                win32print.WritePrinter(hPrinter, SIZE_2X)
                win32print.WritePrinter(hPrinter, trans("RESTA:\n"))
                win32print.WritePrinter(hPrinter, trans(f"${restante:,.2f}\n"))
                win32print.WritePrinter(hPrinter, SIZE_NORMAL)
                win32print.WritePrinter(hPrinter, BOLD_OFF)
                
                win32print.WritePrinter(hPrinter, b"\n")
                
                # 5. PIE
                win32print.WritePrinter(hPrinter, trans("No hay devolucion en apartados\n"))
                win32print.WritePrinter(hPrinter, FEED_N)

                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
            return True
    except Exception:
        return False
    
def imprimir_corte_caja(ventas_empleado, total_dia, detalle_productos):
    """
    Imprime el reporte de cierre de día.
    """
    try:
        hPrinter = win32print.OpenPrinter(NOMBRE_IMPRESORA)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Corte Caja", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                
                # Encabezado
                win32print.WritePrinter(hPrinter, b'\x1b@') # Init
                win32print.WritePrinter(hPrinter, b'\x1ba\x01') # Center
                win32print.WritePrinter(hPrinter, b'\x1d!\x11') # Doble tamaño
                win32print.WritePrinter(hPrinter, b'\x1bE\x01') # Bold ON
                win32print.WritePrinter(hPrinter, b"CORTE DE CAJA\n")
                win32print.WritePrinter(hPrinter, b'\x1d!\x00') # Normal
                win32print.WritePrinter(hPrinter, b'\x1bE\x00') # Bold OFF
                
                fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                win32print.WritePrinter(hPrinter, f"{fecha}\n".encode('cp437'))
                win32print.WritePrinter(hPrinter, b"-"*32 + b"\n")
                
                # 1. Resumen por Vendedor
                win32print.WritePrinter(hPrinter, b'\x1ba\x00') # Left
                win32print.WritePrinter(hPrinter, b'\x1bE\x01') # Bold
                win32print.WritePrinter(hPrinter, b"VENTAS POR VENDEDOR:\n")
                win32print.WritePrinter(hPrinter, b'\x1bE\x00')
                
                for emp, tot in ventas_empleado:
                    linea = f"{emp[:15]:<16} ${tot:>10,.2f}\n"
                    win32print.WritePrinter(hPrinter, linea.encode('cp437'))
                
                win32print.WritePrinter(hPrinter, b"-"*32 + b"\n")
                
                # 2. Total Global
                win32print.WritePrinter(hPrinter, b'\x1ba\x01') # Center
                win32print.WritePrinter(hPrinter, b'\x1d!\x11') # Doble
                win32print.WritePrinter(hPrinter, b"TOTAL DIA:\n")
                win32print.WritePrinter(hPrinter, f"${total_dia:,.2f}\n".encode('cp437'))
                win32print.WritePrinter(hPrinter, b'\x1d!\x00') # Normal
                win32print.WritePrinter(hPrinter, b"-"*32 + b"\n")
                
                # 3. Detalle de Productos
                win32print.WritePrinter(hPrinter, b'\x1ba\x00') # Left
                win32print.WritePrinter(hPrinter, b"DETALLE PRODUCTOS:\n")
                win32print.WritePrinter(hPrinter, b"Folio Prod             Precio\n")
                
                for item in detalle_productos:
                    # item: (Folio, Clave, Nombre, Peso, Precio, Vendedor)
                    folio = str(item[0])
                    nombre = item[2][:15] # Truncar nombre
                    precio = item[4]
                    
                    linea = f"{folio:<4} {nombre:<16} ${precio:>6,.0f}\n"
                    win32print.WritePrinter(hPrinter, linea.encode('cp437'))
                
                win32print.WritePrinter(hPrinter, b"\n\n\n")
                win32print.WritePrinter(hPrinter, b'\x1bd\x04') # Feed 4 lineas

                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
            return True
    except Exception as e:
        print(e)
        return False

def imprimir_inventario(lista_productos):
    """
    Imprime lista simple de inventario.
    lista_productos: [(id, clave, nombre, peso, kilataje, cat, stock)]
    """
    try:
        hPrinter = win32print.OpenPrinter(NOMBRE_IMPRESORA)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Inventario", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                
                # Encabezado
                win32print.WritePrinter(hPrinter, b'\x1b@')
                win32print.WritePrinter(hPrinter, b'\x1ba\x01') # Center
                win32print.WritePrinter(hPrinter, b'\x1bE\x01')
                win32print.WritePrinter(hPrinter, b"INVENTARIO ACTUAL\n")
                win32print.WritePrinter(hPrinter, b'\x1bE\x00')
                win32print.WritePrinter(hPrinter, datetime.datetime.now().strftime("%d/%m/%Y").encode('cp437') + b"\n")
                win32print.WritePrinter(hPrinter, b"-"*32 + b"\n")
                
                # Lista compacta
                win32print.WritePrinter(hPrinter, b'\x1ba\x00') # Left
                # Formato: Clave | Nombre | Stock
                win32print.WritePrinter(hPrinter, b"CLAVE   PRODUCTO         STOCK\n")
                
                for p in lista_productos:
                    # p: (id, clave, nombre, peso, kilataje, cat, stock)
                    clave = str(p[1])[:7]
                    nombre = str(p[2])[:16]
                    stock = str(p[6]) if len(p) > 6 else "1"
                    
                    linea = f"{clave:<7} {nombre:<16} {stock:>5}\n"
                    win32print.WritePrinter(hPrinter, linea.encode('cp437'))
                
                win32print.WritePrinter(hPrinter, b"-"*32 + b"\n")
                win32print.WritePrinter(hPrinter, f"Total Items: {len(lista_productos)}\n".encode('cp437'))
                win32print.WritePrinter(hPrinter, b"\n\n\n")
                win32print.WritePrinter(hPrinter, b'\x1bd\x04')

                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
            return True
    except Exception:
        return False