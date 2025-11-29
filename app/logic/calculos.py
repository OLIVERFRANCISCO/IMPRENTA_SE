"""
Módulo de cálculos matemáticos
Contiene fórmulas para metraje, costos y tiempos
"""
from app.config import MARGEN_GANANCIA_NORMAL


def calcular_area(ancho, alto):
    """
    Calcula el área en metros cuadrados

    Args:
        ancho (float): Ancho en metros
        alto (float): Alto en metros

    Returns:
        float: Área en m2
    """
    return round(ancho * alto, 2)


def calcular_costo_material(ancho, alto, precio_por_m2):
    """
    Calcula el costo del material basado en dimensiones

    Args:
        ancho (float): Ancho en metros
        alto (float): Alto en metros
        precio_por_m2 (float): Precio por metro cuadrado

    Returns:
        float: Costo total del material
    """
    area = calcular_area(ancho, alto)
    return round(area * precio_por_m2, 2)


def calcular_costo_total(costo_material, costo_acabado=0, margen_ganancia=None):
    """
    Calcula el costo total aplicando margen de ganancia

    Regla de Negocio:
    Costo_Total = (Costo_Material + Costo_Acabado) * (1 + Margen_Ganancia/100)

    Args:
        costo_material (float): Costo del material
        costo_acabado (float): Costo del acabado
        margen_ganancia (float): Porcentaje de ganancia (default: config.MARGEN_GANANCIA_NORMAL)

    Returns:
        float: Costo total con margen
    """
    if margen_ganancia is None:
        margen_ganancia = MARGEN_GANANCIA_NORMAL

    costo_base = costo_material + costo_acabado
    costo_total = costo_base * (1 + margen_ganancia / 100)

    return round(costo_total, 2)


def calcular_precio_unitario(ancho, alto, precio_base_servicio, precio_material_por_unidad, margen=None):
    """
    Calcula el precio unitario de un item del pedido

    Args:
        ancho (float): Ancho del producto
        alto (float): Alto del producto
        precio_base_servicio (float): Precio base del servicio
        precio_material_por_unidad (float): Precio del material por unidad
        margen (float): Margen de ganancia

    Returns:
        float: Precio unitario calculado
    """
    area = calcular_area(ancho, alto) if ancho and alto else 1
    costo_material = area * precio_material_por_unidad

    return calcular_costo_total(costo_material + precio_base_servicio, 0, margen)


def calcular_saldo(costo_total, acuenta):
    """
    Calcula el saldo pendiente

    Args:
        costo_total (float): Costo total del pedido
        acuenta (float): Monto pagado a cuenta

    Returns:
        float: Saldo restante
    """
    return round(costo_total - acuenta, 2)


def validar_dimensiones(ancho, alto, max_ancho, max_alto=50):
    """
    Valida que las dimensiones sean correctas

    Args:
        ancho (float): Ancho en metros
        alto (float): Alto en metros
        max_ancho (float): Ancho máximo permitido
        max_alto (float): Alto máximo permitido

    Returns:
        tuple: (es_valido: bool, mensaje_error: str)
    """
    if ancho <= 0 or alto <= 0:
        return False, "Las dimensiones deben ser mayores a cero"

    if ancho > max_ancho:
        return False, f"El ancho máximo permitido es {max_ancho}m"

    if alto > max_alto:
        return False, f"El alto máximo permitido es {max_alto}m"

    return True, ""


def calcular_metraje_requerido(ancho, alto, cantidad, desperdicio_porcentaje=10):
    """
    Calcula el metraje real requerido considerando desperdicio

    Args:
        ancho (float): Ancho en metros
        alto (float): Alto en metros
        cantidad (int): Cantidad de piezas
        desperdicio_porcentaje (float): Porcentaje de desperdicio

    Returns:
        float: Metraje total requerido
    """
    area_unitaria = calcular_area(ancho, alto)
    area_total = area_unitaria * cantidad
    area_con_desperdicio = area_total * (1 + desperdicio_porcentaje / 100)

    return round(area_con_desperdicio, 2)


def convertir_unidades(cantidad, unidad_origen, unidad_destino):
    """
    Convierte entre diferentes unidades de medida

    Args:
        cantidad (float): Cantidad a convertir
        unidad_origen (str): Unidad de origen
        unidad_destino (str): Unidad de destino

    Returns:
        float: Cantidad convertida
    """
    conversiones = {
        ('metros', 'centimetros'): 100,
        ('centimetros', 'metros'): 0.01,
        ('metros', 'milimetros'): 1000,
        ('milimetros', 'metros'): 0.001,
        ('hojas', 'resmas'): 0.002,  # 1 resma = 500 hojas
        ('resmas', 'hojas'): 500,
    }

    clave = (unidad_origen.lower(), unidad_destino.lower())

    if clave in conversiones:
        return round(cantidad * conversiones[clave], 2)

    return cantidad  # Si no hay conversión, retorna el valor original


def calcular_descuento(precio_original, porcentaje_descuento):
    """
    Calcula el precio con descuento

    Args:
        precio_original (float): Precio original
        porcentaje_descuento (float): Porcentaje de descuento

    Returns:
        tuple: (precio_final: float, monto_ahorrado: float)
    """
    monto_descuento = precio_original * (porcentaje_descuento / 100)
    precio_final = precio_original - monto_descuento

    return round(precio_final, 2), round(monto_descuento, 2)

