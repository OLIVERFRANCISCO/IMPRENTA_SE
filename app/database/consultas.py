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
    Pedido, DetallePedido, ConsumoMaterial, ServicioMaterial, MaquinaServicio,
    TipoMaquina, TipoMaterial, UnidadMedida, InventarioMaterial, InventarioDimensionalMaterial,
    CapacidadMaquina, PrecioEscalonado, RestriccionCantidad, ConfiguracionSistema
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


def guardar_servicio(nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida=None, tipo_material='unidad'):
    """
    Crea un nuevo servicio
    
    Args:
        nombre_servicio: Nombre del servicio
        unidad_cobro: Unidad de cobro (m2, unidad, ciento, etc.)
        precio_base: Precio base del servicio
        id_maquina_sugerida: ID de la máquina sugerida
        tipo_material: 'dimension' si requiere ancho/alto, 'unidad' si solo cantidad
        
    Returns:
        int: ID del servicio creado
    """
    session = get_session()
    try:
        # Buscar o crear unidad de cobro
        unidad_med = session.query(UnidadMedida).filter_by(abreviacion=unidad_cobro).first()
        if not unidad_med:
            unidad_med = UnidadMedida(nombre_unidad=unidad_cobro, abreviacion=unidad_cobro, tipo="Otro")
            session.add(unidad_med)
            session.flush()
        
        servicio = Servicio(
            nombre_servicio=nombre_servicio,
            id_unidad_cobro=unidad_med.id_unidad,
            precio_base=precio_base,
            id_maquina_sugerida=id_maquina_sugerida,
            tipo_material=tipo_material
        )
        session.add(servicio)
        session.commit()
        return servicio.id_servicio
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar servicio: {str(e)}")
    finally:
        session.close()


def actualizar_servicio(id_servicio, nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida=None, tipo_material='unidad'):
    """
    Actualiza un servicio existente
    
    Args:
        id_servicio: ID del servicio a actualizar
        nombre_servicio: Nuevo nombre del servicio
        unidad_cobro: Nueva unidad de cobro
        precio_base: Nuevo precio base
        id_maquina_sugerida: ID de la máquina sugerida
        tipo_material: 'dimension' si requiere ancho/alto, 'unidad' si solo cantidad
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        servicio = session.query(Servicio).filter(Servicio.id_servicio == id_servicio).first()
        if servicio:
            # Buscar o crear unidad de cobro
            unidad_med = session.query(UnidadMedida).filter_by(abreviacion=unidad_cobro).first()
            if not unidad_med:
                unidad_med = UnidadMedida(nombre_unidad=unidad_cobro, abreviacion=unidad_cobro, tipo="Otro")
                session.add(unidad_med)
                session.flush()
            
            servicio.nombre_servicio = nombre_servicio
            servicio.id_unidad_cobro = unidad_med.id_unidad
            servicio.precio_base = precio_base
            servicio.id_maquina_sugerida = id_maquina_sugerida
            servicio.tipo_material = tipo_material
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
        # Hacer join con inventario para verificar stock
        materiales = session.query(Material).join(
            InventarioMaterial, Material.id_material == InventarioMaterial.id_material
        ).filter(
            InventarioMaterial.cantidad_stock <= InventarioMaterial.stock_minimo
        ).all()
        return [material.to_dict() for material in materiales]
    finally:
        session.close()


def actualizar_stock_material(id_material, cantidad, es_dimensional=False, largo_agregar=0.0):
    """
    Actualiza el stock de un material (agrega la cantidad, no reemplaza)
    
    Args:
        id_material: ID del material
        cantidad: Cantidad a agregar (para unidades) o ancho (para dimensionales)
        es_dimensional: Si es True, usa inventario dimensional
        largo_agregar: Largo a agregar (solo para dimensionales)
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        if es_dimensional:
            inv_dim = session.query(InventarioDimensionalMaterial).filter_by(id_material=id_material).first()
            if inv_dim:
                inv_dim.largo_disponible += largo_agregar
                session.commit()
                return True
            return False
        else:
            inventario = session.query(InventarioMaterial).filter_by(id_material=id_material).first()
            if inventario:
                inventario.cantidad_stock += cantidad  # SUMA, no reemplaza
            else:
                inventario = InventarioMaterial(id_material=id_material, cantidad_stock=cantidad)
                session.add(inventario)
            session.commit()
            return True
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar stock: {str(e)}")
    finally:
        session.close()


def obtener_materiales_por_tipo(tipo_material='unidad'):
    """
    Obtiene materiales filtrados por tipo
    
    Args:
        tipo_material: Nombre del tipo de material
        
    Returns:
        list: Lista de diccionarios con datos de materiales
    """
    session = get_session()
    try:
        materiales = session.query(Material).join(TipoMaterial).filter(
            TipoMaterial.nombre_tipo == tipo_material
        ).all()
        return [mat.to_dict() for mat in materiales]
    except SQLAlchemyError as e:
        raise Exception(f"Error al obtener materiales por tipo: {str(e)}")
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
        inventario = session.query(InventarioMaterial).filter_by(id_material=id_material).first()
        if inventario:
            inventario.cantidad_stock -= cantidad_usada
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al descontar stock: {str(e)}")
    finally:
        session.close()


