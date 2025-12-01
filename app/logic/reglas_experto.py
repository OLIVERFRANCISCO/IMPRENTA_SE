"""
Motor del Sistema Experto
Contiene las reglas IF-THEN para recomendar máquinas, materiales y tiempos
"""
from datetime import datetime, timedelta
from app.config import (
    ANCHO_MAXIMO_IMPRESORA_PEQUENA,
    TIEMPO_PRODUCCION_BASE,
    TIEMPO_COMPRA_MATERIAL,
    TIEMPO_DISEÑO
)
from app.logic.cola_produccion import (
    calcular_fecha_entrega_con_cola,
    estimar_tiempo_produccion_por_tipo,
    obtener_info_cola_produccion
)
from app.database.consultas import obtener_material_por_id


# ========== REGLA 1: RECOMENDACIÓN DE MÁQUINA ==========

def sugerir_maquina(tipo_trabajo, ancho=0, alto=0):
    """
    Regla de Asignación de Recursos

    SI Tipo_Trabajo = "Recuerdo" ENTONCES Máquina = "Impresora Pequeña"
    SI Tipo_Trabajo = "Gigantografía" ENTONCES Máquina = "Plotter/Grande"
    SI Ancho > 0.45m ENTONCES Máquina = "Plotter/Grande"

    Args:
        tipo_trabajo (str): Tipo de trabajo
        ancho (float): Ancho del trabajo en metros
        alto (float): Alto del trabajo en metros

    Returns:
        dict: {
            'maquina_recomendada': str,
            'tipo_maquina': str,
            'explicacion': str
        }
    """
    tipo_trabajo_lower = tipo_trabajo.lower()

    # Regla 1: Por tipo de trabajo
    if "recuerdo" in tipo_trabajo_lower or "merchandising" in tipo_trabajo_lower:
        if ancho <= ANCHO_MAXIMO_IMPRESORA_PEQUENA:
            return {
                'maquina_recomendada': 'Impresora Pequeña (Láser/Sublimación)',
                'tipo_maquina': 'Pequeño Formato',
                'explicacion': f'Para recuerdos y merchandising de hasta {ANCHO_MAXIMO_IMPRESORA_PEQUENA}m de ancho, se recomienda impresora pequeña para mejor calidad y menor costo.'
            }

    # Regla 2: Por tamaño (dimensiones)
    if ancho > ANCHO_MAXIMO_IMPRESORA_PEQUENA:
        return {
            'maquina_recomendada': 'Plotter de Gran Formato',
            'tipo_maquina': 'Gran Formato',
            'explicacion': f'El ancho de {ancho}m supera la capacidad de impresoras pequeñas. Se requiere Plotter de gran formato.'
        }

    # Regla 3: Gigantografías siempre van a Plotter
    if "gigantograf" in tipo_trabajo_lower or "banner" in tipo_trabajo_lower or "lona" in tipo_trabajo_lower:
        return {
            'maquina_recomendada': 'Plotter de Gran Formato',
            'tipo_maquina': 'Gran Formato',
            'explicacion': 'Las gigantografías y banners requieren impresión en gran formato con Plotter.'
        }

    # Regla 4: Formatos pequeños (tarjetas, flyers, etc.)
    if "tarjeta" in tipo_trabajo_lower or "flyer" in tipo_trabajo_lower or "formato" in tipo_trabajo_lower:
        return {
            'maquina_recomendada': 'Impresora Láser A3',
            'tipo_maquina': 'Pequeño Formato',
            'explicacion': 'Para formatos de papelería, la impresora láser ofrece mejor velocidad y calidad.'
        }

    # Regla por defecto
    return {
        'maquina_recomendada': 'Impresora Láser A3',
        'tipo_maquina': 'Pequeño Formato',
        'explicacion': 'Máquina estándar para trabajos de formato pequeño a mediano.'
    }


# ========== REGLA 2: RECOMENDACIÓN DE MATERIAL ==========

