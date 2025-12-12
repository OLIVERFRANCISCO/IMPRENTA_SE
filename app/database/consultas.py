"""
Funciones de consulta usando SQLAlchemy ORM
Proporciona una interfaz limpia para operaciones CRUD
"""
from datetime import datetime
from sqlalchemy import func, and_, or_
from sqlalchemy.exc import SQLAlchemyError
from app.database.conexion import get_session
from app.database.models import (
    Cliente, Maquina, Material, EstadoPedido, Servicio, 
    Pedido, DetallePedido, ConsumoMaterial, ServicioMaterial
)


# ========== CLIENTES ==========

def obtener_clientes():
    """
    Obtiene todos los clientes ordenados por nombre
    
    Returns:
        list: Lista de diccionarios con datos de clientes
    """
    session = get_session()
    try:
        clientes = session.query(Cliente).order_by(Cliente.nombre_completo).all()
        return [cliente.to_dict() for cliente in clientes]
    finally:
        session.close()


def obtener_cliente_por_id(id_cliente):
    """
    Obtiene un cliente por su ID
    
    Args:
        id_cliente: ID del cliente a buscar
        
    Returns:
        dict: Datos del cliente o None si no existe
    """
    session = get_session()
    try:
        cliente = session.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        return cliente.to_dict() if cliente else None
    finally:
        session.close()


def guardar_cliente(nombre, telefono="", email=""):
    """
    Crea un nuevo cliente
    
    Args:
        nombre: Nombre completo del cliente
        telefono: Teléfono del cliente
        email: Email del cliente
        
    Returns:
        int: ID del cliente creado
    """
    session = get_session()
    try:
        cliente = Cliente(
            nombre_completo=nombre,
            telefono=telefono,
            email=email
        )
        session.add(cliente)
        session.commit()
        return cliente.id_cliente
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar cliente: {str(e)}")
    finally:
        session.close()


def actualizar_cliente(id_cliente, nombre, telefono="", email=""):
    """
    Actualiza los datos de un cliente existente
    
    Args:
        id_cliente: ID del cliente a actualizar
        nombre: Nuevo nombre del cliente
        telefono: Nuevo teléfono
        email: Nuevo email
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        cliente = session.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        if cliente:
            cliente.nombre_completo = nombre
            cliente.telefono = telefono
            cliente.email = email
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar cliente: {str(e)}")
    finally:
        session.close()


def eliminar_cliente(id_cliente):
    """
    Elimina un cliente (solo si no tiene pedidos asociados)
    
    Args:
        id_cliente: ID del cliente a eliminar
        
    Returns:
        bool: True si se eliminó correctamente
    """
    session = get_session()
    try:
        cliente = session.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
        if cliente:
            # Verificar que no tenga pedidos
            if len(cliente.pedidos) > 0:
                raise Exception("No se puede eliminar un cliente con pedidos asociados")
            session.delete(cliente)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar cliente: {str(e)}")
    finally:
        session.close()


# ========== SERVICIOS ==========

def obtener_servicios():
    """
    Obtiene todos los servicios con su información de máquina
    
    Returns:
        list: Lista de diccionarios con datos de servicios
    """
    session = get_session()
    try:
        servicios = session.query(Servicio).all()
        return [servicio.to_dict() for servicio in servicios]
    finally:
        session.close()


def obtener_servicio_por_id(id_servicio):
    """
    Obtiene un servicio por su ID
    
    Args:
        id_servicio: ID del servicio a buscar
        
    Returns:
        dict: Datos del servicio o None si no existe
    """
    session = get_session()
    try:
        servicio = session.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
        return servicio.to_dict() if servicio else None
    finally:
        session.close()


def guardar_servicio(nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida=None):
    """
    Crea un nuevo servicio
    
    Args:
        nombre_servicio: Nombre del servicio
        unidad_cobro: Unidad de cobro (m2, unidad, ciento, etc.)
        precio_base: Precio base del servicio
        id_maquina_sugerida: ID de la máquina sugerida
        
    Returns:
        int: ID del servicio creado
    """
    session = get_session()
    try:
        servicio = Servicio(
            nombre_servicio=nombre_servicio,
            unidad_cobro=unidad_cobro,
            precio_base=precio_base,
            id_maquina_sugerida=id_maquina_sugerida
        )
        session.add(servicio)
        session.commit()
        return servicio.id_servicio
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar servicio: {str(e)}")
    finally:
        session.close()


def actualizar_servicio(id_servicio, nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida=None):
    """
    Actualiza un servicio existente
    
    Args:
        id_servicio: ID del servicio a actualizar
        nombre_servicio: Nuevo nombre del servicio
        unidad_cobro: Nueva unidad de cobro
        precio_base: Nuevo precio base
        id_maquina_sugerida: ID de la máquina sugerida
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        servicio = session.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
        if servicio:
            servicio.nombre_servicio = nombre_servicio
            servicio.unidad_cobro = unidad_cobro
            servicio.precio_base = precio_base
            servicio.id_maquina_sugerida = id_maquina_sugerida
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar servicio: {str(e)}")
    finally:
        session.close()


