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


def calcular_precio_sugerido(nombre_servicio, cantidad, id_servicio=None):
    """
    Calcula el precio unitario sugerido según reglas de negocio almacenadas en BD.

    El sistema consulta la tabla 'precios_escalonados' para determinar el precio
    basado en la cantidad. Las reglas son configurables desde el panel de admin.

    Args:
        nombre_servicio (str): Nombre del servicio/producto (para compatibilidad)
        cantidad (int): Cantidad de unidades
        id_servicio (int): ID del servicio (opcional, mejora precisión)

    Returns:
        float or None: Precio unitario sugerido o None si no hay regla configurada
    """
    from app.database import consultas
    
    # Si tenemos el ID del servicio, buscar directamente
    if id_servicio:
        precio = consultas.obtener_precio_por_cantidad(id_servicio, cantidad)
        if precio:
            return precio
    
    # Fallback: buscar servicio por nombre
    servicios = consultas.obtener_servicios()
    for servicio in servicios:
        if nombre_servicio.lower() in servicio['nombre_servicio'].lower():
            precio = consultas.obtener_precio_por_cantidad(servicio['id_servicio'], cantidad)
            if precio:
                return precio
    
    # No hay regla configurada
    return None


def validar_restricciones_cantidad(nombre_servicio, cantidad, id_servicio=None):
    """
    Valida restricciones de cantidad según reglas almacenadas en BD.

    El sistema consulta la tabla 'restricciones_cantidad' para validar si la
    cantidad es permitida. Las reglas son configurables desde el panel de admin.

    Tipos de restricción soportados:
    - 'lista': Valores específicos permitidos (ej: 25, 50, 100)
    - 'multiplo': Solo múltiplos de un número (ej: múltiplos de 100)
    - 'rango': Entre un mínimo y máximo

    Args:
        nombre_servicio (str): Nombre del servicio/producto (para compatibilidad)
        cantidad (int): Cantidad a validar
        id_servicio (int): ID del servicio (opcional, mejora precisión)

    Returns:
        tuple: (es_valido: bool, mensaje: str, cantidad_sugerida: int)
    """
    from app.database import consultas
    
    # Si tenemos el ID del servicio, validar directamente
    if id_servicio:
        return consultas.validar_cantidad_servicio(id_servicio, cantidad)
    
    # Fallback: buscar servicio por nombre
    servicios = consultas.obtener_servicios()
    for servicio in servicios:
        if nombre_servicio.lower() in servicio['nombre_servicio'].lower():
            return consultas.validar_cantidad_servicio(servicio['id_servicio'], cantidad)
    
    # Sin restricciones configuradas, cualquier cantidad es válida
    return True, "Cantidad válida", cantidad