def sugerir_material(tipo_trabajo, uso_final="general"):
    """
    Regla de Recomendación de Material según el uso

    Args:
        tipo_trabajo (str): Tipo de servicio
        uso_final (str): Uso final del producto (publicidad, recuerdos, formatería)

    Returns:
        dict: {
            'materiales_recomendados': list,
            'explicacion': str
        }
    """
    tipo_lower = tipo_trabajo.lower()
    uso_lower = uso_final.lower()

    materiales = []
    explicacion = ""

    # Regla 1: Publicidad exterior
    if "gigantograf" in tipo_lower or "banner" in tipo_lower or "publicidad" in uso_lower:
        materiales = [
            {'nombre': 'Lona 13oz', 'razon': 'Resistente a exteriores'},
            {'nombre': 'Vinil Adhesivo', 'razon': 'Para superficies lisas'}
        ]
        explicacion = "Para publicidad exterior se recomienda material resistente al agua y rayos UV."

    # Regla 2: Recuerdos y merchandising
    elif "recuerdo" in tipo_lower or "merchandising" in uso_lower or "taza" in tipo_lower:
        materiales = [
            {'nombre': 'Papel Transfer Sublimación', 'razon': 'Para transferencia térmica'},
            {'nombre': 'Tinta Sublimación', 'razon': 'Colores vibrantes en textiles'}
        ]
        explicacion = "Para recuerdos personalizados se recomienda sublimación para mejor durabilidad."

    # Regla 3: Papelería y formatos
    elif "tarjeta" in tipo_lower or "flyer" in tipo_lower or "formato" in uso_lower:
        materiales = [
            {'nombre': 'Papel Couché 300g', 'razon': 'Acabado profesional'},
            {'nombre': 'Papel Bond 75g', 'razon': 'Económico para volumen'}
        ]
        explicacion = "Para papelería se recomienda papel couché para mejor presentación."

    else:
        materiales = [
            {'nombre': 'Papel Bond 75g', 'razon': 'Uso general'},
        ]
        explicacion = "Material estándar para impresiones generales."

    return {
        'materiales_recomendados': materiales,
        'explicacion': explicacion
    }


# ========== REGLA 3: ESTIMACIÓN DE TIEMPO DE ENTREGA ==========

def estimar_tiempo_entrega(tipo_servicio="general", area_m2=0, cantidad=1, material_en_stock=True,
                          requiere_diseño=False, es_urgente=False):
    """
    Regla de Tiempo de Entrega considerando:
    - Cola de producción actual (pedidos pendientes)
    - Jornada laboral de 12 horas/día
    - Tiempo de compra de material si no hay stock
    - Tiempo de diseño si es necesario
    - Pedidos urgentes tienen prioridad

    Args:
        tipo_servicio (str): Tipo de servicio (para estimar tiempo de producción)
        area_m2 (float): Área en metros cuadrados
        cantidad (int): Cantidad de unidades
        material_en_stock (bool): Si hay material disponible
        requiere_diseño (bool): Si requiere diseño gráfico
        es_urgente (bool): Si es pedido urgente (20% recargo)

    Returns:
        dict: {
            'horas_estimadas': float,
            'fecha_entrega': datetime,
            'dias_habiles': int,
            'explicacion': str,
            'alertas': list,
            'info_cola': dict,
            'detalles_calculo': str
        }
    """
    alertas = []
    explicacion_partes = []

    # 1. Estimar tiempo de producción base según el tipo de servicio
    horas_produccion = estimar_tiempo_produccion_por_tipo(tipo_servicio, area_m2, cantidad)
    explicacion_partes.append(f"Tiempo de producción: {horas_produccion:.1f}h")

    # 2. Agregar tiempo de diseño si es necesario
    if requiere_diseño:
        horas_produccion += TIEMPO_DISEÑO
        explicacion_partes.append(f"+ Diseño gráfico: {TIEMPO_DISEÑO}h")

    # 3. Considerar tiempo de compra de material
    if not material_en_stock:
        horas_produccion += TIEMPO_COMPRA_MATERIAL
        alertas.append("ADVERTENCIA: Se requiere comprar material")
        explicacion_partes.append(f"+ Compra de material: {TIEMPO_COMPRA_MATERIAL}h")

    # 4. Calcular fecha de entrega considerando cola de producción
    calculo_cola = calcular_fecha_entrega_con_cola(
        horas_requeridas=horas_produccion,
        es_urgente=es_urgente
    )

    # 5. Agregar alertas sobre urgencia
    if es_urgente:
        alertas.append(f"URGENTE: Pedido urgente con recargo del {calculo_cola['recargo_porcentaje']:.0f}%")

    # 6. Obtener información de la cola
    info_cola = obtener_info_cola_produccion()

    explicacion_completa = "\n".join(explicacion_partes)

    return {
        'horas_estimadas': horas_produccion,
        'fecha_entrega': calculo_cola['fecha_entrega'],
        'dias_habiles': calculo_cola['dias_habiles'],
        'alertas': alertas,
        'explicacion': explicacion_completa,
        'info_cola': {
            'pedidos_pendientes': info_cola['pedidos_en_cola'],
            'horas_en_cola': info_cola['horas_pendientes'],
            'dias_ocupados': info_cola['dias_ocupados'],
            'estado_produccion': info_cola['estado']
        },
        'detalles_calculo': calculo_cola['explicacion']
    }