def eliminar_servicio(id_servicio):
    """
    Elimina un servicio
    
    Args:
        id_servicio: ID del servicio a eliminar
        
    Returns:
        bool: True si se eliminó correctamente
    """
    session = get_session()
    try:
        servicio = session.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
        if servicio:
            session.delete(servicio)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar servicio: {str(e)}")
    finally:
        session.close()


# ========== MATERIALES POR SERVICIO ==========

def obtener_materiales_por_servicio(id_servicio):
    """
    Retorna los materiales compatibles con un servicio específico
    
    Args:
        id_servicio: ID del servicio
        
    Returns:
        list: Lista de diccionarios con datos de materiales
    """
    session = get_session()
    try:
        # Obtener el servicio con sus materiales relacionados
        servicio = session.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
        if servicio:
            return [material.to_dict() for material in servicio.materiales]
        return []
    finally:
        session.close()


def agregar_material_a_servicio(id_servicio, id_material):
    """
    Asocia un material con un servicio
    
    Args:
        id_servicio: ID del servicio
        id_material: ID del material
        
    Returns:
        bool: True si se asoció correctamente
    """
    session = get_session()
    try:
        # Verificar que no exista ya la relación
        existe = session.query(ServicioMaterial).filter(
            and_(
                ServicioMaterial.id_servicio == id_servicio,
                ServicioMaterial.id_material == id_material
            )
        ).first()
        
        if not existe:
            servicio_material = ServicioMaterial(
                id_servicio=id_servicio,
                id_material=id_material
            )
            session.add(servicio_material)
            session.commit()
            return True
        return False
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        session.close()


# ========== MATERIALES ==========

def obtener_materiales():
    """
    Obtiene todos los materiales ordenados por nombre
    
    Returns:
        list: Lista de diccionarios con datos de materiales
    """
    session = get_session()
    try:
        materiales = session.query(Material).order_by(Material.nombre_material).all()
        return [material.to_dict() for material in materiales]
    finally:
        session.close()


def obtener_material_por_id(id_material):
    """
    Obtiene un material por su ID
    
    Args:
        id_material: ID del material a buscar
        
    Returns:
        dict: Datos del material o None si no existe
    """
    session = get_session()
    try:
        material = session.query(Material).filter(Material.id_material == id_material).first()
        return material.to_dict() if material else None
    finally:
        session.close()


def obtener_materiales_bajo_stock():
    """
    Obtiene materiales que están por debajo del stock mínimo
    
    Returns:
        list: Lista de materiales con stock bajo
    """
    session = get_session()
    try:
        materiales = session.query(Material).filter(
            Material.cantidad_stock <= Material.stock_minimo
        ).all()
        return [material.to_dict() for material in materiales]
    finally:
        session.close()


def actualizar_stock_material(id_material, cantidad):
    """
    Actualiza el stock de un material (reemplaza el valor)
    
    Args:
        id_material: ID del material
        cantidad: Nueva cantidad en stock
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        material = session.query(Material).filter(Material.id_material == id_material).first()
        if material:
            material.cantidad_stock = cantidad
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar stock: {str(e)}")
    finally:
        session.close()


def descontar_stock_material(id_material, cantidad_usada):
    """
    Descuenta stock de un material (resta la cantidad)
    
    Args:
        id_material: ID del material
        cantidad_usada: Cantidad a descontar
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        material = session.query(Material).filter(Material.id_material == id_material).first()
        if material:
            material.cantidad_stock -= cantidad_usada
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al descontar stock: {str(e)}")
    finally:
        session.close()


