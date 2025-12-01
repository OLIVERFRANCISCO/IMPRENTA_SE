"""
Funciones CRUD para operaciones con la base de datos
Separa la lógica de acceso a datos de la interfaz
"""
from datetime import datetime
from app.database.conexion import get_db


# ========== CLIENTES ==========

def obtener_clientes():
    """Retorna todos los clientes"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY nombre_completo")
    return cursor.fetchall()


def obtener_cliente_por_id(id_cliente):
    """Retorna un cliente por su ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,))
    return cursor.fetchone()


def guardar_cliente(nombre, telefono="", email=""):
    """Inserta un nuevo cliente"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nombre_completo, telefono, email) VALUES (?, ?, ?)",
        (nombre, telefono, email)
    )
    conn.commit()
    return cursor.lastrowid


def actualizar_cliente(id_cliente, nombre, telefono="", email=""):
    """Actualiza los datos de un cliente"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre_completo = ?, telefono = ?, email = ? WHERE id_cliente = ?",
        (nombre, telefono, email, id_cliente)
    )
    conn.commit()


def eliminar_cliente(id_cliente):
    """Elimina un cliente (solo si no tiene pedidos)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id_cliente = ?", (id_cliente,))
    conn.commit()


# ========== SERVICIOS ==========

def obtener_servicios():
    """Retorna todos los servicios con información de la máquina sugerida"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, m.nombre as nombre_maquina, m.tipo as tipo_maquina
        FROM servicios s
        LEFT JOIN maquinas m ON s.id_maquina_sugerida = m.id_maquina
        ORDER BY s.nombre_servicio
    """)
    return cursor.fetchall()


def obtener_servicio_por_id(id_servicio):
    """Retorna un servicio por su ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, m.nombre as nombre_maquina, m.tipo as tipo_maquina
        FROM servicios s
        LEFT JOIN maquinas m ON s.id_maquina_sugerida = m.id_maquina
        WHERE s.id_servicio = ?
    """, (id_servicio,))
    return cursor.fetchone()


def guardar_servicio(nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida=None):
    """Crea un nuevo servicio"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO servicios (nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida) VALUES (?, ?, ?, ?)",
        (nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida)
    )
    conn.commit()
    return cursor.lastrowid


def actualizar_servicio(id_servicio, nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida=None):
    """Actualiza un servicio existente"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE servicios 
        SET nombre_servicio = ?, unidad_cobro = ?, precio_base = ?, id_maquina_sugerida = ? 
        WHERE id_servicio = ?""",
        (nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida, id_servicio)
    )
    conn.commit()


def eliminar_servicio(id_servicio):
    """Elimina un servicio (solo si no tiene pedidos asociados)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servicios WHERE id_servicio = ?", (id_servicio,))
    conn.commit()


# ========== MATERIALES ==========

def obtener_materiales():
    """Retorna todos los materiales"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materiales ORDER BY nombre_material")
    return cursor.fetchall()


def obtener_material_por_id(id_material):
    """Retorna un material por su ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materiales WHERE id_material = ?", (id_material,))
    return cursor.fetchone()


def obtener_materiales_bajo_stock():
    """Retorna materiales con stock menor al mínimo"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM materiales 
        WHERE cantidad_stock <= stock_minimo
        ORDER BY cantidad_stock ASC
    """)
    return cursor.fetchall()


def actualizar_stock_material(id_material, cantidad):
    """Actualiza el stock de un material (suma o resta)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE materiales SET cantidad_stock = cantidad_stock + ? WHERE id_material = ?",
        (cantidad, id_material)
    )
    conn.commit()


def descontar_stock_material(id_material, cantidad_usada):
    """Descuenta material del inventario"""
    actualizar_stock_material(id_material, -cantidad_usada)


def guardar_material(nombre, cantidad, unidad, stock_minimo=5, precio=0):
    """Inserta un nuevo material"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO materiales (nombre_material, cantidad_stock, unidad_medida, stock_minimo, precio_por_unidad) VALUES (?, ?, ?, ?, ?)",
        (nombre, cantidad, unidad, stock_minimo, precio)
    )
    conn.commit()
    return cursor.lastrowid


def actualizar_material(id_material, nombre, cantidad, unidad, stock_minimo, precio):
    """Actualiza un material existente"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE materiales 
        SET nombre_material = ?, cantidad_stock = ?, unidad_medida = ?, 
            stock_minimo = ?, precio_por_unidad = ? 
        WHERE id_material = ?""",
        (nombre, cantidad, unidad, stock_minimo, precio, id_material)
    )
    conn.commit()


def eliminar_material(id_material):
    """Elimina un material del inventario"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materiales WHERE id_material = ?", (id_material,))
    conn.commit()