def guardar_material(nombre, cantidad, unidad, stock_minimo=5, precio=0, 
                    tipo_material='unidad', sugerencia='', categoria_material='General',
                    ancho_disponible=0.0, largo_disponible=0.0, 
                    ancho_minimo=0.0, largo_minimo=0.0, es_continuo=True):
    """
    Crea un nuevo material con el esquema normalizado
    
    Args:
        nombre: Nombre del material
        cantidad: Cantidad inicial en stock (para materiales de unidad)
        unidad: Unidad de medida (abreviación)
        stock_minimo: Stock mínimo para alertas (para materiales de unidad)
        precio: Precio por unidad
        tipo_material: 'unidad' o 'dimension'
        sugerencia: Descripción/recomendación del material
        categoria_material: Categoría del material (Papel, Vinilo, Lona, etc.)
        ancho_disponible: Ancho del rollo/bobina en metros
        largo_disponible: Largo total disponible en metros
        ancho_minimo: Ancho mínimo para alertas
        largo_minimo: Largo mínimo para alertas
        es_continuo: True si es rollo continuo, False si es plancha
        
    Returns:
        int: ID del material creado
    """
    session = get_session()
    try:
        # Buscar o crear categoría de material
        cat_mat = session.query(TipoMaterial).filter_by(nombre_tipo=categoria_material).first()
        if not cat_mat:
            cat_mat = TipoMaterial(nombre_tipo=categoria_material)
            session.add(cat_mat)
            session.flush()
        
        # Buscar o crear unidad de medida
        unidad_med = session.query(UnidadMedida).filter_by(abreviacion=unidad).first()
        if not unidad_med:
            unidad_med = UnidadMedida(nombre_unidad=unidad, abreviacion=unidad, tipo="Otro")
            session.add(unidad_med)
            session.flush()
        
        # Crear material
        material = Material(
            nombre_material=nombre,
            id_tipo_material=cat_mat.id_tipo_material,
            id_unidad_inventario=unidad_med.id_unidad,
            sugerencia=sugerencia
        )
        session.add(material)
        session.flush()
        
        if tipo_material == 'dimension':
            # Crear inventario dimensional
            inv_dim = InventarioDimensionalMaterial(
                id_material=material.id_material,
                ancho_disponible=ancho_disponible,
                largo_disponible=largo_disponible,
                ancho_minimo=ancho_minimo,
                largo_minimo=largo_minimo,
                es_continuo=es_continuo
            )
            session.add(inv_dim)
        else:
            # Crear inventario de unidades
            inventario = InventarioMaterial(
                id_material=material.id_material,
                cantidad_stock=cantidad,
                stock_minimo=stock_minimo,
                precio_compra_promedio=precio
            )
            session.add(inventario)
        
        session.commit()
        return material.id_material
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar material: {str(e)}")
    finally:
        session.close()


def actualizar_material(id_material, nombre, cantidad, unidad, stock_minimo, precio,
                       tipo_material='unidad', sugerencia='', categoria_material='General',
                       ancho_disponible=0.0, largo_disponible=0.0,
                       ancho_minimo=0.0, largo_minimo=0.0, es_continuo=True):
    """
    Actualiza un material existente con el esquema normalizado
    """
    session = get_session()
    try:
        material = session.query(Material).filter(Material.id_material == id_material).first()
        if not material:
            return False
        
        # Buscar o crear categoría de material
        cat_mat = session.query(TipoMaterial).filter_by(nombre_tipo=categoria_material).first()
        if not cat_mat:
            cat_mat = TipoMaterial(nombre_tipo=categoria_material)
            session.add(cat_mat)
            session.flush()
        
        # Buscar o crear unidad de medida
        unidad_med = session.query(UnidadMedida).filter_by(abreviacion=unidad).first()
        if not unidad_med:
            unidad_med = UnidadMedida(nombre_unidad=unidad, abreviacion=unidad, tipo="Otro")
            session.add(unidad_med)
            session.flush()
        
        # Actualizar material
        material.nombre_material = nombre
        material.id_tipo_material = cat_mat.id_tipo_material
        material.id_unidad_inventario = unidad_med.id_unidad
        material.sugerencia = sugerencia
        
        if tipo_material == 'dimension':
            # Eliminar inventario de unidades si existe
            inv_unidad = session.query(InventarioMaterial).filter_by(id_material=id_material).first()
            if inv_unidad:
                session.delete(inv_unidad)
            
            # Actualizar o crear inventario dimensional
            inv_dim = session.query(InventarioDimensionalMaterial).filter_by(id_material=id_material).first()
            if inv_dim:
                inv_dim.ancho_disponible = ancho_disponible
                inv_dim.largo_disponible = largo_disponible
                inv_dim.ancho_minimo = ancho_minimo
                inv_dim.largo_minimo = largo_minimo
                inv_dim.es_continuo = es_continuo
            else:
                inv_dim = InventarioDimensionalMaterial(
                    id_material=id_material,
                    ancho_disponible=ancho_disponible,
                    largo_disponible=largo_disponible,
                    ancho_minimo=ancho_minimo,
                    largo_minimo=largo_minimo,
                    es_continuo=es_continuo
                )
                session.add(inv_dim)
        else:
            # Eliminar inventario dimensional si existe
            inv_dim = session.query(InventarioDimensionalMaterial).filter_by(id_material=id_material).first()
            if inv_dim:
                session.delete(inv_dim)
            
            # Actualizar o crear inventario de unidades
            inventario = session.query(InventarioMaterial).filter_by(id_material=id_material).first()
            if inventario:
                inventario.cantidad_stock = cantidad
                inventario.stock_minimo = stock_minimo
                inventario.precio_compra_promedio = precio
            else:
                inventario = InventarioMaterial(
                    id_material=id_material,
                    cantidad_stock=cantidad,
                    stock_minimo=stock_minimo,
                    precio_compra_promedio=precio
                )
                session.add(inventario)
        
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar material: {str(e)}")
    finally:
        session.close()


def agregar_stock_dimensional(id_material, ancho_agregar=0.0, largo_agregar=0.0):
    """
    Agrega dimensiones a un material dimensional (suma, no reemplaza)
    
    Args:
        id_material: ID del material
        ancho_agregar: Ancho a agregar (si aplica)
        largo_agregar: Largo a agregar
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        inv_dim = session.query(InventarioDimensionalMaterial).filter_by(id_material=id_material).first()
        if inv_dim:
            if largo_agregar > 0:
                inv_dim.largo_disponible += largo_agregar
            if ancho_agregar > 0:
                inv_dim.ancho_disponible = ancho_agregar  # El ancho generalmente se reemplaza
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al agregar stock dimensional: {str(e)}")
    finally:
        session.close()


def descontar_stock_dimensional(id_material, largo_usado=0.0):
    """
    Descuenta largo de un material dimensional
    
    Args:
        id_material: ID del material
        largo_usado: Largo a descontar
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        inv_dim = session.query(InventarioDimensionalMaterial).filter_by(id_material=id_material).first()
        if inv_dim:
            inv_dim.largo_disponible -= largo_usado
            if inv_dim.largo_disponible < 0:
                inv_dim.largo_disponible = 0
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al descontar stock dimensional: {str(e)}")
    finally:
        session.close()


def obtener_materiales_dimensionales_bajo_stock():
    """
    Obtiene materiales dimensionales que están por debajo del mínimo
    
    Returns:
        list: Lista de materiales dimensionales con stock bajo
    """
    session = get_session()
    try:
        materiales = session.query(Material).join(
            InventarioDimensionalMaterial, Material.id_material == InventarioDimensionalMaterial.id_material
        ).filter(
            or_(
                InventarioDimensionalMaterial.ancho_disponible <= InventarioDimensionalMaterial.ancho_minimo,
                InventarioDimensionalMaterial.largo_disponible <= InventarioDimensionalMaterial.largo_minimo
            )
        ).all()
        return [material.to_dict() for material in materiales]
    finally:
        session.close()


