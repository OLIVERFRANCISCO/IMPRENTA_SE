"""
Motor de Inferencia del Sistema Experto para Imprenta
======================================================
Este módulo implementa la lógica de razonamiento que consulta
la Base de Conocimientos (BD normalizada) para hacer recomendaciones.

DIFERENCIA CON EL ARCHIVO ANTERIOR (reglas_experto.py):
- Antes: if "gigantografia" in tipo → return "Plotter" (HARDCODEADO)
- Ahora: Consulta la BD para saber qué máquinas pueden manejar el ancho X

REGLAS IMPLEMENTADAS (Dinámicas):
1. REGLA-MAQ: Recomendar máquina según dimensiones y servicio
2. REGLA-MAT: Recomendar materiales según servicio y stock
3. REGLA-VAL: Validar si el trabajo cabe en las máquinas disponibles
4. REGLA-TMP: Estimar tiempo según capacidades de máquina
"""
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app.database.conexion import get_session


# =========================================================
# FUNCIONES DE CONSULTA A LA BASE DE CONOCIMIENTOS
# =========================================================

def obtener_maquinas_capaces(ancho_requerido, largo_requerido=0):
    """
    Consulta la BD para obtener máquinas que pueden manejar las dimensiones.
    
    INFERENCIA: Si ancho_requerido > ancho_util_max → Máquina NO puede
    
    Args:
        ancho_requerido (float): Ancho del trabajo en metros
        largo_requerido (float): Largo del trabajo (0 si no importa)
    
    Returns:
        list: Máquinas capaces ordenadas por capacidad
    """
    session = get_session()
    try:
        query = """
            SELECT 
                m.id_maquina,
                m.nombre,
                tm.nombre_tipo as tipo,
                cm.ancho_util_max,
                cm.largo_util_max,
                cm.velocidad_promedio,
                m.sugerencia
            FROM maquinas m
            JOIN tipos_maquinas tm ON m.id_tipo_maquina = tm.id_tipo_maquina
            LEFT JOIN capacidad_maquinas cm ON m.id_maquina = cm.id_maquina
            WHERE cm.ancho_util_max >= :ancho
        """
        
        params = {'ancho': ancho_requerido}
        
        # Si hay largo requerido y la máquina tiene límite de largo
        if largo_requerido > 0:
            query += " AND (cm.largo_util_max = 0 OR cm.largo_util_max >= :largo)"
            params['largo'] = largo_requerido
        
        query += " ORDER BY cm.ancho_util_max ASC"
        
        from sqlalchemy import text
        result = session.execute(text(query), params).fetchall()
        
        maquinas = []
        for row in result:
            maquinas.append({
                'id_maquina': row[0],
                'nombre': row[1],
                'tipo': row[2],
                'ancho_max': row[3],
                'largo_max': row[4],
                'velocidad': row[5],
                'sugerencia': row[6] or ''
            })
        
        return maquinas
    finally:
        session.close()


def obtener_maquinas_por_servicio(id_servicio, ancho_requerido=0):
    """
    Obtiene máquinas compatibles con un servicio específico.
    Prioriza las marcadas como 'recomendadas'.
    
    Args:
        id_servicio: ID del servicio
        ancho_requerido: Filtra por capacidad física
    
    Returns:
        list: Máquinas ordenadas por prioridad
    """
    session = get_session()
    try:
        from sqlalchemy import text
        
        query = """
            SELECT 
                m.id_maquina,
                m.nombre,
                tm.nombre_tipo as tipo,
                ms.es_recomendada,
                cm.ancho_util_max,
                cm.velocidad_promedio,
                m.sugerencia
            FROM maquinas m
            JOIN tipos_maquinas tm ON m.id_tipo_maquina = tm.id_tipo_maquina
            JOIN maquinas_servicios ms ON m.id_maquina = ms.id_maquina
            LEFT JOIN capacidad_maquinas cm ON m.id_maquina = cm.id_maquina
            WHERE ms.id_servicio = :id_servicio
        """
        
        params = {'id_servicio': id_servicio}
        
        if ancho_requerido > 0:
            query += " AND (cm.ancho_util_max IS NULL OR cm.ancho_util_max >= :ancho)"
            params['ancho'] = ancho_requerido
        
        query += " ORDER BY ms.es_recomendada DESC, cm.ancho_util_max ASC"
        
        result = session.execute(text(query), params).fetchall()
        
        maquinas = []
        for row in result:
            maquinas.append({
                'id_maquina': row[0],
                'nombre': row[1],
                'tipo': row[2],
                'es_recomendada': bool(row[3]),
                'ancho_max': row[4],
                'velocidad': row[5],
                'sugerencia': row[6] or ''
            })
        
        return maquinas
    finally:
        session.close()


