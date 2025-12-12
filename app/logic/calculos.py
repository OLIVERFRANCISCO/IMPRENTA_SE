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


def calcular_precio_sugerido(nombre_servicio, cantidad):
    """
    Calcula el precio unitario sugerido según reglas de negocio

    Reglas de Negocio:
    - Tazas Personalizadas: Precios escalonados
        * 1-9 unidades: S/. 25.00
        * 10-99 unidades: S/. 20.00
        * 100+ unidades: S/. 8.00
    - Otros productos: retorna None (precio manual)

    Args:
        nombre_servicio (str): Nombre del servicio/producto
        cantidad (int): Cantidad de unidades

    Returns:
        float or None: Precio unitario sugerido o None si no aplica
    """
    nombre_servicio_lower = nombre_servicio.lower()

    # Precios escalonados para Tazas Personalizadas
    if "taza" in nombre_servicio_lower:
        if cantidad >= 100:
            return 8.00
        elif cantidad >= 10:
            return 20.00
        else:
            return 25.00

    # Para otros servicios, retornar None (precio manual)
    return None


def validar_restricciones_cantidad(nombre_servicio, cantidad):
    """
    Valida restricciones de cantidad según el tipo de producto

    Reglas de Negocio:
    - Llaveros: Solo permitir 25, 50, 100, 200, 300... (múltiplos de 100 después de 100)

    Args:
        nombre_servicio (str): Nombre del servicio/producto
        cantidad (int): Cantidad a validar

    Returns:
        tuple: (es_valido: bool, mensaje: str, cantidad_sugerida: int)
    """
    nombre_servicio_lower = nombre_servicio.lower()

    # Validación estricta para Llaveros
    if "llavero" in nombre_servicio_lower:
        cantidades_validas = [25, 50]

        # Agregar múltiplos de 100
        for i in range(1, 51):  # hasta 5000 unidades
            cantidades_validas.append(i * 100)

        if cantidad in cantidades_validas:
            return True, "Cantidad válida", cantidad
        else:
            # Buscar la cantidad sugerida más cercana
            cantidad_sugerida = 25

            if cantidad < 25:
                cantidad_sugerida = 25
            elif cantidad < 50:
                # Entre 25 y 50, elegir el más cercano
                if (cantidad - 25) <= (50 - cantidad):
                    cantidad_sugerida = 25
                else:
                    cantidad_sugerida = 50
            elif cantidad < 100:
                # Entre 50 y 100, elegir el más cercano
                if (cantidad - 50) <= (100 - cantidad):
                    cantidad_sugerida = 50
                else:
                    cantidad_sugerida = 100
            else:
                # Para cantidades >= 100, redondear al múltiplo de 100 más cercano
                cantidad_sugerida = round(cantidad / 100) * 100
                if cantidad_sugerida < 100:
                    cantidad_sugerida = 100

            mensaje = f"Cantidad inválida. Sugerencia: usar {cantidad_sugerida} unidades (opciones válidas: 25, 50, 100, 200, 300...)"
            return False, mensaje, cantidad_sugerida

    # Para otros productos, cualquier cantidad es válida
    return True, "Cantidad válida", cantidad


def validar_optimizacion_impresion(ancho, nombre_servicio, ancho_maximo_maquina=2.5):
    """
    Valida y sugiere optimización para impresión de gigantografías

    Regla de Negocio:
    - Si el ancho supera el ancho máximo de la máquina (2.5m),
      sugerir dividir en paños o rotar el diseño

    Args:
        ancho (float): Ancho del pedido en metros
        nombre_servicio (str): Nombre del servicio
        ancho_maximo_maquina (float): Ancho máximo de la máquina (default: 2.5m)

    Returns:
        tuple: (requiere_optimizacion: bool, mensaje_sugerencia: str)
    """
    nombre_servicio_lower = nombre_servicio.lower()

    # Solo aplica para gigantografías
    if "gigantografia" in nombre_servicio_lower or "giganto" in nombre_servicio_lower:
        if ancho > ancho_maximo_maquina:
            mensaje = (
                f"⚠️ SUGERENCIA DE OPTIMIZACIÓN:\n\n"
                f"El ancho solicitado ({ancho}m) supera el ancho máximo de la máquina ({ancho_maximo_maquina}m).\n\n"
                f"Opciones recomendadas:\n"
                f"• Dividir el diseño en 2 paños de {ancho_maximo_maquina}m cada uno\n"
                f"• Imprimir rotado para optimizar el uso del material\n"
                f"• Consultar con el cliente sobre ajustes en las dimensiones"
            )
            return True, mensaje

    return False, ""


def convertir_millares_a_unidades(millares):
    """
    Convierte millares a unidades

    Usado para Flyers y Tarjetas donde:
    1 millar = 1000 unidades

    Args:
        millares (float): Cantidad en millares

    Returns:
        int: Cantidad en unidades
    """
    return int(millares * 1000)