def validar_optimizacion_impresion(ancho, alto=0, nombre_servicio=None, ancho_maximo_maquina=None, id_maquina=None, id_servicio=None):
    """
    Valida y sugiere optimización para trabajos de impresión de gran formato.
    
    SISTEMA EXPERTO - REGLA DE OPTIMIZACIÓN DIMENSIONAL:
    Consulta la Base de Conocimientos (BD) para obtener las capacidades reales
    de las máquinas y generar sugerencias inteligentes.
    
    Esta función es GENÉRICA y aplica a cualquier servicio dimensional,
    no solo gigantografías.

    Reglas de Negocio Implementadas:
    - R-OPT-01: Si ancho > ancho_max_maquina → Sugerir división o rotación
    - R-OPT-02: Si alto > largo_max_maquina (cuando no es rollo) → Alertar límite
    - R-OPT-03: Considerar márgenes técnicos (5cm típico)
    - R-OPT-04: Sugerir rotación solo si es beneficioso (ancho < alto y alto <= ancho_max)

    Args:
        ancho (float): Ancho del pedido en metros
        alto (float): Alto del pedido en metros (opcional)
        nombre_servicio (str): Nombre del servicio (opcional, para logging)
        ancho_maximo_maquina (float): Ancho máximo override (opcional)
        id_maquina (int): ID de la máquina para consultar capacidad (opcional)
        id_servicio (int): ID del servicio para buscar máquinas compatibles (opcional)

    Returns:
        dict: {
            'requiere_optimizacion': bool,
            'es_factible': bool,
            'mensaje': str,
            'sugerencias': list,
            'capacidad_maquina': dict,  # Info de la máquina consultada
            'puede_rotar': bool,
            'division_sugerida': int  # Número de paños si aplica
        }
    """
    resultado = {
        'requiere_optimizacion': False,
        'es_factible': True,
        'mensaje': '',
        'sugerencias': [],
        'capacidad_maquina': None,
        'puede_rotar': False,
        'division_sugerida': 0
    }
    
    # Margen técnico para impresión (5cm = 0.05m por cada lado)
    MARGEN_TECNICO = 0.05
    ancho_con_margen = ancho + MARGEN_TECNICO
    alto_con_margen = alto + MARGEN_TECNICO if alto > 0 else 0
    
    # --- PASO 1: Obtener capacidad de máquina desde la BD ---
    capacidad = None
    
    # Prioridad 1: ID de máquina específica
    if id_maquina:
        capacidad = _obtener_capacidad_maquina(id_maquina)
    
    # Prioridad 2: Buscar máquina por servicio
    if not capacidad and id_servicio:
        capacidad = _obtener_mejor_capacidad_por_servicio(id_servicio)
    
    # Prioridad 3: Valor proporcionado o default
    if not capacidad:
        capacidad = {
            'id_maquina': None,
            'nombre': 'Máquina genérica',
            'ancho_util_max': ancho_maximo_maquina or 2.5,
            'largo_util_max': 0,  # 0 = rollo infinito
            'velocidad_promedio': 0
        }
    
    resultado['capacidad_maquina'] = capacidad
    ancho_max = capacidad['ancho_util_max']
    largo_max = capacidad['largo_util_max']
    
    # --- PASO 2: Evaluar si el trabajo cabe ---
    
    # Caso 1: El trabajo cabe perfectamente
    if ancho_con_margen <= ancho_max:
        # Verificar largo si la máquina tiene límite (no es rollo continuo)
        if largo_max > 0 and alto_con_margen > largo_max:
            resultado['requiere_optimizacion'] = True
            resultado['es_factible'] = False
            resultado['mensaje'] = (
                f"⚠️ RESTRICCIÓN DE LARGO:\n"
                f"El alto solicitado ({alto}m + margen) excede el largo máximo "
                f"de la máquina '{capacidad['nombre']}' ({largo_max}m).\n"
                f"Esta máquina no usa material en rollo continuo."
            )
            resultado['sugerencias'].append(
                f"Reducir el alto a máximo {largo_max - MARGEN_TECNICO:.2f}m"
            )
        else:
            # Todo OK, no requiere optimización
            resultado['mensaje'] = "✓ Las dimensiones son compatibles con la máquina."
        
        return resultado
    
    # Caso 2: El ancho excede la capacidad
    resultado['requiere_optimizacion'] = True
    
    # --- PASO 3: Evaluar si se puede rotar ---
    # Rotar es viable si: alto <= ancho_max y ancho <= largo_max (o largo es infinito)
    puede_rotar = False
    if alto > 0 and alto_con_margen <= ancho_max:
        if largo_max == 0 or ancho_con_margen <= largo_max:
            puede_rotar = True
            resultado['puede_rotar'] = True
            resultado['sugerencias'].append(
                f"🔄 ROTAR EL DISEÑO: Imprimir a {alto}m de ancho × {ancho}m de largo"
            )
    
    # --- PASO 4: Calcular división en paños ---
    if ancho > 0:
        # Número de paños necesarios (considerando solapamiento de 2cm para unión)
        SOLAPAMIENTO = 0.02
        ancho_util_paño = ancho_max - SOLAPAMIENTO
        num_paños = int((ancho_con_margen / ancho_util_paño) + 0.99)  # Redondear arriba
        resultado['division_sugerida'] = num_paños
        
        if num_paños <= 4:  # Máximo razonable de paños
            resultado['sugerencias'].append(
                f"✂️ DIVIDIR EN {num_paños} PAÑOS: "
                f"Cada paño de ~{ancho_util_paño:.2f}m con {SOLAPAMIENTO*100:.0f}cm de traslape"
            )
        else:
            resultado['sugerencias'].append(
                f"⚠️ Se necesitarían {num_paños} paños, considerar otro método de producción"
            )
    
    # --- PASO 5: Construir mensaje final ---
    if puede_rotar:
        resultado['es_factible'] = True
        resultado['mensaje'] = (
            f"⚠️ OPTIMIZACIÓN RECOMENDADA:\n\n"
            f"El ancho solicitado ({ancho}m) supera la capacidad de la máquina "
            f"'{capacidad['nombre']}' ({ancho_max}m).\n\n"
            f"Sin embargo, el trabajo PUEDE realizarse rotando el diseño."
        )
    elif resultado['division_sugerida'] <= 4:
        resultado['es_factible'] = True
        resultado['mensaje'] = (
            f"⚠️ OPTIMIZACIÓN REQUERIDA:\n\n"
            f"El ancho solicitado ({ancho}m) supera el máximo de la máquina "
            f"'{capacidad['nombre']}' ({ancho_max}m).\n\n"
            f"Se recomienda dividir el diseño en {resultado['division_sugerida']} paños."
        )
    else:
        resultado['es_factible'] = False
        resultado['mensaje'] = (
            f"❌ TRABAJO NO FACTIBLE:\n\n"
            f"El ancho solicitado ({ancho}m) excede significativamente la capacidad "
            f"de '{capacidad['nombre']}' ({ancho_max}m).\n\n"
            f"Consulte con el cliente para ajustar las dimensiones."
        )
    
    # Agregar sugerencia de consultar cliente
    resultado['sugerencias'].append(
        "📞 Consultar con el cliente sobre ajustes en las dimensiones"
    )
    
    return resultado