def guardar_material(nombre, cantidad, unidad, stock_minimo=5, precio=0):
    """
    Crea un nuevo material
    
    Args:
        nombre: Nombre del material
        cantidad: Cantidad inicial en stock
        unidad: Unidad de medida
        stock_minimo: Stock mínimo para alertas
        precio: Precio por unidad
        
    Returns:
        int: ID del material creado
    """
    session = get_session()
    try:
        material = Material(
            nombre_material=nombre,
            cantidad_stock=cantidad,
            unidad_medida=unidad,
            stock_minimo=stock_minimo,
            precio_por_unidad=precio
        )
        session.add(material)
        session.commit()
        return material.id_material
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar material: {str(e)}")
    finally:
        session.close()


def actualizar_material(id_material, nombre, cantidad, unidad, stock_minimo, precio):
    """
    Actualiza un material existente
    
    Args:
        id_material: ID del material a actualizar
        nombre: Nuevo nombre
        cantidad: Nueva cantidad
        unidad: Nueva unidad de medida
        stock_minimo: Nuevo stock mínimo
        precio: Nuevo precio
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        material = session.query(Material).filter(Material.id_material == id_material).first()
        if material:
            material.nombre_material = nombre
            material.cantidad_stock = cantidad
            material.unidad_medida = unidad
            material.stock_minimo = stock_minimo
            material.precio_por_unidad = precio
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar material: {str(e)}")
    finally:
        session.close()


def actualizar_material_con_ancho(id_material, nombre, cantidad, unidad, stock_minimo, precio, ancho_bobina):
    """
    Actualiza un material incluyendo el ancho de bobina (para materiales en rollo)
    
    Args:
        id_material: ID del material a actualizar
        nombre: Nuevo nombre
        cantidad: Nueva cantidad
        unidad: Nueva unidad de medida
        stock_minimo: Nuevo stock mínimo
        precio: Nuevo precio
        ancho_bobina: Ancho de la bobina en metros
        
    Returns:
        bool: True si se actualizó correctamente
    """
    # Esta función se mantiene por compatibilidad pero el modelo ORM no incluye ancho_bobina
    # Si se requiere, agregar el campo al modelo Material
    return actualizar_material(id_material, nombre, cantidad, unidad, stock_minimo, precio)


def eliminar_material(id_material):
    """
    Elimina un material
    
    Args:
        id_material: ID del material a eliminar
        
    Returns:
        bool: True si se eliminó correctamente
    """
    session = get_session()
    try:
        material = session.query(Material).filter(Material.id_material == id_material).first()
        if material:
            session.delete(material)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar material: {str(e)}")
    finally:
        session.close()


# ========== PEDIDOS ==========

def obtener_pedidos(estado=None):
    """
    Obtiene pedidos con opción de filtrar por estado
    
    Args:
        estado: Nombre del estado para filtrar (opcional)
        
    Returns:
        list: Lista de pedidos con información completa
    """
    session = get_session()
    try:
        query = session.query(Pedido)
        
        if estado:
            query = query.join(EstadoPedido).filter(EstadoPedido.nombre == estado)
        
        pedidos = query.order_by(Pedido.fecha_ingreso.desc()).all()
        return [pedido.to_dict() for pedido in pedidos]
    finally:
        session.close()


def obtener_pedido_por_id(id_pedido):
    """
    Obtiene un pedido completo con sus detalles
    
    Args:
        id_pedido: ID del pedido a buscar
        
    Returns:
        dict: Diccionario con 'pedido' y 'detalles'
    """
    session = get_session()
    try:
        pedido = session.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        if not pedido:
            return None
        
        return {
            'pedido': pedido.to_dict(),
            'detalles': [detalle.to_dict() for detalle in pedido.detalles]
        }
    finally:
        session.close()


def guardar_pedido(id_cliente, fecha_entrega, estado="Cotizado", estado_pago="Pendiente", 
                   costo_total=0, acuenta=0, observaciones=""):
    """
    Crea un nuevo pedido
    
    Args:
        id_cliente: ID del cliente que hace el pedido
        fecha_entrega: Fecha de entrega estimada
        estado: Estado inicial del pedido
        estado_pago: Estado de pago inicial
        costo_total: Costo total del pedido
        acuenta: Monto pagado a cuenta
        observaciones: Observaciones del pedido
        
    Returns:
        int: ID del pedido creado
    """
    session = get_session()
    try:
        # Obtener el ID del estado por nombre
        estado_obj = session.query(EstadoPedido).filter(EstadoPedido.nombre == estado).first()
        id_estado = estado_obj.id if estado_obj else 1
        
        # Convertir fecha_entrega a datetime si es string
        if isinstance(fecha_entrega, str):
            fecha_entrega = datetime.fromisoformat(fecha_entrega)
        
        pedido = Pedido(
            id_cliente=id_cliente,
            fecha_entrega_estimada=fecha_entrega,
            id_estado=id_estado,
            estado_pago=estado_pago,
            costo_total=costo_total,
            acuenta=acuenta,
            observaciones=observaciones
        )
        session.add(pedido)
        session.commit()
        return pedido.id_pedido
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar pedido: {str(e)}")
    finally:
        session.close()


def actualizar_estado_pedido(id_pedido, nuevo_estado):
    """
    Actualiza el estado de un pedido (deprecated, usar actualizar_estado_de_pedido)
    
    Args:
        id_pedido: ID del pedido
        nuevo_estado: Nombre del nuevo estado
        
    Returns:
        bool: True si se actualizó correctamente
    """
    return actualizar_estado_de_pedido(id_pedido, None, nuevo_estado)


def actualizar_estado_de_pedido(id_pedido, id_estado=None, nombre_estado=None):
    """
    Actualiza el estado de un pedido
    
    Args:
        id_pedido: ID del pedido
        id_estado: ID del estado (opcional si se proporciona nombre_estado)
        nombre_estado: Nombre del estado (opcional si se proporciona id_estado)
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        pedido = session.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        if not pedido:
            return False
        
        # Si se proporciona nombre_estado, buscar su ID
        if nombre_estado and not id_estado:
            estado_obj = session.query(EstadoPedido).filter(EstadoPedido.nombre == nombre_estado).first()
            if estado_obj:
                id_estado = estado_obj.id
        
        if id_estado:
            pedido.id_estado = id_estado
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar estado: {str(e)}")
    finally:
        session.close()