def convertir_unidades_a_millares(unidades):
    """
    Convierte unidades a millares

    Args:
        unidades (int): Cantidad en unidades

    Returns:
        float: Cantidad en millares
    """
    return round(unidades / 1000, 2)


def validar_fecha_entrega(fecha_entrega, horas_minimas_anticipacion=24):
    """
    Valida que la fecha de entrega sea al menos 24 horas después de la fecha actual

    Regla de Negocio (R13):
    - La fecha de entrega debe ser mínimo 24 horas después

    Args:
        fecha_entrega (datetime): Fecha de entrega solicitada
        horas_minimas_anticipacion (int): Horas mínimas de anticipación requeridas

    Returns:
        tuple: (es_valida: bool, mensaje: str)
    """
    from datetime import datetime, timedelta

    fecha_actual = datetime.now()
    fecha_minima = fecha_actual + timedelta(hours=horas_minimas_anticipacion)

    if fecha_entrega < fecha_minima:
        mensaje = (
            f"❌ Fecha de entrega inválida\n\n"
            f"La fecha debe ser al menos {horas_minimas_anticipacion} horas después de ahora.\n\n"
            f"Fecha mínima permitida: {fecha_minima.strftime('%d/%m/%Y %H:%M')}"
        )
        return False, mensaje

    return True, "Fecha de entrega válida"


def validar_hora_entrega(hora, hora_minima=8, hora_maxima=20):
    """
    Valida que la hora de entrega esté dentro del horario permitido

    Regla de Negocio (R14):
    - Solo se permiten entregas entre 08:00 AM y 08:00 PM

    Args:
        hora (int): Hora en formato 24h (0-23)
        hora_minima (int): Hora mínima permitida (default: 8)
        hora_maxima (int): Hora máxima permitida (default: 20)

    Returns:
        tuple: (es_valida: bool, mensaje: str)
    """
    if hora < hora_minima or hora > hora_maxima:
        mensaje = (
            f"❌ Hora de entrega inválida\n\n"
            f"Las entregas solo se permiten entre las {hora_minima:02d}:00 y las {hora_maxima:02d}:00.\n\n"
            f"Hora ingresada: {hora:02d}:00"
        )
        return False, mensaje

    return True, "Hora de entrega válida"


def validar_fecha_hora_entrega_completa(fecha_entrega, horas_minimas_anticipacion=24, hora_minima=8, hora_maxima=20):
    """
    Valida fecha y hora de entrega de forma completa

    Args:
        fecha_entrega (datetime): Fecha y hora de entrega
        horas_minimas_anticipacion (int): Horas mínimas de anticipación
        hora_minima (int): Hora mínima del día permitida
        hora_maxima (int): Hora máxima del día permitida

    Returns:
        tuple: (es_valida: bool, mensaje: str)
    """
    # Validar fecha
    es_valida_fecha, msg_fecha = validar_fecha_entrega(fecha_entrega, horas_minimas_anticipacion)
    if not es_valida_fecha:
        return False, msg_fecha

    # Validar hora
    hora = fecha_entrega.hour
    es_valida_hora, msg_hora = validar_hora_entrega(hora, hora_minima, hora_maxima)
    if not es_valida_hora:
        return False, msg_hora

    return True, "Fecha y hora de entrega válidas"


# ========== GESTIÓN DE ROLLOS Y BOBINAS ==========

def seleccionar_rollo_optimo(ancho_diseno, tipo_material, materiales_disponibles):
    """
    Selecciona el rollo óptimo para un trabajo según el ancho requerido.

    Reglas de Negocio (R6, R7, R8, R9):
    - Aplica margen técnico de 0.05 m (5 cm)
    - Selecciona el rollo más estrecho que cumpla el requisito
    - Filtra por tipo de material
    - Maneja casos donde no existe rollo suficientemente ancho

    Args:
        ancho_diseno (float): Ancho del diseño en metros
        tipo_material (str): Nombre del tipo de material (ej: "Lona 13oz")
        materiales_disponibles (list): Lista de diccionarios con materiales disponibles
            Cada dict debe tener: id_material, nombre_material, ancho_bobina, cantidad_stock

    Returns:
        dict or None: Material seleccionado o None si no hay opciones
            {
                'id_material': int,
                'nombre_material': str,
                'ancho_bobina': float,
                'cantidad_stock': float,
                'ancho_necesario': float,
                'margen_aplicado': float
            }
    """
    # R6: Aplicar margen técnico de 5 cm
    MARGEN_TECNICO = 0.05
    ancho_necesario = ancho_diseno + MARGEN_TECNICO

    # R9: Filtrar por tipo de material
    materiales_filtrados = [
        m for m in materiales_disponibles
        if tipo_material.lower() in m['nombre_material'].lower()
    ]

    if not materiales_filtrados:
        return None

    # R7: Seleccionar rollos que cumplan el ancho requerido
    rollos_validos = [
        m for m in materiales_filtrados
        if m.get('ancho_bobina', 0) >= ancho_necesario
    ]

    # R8: Si no hay rollos suficientemente anchos, retornar None
    if not rollos_validos:
        return None

    # R7: Elegir el rollo más estrecho posible (optimización de material)
    rollo_optimo = min(rollos_validos, key=lambda m: m['ancho_bobina'])

    # Agregar información adicional
    rollo_optimo['ancho_necesario'] = ancho_necesario
    rollo_optimo['margen_aplicado'] = MARGEN_TECNICO

    return rollo_optimo


