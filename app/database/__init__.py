"""
Capa de acceso a datos con SQLAlchemy ORM
Maneja la conexión y operaciones con SQLite usando modelos ORM
"""

from .conexion import DatabaseConnection, get_session, get_db
from .models import (
    Base, Cliente, Maquina, Material, EstadoPedido, 
    Servicio, Pedido, DetallePedido, ConsumoMaterial, ServicioMaterial,
    Usuario, Rol, Permiso, MaquinaServicio,
    # Nuevas tablas del sistema experto
    UnidadMedida, TipoMaterial, TipoMaquina, CapacidadMaquina,
    InventarioMaterial, AtributoRolloImpresion
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
    'MaquinaServicio',
    'Usuario',
    'Rol',
    'Permiso',
    # Nuevas
    'UnidadMedida',
    'TipoMaterial',
    'TipoMaquina',
    'CapacidadMaquina',
    'InventarioMaterial',
    'AtributoRolloImpresion'
]