def obtener_materiales_por_servicio(id_servicio, solo_con_stock=False):
    """
    Obtiene materiales válidos para un servicio.
    
    Args:
        id_servicio: ID del servicio
        solo_con_stock: Si es True, solo materiales disponibles
    
    Returns:
        list: Materiales ordenados por preferencia
    """
    session = get_session()
    try:
        from sqlalchemy import text
        
        query = """
            SELECT 
                mat.id_material,
                mat.nombre_material,
                tm.nombre_tipo as tipo,
                sm.es_preferido,
                inv.cantidad_stock,
                inv.stock_minimo,
                mat.sugerencia,
                um.abreviacion as unidad
            FROM materiales mat
            JOIN tipos_materiales tm ON mat.id_tipo_material = tm.id_tipo_material
            JOIN servicios_materiales sm ON mat.id_material = sm.id_material
            LEFT JOIN inventario_materiales inv ON mat.id_material = inv.id_material
            LEFT JOIN unidades_medida um ON mat.id_unidad_inventario = um.id_unidad
            WHERE sm.id_servicio = :id_servicio
        """
        
        params = {'id_servicio': id_servicio}
        
        if solo_con_stock:
            query += " AND (inv.cantidad_stock IS NULL OR inv.cantidad_stock > 0)"
        
        query += " ORDER BY sm.es_preferido DESC, mat.nombre_material ASC"
        
        result = session.execute(text(query), params).fetchall()
        
        materiales = []
        for row in result:
            stock_actual = row[4] or 0
            stock_min = row[5] or 5
            
            # Generar alertas de stock
            alerta = None
            if stock_actual <= 0:
                alerta = "🔴 SIN STOCK"
            elif stock_actual <= stock_min:
                alerta = "⚠️ Stock bajo"
            
            materiales.append({
                'id_material': row[0],
                'nombre': row[1],
                'tipo': row[2],
                'es_preferido': bool(row[3]),
                'stock': stock_actual,
                'stock_minimo': stock_min,
                'sugerencia': row[6] or '',
                'unidad': row[7] or '',
                'alerta_stock': alerta
            })
        
        return materiales
    finally:
        session.close()


def obtener_rollos_compatibles(ancho_trabajo):
    """
    Obtiene rollos de material que pueden contener el ancho del trabajo.
    
    INFERENCIA: ancho_fijo_rollo >= ancho_trabajo
    
    Args:
        ancho_trabajo: Ancho requerido en metros
    
    Returns:
        list: Rollos compatibles con desperdicio calculado
    """
    session = get_session()
    try:
        from sqlalchemy import text
        
        query = """
            SELECT 
                mat.id_material,
                mat.nombre_material,
                ari.ancho_fijo_rollo,
                inv.cantidad_stock,
                (ari.ancho_fijo_rollo - :ancho) as desperdicio
            FROM materiales mat
            JOIN atributos_rollos_impresion ari ON mat.id_material = ari.id_material
            LEFT JOIN inventario_materiales inv ON mat.id_material = inv.id_material
            WHERE ari.ancho_fijo_rollo >= :ancho
            ORDER BY desperdicio ASC
        """
        
        result = session.execute(text(query), {'ancho': ancho_trabajo}).fetchall()
        
        rollos = []
        for row in result:
            rollos.append({
                'id_material': row[0],
                'nombre': row[1],
                'ancho_rollo': row[2],
                'stock': row[3] or 0,
                'desperdicio_metros': row[4],
                'eficiencia': round((ancho_trabajo / row[2]) * 100, 1) if row[2] > 0 else 0
            })
        
        return rollos
    finally:
        session.close()


