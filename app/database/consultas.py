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


# ========== PEDIDOS ==========

def obtener_pedidos(estado=None):
    """Retorna todos los pedidos o filtrados por estado"""
    conn = get_db()
    cursor = conn.cursor()

    if estado:
        cursor.execute("""
            SELECT p.*, c.nombre_completo
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            WHERE p.estado_pedido = ?
            ORDER BY p.fecha_ingreso DESC
        """, (estado,))
    else:
        cursor.execute("""
            SELECT p.*, c.nombre_completo
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
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
    cursor.execute(
        """INSERT INTO pedidos 
        (id_cliente, fecha_entrega_estimada, estado_pedido, estado_pago, costo_total, acuenta, observaciones) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (id_cliente, fecha_entrega, estado, estado_pago, costo_total, acuenta, observaciones)
    )
    conn.commit()
    return cursor.lastrowid


def actualizar_estado_pedido(id_pedido, nuevo_estado):
    """Actualiza el estado de un pedido"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pedidos SET estado_pedido = ? WHERE id_pedido = ?",
        (nuevo_estado, id_pedido)
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