def actualizar_estado_pago(id_pedido, nuevo_estado, monto_acuenta=0):
    """
    Actualiza el estado de pago de un pedido
    
    Args:
        id_pedido: ID del pedido
        nuevo_estado: Nuevo estado de pago
        monto_acuenta: Monto pagado a cuenta
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        pedido = session.query(Pedido).filter(Pedido.id_pedido == id_pedido).first()
        if pedido:
            pedido.estado_pago = nuevo_estado
            if monto_acuenta > 0:
                pedido.acuenta = monto_acuenta
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar estado de pago: {str(e)}")
    finally:
        session.close()


# ========== DETALLES DE PEDIDO ==========

def guardar_detalle_pedido(id_pedido, id_servicio, id_material, descripcion, ancho, alto, cantidad, precio_unitario):
    """
    Guarda un detalle de pedido
    
    Args:
        id_pedido: ID del pedido
        id_servicio: ID del servicio
        id_material: ID del material
        descripcion: Descripción del detalle
        ancho: Ancho en metros
        alto: Alto en metros
        cantidad: Cantidad de unidades
        precio_unitario: Precio por unidad
        
    Returns:
        int: ID del detalle creado
    """
    session = get_session()
    try:
        detalle = DetallePedido(
            id_pedido=id_pedido,
            id_servicio=id_servicio,
            id_material=id_material,
            descripcion=descripcion,
            ancho=ancho,
            alto=alto,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )
        session.add(detalle)
        session.commit()
        return detalle.id_detalle
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar detalle de pedido: {str(e)}")
    finally:
        session.close()


# ========== CONSUMO DE MATERIALES ==========

def registrar_consumo_material(id_detalle, id_material, cantidad_usada):
    """
    Registra el consumo de material y descuenta del stock
    
    Args:
        id_detalle: ID del detalle de pedido
        id_material: ID del material consumido
        cantidad_usada: Cantidad consumida
        
    Returns:
        int: ID del registro de consumo
    """
    session = get_session()
    try:
        # Registrar consumo
        consumo = ConsumoMaterial(
            id_detalle=id_detalle,
            id_material=id_material,
            cantidad_usada=cantidad_usada
        )
        session.add(consumo)
        
        # Descontar del stock
        material = session.query(Material).filter(Material.id_material == id_material).first()
        if material:
            material.cantidad_stock -= cantidad_usada
        
        session.commit()
        return consumo.id_consumo
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al registrar consumo: {str(e)}")
    finally:
        session.close()


def obtener_historial_consumo(id_material=None):
    """
    Obtiene el historial de consumo de materiales
    
    Args:
        id_material: ID del material para filtrar (opcional)
        
    Returns:
        list: Lista de registros de consumo
    """
    session = get_session()
    try:
        query = session.query(ConsumoMaterial)
        
        if id_material:
            query = query.filter(ConsumoMaterial.id_material == id_material)
        
        consumos = query.order_by(ConsumoMaterial.fecha_consumo.desc()).all()
        return [consumo.to_dict() for consumo in consumos]
    finally:
        session.close()


# ========== MÁQUINAS ==========

def obtener_maquinas():
    """
    Obtiene todas las máquinas
    
    Returns:
        list: Lista de diccionarios con datos de máquinas
    """
    session = get_session()
    try:
        maquinas = session.query(Maquina).all()
        return [maquina.to_dict() for maquina in maquinas]
    finally:
        session.close()


def obtener_maquina_por_id(id_maquina):
    """
    Obtiene una máquina por su ID
    
    Args:
        id_maquina: ID de la máquina
        
    Returns:
        dict: Datos de la máquina o None
    """
    session = get_session()
    try:
        maquina = session.query(Maquina).filter(Maquina.id_maquina == id_maquina).first()
        return maquina.to_dict() if maquina else None
    finally:
        session.close()


def guardar_maquina(nombre, tipo):
    """
    Crea una nueva máquina
    
    Args:
        nombre: Nombre de la máquina
        tipo: Tipo de máquina
        
    Returns:
        int: ID de la máquina creada
    """
    session = get_session()
    try:
        maquina = Maquina(nombre=nombre, tipo=tipo)
        session.add(maquina)
        session.commit()
        return maquina.id_maquina
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar máquina: {str(e)}")
    finally:
        session.close()


def actualizar_maquina(id_maquina, nombre, tipo):
    """
    Actualiza una máquina existente
    
    Args:
        id_maquina: ID de la máquina
        nombre: Nuevo nombre
        tipo: Nuevo tipo
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        maquina = session.query(Maquina).filter(Maquina.id_maquina == id_maquina).first()
        if maquina:
            maquina.nombre = nombre
            maquina.tipo = tipo
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar máquina: {str(e)}")
    finally:
        session.close()