def guardar_nuevo_rollo(nombre, ancho_disponible, largo_disponible, unidad, 
                       ancho_minimo=0.0, largo_minimo=5.0, precio=0, 
                       sugerencia='', es_continuo=True):
    """
    Crea un nuevo material en formato de rollo/bobina
    """
    return guardar_material(
        nombre=nombre,
        cantidad=0,
        unidad=unidad,
        stock_minimo=0,
        precio=precio,
        tipo_material='dimension',
        sugerencia=sugerencia,
        categoria_material='Rollo',
        ancho_disponible=ancho_disponible,
        largo_disponible=largo_disponible,
        ancho_minimo=ancho_minimo,
        largo_minimo=largo_minimo,
        es_continuo=es_continuo
    )


def actualizar_material_dimensional(id_material, nombre, unidad, 
                                   ancho_disponible, largo_disponible,
                                   ancho_minimo, largo_minimo, precio=0,
                                   sugerencia='', es_continuo=True):
    """
    Actualiza un material dimensional (rollo/bobina)
    """
    return actualizar_material(
        id_material=id_material,
        nombre=nombre,
        cantidad=0,
        unidad=unidad,
        stock_minimo=0,
        precio=precio,
        tipo_material='dimension',
        sugerencia=sugerencia,
        categoria_material='Rollo',
        ancho_disponible=ancho_disponible,
        largo_disponible=largo_disponible,
        ancho_minimo=ancho_minimo,
        largo_minimo=largo_minimo,
        es_continuo=es_continuo
    )


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


def guardar_maquina(nombre, tipo, sugerencia=''):
    """
    Crea una nueva máquina
    
    Args:
        nombre: Nombre de la máquina
        tipo: Tipo de máquina (string, se busca o crea el TipoMaquina)
        sugerencia: Recomendación de uso
        
    Returns:
        int: ID de la máquina creada
    """
    session = get_session()
    try:
        # Buscar o crear el tipo de máquina
        tipo_maq = session.query(TipoMaquina).filter_by(nombre_tipo=tipo).first()
        if not tipo_maq:
            tipo_maq = TipoMaquina(nombre_tipo=tipo)
            session.add(tipo_maq)
            session.flush()
        
        maquina = Maquina(nombre=nombre, id_tipo_maquina=tipo_maq.id_tipo_maquina, sugerencia=sugerencia)
        session.add(maquina)
        session.commit()
        return maquina.id_maquina
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar máquina: {str(e)}")
    finally:
        session.close()


