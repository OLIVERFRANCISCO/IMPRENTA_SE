"""
Servicio de Autenticación y Gestión de Sesión
Maneja el usuario actual y verifica permisos en tiempo real
"""


class AuthService:
    """
    Servicio singleton para gestión de autenticación y sesión
    
    Mantiene el estado del usuario actual y proporciona
    métodos para verificar permisos
    """
    
    _instance = None
    _usuario_actual = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def login(self, usuario_dict):
        """
        Establece el usuario actual después de login exitoso
        
        Args:
            usuario_dict: Diccionario con datos del usuario
        """
        self._usuario_actual = usuario_dict
    
    def logout(self):
        """Cierra la sesión del usuario actual"""
        self._usuario_actual = None
    
    def get_usuario_actual(self):
        """
        Obtiene el usuario actualmente autenticado
        
        Returns:
            dict: Datos del usuario o None si no hay sesión
        """
        return self._usuario_actual
    
    def is_authenticated(self):
        """
        Verifica si hay un usuario autenticado
        
        Returns:
            bool: True si hay sesión activa
        """
        return self._usuario_actual is not None
    
    def is_admin(self):
        """
        Verifica si el usuario actual es administrador
        
        Returns:
            bool: True si es admin
        """
        if not self.is_authenticated():
            return False
        return self._usuario_actual.get('nombre_rol', '').lower() == 'admin'
    
    def get_rol_actual(self):
        """
        Obtiene el nombre del rol del usuario actual
        
        Returns:
            str: Nombre del rol o None
        """
        if not self.is_authenticated():
            return None
        return self._usuario_actual.get('nombre_rol')
    
    def get_id_usuario(self):
        """
        Obtiene el ID del usuario actual
        
        Returns:
            int: ID del usuario o None
        """
        if not self.is_authenticated():
            return None
        return self._usuario_actual.get('id')
    
    def get_username(self):
        """
        Obtiene el username del usuario actual
        
        Returns:
            str: Username o None
        """
        if not self.is_authenticated():
            return None
        return self._usuario_actual.get('username')
    
    def tiene_permiso(self, panel, accion):
        """
        Verifica si el usuario actual tiene permiso para una acción
        
        Args:
            panel: Nombre del panel
            accion: Acción a verificar (crear, editar, eliminar, ver)
            
        Returns:
            bool: True si tiene permiso
        """
        if not self.is_authenticated():
            return False
        
        # Admin siempre tiene todos los permisos
        if self.is_admin():
            return True
        
        # Verificar permisos desde la base de datos
        from app.database.consultas_auth import verificar_permiso_usuario
        return verificar_permiso_usuario(
            self.get_id_usuario(),
            panel,
            accion
        )
    
    def puede_ver_panel(self, panel):
        """
        Verifica si el usuario puede ver un panel
        
        Args:
            panel: Nombre del panel
            
        Returns:
            bool: True si puede ver el panel
        """
        return self.tiene_permiso(panel, 'ver')
    
    def puede_crear(self, panel):
        """Verifica si puede crear en un panel"""
        return self.tiene_permiso(panel, 'crear')
    
    def puede_editar(self, panel):
        """Verifica si puede editar en un panel"""
        return self.tiene_permiso(panel, 'editar')
    
    def puede_eliminar(self, panel):
        """Verifica si puede eliminar en un panel"""
        return self.tiene_permiso(panel, 'eliminar')
    
    def obtener_paneles_permitidos(self):
        """
        Obtiene lista de paneles permitidos para el usuario actual
        
        Returns:
            list: Lista de nombres de paneles
        """
        if not self.is_authenticated():
            return []
        
        if self.is_admin():
            # Admin tiene acceso a todos los paneles
            return [
                'panel_pedidos',
                'panel_pedidos_clientes',
                'panel_clientes',
                'panel_servicios',
                'panel_inventario',
                'panel_maquinas',
                'panel_reportes',
                'panel_admin'  # Panel exclusivo de admin
            ]
        
        from app.database.consultas_auth import obtener_paneles_usuario
        return obtener_paneles_usuario(self.get_id_usuario())


# Instancia global del servicio
auth_service = AuthService()


def require_permission(panel, accion):
    """
    Decorador para requerir permisos en funciones
    
    Args:
        panel: Nombre del panel
        accion: Acción requerida
        
    Returns:
        Decorador que verifica permisos antes de ejecutar la función
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not auth_service.tiene_permiso(panel, accion):
                raise PermissionError(f"No tiene permiso para {accion} en {panel}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_admin(func):
    """
    Decorador para requerir rol de administrador
    
    Args:
        func: Función a proteger
        
    Returns:
        Función decorada que verifica si es admin
    """
    def wrapper(*args, **kwargs):
        if not auth_service.is_admin():
            raise PermissionError("Esta acción requiere permisos de administrador")
        return func(*args, **kwargs)
    return wrapper


def require_auth(func):
    """
    Decorador para requerir autenticación
    
    Args:
        func: Función a proteger
        
    Returns:
        Función decorada que verifica autenticación
    """
    def wrapper(*args, **kwargs):
        if not auth_service.is_authenticated():
            raise PermissionError("Debe iniciar sesión para acceder")
        return func(*args, **kwargs)
    return wrapper
