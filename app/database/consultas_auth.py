"""
Funciones de consulta para autenticación y gestión de usuarios/roles
Proporciona operaciones CRUD para usuarios, roles y permisos
"""
import hashlib
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.database.conexion import get_session
from app.database.models import Usuario, Rol, Permiso


# ========== UTILIDADES DE HASH ==========

def hash_password(password):
    """
    Genera hash seguro de contraseña usando SHA-256
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        str: Hash de la contraseña
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verificar_password(password, password_hash):
    """
    Verifica si una contraseña coincide con el hash
    
    Args:
        password: Contraseña en texto plano
        password_hash: Hash almacenado
        
    Returns:
        bool: True si coincide
    """
    return hash_password(password) == password_hash


# ========== AUTENTICACIÓN ==========

def autenticar_usuario(username, password):
    """
    Autentica un usuario con username y password
    
    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano
        
    Returns:
        dict: Datos del usuario si la autenticación es exitosa, None si falla
    """
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(
            Usuario.username == username,
            Usuario.activo == 1
        ).first()
        
        if usuario and verificar_password(password, usuario.password_hash):
            # Actualizar último acceso
            usuario.ultimo_acceso = datetime.now()
            session.commit()
            return usuario.to_dict()
        
        return None
    finally:
        session.close()


# ========== USUARIOS ==========

def obtener_usuarios():
    """
    Obtiene todos los usuarios del sistema
    
    Returns:
        list: Lista de diccionarios con datos de usuarios
    """
    session = get_session()
    try:
        usuarios = session.query(Usuario).order_by(Usuario.username).all()
        return [usuario.to_dict() for usuario in usuarios]
    finally:
        session.close()


def obtener_usuario_por_id(id_usuario):
    """
    Obtiene un usuario por su ID
    
    Args:
        id_usuario: ID del usuario
        
    Returns:
        dict: Datos del usuario o None
    """
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        return usuario.to_dict() if usuario else None
    finally:
        session.close()


def obtener_usuario_por_username(username):
    """
    Obtiene un usuario por su username
    
    Args:
        username: Nombre de usuario
        
    Returns:
        dict: Datos del usuario o None
    """
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.username == username).first()
        return usuario.to_dict() if usuario else None
    finally:
        session.close()


def crear_usuario(username, password, rol_id):
    """
    Crea un nuevo usuario
    
    Args:
        username: Nombre de usuario (único)
        password: Contraseña en texto plano
        rol_id: ID del rol asignado
        
    Returns:
        int: ID del usuario creado
        
    Raises:
        Exception: Si el username ya existe o hay error de BD
    """
    session = get_session()
    try:
        # Verificar que el rol existe
        rol = session.query(Rol).filter(Rol.id == rol_id).first()
        if not rol:
            raise Exception("El rol especificado no existe")
        
        usuario = Usuario(
            username=username,
            password_hash=hash_password(password),
            rol_id=rol_id,
            activo=1
        )
        session.add(usuario)
        session.commit()
        return usuario.id
    except IntegrityError:
        session.rollback()
        raise Exception(f"El usuario '{username}' ya existe")
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al crear usuario: {str(e)}")
    finally:
        session.close()


def actualizar_usuario(id_usuario, username=None, password=None, rol_id=None, activo=None):
    """
    Actualiza un usuario existente
    
    Args:
        id_usuario: ID del usuario a actualizar
        username: Nuevo nombre de usuario (opcional)
        password: Nueva contraseña en texto plano (opcional)
        rol_id: Nuevo rol (opcional)
        activo: Estado activo (opcional)
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            return False
        
        if username:
            usuario.username = username
        if password:
            usuario.password_hash = hash_password(password)
        if rol_id is not None:
            usuario.rol_id = rol_id
        if activo is not None:
            usuario.activo = activo
        
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        raise Exception(f"El username '{username}' ya está en uso")
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar usuario: {str(e)}")
    finally:
        session.close()


def eliminar_usuario(id_usuario):
    """
    Elimina un usuario (soft delete - lo marca como inactivo)
    
    Args:
        id_usuario: ID del usuario a eliminar
        
    Returns:
        bool: True si se eliminó correctamente
    """
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if usuario:
            usuario.activo = 0
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar usuario: {str(e)}")
    finally:
        session.close()


def cambiar_password(id_usuario, password_actual, password_nueva):
    """
    Cambia la contraseña de un usuario
    
    Args:
        id_usuario: ID del usuario
        password_actual: Contraseña actual en texto plano
        password_nueva: Nueva contraseña en texto plano
        
    Returns:
        bool: True si se cambió correctamente
    """
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            return False
        
        if not verificar_password(password_actual, usuario.password_hash):
            raise Exception("La contraseña actual es incorrecta")
        
        usuario.password_hash = hash_password(password_nueva)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al cambiar contraseña: {str(e)}")
    finally:
        session.close()


# ========== ROLES ==========

def obtener_roles():
    """
    Obtiene todos los roles del sistema
    
    Returns:
        list: Lista de diccionarios con datos de roles
    """
    session = get_session()
    try:
        roles = session.query(Rol).order_by(Rol.nombre_rol).all()
        return [rol.to_dict() for rol in roles]
    finally:
        session.close()


def obtener_rol_por_id(id_rol):
    """
    Obtiene un rol por su ID
    
    Args:
        id_rol: ID del rol
        
    Returns:
        dict: Datos del rol o None
    """
    session = get_session()
    try:
        rol = session.query(Rol).filter(Rol.id == id_rol).first()
        return rol.to_dict() if rol else None
    finally:
        session.close()