# =========================================================
# MOTOR DE INFERENCIA PRINCIPAL
# =========================================================

def sugerir_maquina_experto(ancho, alto, id_servicio=None):
    """
    REGLA DINÁMICA: Recomendar máquina basándose en la BD.
    
    Proceso de Inferencia:
    1. Si hay servicio → Buscar máquinas asociadas al servicio
    2. Filtrar por capacidad física (ancho/largo)
    3. Ordenar por: recomendadas > menor capacidad suficiente
    4. Si no hay datos → Fallback a búsqueda por capacidad general
    
    Args:
        ancho (float): Ancho del trabajo en metros
        alto (float): Alto del trabajo en metros
        id_servicio (int): ID del servicio (opcional)
    
    Returns:
        dict: {
            'maquina_recomendada': str,
            'id_maquina': int,
            'explicacion': str,
            'alternativas': list,
            'origen': str  # 'bd_servicio', 'bd_capacidad', 'sin_datos'
        }
    """
    resultado = {
        'maquina_recomendada': None,
        'id_maquina': None,
        'explicacion': '',
        'alternativas': [],
        'origen': 'sin_datos',
        'advertencias': []
    }
    
    # PASO 1: Intentar por servicio si existe
    if id_servicio:
        maquinas = obtener_maquinas_por_servicio(id_servicio, ancho)
        
        if maquinas:
            # Primera máquina es la recomendada (ordenada por preferencia)
            mejor = maquinas[0]
            resultado['maquina_recomendada'] = mejor['nombre']
            resultado['id_maquina'] = mejor['id_maquina']
            resultado['origen'] = 'bd_servicio'
            
            # Construir explicación
            exp_parts = []
            if mejor['es_recomendada']:
                exp_parts.append("⭐ Máquina recomendada para este servicio")
            if mejor['ancho_max']:
                exp_parts.append(f"Capacidad: {mejor['ancho_max']}m de ancho")
            if mejor['sugerencia']:
                exp_parts.append(f"💡 {mejor['sugerencia']}")
            
            resultado['explicacion'] = ". ".join(exp_parts)
            
            # Alternativas
            if len(maquinas) > 1:
                resultado['alternativas'] = [
                    {'nombre': m['nombre'], 'id': m['id_maquina'], 'es_recomendada': m['es_recomendada']}
                    for m in maquinas[1:4]  # Máximo 3 alternativas
                ]
            
            return resultado
    
    # PASO 2: Fallback - Buscar por capacidad física
    maquinas = obtener_maquinas_capaces(ancho, alto)
    
    if maquinas:
        mejor = maquinas[0]  # La de menor capacidad suficiente (más eficiente)
        resultado['maquina_recomendada'] = mejor['nombre']
        resultado['id_maquina'] = mejor['id_maquina']
        resultado['origen'] = 'bd_capacidad'
        
        resultado['explicacion'] = (
            f"Seleccionada por capacidad física: soporta hasta {mejor['ancho_max']}m de ancho. "
            f"El trabajo requiere {ancho}m."
        )
        
        if len(maquinas) > 1:
            resultado['alternativas'] = [
                {'nombre': m['nombre'], 'id': m['id_maquina']}
                for m in maquinas[1:4]
            ]
        
        return resultado
    
    # PASO 3: No hay máquinas capaces
    resultado['explicacion'] = (
        f"⚠️ No se encontró ninguna máquina capaz de manejar {ancho}m de ancho. "
        "Revise las capacidades registradas en el panel de máquinas."
    )
    resultado['advertencias'].append("Ninguna máquina tiene capacidad suficiente")
    
    return resultado


