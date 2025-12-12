"""
Funciones de consulta para Reglas del Sistema Experto
Proporciona operaciones CRUD para gestionar reglas IF-THEN
"""
import json
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.database.conexion import get_session
from app.database.models import ReglaExperto


# ========== REGLAS DEL SISTEMA EXPERTO ==========

def obtener_reglas(categoria=None, solo_activas=True):
    """
    Obtiene todas las reglas del sistema experto
    
    Args:
        categoria: Filtrar por categoría (opcional)
        solo_activas: Si True, solo devuelve reglas activas
        
    Returns:
        list: Lista de diccionarios con datos de reglas
    """
    session = get_session()
    try:
        query = session.query(ReglaExperto)
        
        if categoria:
            query = query.filter(ReglaExperto.categoria == categoria)
        
        if solo_activas:
            query = query.filter(ReglaExperto.activa == 1)
        
        reglas = query.order_by(ReglaExperto.prioridad, ReglaExperto.numero_regla).all()
        
        return [regla.to_dict() for regla in reglas]
    except Exception as e:
        print(f"Error al obtener reglas: {e}")
        return []
    finally:
        session.close()


def obtener_regla_por_id(id_regla):
    """
    Obtiene una regla específica por ID
    
    Args:
        id_regla: ID de la regla
        
    Returns:
        dict: Datos de la regla o None
    """
    session = get_session()
    try:
        regla = session.query(ReglaExperto).filter(ReglaExperto.id == id_regla).first()
        return regla.to_dict() if regla else None
    except Exception as e:
        print(f"Error al obtener regla: {e}")
        return None
    finally:
        session.close()


def obtener_regla_por_numero(numero_regla):
    """
    Obtiene una regla por su número (REGLA-01, etc.)
    
    Args:
        numero_regla: Número de regla
        
    Returns:
        dict: Datos de la regla o None
    """
    session = get_session()
    try:
        regla = session.query(ReglaExperto).filter(
            ReglaExperto.numero_regla == numero_regla
        ).first()
        return regla.to_dict() if regla else None
    except Exception as e:
        print(f"Error al obtener regla por número: {e}")
        return None
    finally:
        session.close()


def crear_regla(numero_regla, categoria, nombre, descripcion, condiciones, acciones,
                prioridad=5, activa=True, creada_por=None):
    """
    Crea una nueva regla del sistema experto
    
    Args:
        numero_regla: Número único de regla (ej: REGLA-01)
        categoria: Categoría de la regla
        nombre: Nombre descriptivo
        descripcion: Descripción completa
        condiciones: Condiciones IF (dict o JSON string)
        acciones: Acciones THEN (dict o JSON string)
        prioridad: Prioridad (1-10)
        activa: Si está activa o no
        creada_por: ID del usuario creador
        
    Returns:
        int: ID de la regla creada
        
    Raises:
        ValueError: Si ya existe una regla con ese número
        Exception: Error en creación
    """
    session = get_session()
    try:
        # Verificar si ya existe
        existe = session.query(ReglaExperto).filter(
            ReglaExperto.numero_regla == numero_regla
        ).first()
        
        if existe:
            raise ValueError(f"Ya existe una regla con el número {numero_regla}")
        
        # Convertir condiciones y acciones a JSON si son diccionarios
        if isinstance(condiciones, dict):
            condiciones = json.dumps(condiciones, ensure_ascii=False)
        if isinstance(acciones, dict):
            acciones = json.dumps(acciones, ensure_ascii=False)
        
        # Crear regla
        nueva_regla = ReglaExperto(
            numero_regla=numero_regla,
            categoria=categoria,
            nombre=nombre,
            descripcion=descripcion,
            condiciones=condiciones,
            acciones=acciones,
            prioridad=prioridad,
            activa=1 if activa else 0,
            creada_por=creada_por,
            fecha_creacion=datetime.now(),
            fecha_modificacion=datetime.now()
        )
        
        session.add(nueva_regla)
        session.commit()
        
        return nueva_regla.id
        
    except IntegrityError:
        session.rollback()
        raise ValueError(f"Ya existe una regla con el número {numero_regla}")
    except Exception as e:
        session.rollback()
        raise Exception(f"Error al crear regla: {str(e)}")
    finally:
        session.close()