# ========== REGLA 4: VALIDACIÓN DE METRAJE ==========

def validar_metraje(ancho, alto, tipo_trabajo):
    """
    Detecta inconsistencias o errores frecuentes en el metraje

    Args:
        ancho (float): Ancho en metros
        alto (float): Alto en metros
        tipo_trabajo (str): Tipo de trabajo

    Returns:
        dict: {
            'es_valido': bool,
            'errores': list,
            'advertencias': list
        }
    """
    errores = []
    advertencias = []

    # Validación 1: Dimensiones mínimas
    if ancho <= 0 or alto <= 0:
        errores.append("Las dimensiones deben ser mayores a cero")

    # Validación 2: Dimensiones sospechosamente grandes
    if ancho > 5 or alto > 20:
        advertencias.append(f"ADVERTENCIA: Dimensiones muy grandes: {ancho}m x {alto}m. Verificar si es correcto.")

    # Validación 3: Dimensiones muy pequeñas para gigantografías
    tipo_lower = tipo_trabajo.lower()
    if "gigantograf" in tipo_lower or "banner" in tipo_lower:
        if ancho < 0.5 or alto < 0.5:
            advertencias.append("ADVERTENCIA: Las gigantografías normalmente son más grandes. Verificar medidas.")

    # Validación 4: Ancho vs Alto invertidos (error común)
    if "tarjeta" in tipo_lower and ancho > alto:
        advertencias.append("ADVERTENCIA: Posible error - el ancho es mayor que el alto en una tarjeta. Verificar orientación.")

    # Validación 5: Dimensiones decimales muy precisas (posible error de conversión)
    if (ancho % 0.05 != 0) or (alto % 0.05 != 0):
        advertencias.append("SUGERENCIA: Redondear a 5cm para facilitar el corte.")

    es_valido = len(errores) == 0

    return {
        'es_valido': es_valido,
        'errores': errores,
        'advertencias': advertencias
    }


# ========== REGLA 5: RECOMENDACIÓN DE ACABADO ==========

