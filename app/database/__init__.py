"""
Capa de acceso a datos
Maneja la conexión y operaciones con SQLite
"""

from .conexion import get_db, DatabaseConnection

__all__ = ['get_db', 'DatabaseConnection']

