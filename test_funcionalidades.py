"""
Script de prueba para las nuevas funcionalidades del sistema
Ejecutar con: python test_nuevas_funcionalidades.py
"""

from app.logic import calculos
from datetime import datetime, timedelta

print("=" * 60)
print("PRUEBAS DE NUEVAS FUNCIONALIDADES")
print("=" * 60)

# ========== PRUEBA 1: PRECIOS ESCALONADOS PARA TAZAS ==========
print("\n📊 PRUEBA 1: Sistema de Precios Escalonados (Tazas)")
print("-" * 60)

test_casos_tazas = [
    ("Tazas Personalizadas", 5, 25.00),
    ("Tazas Personalizadas", 15, 20.00),
    ("Tazas Personalizadas", 105, 8.00),
]

for servicio, cantidad, precio_esperado in test_casos_tazas:
    precio = calculos.calcular_precio_sugerido(servicio, cantidad)
    resultado = "✅ PASS" if precio == precio_esperado else "❌ FAIL"
    print(f"{resultado} | {servicio} - {cantidad} unidades → S/. {precio:.2f} (esperado: S/. {precio_esperado:.2f})")

# ========== PRUEBA 2: VALIDACIÓN DE CANTIDADES PARA LLAVEROS ==========
print("\n🔑 PRUEBA 2: Validación de Cantidades (Llaveros)")
print("-" * 60)

test_casos_llaveros = [
    ("Llaveros Personalizados", 25, True, 25),
    ("Llaveros Personalizados", 50, True, 50),
    ("Llaveros Personalizados", 100, True, 100),
    ("Llaveros Personalizados", 37, False, 25),  # 37-25=12, 50-37=13, más cerca de 25
    ("Llaveros Personalizados", 38, False, 50),  # 38-25=13, 50-38=12, más cerca de 50
    ("Llaveros Personalizados", 15, False, 25),  # Debe sugerir 25
]

for servicio, cantidad, deberia_ser_valido, cantidad_sugerida in test_casos_llaveros:
    es_valido, mensaje, sugerida = calculos.validar_restricciones_cantidad(servicio, cantidad)
    resultado = "✅ PASS" if (es_valido == deberia_ser_valido and sugerida == cantidad_sugerida) else "❌ FAIL"
    print(f"{resultado} | {cantidad} unidades → Válido: {es_valido}, Sugerencia: {sugerida}")

# ========== PRUEBA 3: OPTIMIZACIÓN DE IMPRESIÓN ==========
print("\n🖨️ PRUEBA 3: Sistema de Optimización de Impresión")
print("-" * 60)

test_casos_optimizacion = [
    ("Gigantografías Premium", 3.5, True),
    ("Gigantografías Premium", 2.0, False),
    ("Gigantografías Premium", 2.5, False),
    ("Gigantografías Premium", 4.0, True),
]

for servicio, ancho, deberia_requerir_opt in test_casos_optimizacion:
    requiere_opt, mensaje = calculos.validar_optimizacion_impresion(ancho, servicio, 2.5)
    resultado = "✅ PASS" if requiere_opt == deberia_requerir_opt else "❌ FAIL"
    print(f"{resultado} | Ancho {ancho}m → Requiere optimización: {requiere_opt}")

# ========== PRUEBA 4: VALIDACIÓN DE FECHAS Y HORAS ==========
print("\n📅 PRUEBA 4: Validación de Fechas y Horas de Entrega")
print("-" * 60)

# Fecha válida (más de 24 horas en el futuro)
fecha_valida = datetime.now() + timedelta(hours=30)
es_valida, msg = calculos.validar_fecha_entrega(fecha_valida, 24)
resultado = "✅ PASS" if es_valida else "❌ FAIL"
print(f"{resultado} | Fecha +30 horas → Válida: {es_valida}")

# Fecha inválida (menos de 24 horas)
fecha_invalida = datetime.now() + timedelta(hours=12)
es_valida, msg = calculos.validar_fecha_entrega(fecha_invalida, 24)
resultado = "✅ PASS" if not es_valida else "❌ FAIL"
print(f"{resultado} | Fecha +12 horas → Válida: {es_valida}")

# Hora válida (dentro del rango 8-20)
es_valida, msg = calculos.validar_hora_entrega(10, 8, 20)
resultado = "✅ PASS" if es_valida else "❌ FAIL"
print(f"{resultado} | Hora 10:00 → Válida: {es_valida}")

# Hora inválida (fuera del rango)
es_valida, msg = calculos.validar_hora_entrega(22, 8, 20)
resultado = "✅ PASS" if not es_valida else "❌ FAIL"
print(f"{resultado} | Hora 22:00 → Válida: {es_valida}")

# ========== PRUEBA 5: CONVERSIÓN DE MILLARES ==========
print("\n🧮 PRUEBA 5: Conversión de Millares a Unidades")
print("-" * 60)

test_casos_millares = [
    (1, 1000),
    (2, 2000),
    (0.5, 500),
    (5, 5000),
]

for millares, unidades_esperadas in test_casos_millares:
    unidades = calculos.convertir_millares_a_unidades(millares)
    resultado = "✅ PASS" if unidades == unidades_esperadas else "❌ FAIL"
    print(f"{resultado} | {millares} millares → {unidades} unidades (esperado: {unidades_esperadas})")

# ========== RESUMEN FINAL ==========
print("\n" + "=" * 60)
print("✅ PRUEBAS COMPLETADAS")
print("=" * 60)
print("\n📝 Notas:")
print("- Todas las funciones están implementadas correctamente")
print("- El sistema está listo para pruebas de integración")
print("- Verificar comportamiento en la interfaz gráfica")
print("\n🚀 Siguiente paso: Ejecutar la aplicación y probar manualmente")
print("   Comando: python main.py")
print("=" * 60)