def sugerir_material_experto(id_servicio, ancho_trabajo=0, requiere_stock=True):
    """
    REGLA DINÁMICA: Recomendar material basándose en la BD.
    
    Proceso de Inferencia:
    1. Obtener materiales asociados al servicio
    2. Filtrar por stock si es requerido
    3. Si es material en rollo, verificar ancho compatible
    4. Ordenar por: preferidos > con stock > por nombre
    
    Args:
        id_servicio (int): ID del servicio
        ancho_trabajo (float): Ancho para verificar rollos
        requiere_stock (bool): Solo materiales con stock
    
    Returns:
        dict: {
            'material_recomendado': str,
            'id_material': int,
            'alternativas': list,
            'alertas': list
        }
    """
    resultado = {
        'material_recomendado': None,
        'id_material': None,
        'explicacion': '',
        'alternativas': [],
        'alertas': []
    }
    
    materiales = obtener_materiales_por_servicio(id_servicio, solo_con_stock=requiere_stock)
    
    if not materiales:
        resultado['explicacion'] = (
            "No hay materiales asociados a este servicio. "
            "Configure los materiales válidos en el panel de servicios."
        )
        resultado['alertas'].append("Sin materiales configurados")
        return resultado
    
    # Filtrar rollos por ancho si es necesario
    if ancho_trabajo > 0:
        rollos_compat = obtener_rollos_compatibles(ancho_trabajo)
        ids_rollos_ok = {r['id_material'] for r in rollos_compat}
        
        # Separar materiales tipo rollo
        materiales_filtrados = []
        for mat in materiales:
            # Si es rollo, verificar compatibilidad
            if mat['tipo'] in ('Lona', 'Vinilo', 'Tela'):
                if mat['id_material'] in ids_rollos_ok:
                    materiales_filtrados.append(mat)
                else:
                    resultado['alertas'].append(
                        f"'{mat['nombre']}' descartado: rollo muy angosto para {ancho_trabajo}m"
                    )
            else:
                materiales_filtrados.append(mat)
        
        materiales = materiales_filtrados
    
    if not materiales:
        resultado['explicacion'] = "No hay materiales compatibles con las dimensiones requeridas."
        return resultado
    
    # Recopilar alertas de stock
    for mat in materiales:
        if mat['alerta_stock']:
            resultado['alertas'].append(f"{mat['nombre']}: {mat['alerta_stock']}")
    
    # Primer material es el recomendado
    mejor = materiales[0]
    resultado['material_recomendado'] = mejor['nombre']
    resultado['id_material'] = mejor['id_material']
    
    exp_parts = []
    if mejor['es_preferido']:
        exp_parts.append("⭐ Material preferido para este servicio")
    if mejor['sugerencia']:
        exp_parts.append(f"💡 {mejor['sugerencia']}")
    exp_parts.append(f"Stock actual: {mejor['stock']} {mejor['unidad']}")
    
    resultado['explicacion'] = ". ".join(exp_parts)
    
    if len(materiales) > 1:
        resultado['alternativas'] = [
            {
                'nombre': m['nombre'],
                'id': m['id_material'],
                'es_preferido': m['es_preferido'],
                'stock': m['stock']
            }
            for m in materiales[1:5]
        ]
    
    return resultado


def validar_trabajo_experto(ancho, alto, id_servicio=None):
    """
    REGLA DE VALIDACIÓN: Verifica si el trabajo es factible.
    
    Consulta la BD para verificar:
    1. ¿Existe alguna máquina capaz?
    2. ¿Hay materiales disponibles?
    3. ¿Las dimensiones son lógicas?
    
    Returns:
        dict: {
            'es_factible': bool,
            'errores': list,
            'advertencias': list
        }
    """
    errores = []
    advertencias = []
    
    # Validación básica
    if ancho <= 0 or alto <= 0:
        errores.append("Las dimensiones deben ser mayores a cero")
    
    if ancho > 5:
        advertencias.append(f"Ancho inusualmente grande: {ancho}m. ¿Está en metros?")
    
    if alto > 50:
        advertencias.append(f"Largo muy extenso: {alto}m. Verificar si es correcto.")
    
    # Consultar BD para máquinas
    maquinas = obtener_maquinas_capaces(ancho, alto)
    if not maquinas:
        errores.append(
            f"No hay máquinas registradas que soporten {ancho}m de ancho. "
            "Máximo disponible: revisar capacidad_maquinas."
        )
    
    # Si hay servicio, verificar materiales
    if id_servicio:
        materiales = obtener_materiales_por_servicio(id_servicio, solo_con_stock=True)
        if not materiales:
            advertencias.append("No hay materiales con stock para este servicio")
    
    return {
        'es_factible': len(errores) == 0,
        'errores': errores,
        'advertencias': advertencias
    }


