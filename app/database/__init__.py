"""
Capa de acceso a datos con SQLAlchemy ORM
Maneja la conexión y operaciones con SQLite usando modelos ORM
"""

from .conexion import DatabaseConnection, get_session, get_db
from .models import (
    Base, Cliente, Maquina, Material, EstadoPedido, 
    Servicio, Pedido, DetallePedido, ConsumoMaterial, ServicioMaterial,
    Usuario, Rol, Permiso, ReglaExperto
)

__all__ = [
    'DatabaseConnection',
    'get_session',
    'get_db',
    'Base',
    'Cliente',
    'Maquina',
    'Material',
    'EstadoPedido',
    'Servicio',
    'Pedido',
    'DetallePedido',
    'ConsumoMaterial',
    'ServicioMaterial',
    'Usuario',
    'Rol',
    'Permiso',
    'ReglaExperto'
]