def crear_rol(nombre_rol):
    """
    Crea un nuevo rol
    
    Args:
        nombre_rol: Nombre del rol (único)
        
    Returns:
        int: ID del rol creado
    """
    session = get_session()
    try:
        rol = Rol(nombre_rol=nombre_rol)
        session.add(rol)
        session.commit()
        return rol.id
    except IntegrityError:
        session.rollback()
        raise Exception(f"El rol '{nombre_rol}' ya existe")
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al crear rol: {str(e)}")
    finally:
        session.close()


def actualizar_rol(id_rol, nombre_rol):
    """
    Actualiza un rol existente
    
    Args:
        id_rol: ID del rol a actualizar
        nombre_rol: Nuevo nombre del rol
        
    Returns:
        bool: True si se actualizó correctamente
    """
    session = get_session()
    try:
        rol = session.query(Rol).filter(Rol.id == id_rol).first()
        if rol:
            rol.nombre_rol = nombre_rol
            session.commit()
            return True
        return False
    except IntegrityError:
        session.rollback()
        raise Exception(f"El nombre '{nombre_rol}' ya está en uso")
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al actualizar rol: {str(e)}")
    finally:
        session.close()


def eliminar_rol(id_rol):
    """
    Elimina un rol (no permite eliminar si tiene usuarios asignados)
    
    Args:
        id_rol: ID del rol a eliminar
        
    Returns:
        bool: True si se eliminó correctamente
    """
    session = get_session()
    try:
        rol = session.query(Rol).filter(Rol.id == id_rol).first()
        if not rol:
            return False
        
        # Verificar que no sea admin o empleado (roles base)
        if rol.nombre_rol.lower() in ['admin', 'empleado']:
            raise Exception("No se pueden eliminar los roles base del sistema")
        
        # Verificar que no tenga usuarios asignados
        if len(rol.usuarios) > 0:
            raise Exception(f"No se puede eliminar el rol porque tiene {len(rol.usuarios)} usuario(s) asignado(s)")
        
        session.delete(rol)
        session.commit()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar rol: {str(e)}")
    finally:
        session.close()


# ========== PERMISOS ==========

def obtener_permisos_por_rol(id_rol):
    """
    Obtiene todos los permisos de un rol
    
    Args:
        id_rol: ID del rol
        
    Returns:
        list: Lista de diccionarios con permisos
    """
    session = get_session()
    try:
        permisos = session.query(Permiso).filter(Permiso.rol_id == id_rol).all()
        return [permiso.to_dict() for permiso in permisos]
    finally:
        session.close()


def agregar_permiso(rol_id, panel, permiso):
    """
    Agrega un permiso a un rol
    
    Args:
        rol_id: ID del rol
        panel: Nombre del panel
        permiso: Tipo de permiso (crear, editar, eliminar, ver)
        
    Returns:
        int: ID del permiso creado
    """
    session = get_session()
    try:
        nuevo_permiso = Permiso(
            rol_id=rol_id,
            panel=panel,
            permiso=permiso
        )
        session.add(nuevo_permiso)
        session.commit()
        return nuevo_permiso.id
    except IntegrityError:
        session.rollback()
        # Permiso ya existe, no es error crítico
        return None
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al agregar permiso: {str(e)}")
    finally:
        session.close()


def eliminar_permiso(id_permiso):
    """
    Elimina un permiso específico
    
    Args:
        id_permiso: ID del permiso
        
    Returns:
        bool: True si se eliminó correctamente
    """
    session = get_session()
    try:
        permiso = session.query(Permiso).filter(Permiso.id == id_permiso).first()
        if permiso:
            session.delete(permiso)
            session.commit()
            return True
        return False
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar permiso: {str(e)}")
    finally:
        session.close()


def eliminar_permisos_rol(id_rol):
    """
    Elimina todos los permisos de un rol
    
    Args:
        id_rol: ID del rol
        
    Returns:
        int: Cantidad de permisos eliminados
    """
    session = get_session()
    try:
        count = session.query(Permiso).filter(Permiso.rol_id == id_rol).delete()
        session.commit()
        return count
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al eliminar permisos: {str(e)}")
    finally:
        session.close()


def configurar_permisos_rol(id_rol, permisos_dict):
    """
    Configura todos los permisos de un rol (reemplaza los existentes)
    
    Args:
        id_rol: ID del rol
        permisos_dict: Diccionario {panel: [lista de acciones]}
                      Ejemplo: {'panel_clientes': ['ver', 'crear', 'editar']}
        
    Returns:
        int: Cantidad de permisos configurados
    """
    session = get_session()
    try:
        # Eliminar permisos existentes
        session.query(Permiso).filter(Permiso.rol_id == id_rol).delete()
        
        # Agregar nuevos permisos
        count = 0
        for panel, acciones in permisos_dict.items():
            for accion in acciones:
                permiso = Permiso(
                    rol_id=id_rol,
                    panel=panel,
                    permiso=accion
                )
                session.add(permiso)
                count += 1
        
        session.commit()
        return count
    except SQLAlchemyError as e:
        session.rollback()
        raise Exception(f"Error al configurar permisos: {str(e)}")
    finally:
        session.close()


def verificar_permiso_usuario(id_usuario, panel, accion):
    """
    Verifica si un usuario tiene permiso para realizar una acción en un panel
    
    Args:
        id_usuario: ID del usuario
        panel: Nombre del panel
        accion: Acción a realizar
        
    Returns:
        bool: True si tiene permiso
    """
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            return False
        
        return usuario.tiene_permiso(panel, accion)
    finally:
        session.close()


def obtener_paneles_usuario(id_usuario):
    """
    Obtiene la lista de paneles a los que tiene acceso un usuario
    
    Args:
        id_usuario: ID del usuario
        
    Returns:
        list: Lista de nombres de paneles
    """
    session = get_session()
    try:
        usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
        if not usuario:
            return []
        
        return usuario.obtener_paneles_permitidos()
    finally:
        session.close()