def estimar_tiempo_experto(id_maquina, area_m2, cantidad=1):
    """
    REGLA DE TIEMPO: Estima duración basándose en velocidad de máquina.
    
    Args:
        id_maquina: ID de la máquina seleccionada
        area_m2: Área total a producir
        cantidad: Número de unidades
    
    Returns:
        dict: {'horas_estimadas': float, 'explicacion': str}
    """
    session = get_session()
    try:
        from sqlalchemy import text
        
        query = """
            SELECT m.nombre, cm.velocidad_promedio
            FROM maquinas m
            LEFT JOIN capacidad_maquinas cm ON m.id_maquina = cm.id_maquina
            WHERE m.id_maquina = :id_maq
        """
        
        result = session.execute(text(query), {'id_maq': id_maquina}).fetchone()
        
        if not result:
            return {
                'horas_estimadas': 2.0,
                'explicacion': "Máquina no encontrada. Tiempo estimado por defecto."
            }
        
        nombre, velocidad = result[0], result[1] or 10  # 10 unidades/hora por defecto
        
        # Calcular tiempo
        if area_m2 > 0:
            horas = (area_m2 * cantidad) / velocidad
        else:
            horas = cantidad / velocidad
        
        horas = max(0.5, round(horas, 1))  # Mínimo 30 minutos
        
        return {
            'horas_estimadas': horas,
            'explicacion': f"Máquina '{nombre}' a {velocidad} unidades/hora → {horas}h estimadas"
        }
    finally:
        session.close()


# =========================================================
# FUNCIÓN INTEGRADORA
# =========================================================

def analizar_pedido_experto(id_servicio, ancho, alto, cantidad=1):
    """
    Análisis completo de un pedido usando el Sistema Experto.
    
    Ejecuta todas las reglas de inferencia y consolida resultados.
    
    Args:
        id_servicio: ID del servicio solicitado
        ancho: Ancho del trabajo en metros
        alto: Alto del trabajo en metros
        cantidad: Número de unidades
    
    Returns:
        dict: Análisis completo con recomendaciones
    """
    area = ancho * alto
    
    # 1. Validar factibilidad
    validacion = validar_trabajo_experto(ancho, alto, id_servicio)
    
    # 2. Recomendar máquina
    rec_maquina = sugerir_maquina_experto(ancho, alto, id_servicio)
    
    # 3. Recomendar material
    rec_material = sugerir_material_experto(id_servicio, ancho)
    
    # 4. Estimar tiempo
    tiempo = {'horas_estimadas': 2.0, 'explicacion': 'Tiempo base'}
    if rec_maquina['id_maquina']:
        tiempo = estimar_tiempo_experto(rec_maquina['id_maquina'], area, cantidad)
    
    # Consolidar alertas
    todas_alertas = []
    todas_alertas.extend(validacion.get('advertencias', []))
    todas_alertas.extend(rec_maquina.get('advertencias', []))
    todas_alertas.extend(rec_material.get('alertas', []))
    
    return {
        'es_factible': validacion['es_factible'],
        'errores': validacion['errores'],
        'alertas': todas_alertas,
        'recomendacion_maquina': {
            'nombre': rec_maquina['maquina_recomendada'],
            'id': rec_maquina['id_maquina'],
            'explicacion': rec_maquina['explicacion'],
            'alternativas': rec_maquina['alternativas'],
            'origen_inferencia': rec_maquina['origen']
        },
        'recomendacion_material': {
            'nombre': rec_material['material_recomendado'],
            'id': rec_material['id_material'],
            'explicacion': rec_material['explicacion'],
            'alternativas': rec_material['alternativas']
        },
        'tiempo_estimado': tiempo,
        'resumen': {
            'area_m2': round(area, 2),
            'cantidad': cantidad,
            'maquina': rec_maquina['maquina_recomendada'] or 'No disponible',
            'material': rec_material['material_recomendado'] or 'No disponible'
        }
    }