# ========== PEDIDOS ==========

def obtener_pedidos(estado=None):
    """Retorna todos los pedidos o filtrados por estado"""
    conn = get_db()
    cursor = conn.cursor()

    if estado:
        cursor.execute("""
            SELECT p.*, c.nombre_completo, e.nombre as estado_nombre, e.color as estado_color
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            LEFT JOIN estados_pedidos e ON p.id_estado = e.id
            WHERE e.nombre = ?
            ORDER BY p.fecha_ingreso DESC
        """, (estado,))
    else:
        cursor.execute("""
            SELECT p.*, c.nombre_completo, e.nombre as estado_nombre, e.color as estado_color
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            LEFT JOIN estados_pedidos e ON p.id_estado = e.id
            ORDER BY p.fecha_ingreso DESC
        """)

    return cursor.fetchall()


def obtener_pedido_por_id(id_pedido):
    """Retorna un pedido completo con sus detalles"""
    conn = get_db()
    cursor = conn.cursor()

    # Pedido principal
    cursor.execute("""
        SELECT p.*, c.nombre_completo, c.telefono, c.email
        FROM pedidos p
        JOIN clientes c ON p.id_cliente = c.id_cliente
        WHERE p.id_pedido = ?
    """, (id_pedido,))
    pedido = cursor.fetchone()

    # Detalles del pedido
    cursor.execute("""
        SELECT d.*, s.nombre_servicio, s.unidad_cobro, m.nombre_material
        FROM detalles_pedido d
        JOIN servicios s ON d.id_servicio = s.id_servicio
        LEFT JOIN materiales m ON d.id_material = m.id_material
        WHERE d.id_pedido = ?
    """, (id_pedido,))
    detalles = cursor.fetchall()

    return {'pedido': pedido, 'detalles': detalles}


def guardar_pedido(id_cliente, fecha_entrega, estado="Cotizado", estado_pago="Pendiente", costo_total=0, acuenta=0, observaciones=""):
    """Crea un nuevo pedido"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener ID del estado por nombre (por defecto "Cotizado" = 1)
    id_estado = 1  # Por defecto Cotizado
    if estado != "Cotizado":
        estado_obj = obtener_estado_por_nombre(estado)
        if estado_obj:
            id_estado = estado_obj['id']

    cursor.execute(
        """INSERT INTO pedidos 
        (id_cliente, fecha_entrega_estimada, id_estado, estado_pago, costo_total, acuenta, observaciones) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (id_cliente, fecha_entrega, id_estado, estado_pago, costo_total, acuenta, observaciones)
    )
    conn.commit()
    return cursor.lastrowid


def actualizar_estado_pedido(id_pedido, nuevo_estado):
    """Actualiza el estado de un pedido (función de compatibilidad - usa nombre de estado)"""
    conn = get_db()
    cursor = conn.cursor()

    # Obtener ID del estado por nombre
    estado_obj = obtener_estado_por_nombre(nuevo_estado)
    if estado_obj:
        id_estado = estado_obj['id']
        cursor.execute(
            "UPDATE pedidos SET id_estado = ? WHERE id_pedido = ?",
            (id_estado, id_pedido)
        )
        conn.commit()


def actualizar_estado_pago(id_pedido, nuevo_estado, monto_acuenta=0):
    """Actualiza el estado de pago y el adelanto"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pedidos SET estado_pago = ?, acuenta = ? WHERE id_pedido = ?",
        (nuevo_estado, monto_acuenta, id_pedido)
    )
    conn.commit()


# ========== DETALLES DE PEDIDO ==========

def guardar_detalle_pedido(id_pedido, id_servicio, id_material, descripcion, ancho, alto, cantidad, precio_unitario):
    """Inserta un detalle/item del pedido"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO detalles_pedido 
        (id_pedido, id_servicio, id_material, descripcion, ancho, alto, cantidad, precio_unitario) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (id_pedido, id_servicio, id_material, descripcion, ancho, alto, cantidad, precio_unitario)
    )
    conn.commit()
    return cursor.lastrowid


# ========== CONSUMO DE MATERIALES ==========

def registrar_consumo_material(id_detalle, id_material, cantidad_usada):
    """Registra el consumo de material y descuenta del stock"""
    conn = get_db()
    cursor = conn.cursor()

    # Registrar el consumo
    cursor.execute(
        "INSERT INTO consumo_materiales (id_detalle, id_material, cantidad_usada) VALUES (?, ?, ?)",
        (id_detalle, id_material, cantidad_usada)
    )

    # Descontar del inventario
    descontar_stock_material(id_material, cantidad_usada)

    conn.commit()