def eliminar_maquina(id_maquina):
    """
    Elimina una máquina
    
    Args:
        id_maquina: ID de la máquina a eliminar
        
    Returns:
        bool: True si se eliminó correctamente
    """
    session = get_session()
    try:
        maquina = session.query(Maquina).filter(Maquina.id_maquina == id_maquina).first()
        if maquina:
            session.delete(maquina)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar máquina: {str(e)}")
    finally:
        session.close()


# ========== MATERIALES POR TIPO Y ANCHO ==========

def obtener_materiales_por_tipo_y_ancho(tipo_material):
    """
    Obtiene todos los rollos disponibles de un tipo de material
    
    R2, R3: Retorna todas las variantes por ancho de bobina
    
    Args:
        tipo_material: Nombre del tipo de material (ej: "Lona 13oz")
        
    Returns:
        list: Lista de diccionarios con información de cada rollo
    """
    session = get_session()
    try:
        materiales = session.query(Material).filter(
            and_(
                Material.nombre_material.ilike(f"%{tipo_material}%"),
                Material.ancho_bobina > 0
            )
        ).order_by(Material.ancho_bobina).all()
        return [material.to_dict() for material in materiales]
    finally:
        session.close()


def obtener_rollo_por_id(id_material):
    """
    Obtiene información detallada de un rollo específico
    
    Args:
        id_material: ID del material/rollo
        
    Returns:
        dict or None: Información del rollo
    """
    session = get_session()
    try:
        material = session.query(Material).filter(Material.id_material == id_material).first()
        return material.to_dict() if material else None
    finally:
        session.close()