def actualizar_maquina(id_maquina, nombre, tipo, sugerencia=''):
    """
    Actualiza una máquina existente
    
    Args:
        id_maquina: ID de la máquina
        nombre: Nuevo nombre
        tipo: Nuevo tipo (string)
        sugerencia: Recomendación de uso
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        maquina = session.query(Maquina).filter(Maquina.id_maquina == id_maquina).first()
        if maquina:
            # Buscar o crear el tipo de máquina
            tipo_maq = session.query(TipoMaquina).filter_by(nombre_tipo=tipo).first()
            if not tipo_maq:
                tipo_maq = TipoMaquina(nombre_tipo=tipo)
                session.add(tipo_maq)
                session.flush()
            
            maquina.nombre = nombre
            maquina.id_tipo_maquina = tipo_maq.id_tipo_maquina
            maquina.sugerencia = sugerencia
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


def guardar_estado_pedido(nombre, color='#808080'):
    """
    Crea un nuevo estado de pedido
    
    Args:
        nombre: Nombre del estado
        color: Color hexadecimal
        
    Returns:
        int: ID del estado creado
    """
    session = get_session()
    try:
        estado = EstadoPedido(nombre=nombre, color=color)
        session.add(estado)
        session.commit()
        return estado.id
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar estado: {str(e)}")
    finally:
        session.close()


def actualizar_estado_pedido(id_estado, nombre, color='#808080'):
    """Actualiza un estado de pedido"""
    session = get_session()
    try:
        estado = session.query(EstadoPedido).filter(EstadoPedido.id == id_estado).first()
        if estado:
            estado.nombre = nombre
            estado.color = color
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar estado: {str(e)}")
    finally:
        session.close()


def eliminar_estado_pedido(id_estado):
    """Elimina un estado de pedido (si no tiene pedidos asociados)"""
    session = get_session()
    try:
        estado = session.query(EstadoPedido).filter(EstadoPedido.id == id_estado).first()
        if estado:
            if estado.pedidos:
                raise Exception("No se puede eliminar: hay pedidos con este estado")
            session.delete(estado)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar estado: {str(e)}")
    finally:
        session.close()


# ========== CATÁLOGO: UNIDADES DE MEDIDA ==========

def obtener_unidades_medida():
    """
    Obtiene todas las unidades de medida
    
    Returns:
        list: Lista de diccionarios con datos de unidades
    """
    session = get_session()
    try:
        unidades = session.query(UnidadMedida).order_by(UnidadMedida.nombre_unidad).all()
        return [unidad.to_dict() for unidad in unidades]
    finally:
        session.close()


def guardar_unidad_medida(nombre, abreviacion, tipo, factor_conversion=1.0):
    """
    Crea una nueva unidad de medida
    
    Args:
        nombre: Nombre completo (Ej: Metro Cuadrado)
        abreviacion: Abreviación (Ej: m²)
        tipo: Tipo de unidad (Área, Longitud, Conteo)
        factor_conversion: Factor de conversión base
        
    Returns:
        int: ID de la unidad creada
    """
    session = get_session()
    try:
        unidad = UnidadMedida(
            nombre_unidad=nombre,
            abreviacion=abreviacion,
            tipo=tipo,
            factor_conversion=factor_conversion
        )
        session.add(unidad)
        session.commit()
        return unidad.id_unidad
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar unidad: {str(e)}")
    finally:
        session.close()


def actualizar_unidad_medida(id_unidad, nombre, abreviacion, tipo, factor_conversion=1.0):
    """Actualiza una unidad de medida"""
    session = get_session()
    try:
        unidad = session.query(UnidadMedida).filter(UnidadMedida.id_unidad == id_unidad).first()
        if unidad:
            unidad.nombre_unidad = nombre
            unidad.abreviacion = abreviacion
            unidad.tipo = tipo
            unidad.factor_conversion = factor_conversion
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar unidad: {str(e)}")
    finally:
        session.close()


def eliminar_unidad_medida(id_unidad):
    """Elimina una unidad de medida (si no está en uso)"""
    session = get_session()
    try:
        unidad = session.query(UnidadMedida).filter(UnidadMedida.id_unidad == id_unidad).first()
        if unidad:
            if unidad.materiales or unidad.servicios:
                raise Exception("No se puede eliminar: la unidad está en uso")
            session.delete(unidad)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar unidad: {str(e)}")
    finally:
        session.close()


def obtener_unidad_por_abreviacion(abreviacion):
    """Obtiene una unidad por su abreviación"""
    session = get_session()
    try:
        unidad = session.query(UnidadMedida).filter(UnidadMedida.abreviacion == abreviacion).first()
        return unidad.to_dict() if unidad else None
    finally:
        session.close()


# ========== CATÁLOGO: TIPOS DE MÁQUINA ==========

def obtener_tipos_maquina():
    """
    Obtiene todos los tipos de máquina
    
    Returns:
        list: Lista de diccionarios con datos de tipos
    """
    session = get_session()
    try:
        tipos = session.query(TipoMaquina).order_by(TipoMaquina.nombre_tipo).all()
        return [tipo.to_dict() for tipo in tipos]
    finally:
        session.close()


def guardar_tipo_maquina(nombre):
    """
    Crea un nuevo tipo de máquina
    
    Args:
        nombre: Nombre del tipo (Ej: Gran Formato, Láser)
        
    Returns:
        int: ID del tipo creado
    """
    session = get_session()
    try:
        tipo = TipoMaquina(nombre_tipo=nombre)
        session.add(tipo)
        session.commit()
        return tipo.id_tipo_maquina
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar tipo: {str(e)}")
    finally:
        session.close()


def actualizar_tipo_maquina(id_tipo, nombre):
    """Actualiza un tipo de máquina"""
    session = get_session()
    try:
        tipo = session.query(TipoMaquina).filter(TipoMaquina.id_tipo_maquina == id_tipo).first()
        if tipo:
            tipo.nombre_tipo = nombre
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar tipo: {str(e)}")
    finally:
        session.close()


def eliminar_tipo_maquina(id_tipo):
    """Elimina un tipo de máquina (si no está en uso)"""
    session = get_session()
    try:
        tipo = session.query(TipoMaquina).filter(TipoMaquina.id_tipo_maquina == id_tipo).first()
        if tipo:
            if tipo.maquinas:
                raise Exception("No se puede eliminar: hay máquinas de este tipo")
            session.delete(tipo)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar tipo: {str(e)}")
    finally:
        session.close()


def obtener_tipo_maquina_por_nombre(nombre):
    """Obtiene un tipo de máquina por su nombre"""
    session = get_session()
    try:
        tipo = session.query(TipoMaquina).filter(TipoMaquina.nombre_tipo == nombre).first()
        return tipo.to_dict() if tipo else None
    finally:
        session.close()


# ========== CATÁLOGO: TIPOS DE MATERIAL ==========

def obtener_tipos_material():
    """
    Obtiene todos los tipos de material
    
    Returns:
        list: Lista de diccionarios con datos de tipos
    """
    session = get_session()
    try:
        tipos = session.query(TipoMaterial).order_by(TipoMaterial.nombre_tipo).all()
        return [tipo.to_dict() for tipo in tipos]
    finally:
        session.close()


def guardar_tipo_material(nombre):
    """
    Crea un nuevo tipo de material
    
    Args:
        nombre: Nombre del tipo (Ej: Papel, Vinilo, Lona)
        
    Returns:
        int: ID del tipo creado
    """
    session = get_session()
    try:
        tipo = TipoMaterial(nombre_tipo=nombre)
        session.add(tipo)
        session.commit()
        return tipo.id_tipo_material
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar tipo: {str(e)}")
    finally:
        session.close()


def actualizar_tipo_material(id_tipo, nombre):
    """Actualiza un tipo de material"""
    session = get_session()
    try:
        tipo = session.query(TipoMaterial).filter(TipoMaterial.id_tipo_material == id_tipo).first()
        if tipo:
            tipo.nombre_tipo = nombre
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar tipo: {str(e)}")
    finally:
        session.close()


def eliminar_tipo_material(id_tipo):
    """Elimina un tipo de material (si no está en uso)"""
    session = get_session()
    try:
        tipo = session.query(TipoMaterial).filter(TipoMaterial.id_tipo_material == id_tipo).first()
        if tipo:
            if tipo.materiales:
                raise Exception("No se puede eliminar: hay materiales de este tipo")
            session.delete(tipo)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar tipo: {str(e)}")
    finally:
        session.close()


def obtener_tipo_material_por_nombre(nombre):
    """Obtiene un tipo de material por su nombre"""
    session = get_session()
    try:
        tipo = session.query(TipoMaterial).filter(TipoMaterial.nombre_tipo == nombre).first()
        return tipo.to_dict() if tipo else None
    finally:
        session.close()


# ========== REGLAS DE NEGOCIO: PRECIOS ESCALONADOS ==========

def obtener_precios_escalonados(id_servicio=None):
    """
    Obtiene los precios escalonados, opcionalmente filtrados por servicio
    
    Args:
        id_servicio: ID del servicio para filtrar (opcional)
        
    Returns:
        list: Lista de diccionarios con precios escalonados
    """
    session = get_session()
    try:
        query = session.query(PrecioEscalonado)
        if id_servicio:
            query = query.filter(PrecioEscalonado.id_servicio == id_servicio)
        precios = query.order_by(PrecioEscalonado.id_servicio, PrecioEscalonado.cantidad_minima).all()
        
        result = []
        for p in precios:
            d = p.to_dict()
            d['nombre_servicio'] = p.servicio.nombre_servicio if p.servicio else None
            result.append(d)
        return result
    finally:
        session.close()


def guardar_precio_escalonado(id_servicio, cantidad_minima, cantidad_maxima, precio_unitario):
    """
    Crea un nuevo precio escalonado
    
    Args:
        id_servicio: ID del servicio
        cantidad_minima: Cantidad desde la cual aplica
        cantidad_maxima: Cantidad hasta la cual aplica (None = sin límite)
        precio_unitario: Precio por unidad
        
    Returns:
        int: ID del precio creado
    """
    session = get_session()
    try:
        precio = PrecioEscalonado(
            id_servicio=id_servicio,
            cantidad_minima=cantidad_minima,
            cantidad_maxima=cantidad_maxima,
            precio_unitario=precio_unitario
        )
        session.add(precio)
        session.commit()
        return precio.id
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar precio escalonado: {str(e)}")
    finally:
        session.close()


def actualizar_precio_escalonado(id_precio, cantidad_minima, cantidad_maxima, precio_unitario):
    """Actualiza un precio escalonado existente"""
    session = get_session()
    try:
        precio = session.query(PrecioEscalonado).filter(PrecioEscalonado.id == id_precio).first()
        if precio:
            precio.cantidad_minima = cantidad_minima
            precio.cantidad_maxima = cantidad_maxima
            precio.precio_unitario = precio_unitario
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar precio: {str(e)}")
    finally:
        session.close()


def eliminar_precio_escalonado(id_precio):
    """Elimina un precio escalonado"""
    session = get_session()
    try:
        precio = session.query(PrecioEscalonado).filter(PrecioEscalonado.id == id_precio).first()
        if precio:
            session.delete(precio)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar precio: {str(e)}")
    finally:
        session.close()


def obtener_precio_por_cantidad(id_servicio, cantidad):
    """
    Obtiene el precio unitario para una cantidad específica de un servicio.
    Usado por el motor de cálculos.
    
    Args:
        id_servicio: ID del servicio
        cantidad: Cantidad a consultar
        
    Returns:
        float or None: Precio unitario o None si no hay regla
    """
    session = get_session()
    try:
        # Buscar precio escalonado que aplique
        precio = session.query(PrecioEscalonado).filter(
            PrecioEscalonado.id_servicio == id_servicio,
            PrecioEscalonado.cantidad_minima <= cantidad,
            or_(
                PrecioEscalonado.cantidad_maxima >= cantidad,
                PrecioEscalonado.cantidad_maxima == None
            )
        ).first()
        
        return precio.precio_unitario if precio else None
    finally:
        session.close()


# ========== REGLAS DE NEGOCIO: RESTRICCIONES DE CANTIDAD ==========

def obtener_restricciones_cantidad(id_servicio=None):
    """
    Obtiene las restricciones de cantidad, opcionalmente filtradas por servicio
    
    Args:
        id_servicio: ID del servicio para filtrar (opcional)
        
    Returns:
        list: Lista de diccionarios con restricciones
    """
    session = get_session()
    try:
        query = session.query(RestriccionCantidad)
        if id_servicio:
            query = query.filter(RestriccionCantidad.id_servicio == id_servicio)
        restricciones = query.all()
        
        result = []
        for r in restricciones:
            d = r.to_dict()
            d['nombre_servicio'] = r.servicio.nombre_servicio if r.servicio else None
            result.append(d)
        return result
    finally:
        session.close()


def guardar_restriccion_cantidad(id_servicio, tipo_restriccion, valores_permitidos=None,
                                  multiplo_base=None, multiplo_desde=None,
                                  cantidad_minima=None, cantidad_maxima=None, mensaje_error=None):
    """
    Crea una nueva restricción de cantidad
    
    Args:
        id_servicio: ID del servicio
        tipo_restriccion: 'lista', 'multiplo' o 'rango'
        valores_permitidos: Para tipo 'lista', valores separados por coma
        multiplo_base: Para tipo 'multiplo', el valor base
        multiplo_desde: Para tipo 'multiplo', desde qué cantidad aplicar
        cantidad_minima: Para tipo 'rango'
        cantidad_maxima: Para tipo 'rango'
        mensaje_error: Mensaje personalizado de error
        
    Returns:
        int: ID de la restricción creada
    """
    session = get_session()
    try:
        restriccion = RestriccionCantidad(
            id_servicio=id_servicio,
            tipo_restriccion=tipo_restriccion,
            valores_permitidos=valores_permitidos,
            multiplo_base=multiplo_base,
            multiplo_desde=multiplo_desde,
            cantidad_minima=cantidad_minima,
            cantidad_maxima=cantidad_maxima,
            mensaje_error=mensaje_error
        )
        session.add(restriccion)
        session.commit()
        return restriccion.id
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al guardar restricción: {str(e)}")
    finally:
        session.close()


def actualizar_restriccion_cantidad(id_restriccion, tipo_restriccion, valores_permitidos=None,
                                     multiplo_base=None, multiplo_desde=None,
                                     cantidad_minima=None, cantidad_maxima=None, mensaje_error=None):
    """Actualiza una restricción de cantidad existente"""
    session = get_session()
    try:
        restriccion = session.query(RestriccionCantidad).filter(RestriccionCantidad.id == id_restriccion).first()
        if restriccion:
            restriccion.tipo_restriccion = tipo_restriccion
            restriccion.valores_permitidos = valores_permitidos
            restriccion.multiplo_base = multiplo_base
            restriccion.multiplo_desde = multiplo_desde
            restriccion.cantidad_minima = cantidad_minima
            restriccion.cantidad_maxima = cantidad_maxima
            restriccion.mensaje_error = mensaje_error
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar restricción: {str(e)}")
    finally:
        session.close()


def eliminar_restriccion_cantidad(id_restriccion):
    """Elimina una restricción de cantidad"""
    session = get_session()
    try:
        restriccion = session.query(RestriccionCantidad).filter(RestriccionCantidad.id == id_restriccion).first()
        if restriccion:
            session.delete(restriccion)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar restricción: {str(e)}")
    finally:
        session.close()


def validar_cantidad_servicio(id_servicio, cantidad):
    """
    Valida si una cantidad es permitida para un servicio según sus restricciones.
    Usado por el motor de cálculos.
    
    Args:
        id_servicio: ID del servicio
        cantidad: Cantidad a validar
        
    Returns:
        tuple: (es_valido: bool, mensaje: str, cantidad_sugerida: int)
    """
    session = get_session()
    try:
        restriccion = session.query(RestriccionCantidad).filter(
            RestriccionCantidad.id_servicio == id_servicio
        ).first()
        
        if not restriccion:
            # Sin restricciones, cualquier cantidad es válida
            return True, "Cantidad válida", cantidad
        
        tipo = restriccion.tipo_restriccion
        
        if tipo == 'lista':
            # Validar contra lista de valores permitidos
            valores = [int(v.strip()) for v in restriccion.valores_permitidos.split(',')]
            
            # Agregar múltiplos si están definidos
            if restriccion.multiplo_base and restriccion.multiplo_desde:
                for i in range(1, 51):
                    multiplo = restriccion.multiplo_base * i
                    if multiplo >= restriccion.multiplo_desde and multiplo not in valores:
                        valores.append(multiplo)
            
            valores.sort()
            
            if cantidad in valores:
                return True, "Cantidad válida", cantidad
            
            # Encontrar cantidad sugerida más cercana
            cantidad_sugerida = min(valores, key=lambda x: abs(x - cantidad))
            mensaje = restriccion.mensaje_error or f"Cantidad inválida. Opciones: {', '.join(map(str, valores[:10]))}..."
            return False, mensaje, cantidad_sugerida
            
        elif tipo == 'multiplo':
            base = restriccion.multiplo_base or 1
            desde = restriccion.multiplo_desde or 1
            
            if cantidad < desde:
                return False, f"La cantidad mínima es {desde}", desde
            
            if cantidad % base == 0:
                return True, "Cantidad válida", cantidad
            
            cantidad_sugerida = round(cantidad / base) * base
            if cantidad_sugerida < desde:
                cantidad_sugerida = desde
            mensaje = restriccion.mensaje_error or f"Solo se permiten múltiplos de {base}"
            return False, mensaje, cantidad_sugerida
            
        elif tipo == 'rango':
            min_cant = restriccion.cantidad_minima or 1
            max_cant = restriccion.cantidad_maxima or 999999
            
            if min_cant <= cantidad <= max_cant:
                return True, "Cantidad válida", cantidad
            
            if cantidad < min_cant:
                return False, f"La cantidad mínima es {min_cant}", min_cant
            else:
                return False, f"La cantidad máxima es {max_cant}", max_cant
        
        return True, "Cantidad válida", cantidad
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


# ========== RELACIÓN SERVICIO ↔ MATERIAL ==========

def asociar_material_a_servicio(id_servicio, id_material, es_preferido=False):
    """
    Asocia un material a un servicio
    
    Args:
        id_servicio: ID del servicio
        id_material: ID del material
        es_preferido: Si es un material preferido (True/False)
        
    Returns:
        bool: True si se asoció correctamente, False si ya existe
    """
    session = get_session()
    try:
        # Verificar si ya existe la asociación
        existe = session.query(ServicioMaterial).filter(
            ServicioMaterial.id_servicio == id_servicio,
            ServicioMaterial.id_material == id_material
        ).first()
        
        if existe:
            return False
        
        # Crear nueva asociación
        asociacion = ServicioMaterial(
            id_servicio=id_servicio,
            id_material=id_material,
            es_preferido=1 if es_preferido else 0
        )
        session.add(asociacion)
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        session.close()


def desasociar_material_de_servicio(id_servicio, id_material):
    """
    Elimina la asociación entre un servicio y un material
    
    Args:
        id_servicio: ID del servicio
        id_material: ID del material
        
    Returns:
        bool: True si se eliminó correctamente
    """
    session = get_session()
    try:
        asociacion = session.query(ServicioMaterial).filter(
            ServicioMaterial.id_servicio == id_servicio,
            ServicioMaterial.id_material == id_material
        ).first()
        
        if asociacion:
            session.delete(asociacion)
            session.commit()
            return True
        return False
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        session.close()


def obtener_materiales_por_servicio(id_servicio, solo_preferidos=False):
    """
    Obtiene los materiales asociados a un servicio
    
    Args:
        id_servicio: ID del servicio
        solo_preferidos: Si True, solo retorna materiales preferidos
        
    Returns:
        list: Lista de diccionarios con datos de materiales y su asociación
    """
    session = get_session()
    try:
        query = session.query(Material, ServicioMaterial).join(
            ServicioMaterial,
            Material.id_material == ServicioMaterial.id_material
        ).filter(ServicioMaterial.id_servicio == id_servicio)
        
        if solo_preferidos:
            query = query.filter(ServicioMaterial.es_preferido == 1)
        
        resultados = query.all()
        
        materiales = []
        for material, asociacion in resultados:
            material_dict = material.to_dict()
            material_dict['es_preferido'] = bool(asociacion.es_preferido)
            materiales.append(material_dict)
        
        return materiales
    finally:
        session.close()


def obtener_servicios_por_material(id_material):
    """
    Obtiene los servicios que usan un material específico
    
    Args:
        id_material: ID del material
        
    Returns:
        list: Lista de diccionarios con datos de servicios
    """
    session = get_session()
    try:
        servicios = session.query(Servicio).join(
            ServicioMaterial,
            Servicio.id_servicio == ServicioMaterial.id_servicio
        ).filter(ServicioMaterial.id_material == id_material).all()
        
        return [servicio.to_dict() for servicio in servicios]
    finally:
        session.close()


def marcar_material_preferido(id_servicio, id_material, es_preferido=True):
    """
    Marca o desmarca un material como preferido para un servicio
    
    Args:
        id_servicio: ID del servicio
        id_material: ID del material
        es_preferido: True para marcar como preferido, False para normal
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        asociacion = session.query(ServicioMaterial).filter(
            ServicioMaterial.id_servicio == id_servicio,
            ServicioMaterial.id_material == id_material
        ).first()
        
        if asociacion:
            asociacion.es_preferido = 1 if es_preferido else 0
            session.commit()
            return True
        return False
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        session.close()