def obtener_historial_consumo(id_material=None):
    """Retorna el historial de consumo de materiales"""
    conn = get_db()
    cursor = conn.cursor()

    if id_material:
        cursor.execute("""
            SELECT c.*, m.nombre_material, d.descripcion, p.id_pedido
            FROM consumo_materiales c
            JOIN materiales m ON c.id_material = m.id_material
            JOIN detalles_pedido d ON c.id_detalle = d.id_detalle
            JOIN pedidos p ON d.id_pedido = p.id_pedido
            WHERE c.id_material = ?
            ORDER BY c.fecha_consumo DESC
        """, (id_material,))
    else:
        cursor.execute("""
            SELECT c.*, m.nombre_material, d.descripcion, p.id_pedido
            FROM consumo_materiales c
            JOIN materiales m ON c.id_material = m.id_material
            JOIN detalles_pedido d ON c.id_detalle = d.id_detalle
            JOIN pedidos p ON d.id_pedido = p.id_pedido
            ORDER BY c.fecha_consumo DESC
            LIMIT 100
        """)

    return cursor.fetchall()


# ========== MÁQUINAS ==========

def obtener_maquinas():
    """Retorna todas las máquinas"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maquinas ORDER BY nombre")
    return cursor.fetchall()


def obtener_maquina_por_id(id_maquina):
    """Retorna una máquina por su ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM maquinas WHERE id_maquina = ?", (id_maquina,))
    return cursor.fetchone()


def guardar_maquina(nombre, tipo):
    """Inserta una nueva máquina"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO maquinas (nombre, tipo) VALUES (?, ?)",
        (nombre, tipo)
    )
    conn.commit()
    return cursor.lastrowid


def actualizar_maquina(id_maquina, nombre, tipo):
    """Actualiza una máquina existente"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE maquinas SET nombre = ?, tipo = ? WHERE id_maquina = ?",
        (nombre, tipo, id_maquina)
    )
    conn.commit()


def eliminar_maquina(id_maquina):
    """Elimina una máquina"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM maquinas WHERE id_maquina = ?", (id_maquina,))
    conn.commit()


# ========== ESTADOS DE PEDIDOS ==========

def obtener_estados_pedidos():
    """Retorna todos los estados de pedidos"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estados_pedidos ORDER BY id")
    return cursor.fetchall()


def obtener_estado_por_id(id_estado):
    """Retorna un estado por su ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estados_pedidos WHERE id = ?", (id_estado,))
    return cursor.fetchone()


def obtener_estado_por_nombre(nombre):
    """Retorna un estado por su nombre"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estados_pedidos WHERE nombre = ?", (nombre,))
    return cursor.fetchone()


def guardar_estado_pedido(nombre, color):
    """Crea un nuevo estado de pedido"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO estados_pedidos (nombre, color) VALUES (?, ?)",
        (nombre, color)
    )
    conn.commit()
    return cursor.lastrowid


def actualizar_estado_pedido_completo(id_estado, nombre, color):
    """Actualiza un estado de pedido existente (la definición del estado en sí)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE estados_pedidos SET nombre = ?, color = ? WHERE id = ?",
        (nombre, color, id_estado)
    )
    conn.commit()


def eliminar_estado_pedido(id_estado):
    """Elimina un estado de pedido"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM estados_pedidos WHERE id = ?", (id_estado,))
    conn.commit()


# ========== MATERIALES POR SERVICIO ==========

def obtener_materiales_por_servicio(id_servicio):
    """Retorna los materiales compatibles con un servicio específico"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.*
        FROM materiales m
        INNER JOIN servicios_materiales sm ON m.id_material = sm.id_material
        WHERE sm.id_servicio = ?
        ORDER BY m.nombre_material
    """, (id_servicio,))
    return cursor.fetchall()


def agregar_material_a_servicio(id_servicio, id_material):
    """Asocia un material con un servicio"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO servicios_materiales (id_servicio, id_material) VALUES (?, ?)",
            (id_servicio, id_material)
        )
        conn.commit()
        return True
    except:
        return False