def actualizar_stock_rollo(id_material, metros_a_descontar):
    """
    Actualiza el stock de un rollo específico descontando metros lineales
    
    R4, R5, R19: Descuento lineal solo del rollo específico
    
    Args:
        id_material: ID del rollo
        metros_a_descontar: Metros a descontar (positivo)
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        material = session.query(Material).filter(Material.id_material == id_material).first()
        if material:
            material.cantidad_stock -= metros_a_descontar
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar stock de rollo: {str(e)}")
    finally:
        session.close()


# ========== ESTADOS DE PEDIDOS ==========

def obtener_estados_pedidos():
    """
    Obtiene todos los estados de pedidos
    
    Returns:
        list: Lista de diccionarios con datos de estados
    """
    session = get_session()
    try:
        estados = session.query(EstadoPedido).all()
        return [estado.to_dict() for estado in estados]
    finally:
        session.close()


def obtener_estado_por_id(id_estado):
    """
    Obtiene un estado por su ID
    
    Args:
        id_estado: ID del estado
        
    Returns:
        dict: Datos del estado o None
    """
    session = get_session()
    try:
        estado = session.query(EstadoPedido).filter(EstadoPedido.id == id_estado).first()
        return estado.to_dict() if estado else None
    finally:
        session.close()


def obtener_estado_por_nombre(nombre):
    """
    Obtiene un estado por su nombre
    
    Args:
        nombre: Nombre del estado
        
    Returns:
        dict: Datos del estado o None
    """
    session = get_session()
    try:
        estado = session.query(EstadoPedido).filter(EstadoPedido.nombre == nombre).first()
        return estado.to_dict() if estado else None
    finally:
        session.close()


# ========== FUNCIONES AVANZADAS DE PEDIDOS ==========

def obtener_pedidos_filtrados(filtro_estado=None, fecha_ingreso_desde=None, 
                              fecha_ingreso_hasta=None, orden_campo='fecha_ingreso', 
                              orden_direccion='DESC', pagina=1, items_por_pagina=20):
    """
    Obtiene pedidos con filtros, ordenamiento y paginación
    
    Args:
        filtro_estado: ID del estado para filtrar
        fecha_ingreso_desde: Fecha desde (formato ISO o datetime)
        fecha_ingreso_hasta: Fecha hasta (formato ISO o datetime)
        orden_campo: Campo para ordenar
        orden_direccion: 'ASC' o 'DESC'
        pagina: Número de página (comenzando en 1)
        items_por_pagina: Cantidad de items por página
        
    Returns:
        dict: Diccionario con 'pedidos', 'total', 'pagina_actual', 'total_paginas'
    """
    session = get_session()
    try:
        # Construir query base
        query = session.query(Pedido)
        
        # Aplicar filtros
        if filtro_estado:
            query = query.filter(Pedido.id_estado == filtro_estado)
        
        if fecha_ingreso_desde:
            if isinstance(fecha_ingreso_desde, str):
                fecha_ingreso_desde = datetime.fromisoformat(fecha_ingreso_desde)
            query = query.filter(Pedido.fecha_ingreso >= fecha_ingreso_desde)
        
        if fecha_ingreso_hasta:
            if isinstance(fecha_ingreso_hasta, str):
                fecha_ingreso_hasta = datetime.fromisoformat(fecha_ingreso_hasta)
            query = query.filter(Pedido.fecha_ingreso <= fecha_ingreso_hasta)
        
        # Contar total de resultados
        total = query.count()
        
        # Aplicar ordenamiento
        campo_orden = getattr(Pedido, orden_campo, Pedido.fecha_ingreso)
        if orden_direccion.upper() == 'DESC':
            query = query.order_by(campo_orden.desc())
        else:
            query = query.order_by(campo_orden.asc())
        
        # Calcular offset para paginación
        offset = (pagina - 1) * items_por_pagina
        
        # Aplicar paginación
        pedidos = query.limit(items_por_pagina).offset(offset).all()
        
        # Calcular total de páginas
        total_paginas = (total + items_por_pagina - 1) // items_por_pagina
        
        return {
            'pedidos': [pedido.to_dict() for pedido in pedidos],
            'total': total,
            'pagina_actual': pagina,
            'total_paginas': total_paginas,
            'items_por_pagina': items_por_pagina
        }
    finally:
        session.close()