def _obtener_capacidad_maquina(id_maquina):
    """
    Helper: Obtiene la capacidad de una máquina específica desde la BD.
    
    Args:
        id_maquina (int): ID de la máquina
    
    Returns:
        dict or None: Datos de capacidad
    """
    try:
        from app.database.conexion import get_session
        from app.database.models import Maquina, CapacidadMaquina
        
        session = get_session()
        try:
            capacidad = session.query(CapacidadMaquina).filter(
                CapacidadMaquina.id_maquina == id_maquina
            ).first()
            
            if capacidad:
                maquina = session.query(Maquina).filter(
                    Maquina.id_maquina == id_maquina
                ).first()
                
                return {
                    'id_maquina': id_maquina,
                    'nombre': maquina.nombre if maquina else f'Máquina #{id_maquina}',
                    'ancho_util_max': capacidad.ancho_util_max or 0,
                    'largo_util_max': capacidad.largo_util_max or 0,
                    'velocidad_promedio': capacidad.velocidad_promedio or 0
                }
        finally:
            session.close()
    except Exception:
        pass
    
    return None


def _obtener_mejor_capacidad_por_servicio(id_servicio):
    """
    Helper: Obtiene la capacidad de la mejor máquina para un servicio.
    
    Busca la máquina recomendada o la de mayor capacidad entre las
    asociadas al servicio.
    
    Args:
        id_servicio (int): ID del servicio
    
    Returns:
        dict or None: Datos de capacidad de la mejor máquina
    """
    try:
        from app.database.conexion import get_session
        from sqlalchemy import text
        
        session = get_session()
        try:
            query = """
                SELECT 
                    m.id_maquina,
                    m.nombre,
                    cm.ancho_util_max,
                    cm.largo_util_max,
                    cm.velocidad_promedio,
                    ms.es_recomendada
                FROM maquinas m
                JOIN maquinas_servicios ms ON m.id_maquina = ms.id_maquina
                LEFT JOIN capacidad_maquinas cm ON m.id_maquina = cm.id_maquina
                WHERE ms.id_servicio = :id_servicio
                ORDER BY ms.es_recomendada DESC, cm.ancho_util_max DESC
                LIMIT 1
            """
            
            result = session.execute(text(query), {'id_servicio': id_servicio}).fetchone()
            
            if result:
                return {
                    'id_maquina': result[0],
                    'nombre': result[1],
                    'ancho_util_max': result[2] or 0,
                    'largo_util_max': result[3] or 0,
                    'velocidad_promedio': result[4] or 0
                }
        finally:
            session.close()
    except Exception:
        pass
    
    return None


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