def verificar_disponibilidad_lineal(rollo_id, metros_requeridos, obtener_material_func):
    """
    Verifica si hay suficiente material en el rollo para el trabajo.

    Reglas de Negocio (R10, R11, R12):
    - Valida disponibilidad lineal del rollo
    - Emite alerta si stock < 5 m
    - Bloquea pedido si no hay suficiente material

    Args:
        rollo_id (int): ID del material/rollo en la base de datos
        metros_requeridos (float): Metros lineales necesarios
        obtener_material_func (callable): Función para obtener datos del material
            Debe retornar dict con 'cantidad_stock' al menos

    Returns:
        dict: Resultado de la validación
            {
                'disponible': bool,
                'metros_actuales': float,
                'metros_requeridos': float,
                'stock_critico': bool,
                'mensaje': str,
                'puede_continuar': bool
            }
    """
    # Obtener información del rollo
    material = obtener_material_func(rollo_id)

    if not material:
        return {
            'disponible': False,
            'metros_actuales': 0,
            'metros_requeridos': metros_requeridos,
            'stock_critico': True,
            'mensaje': 'Material no encontrado en la base de datos',
            'puede_continuar': False
        }

    metros_actuales = material.get('cantidad_stock', 0)

    # R11: Verificar stock crítico (< 5 m)
    STOCK_CRITICO_METROS = 5.0
    stock_critico = metros_actuales < STOCK_CRITICO_METROS

    # R10: Validar disponibilidad lineal
    disponible = metros_actuales >= metros_requeridos

    # Construir mensaje
    if not disponible:
        # R12: Material insuficiente
        mensaje = (
            f"❌ Material insuficiente en el rollo.\n"
            f"Restan {metros_actuales:.2f} m, se requieren {metros_requeridos:.2f} m.\n"
            f"Faltan {(metros_requeridos - metros_actuales):.2f} m."
        )
        puede_continuar = False
    elif stock_critico:
        # R11: Stock crítico pero suficiente para este trabajo
        mensaje = (
            f"⚠️ Stock Crítico: {metros_actuales:.2f} m disponibles.\n"
            f"Recomendación: Comprar material o cambiar rollo después de este trabajo."
        )
        puede_continuar = True
    else:
        # Stock normal
        mensaje = f"✓ Stock suficiente: {metros_actuales:.2f} m disponibles"
        puede_continuar = True

    return {
        'disponible': disponible,
        'metros_actuales': metros_actuales,
        'metros_requeridos': metros_requeridos,
        'stock_critico': stock_critico,
        'mensaje': mensaje,
        'puede_continuar': puede_continuar
    }


def descontar_stock_lineal(rollo_id, metros_consumidos, actualizar_stock_func):
    """
    Descuenta metros lineales del stock de un rollo específico.

    Reglas de Negocio (R4, R5, R19):
    - Descuenta solo del rollo específico seleccionado
    - El consumo depende solo del largo impreso, no del ancho
    - No comparte stock entre rollos de diferente ancho

    Args:
        rollo_id (int): ID del material/rollo
        metros_consumidos (float): Metros lineales a descontar
        actualizar_stock_func (callable): Función para actualizar el stock
            Debe aceptar (id_material, nueva_cantidad)

    Returns:
        dict: Resultado de la operación
            {
                'exito': bool,
                'stock_anterior': float,
                'stock_nuevo': float,
                'metros_consumidos': float,
                'mensaje': str
            }
    """
    try:
        # Esta función debe ser llamada después de verificar disponibilidad
        # R4, R5: Descuento lineal solo del rollo específico
        resultado = actualizar_stock_func(rollo_id, metros_consumidos)

        return {
            'exito': True,
            'stock_anterior': resultado.get('stock_anterior', 0),
            'stock_nuevo': resultado.get('stock_nuevo', 0),
            'metros_consumidos': metros_consumidos,
            'mensaje': f"Stock actualizado correctamente. Nuevo stock: {resultado.get('stock_nuevo', 0):.2f} m"
        }
    except Exception as e:
        return {
            'exito': False,
            'stock_anterior': 0,
            'stock_nuevo': 0,
            'metros_consumidos': metros_consumidos,
            'mensaje': f"Error al actualizar stock: {str(e)}"
        }