def obtener_materiales_disponibles_para_servicio(id_servicio):
    """
    Obtiene materiales NO asociados a un servicio (disponibles para asociar)
    
    Args:
        id_servicio: ID del servicio
        
    Returns:
        list: Lista de materiales no asociados
    """
    session = get_session()
    try:
        # Subconsulta de IDs de materiales ya asociados (usando select() para evitar SAWarning)
        ids_asociados = session.query(ServicioMaterial.id_material).filter(
            ServicioMaterial.id_servicio == id_servicio
        ).scalar_subquery()
        
        # Materiales que NO están en la lista de asociados
        materiales = session.query(Material).filter(
            ~Material.id_material.in_(ids_asociados)
        ).order_by(Material.nombre_material).all()
        
        return [material.to_dict() for material in materiales]
    finally:
        session.close()


# ========== RELACIÓN MAQUINA ↔ SERVICIO ==========

def asociar_servicio_a_maquina(id_maquina, id_servicio, es_recomendada=False):
    """
    Asocia un servicio a una máquina
    
    Args:
        id_maquina: ID de la máquina
        id_servicio: ID del servicio
        es_recomendada: Si es una máquina recomendada para el servicio (True/False)
        
    Returns:
        bool: True si se asoció correctamente, False si ya existe
    """
    session = get_session()
    try:
        # Verificar si ya existe la asociación
        existe = session.query(MaquinaServicio).filter(
            MaquinaServicio.id_maquina == id_maquina,
            MaquinaServicio.id_servicio == id_servicio
        ).first()
        
        if existe:
            return False
        
        # Crear nueva asociación
        asociacion = MaquinaServicio(
            id_maquina=id_maquina,
            id_servicio=id_servicio,
            es_recomendada=1 if es_recomendada else 0
        )
        session.add(asociacion)
        session.commit()
        return True
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        session.close()


