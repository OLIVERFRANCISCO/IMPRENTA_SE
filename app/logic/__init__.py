"""
Capa de lógica de negocio
Contiene cálculos y reglas del sistema experto
"""

from .calculos import *
from .motor_inferencia import *

__all__ = [
    'calcular_area',
    'calcular_costo_material',
    'calcular_costo_total',
    # Funciones del motor de inferencia (reemplazan reglas_experto)
    'sugerir_maquina_experto',
    'sugerir_material_experto',
    'validar_trabajo_experto',
    'estimar_tiempo_experto',
    'analizar_pedido_experto'
]