def sugerir_acabado(tipo_trabajo, uso_final=""):
    """
    Sugiere acabados según el tipo de trabajo

    Args:
        tipo_trabajo (str): Tipo de servicio
        uso_final (str): Uso del producto

    Returns:
        dict: {
            'acabados_recomendados': list,
            'explicacion': str
        }
    """
    tipo_lower = tipo_trabajo.lower()

    acabados = []

    if "gigantograf" in tipo_lower or "banner" in tipo_lower:
        acabados = [
            {'nombre': 'Laminado Mate', 'beneficio': 'Protege de rayos UV', 'costo_aprox': 5.0},
            {'nombre': 'Laminado Brillante', 'beneficio': 'Más impacto visual', 'costo_aprox': 5.5},
            {'nombre': 'Ojales metálicos', 'beneficio': 'Facilita instalación', 'costo_aprox': 1.0}
        ]
    elif "tarjeta" in tipo_lower:
        acabados = [
            {'nombre': 'Laminado Mate', 'beneficio': 'Elegante y duradero', 'costo_aprox': 3.0},
            {'nombre': 'Barniz UV', 'beneficio': 'Acabado premium', 'costo_aprox': 5.0},
            {'nombre': 'Sin acabado', 'beneficio': 'Económico', 'costo_aprox': 0}
        ]
    else:
        acabados = [
            {'nombre': 'Sin acabado', 'beneficio': 'Estándar', 'costo_aprox': 0}
        ]

    return {
        'acabados_recomendados': acabados,
        'explicacion': 'Acabados recomendados para mayor durabilidad y presentación'
    }


# ========== REGLA 6: ANÁLISIS DE RENTABILIDAD ==========

def analizar_rentabilidad(costo_material, costo_mano_obra, precio_venta):
    """
    Analiza si un pedido es rentable según los márgenes

    Args:
        costo_material (float): Costo de materiales
        costo_mano_obra (float): Costo de mano de obra
        precio_venta (float): Precio de venta al cliente

    Returns:
        dict: {
            'es_rentable': bool,
            'margen_porcentaje': float,
            'ganancia_neta': float,
            'recomendacion': str
        }
    """
    costo_total = costo_material + costo_mano_obra
    ganancia_neta = precio_venta - costo_total

    if costo_total == 0:
        margen_porcentaje = 0
    else:
        margen_porcentaje = (ganancia_neta / costo_total) * 100

    # Reglas de rentabilidad
    if margen_porcentaje < 20:
        return {
            'es_rentable': False,
            'margen_porcentaje': round(margen_porcentaje, 2),
            'ganancia_neta': round(ganancia_neta, 2),
            'recomendacion': 'Margen muy bajo. Se recomienda aumentar el precio o reducir costos.'
        }
    elif margen_porcentaje < 30:
        return {
            'es_rentable': True,
            'margen_porcentaje': round(margen_porcentaje, 2),
            'ganancia_neta': round(ganancia_neta, 2),
            'recomendacion': 'Margen aceptable pero ajustado. Considerar optimizar costos.'
        }
    else:
        return {
            'es_rentable': True,
            'margen_porcentaje': round(margen_porcentaje, 2),
            'ganancia_neta': round(ganancia_neta, 2),
            'recomendacion': 'Margen saludable. Pedido rentable.'
        }


# ========== FUNCIÓN INTEGRADORA ==========

def analizar_pedido_completo(tipo_trabajo, ancho, alto, cantidad=1, material_disponible=True,
                            requiere_diseño=False, es_urgente=False):
    """
    Función integradora que ejecuta todas las reglas del sistema experto

    Args:
        tipo_trabajo (str): Tipo de servicio
        ancho (float): Ancho en metros
        alto (float): Alto en metros
        cantidad (int): Cantidad de unidades
        material_disponible (bool): Si hay material en stock
        requiere_diseño (bool): Si requiere diseño
        es_urgente (bool): Si es pedido urgente

    Returns:
        dict: Análisis completo con todas las recomendaciones
    """
    # Calcular área
    from app.logic.calculos import calcular_area
    area_m2 = calcular_area(ancho, alto)

    return {
        'maquina': sugerir_maquina(tipo_trabajo, ancho, alto),
        'material': sugerir_material(tipo_trabajo),
        'tiempo': estimar_tiempo_entrega(
            tipo_servicio=tipo_trabajo,
            area_m2=area_m2,
            cantidad=cantidad,
            material_en_stock=material_disponible,
            requiere_diseño=requiere_diseño,
            es_urgente=es_urgente
        ),
        'validacion_metraje': validar_metraje(ancho, alto, tipo_trabajo),
        'acabados': sugerir_acabado(tipo_trabajo)
    }