def eliminar_material_de_servicio(id_servicio, id_material):
    """Elimina la asociación entre un material y un servicio"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM servicios_materiales WHERE id_servicio = ? AND id_material = ?",
        (id_servicio, id_material)
    )
    conn.commit()


# ========== ACTUALIZACIÓN DE ESTADO DE PEDIDOS ==========

def actualizar_estado_de_pedido(id_pedido, id_estado):
    """Actualiza el estado de un pedido"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pedidos SET id_estado = ? WHERE id_pedido = ?",
        (id_estado, id_pedido)
    )
    conn.commit()


# ========== PEDIDOS CON FILTROS Y PAGINACIÓN ==========

def obtener_pedidos_filtrados(filtro_estado=None, fecha_ingreso_desde=None, fecha_ingreso_hasta=None,
                              fecha_entrega_desde=None, fecha_entrega_hasta=None,
                              orden_campo='fecha_ingreso', orden_direccion='DESC',
                              pagina=1, items_por_pagina=20):
    """
    Retorna pedidos con filtros, ordenamiento y paginación

    Args:
        filtro_estado (int): ID del estado para filtrar
        fecha_ingreso_desde (str): Fecha de ingreso desde (formato: YYYY-MM-DD)
        fecha_ingreso_hasta (str): Fecha de ingreso hasta
        fecha_entrega_desde (str): Fecha de entrega desde
        fecha_entrega_hasta (str): Fecha de entrega hasta
        orden_campo (str): Campo por el cual ordenar
        orden_direccion (str): 'ASC' o 'DESC'
        pagina (int): Número de página (1-indexed)
        items_por_pagina (int): Cantidad de items por página

    Returns:
        dict: {
            'pedidos': lista de pedidos,
            'total': total de pedidos,
            'pagina_actual': número de página actual,
            'total_paginas': total de páginas,
            'items_por_pagina': items por página
        }
    """
    conn = get_db()
    cursor = conn.cursor()

    # Construir query base
    query = """
        SELECT 
            p.id_pedido,
            p.id_cliente,
            c.nombre_completo as nombre_cliente,
            p.fecha_ingreso,
            p.fecha_entrega_estimada,
            p.id_estado,
            e.nombre as estado_nombre,
            e.color as estado_color,
            p.estado_pago,
            p.costo_total,
            p.acuenta,
            p.observaciones
        FROM pedidos p
        LEFT JOIN clientes c ON p.id_cliente = c.id_cliente
        LEFT JOIN estados_pedidos e ON p.id_estado = e.id
        WHERE 1=1
    """

    params = []

    # Agregar filtros
    if filtro_estado is not None:
        query += " AND p.id_estado = ?"
        params.append(filtro_estado)

    if fecha_ingreso_desde:
        query += " AND DATE(p.fecha_ingreso) >= DATE(?)"
        params.append(fecha_ingreso_desde)

    if fecha_ingreso_hasta:
        query += " AND DATE(p.fecha_ingreso) <= DATE(?)"
        params.append(fecha_ingreso_hasta)

    if fecha_entrega_desde:
        query += " AND DATE(p.fecha_entrega_estimada) >= DATE(?)"
        params.append(fecha_entrega_desde)

    if fecha_entrega_hasta:
        query += " AND DATE(p.fecha_entrega_estimada) <= DATE(?)"
        params.append(fecha_entrega_hasta)

    # Contar total de registros
    count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
    cursor.execute(count_query, params)
    total_registros = cursor.fetchone()['total']

    # Calcular paginación
    total_paginas = (total_registros + items_por_pagina - 1) // items_por_pagina
    offset = (pagina - 1) * items_por_pagina

    # Agregar ordenamiento
    campos_validos = ['fecha_ingreso', 'fecha_entrega_estimada', 'costo_total', 'estado_nombre', 'nombre_cliente']
    if orden_campo not in campos_validos:
        orden_campo = 'fecha_ingreso'

    if orden_direccion.upper() not in ['ASC', 'DESC']:
        orden_direccion = 'DESC'

    query += f" ORDER BY {orden_campo} {orden_direccion}"

    # Agregar límite y offset
    query += " LIMIT ? OFFSET ?"
    params.extend([items_por_pagina, offset])

    # Ejecutar query
    cursor.execute(query, params)
    pedidos = cursor.fetchall()

    return {
        'pedidos': pedidos,
        'total': total_registros,
        'pagina_actual': pagina,
        'total_paginas': max(total_paginas, 1),
        'items_por_pagina': items_por_pagina
    }


def obtener_pedidos_con_detalles_paginados(pagina=1, items_por_pagina=20):
    """
    Retorna todos los pedidos con información completa y paginación
    Versión simplificada para compatibilidad
    """
    return obtener_pedidos_filtrados(
        pagina=pagina,
        items_por_pagina=items_por_pagina
    )
