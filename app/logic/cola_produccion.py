"""
Módulo de Gestión de Cola de Producción
Maneja la planificación de trabajos y cálculo de fechas de entrega
"""
from datetime import datetime, timedelta
from app.database.consultas import obtener_pedidos


def estimar_tiempo_produccion_por_tipo(tipo_servicio, area_m2=0, cantidad=1):
    """
    Estima el tiempo de producción en horas según el tipo de servicio

    Args:
        tipo_servicio (str): Tipo de servicio a realizar
        area_m2 (float): Área en metros cuadrados
        cantidad (int): Cantidad de unidades

    Returns:
        float: Horas estimadas de producción
    """
    tipo = tipo_servicio.upper()

    # Tiempos base por tipo de trabajo (horas)
    tiempos_base = {
        'MERCHANDISING': 2.0,
        'RECUERDOS': 1.5,
        'FORMATOS': 3.0,
        'FORMATERIA': 3.0,
        'GIGANTOGRAFIA': 4.0,
        'GIGANTOGRAFÍA': 4.0
    }

    # Obtener tiempo base, si no existe usar 2.0 horas por defecto
    tiempo_base = tiempos_base.get(tipo, 2.0)

    # Calcular tiempo según cantidad y área
    if area_m2 > 0:
        # Para trabajos con área, agregar tiempo proporcional al área
        tiempo_area = area_m2 * 0.5  # 0.5 horas por metro cuadrado
        tiempo_total = tiempo_base + tiempo_area
    else:
        # Para trabajos sin área específica, usar cantidad
        tiempo_total = tiempo_base * cantidad

    # Mínimo 1 hora
    return max(tiempo_total, 1.0)


def calcular_fecha_entrega_con_cola(horas_requeridas, es_urgente=False):
    """
    Calcula la fecha de entrega considerando la cola de producción actual

    Args:
        horas_requeridas (float): Horas necesarias para el trabajo
        es_urgente (bool): Si es un pedido urgente

    Returns:
        dict: {
            'fecha_entrega': datetime,
            'dias_habiles': int,
            'recargo_porcentaje': float,
            'explicacion': str
        }
    """
    # Obtener carga actual de trabajo
    info_cola = obtener_info_cola_produccion()
    horas_pendientes = info_cola['horas_pendientes']

    # Calcular horas totales
    horas_totales = horas_pendientes + horas_requeridas

    # Configuración de trabajo
    HORAS_LABORALES_POR_DIA = 8
    DIAS_LABORALES_POR_SEMANA = 6  # Lunes a Sábado

    # Calcular días necesarios
    dias_necesarios = horas_totales / HORAS_LABORALES_POR_DIA

    # Si es urgente, se prioriza (50% más rápido pero con recargo)
    if es_urgente:
        dias_necesarios = dias_necesarios * 0.5
        recargo_porcentaje = 30.0  # 30% de recargo por urgencia
    else:
        recargo_porcentaje = 0.0

    # Redondear hacia arriba
    dias_necesarios = int(dias_necesarios) + 1

    # Calcular fecha de entrega (solo días hábiles)
    fecha_actual = datetime.now()
    dias_agregados = 0
    fecha_entrega = fecha_actual

    while dias_agregados < dias_necesarios:
        fecha_entrega += timedelta(days=1)
        # Saltar domingos (weekday: 0=Lunes, 6=Domingo)
        if fecha_entrega.weekday() != 6:
            dias_agregados += 1

    # Generar explicación
    explicacion_partes = []
    explicacion_partes.append(f"Horas pendientes en cola: {horas_pendientes:.1f}h")
    explicacion_partes.append(f"Horas de este trabajo: {horas_requeridas:.1f}h")
    explicacion_partes.append(f"Total: {horas_totales:.1f}h = {dias_necesarios} días hábiles")

    if es_urgente:
        explicacion_partes.append(f"URGENTE: Prioridad alta con recargo del {recargo_porcentaje:.0f}%")

    explicacion = " | ".join(explicacion_partes)

    return {
        'fecha_entrega': fecha_entrega,
        'dias_habiles': dias_necesarios,
        'recargo_porcentaje': recargo_porcentaje,
        'explicacion': explicacion
    }