def desasociar_servicio_de_maquina(id_maquina, id_servicio):
    """
    Elimina la asociación entre una máquina y un servicio
    
    Args:
        id_maquina: ID de la máquina
        id_servicio: ID del servicio
        
    Returns:
        bool: True si se eliminó correctamente
    """
    session = get_session()
    try:
        asociacion = session.query(MaquinaServicio).filter(
            MaquinaServicio.id_maquina == id_maquina,
            MaquinaServicio.id_servicio == id_servicio
        ).first()
        
        if asociacion:
            session.delete(asociacion)
            session.commit()
            return True
        return False
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        session.close()


def obtener_servicios_por_maquina(id_maquina, solo_recomendados=False):
    """
    Obtiene los servicios asociados a una máquina
    
    Args:
        id_maquina: ID de la máquina
        solo_recomendados: Si True, solo retorna servicios recomendados
        
    Returns:
        list: Lista de diccionarios con datos de servicios y su asociación
    """
    session = get_session()
    try:
        query = session.query(Servicio, MaquinaServicio).join(
            MaquinaServicio,
            Servicio.id_servicio == MaquinaServicio.id_servicio
        ).filter(MaquinaServicio.id_maquina == id_maquina)
        
        if solo_recomendados:
            query = query.filter(MaquinaServicio.es_recomendada == 1)
        
        resultados = query.all()
        
        servicios = []
        for servicio, asociacion in resultados:
            servicio_dict = servicio.to_dict()
            servicio_dict['es_recomendada'] = bool(asociacion.es_recomendada)
            servicios.append(servicio_dict)
        
        return servicios
    finally:
        session.close()