def actualizar_regla(id_regla, numero_regla=None, categoria=None, nombre=None,
                    descripcion=None, condiciones=None, acciones=None,
                    prioridad=None, activa=None):
    """
    Actualiza una regla existente
    
    Args:
        id_regla: ID de la regla a actualizar
        numero_regla: Nuevo número (opcional)
        categoria: Nueva categoría (opcional)
        nombre: Nuevo nombre (opcional)
        descripcion: Nueva descripción (opcional)
        condiciones: Nuevas condiciones (opcional)
        acciones: Nuevas acciones (opcional)
        prioridad: Nueva prioridad (opcional)
        activa: Nuevo estado activo (opcional)
        
    Raises:
        ValueError: Si la regla no existe
        Exception: Error en actualización
    """
    session = get_session()
    try:
        regla = session.query(ReglaExperto).filter(ReglaExperto.id == id_regla).first()
        
        if not regla:
            raise ValueError(f"No existe regla con ID {id_regla}")
        
        # Actualizar campos si se proporcionaron
        if numero_regla is not None:
            # Verificar que no exista otra regla con ese número
            otra = session.query(ReglaExperto).filter(
                ReglaExperto.numero_regla == numero_regla,
                ReglaExperto.id != id_regla
            ).first()
            if otra:
                raise ValueError(f"Ya existe otra regla con el número {numero_regla}")
            regla.numero_regla = numero_regla
        
        if categoria is not None:
            regla.categoria = categoria
        if nombre is not None:
            regla.nombre = nombre
        if descripcion is not None:
            regla.descripcion = descripcion
        
        if condiciones is not None:
            if isinstance(condiciones, dict):
                condiciones = json.dumps(condiciones, ensure_ascii=False)
            regla.condiciones = condiciones
        
        if acciones is not None:
            if isinstance(acciones, dict):
                acciones = json.dumps(acciones, ensure_ascii=False)
            regla.acciones = acciones
        
        if prioridad is not None:
            regla.prioridad = prioridad
        
        if activa is not None:
            regla.activa = 1 if activa else 0
        
        regla.fecha_modificacion = datetime.now()
        
        session.commit()
        
    except IntegrityError:
        session.rollback()
        raise ValueError(f"Conflicto al actualizar regla: número duplicado")
    except Exception as e:
        session.rollback()
        raise Exception(f"Error al actualizar regla: {str(e)}")
    finally:
        session.close()


def eliminar_regla(id_regla):
    """
    Elimina una regla del sistema experto
    
    Args:
        id_regla: ID de la regla a eliminar
        
    Raises:
        ValueError: Si la regla no existe
        Exception: Error en eliminación
    """
    session = get_session()
    try:
        regla = session.query(ReglaExperto).filter(ReglaExperto.id == id_regla).first()
        
        if not regla:
            raise ValueError(f"No existe regla con ID {id_regla}")
        
        session.delete(regla)
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise Exception(f"Error al eliminar regla: {str(e)}")
    finally:
        session.close()


def activar_desactivar_regla(id_regla, activa):
    """
    Activa o desactiva una regla sin eliminarla
    
    Args:
        id_regla: ID de la regla
        activa: True para activar, False para desactivar
    """
    session = get_session()
    try:
        regla = session.query(ReglaExperto).filter(ReglaExperto.id == id_regla).first()
        
        if not regla:
            raise ValueError(f"No existe regla con ID {id_regla}")
        
        regla.activa = 1 if activa else 0
        regla.fecha_modificacion = datetime.now()
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise Exception(f"Error al cambiar estado de regla: {str(e)}")
    finally:
        session.close()


def obtener_categorias():
    """
    Obtiene las categorías únicas de reglas
    
    Returns:
        list: Lista de categorías
    """
    session = get_session()
    try:
        categorias = session.query(ReglaExperto.categoria).distinct().order_by(
            ReglaExperto.categoria
        ).all()
        return [cat[0] for cat in categorias]
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        return []
    finally:
        session.close()


def contar_reglas_por_categoria():
    """
    Cuenta reglas activas por categoría
    
    Returns:
        dict: {categoria: cantidad}
    """
    session = get_session()
    try:
        from sqlalchemy import func
        resultados = session.query(
            ReglaExperto.categoria,
            func.count(ReglaExperto.id)
        ).filter(
            ReglaExperto.activa == 1
        ).group_by(
            ReglaExperto.categoria
        ).all()
        
        return {cat: count for cat, count in resultados}
    except Exception as e:
        print(f"Error al contar reglas: {e}")
        return {}
    finally:
        session.close()


def parsear_condiciones(regla):
    """
    Convierte las condiciones JSON de una regla a diccionario
    
    Args:
        regla: Diccionario con datos de regla
        
    Returns:
        dict: Condiciones parseadas
    """
    try:
        if isinstance(regla['condiciones'], str):
            return json.loads(regla['condiciones'])
        return regla['condiciones']
    except:
        return {}


def parsear_acciones(regla):
    """
    Convierte las acciones JSON de una regla a diccionario
    
    Args:
        regla: Diccionario con datos de regla
        
    Returns:
        dict: Acciones parseadas
    """
    try:
        if isinstance(regla['acciones'], str):
            return json.loads(regla['acciones'])
        return regla['acciones']
    except:
        return {}