def obtener_info_cola_produccion():
    """
    Obtiene información sobre el estado actual de la cola de producción

    Returns:
        dict: {
            'pedidos_en_cola': int,
            'horas_pendientes': float,
            'dias_ocupados': int,
            'estado': str
        }
    """
    try:
        # Obtener pedidos pendientes y en proceso
        pedidos = obtener_pedidos()

        # Función auxiliar para acceder de forma segura a sqlite3.Row
        def get_field(row, field, default=None):
            try:
                return row[field] if row[field] is not None else default
            except (KeyError, IndexError):
                return default

        # Filtrar pedidos que no están entregados o cancelados
        pedidos_activos = [
            p for p in pedidos
            if get_field(p, 'estado_nombre') in ['Cotizado', 'Confirmado', 'En Diseño',
                                                   'Previsualización Enviada', 'En Preparación',
                                                   'Listo para Entrega']
        ]

        # Estimar horas pendientes (aproximación simple)
        # En un sistema real, cada pedido tendría su tiempo estimado guardado
        horas_pendientes = len(pedidos_activos) * 8.0  # Promedio de 8 horas por pedido

        # Calcular días ocupados
        HORAS_LABORALES_POR_DIA = 8
        dias_ocupados = int(horas_pendientes / HORAS_LABORALES_POR_DIA) + 1

        # Determinar estado de la producción
        if dias_ocupados <= 2:
            estado = "Baja carga"
        elif dias_ocupados <= 5:
            estado = "Carga normal"
        elif dias_ocupados <= 10:
            estado = "Alta carga"
        else:
            estado = "Saturado"

        return {
            'pedidos_en_cola': len(pedidos_activos),
            'horas_pendientes': horas_pendientes,
            'dias_ocupados': dias_ocupados,
            'estado': estado
        }

    except Exception as e:
        # Si hay error, devolver valores por defecto
        return {
            'pedidos_en_cola': 0,
            'horas_pendientes': 0.0,
            'dias_ocupados': 0,
            'estado': "Sin información"
        }


def obtener_estadisticas_produccion():
    """
    Obtiene estadísticas generales de producción

    Returns:
        dict: Estadísticas de producción
    """
    try:
        pedidos = obtener_pedidos()

        # Función auxiliar para acceder de forma segura a sqlite3.Row
        def get_field(row, field, default=None):
            try:
                return row[field] if row[field] is not None else default
            except (KeyError, IndexError):
                return default

        total_pedidos = len(pedidos)
        pedidos_completados = len([p for p in pedidos if get_field(p, 'estado_nombre') == 'Entregado'])
        pedidos_pendientes = len([p for p in pedidos if get_field(p, 'estado_nombre') in [
            'Cotizado', 'Confirmado', 'En Diseño', 'Previsualización Enviada',
            'En Preparación', 'Listo para Entrega'
        ]])

        # Calcular tasa de completitud
        if total_pedidos > 0:
            tasa_completitud = (pedidos_completados / total_pedidos) * 100
        else:
            tasa_completitud = 0.0

        return {
            'total_pedidos': total_pedidos,
            'completados': pedidos_completados,
            'pendientes': pedidos_pendientes,
            'tasa_completitud': tasa_completitud
        }

    except Exception as e:
        return {
            'total_pedidos': 0,
            'completados': 0,
            'pendientes': 0,
            'tasa_completitud': 0.0
        }


def priorizar_pedido(id_pedido):
    """
    Marca un pedido como prioritario en la cola

    Args:
        id_pedido (int): ID del pedido a priorizar

    Returns:
        bool: True si se priorizó correctamente
    """
    # Esta función se puede implementar más adelante con una columna de prioridad
    # Por ahora es un placeholder
    return True


def estimar_capacidad_disponible(dias=7):
    """
    Estima la capacidad de producción disponible en los próximos días

    Args:
        dias (int): Número de días a calcular

    Returns:
        dict: Capacidad disponible
    """
    info_cola = obtener_info_cola_produccion()

    HORAS_LABORALES_POR_DIA = 8
    capacidad_total = dias * HORAS_LABORALES_POR_DIA
    horas_ocupadas = min(info_cola['horas_pendientes'], capacidad_total)
    horas_disponibles = capacidad_total - horas_ocupadas

    porcentaje_disponible = (horas_disponibles / capacidad_total) * 100 if capacidad_total > 0 else 0

    return {
        'dias': dias,
        'horas_totales': capacidad_total,
        'horas_ocupadas': horas_ocupadas,
        'horas_disponibles': horas_disponibles,
        'porcentaje_disponible': porcentaje_disponible
    }