def obtener_maquinas_por_servicio(id_servicio):
    """
    Obtiene las máquinas que pueden realizar un servicio específico
    
    Args:
        id_servicio: ID del servicio
        
    Returns:
        list: Lista de diccionarios con datos de máquinas
    """
    session = get_session()
    try:
        maquinas = session.query(Maquina).join(
            MaquinaServicio,
            Maquina.id_maquina == MaquinaServicio.id_maquina
        ).filter(MaquinaServicio.id_servicio == id_servicio).all()
        
        return [maquina.to_dict() for maquina in maquinas]
    finally:
        session.close()


def marcar_maquina_recomendada(id_maquina, id_servicio, es_recomendada=True):
    """
    Marca o desmarca una máquina como recomendada para un servicio
    
    Args:
        id_maquina: ID de la máquina
        id_servicio: ID del servicio
        es_recomendada: True para marcar como recomendada, False para normal
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        asociacion = session.query(MaquinaServicio).filter(
            MaquinaServicio.id_maquina == id_maquina,
            MaquinaServicio.id_servicio == id_servicio
        ).first()
        
        if asociacion:
            asociacion.es_recomendada = 1 if es_recomendada else 0
            session.commit()
            return True
        return False
    except SQLAlchemyError:
        session.rollback()
        return False
    finally:
        session.close()


def obtener_servicios_disponibles_para_maquina(id_maquina):
    """
    Obtiene servicios NO asociados a una máquina (disponibles para asociar)
    
    Args:
        id_maquina: ID de la máquina
        
    Returns:
        list: Lista de servicios no asociados
    """
    session = get_session()
    try:
        # Subconsulta de IDs de servicios ya asociados (usando scalar_subquery() para evitar SAWarning)
        ids_asociados = session.query(MaquinaServicio.id_servicio).filter(
            MaquinaServicio.id_maquina == id_maquina
        ).scalar_subquery()
        
        # Servicios que NO están en la lista de asociados
        servicios = session.query(Servicio).filter(
            ~Servicio.id_servicio.in_(ids_asociados)
        ).order_by(Servicio.nombre_servicio).all()
        
        return [servicio.to_dict() for servicio in servicios]
    finally:
        session.close()


# ========== CONFIGURACIÓN DEL SISTEMA ==========

# Valores por defecto para inicializar la BD
CONFIGURACIONES_DEFECTO = [
    # Producción - Horarios y días laborales
    {'clave': 'hora_apertura', 'valor': '8', 'tipo_dato': 'int', 'categoria': 'produccion', 
     'descripcion': 'Hora de apertura del taller (formato 24h)'},
    {'clave': 'hora_cierre', 'valor': '18', 'tipo_dato': 'int', 'categoria': 'produccion',
     'descripcion': 'Hora de cierre del taller (formato 24h)'},
    {'clave': 'dias_laborales', 'valor': '1,2,3,4,5,6', 'tipo_dato': 'str', 'categoria': 'produccion',
     'descripcion': 'Días laborales (1=Lunes, 7=Domingo). Separados por coma'},
    {'clave': 'horas_laborales_dia', 'valor': '8', 'tipo_dato': 'int', 'categoria': 'produccion',
     'descripcion': 'Horas de trabajo efectivas por día'},
    {'clave': 'tiempo_promedio_pedido', 'valor': '4', 'tipo_dato': 'float', 'categoria': 'produccion',
     'descripcion': 'Tiempo promedio en horas para completar un pedido'},
    
    # Negocio - Márgenes y tiempos
    {'clave': 'margen_ganancia_minimo', 'valor': '30', 'tipo_dato': 'int', 'categoria': 'negocio',
     'descripcion': 'Margen de ganancia mínimo (%)'},
    {'clave': 'margen_ganancia_normal', 'valor': '50', 'tipo_dato': 'int', 'categoria': 'negocio',
     'descripcion': 'Margen de ganancia estándar (%)'},
    {'clave': 'margen_ganancia_premium', 'valor': '70', 'tipo_dato': 'int', 'categoria': 'negocio',
     'descripcion': 'Margen de ganancia premium (%)'},
    {'clave': 'recargo_urgente', 'valor': '30', 'tipo_dato': 'int', 'categoria': 'negocio',
     'descripcion': 'Recargo por pedidos urgentes (%)'},
    {'clave': 'horas_minimas_anticipacion', 'valor': '24', 'tipo_dato': 'int', 'categoria': 'negocio',
     'descripcion': 'Horas mínimas de anticipación para pedidos'},
    
    # Inventario - Alertas
    {'clave': 'stock_minimo_porcentaje', 'valor': '20', 'tipo_dato': 'int', 'categoria': 'inventario',
     'descripcion': 'Porcentaje para alerta de stock bajo (%)'},
    {'clave': 'stock_critico_porcentaje', 'valor': '10', 'tipo_dato': 'int', 'categoria': 'inventario',
     'descripcion': 'Porcentaje para alerta de stock crítico (%)'},
    {'clave': 'metros_minimos_rollo', 'valor': '5', 'tipo_dato': 'float', 'categoria': 'inventario',
     'descripcion': 'Metros mínimos en rollo para alerta'},
    
    # Técnico - Impresión
    {'clave': 'margen_tecnico_impresion', 'valor': '0.05', 'tipo_dato': 'float', 'categoria': 'tecnico',
     'descripcion': 'Margen técnico para impresión (metros)'},
    {'clave': 'solapamiento_paños', 'valor': '0.02', 'tipo_dato': 'float', 'categoria': 'tecnico',
     'descripcion': 'Solapamiento entre paños para unión (metros)'},
    {'clave': 'ancho_maximo_default', 'valor': '2.5', 'tipo_dato': 'float', 'categoria': 'tecnico',
     'descripcion': 'Ancho máximo por defecto para máquinas sin configurar (metros)'},
]


def obtener_configuraciones(categoria=None):
    """
    Obtiene todas las configuraciones del sistema
    
    Args:
        categoria: Filtrar por categoría (opcional)
    
    Returns:
        list: Lista de diccionarios con configuraciones
    """
    session = get_session()
    try:
        query = session.query(ConfiguracionSistema)
        if categoria:
            query = query.filter(ConfiguracionSistema.categoria == categoria)
        configs = query.order_by(ConfiguracionSistema.categoria, ConfiguracionSistema.clave).all()
        return [c.to_dict() for c in configs]
    finally:
        session.close()


def obtener_configuracion(clave, default=None):
    """
    Obtiene el valor de una configuración específica
    
    Args:
        clave: Clave de la configuración
        default: Valor por defecto si no existe
    
    Returns:
        Valor de la configuración (tipado correctamente)
    """
    session = get_session()
    try:
        config = session.query(ConfiguracionSistema).filter(
            ConfiguracionSistema.clave == clave
        ).first()
        
        if config:
            return config.get_valor_tipado()
        return default
    finally:
        session.close()


def guardar_configuracion(clave, valor, tipo_dato='str', categoria='general', descripcion=None):
    """
    Guarda o actualiza una configuración
    
    Args:
        clave: Identificador único
        valor: Valor a guardar
        tipo_dato: Tipo de dato ('str', 'int', 'float', 'bool', 'json')
        categoria: Categoría para agrupar
        descripcion: Descripción para el usuario
    
    Returns:
        dict: Configuración guardada
    """
    session = get_session()
    try:
        config = session.query(ConfiguracionSistema).filter(
            ConfiguracionSistema.clave == clave
        ).first()
        
        if config:
            config.valor = str(valor)
            config.tipo_dato = tipo_dato
            if categoria:
                config.categoria = categoria
            if descripcion:
                config.descripcion = descripcion
        else:
            config = ConfiguracionSistema(
                clave=clave,
                valor=str(valor),
                tipo_dato=tipo_dato,
                categoria=categoria,
                descripcion=descripcion
            )
            session.add(config)
        
        session.commit()
        session.refresh(config)
        return config.to_dict()
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()


def actualizar_configuracion(clave, valor):
    """
    Actualiza solo el valor de una configuración existente
    
    Args:
        clave: Clave de la configuración
        valor: Nuevo valor
    
    Returns:
        bool: True si se actualizó, False si no existe
    """
    session = get_session()
    try:
        config = session.query(ConfiguracionSistema).filter(
            ConfiguracionSistema.clave == clave
        ).first()
        
        if config:
            config.valor = str(valor)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise e
    finally:
        session.close()


def eliminar_configuracion(clave):
    """Elimina una configuración"""
    session = get_session()
    try:
        config = session.query(ConfiguracionSistema).filter(
            ConfiguracionSistema.clave == clave
        ).first()
        
        if config:
            session.delete(config)
            session.commit()
            return True
        return False
    finally:
        session.close()


def inicializar_configuraciones_defecto():
    """
    Inicializa las configuraciones por defecto si no existen
    Se llama al iniciar la aplicación
    """
    session = get_session()
    try:
        for cfg in CONFIGURACIONES_DEFECTO:
            existe = session.query(ConfiguracionSistema).filter(
                ConfiguracionSistema.clave == cfg['clave']
            ).first()
            
            if not existe:
                nueva = ConfiguracionSistema(
                    clave=cfg['clave'],
                    valor=cfg['valor'],
                    tipo_dato=cfg['tipo_dato'],
                    categoria=cfg['categoria'],
                    descripcion=cfg['descripcion']
                )
                session.add(nueva)
        
        session.commit()
    except SQLAlchemyError:
        session.rollback()
    finally:
        session.close()


def obtener_configuracion_produccion():
    """
    Obtiene todas las configuraciones de producción como diccionario
    Útil para cola_produccion.py
    
    Returns:
        dict: Configuraciones de producción
    """
    return {
        'hora_apertura': obtener_configuracion('hora_apertura', 8),
        'hora_cierre': obtener_configuracion('hora_cierre', 18),
        'dias_laborales': obtener_configuracion('dias_laborales', '1,2,3,4,5,6'),
        'horas_laborales_dia': obtener_configuracion('horas_laborales_dia', 8),
        'tiempo_promedio_pedido': obtener_configuracion('tiempo_promedio_pedido', 4.0),
        'recargo_urgente': obtener_configuracion('recargo_urgente', 30),
    }


def obtener_configuracion_negocio():
    """
    Obtiene todas las configuraciones de negocio como diccionario
    
    Returns:
        dict: Configuraciones de negocio
    """
    return {
        'margen_ganancia_minimo': obtener_configuracion('margen_ganancia_minimo', 30),
        'margen_ganancia_normal': obtener_configuracion('margen_ganancia_normal', 50),
        'margen_ganancia_premium': obtener_configuracion('margen_ganancia_premium', 70),
        'horas_minimas_anticipacion': obtener_configuracion('horas_minimas_anticipacion', 24),
    }
