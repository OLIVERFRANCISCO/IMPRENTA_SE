"""
Script de prueba rápida del sistema
Verifica que todos los módulos se importen correctamente
"""

print("=== Iniciando prueba del sistema ===\n")

# Test 1: Imports básicos
print("1. Probando imports básicos...")
try:
    import sys
    import os
    print("   ✓ sys, os")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Config
print("\n2. Probando módulo config...")
try:
    from app.config import COLOR_PRIMARY, DB_PATH, ESTADOS_PEDIDO
    print(f"   ✓ config cargado")
    print(f"   - COLOR_PRIMARY: {COLOR_PRIMARY}")
    print(f"   - DB_PATH: {DB_PATH}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Database
print("\n3. Probando conexión a base de datos...")
try:
    from app.database.conexion import DatabaseConnection
    db = DatabaseConnection()
    conn = db.get_connection()
    print("   ✓ Base de datos inicializada")

    # Contar registros
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clientes")
    print(f"   - Clientes: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM materiales")
    print(f"   - Materiales: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM servicios")
    print(f"   - Servicios: {cursor.fetchone()[0]}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Lógica
print("\n4. Probando módulos de lógica...")
try:
    from app.logic.calculos import calcular_area, calcular_costo_total
    from app.logic.reglas_experto import sugerir_maquina, analizar_pedido_completo

    area = calcular_area(2.0, 1.5)
    print(f"   ✓ calcular_area(2.0, 1.5) = {area} m²")

    resultado = sugerir_maquina("Gigantografía", 1.0, 2.0)
    print(f"   ✓ sugerir_maquina: {resultado['maquina_recomendada']}")

except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: CustomTkinter
print("\n5. Probando CustomTkinter...")
try:
    import customtkinter as ctk
    print(f"   ✓ CustomTkinter versión: {ctk.__version__}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 6: Tkinter
print("\n6. Probando Tkinter...")
try:
    import tkinter as tk
    print(f"   ✓ Tkinter versión: {tk.TkVersion}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    print("   ⚠️ Problema con Tkinter - La interfaz gráfica no funcionará")

print("\n=== Prueba completada ===")
print("\nSi todos los tests pasaron, el sistema está listo.")
print("Si hay error en Tkinter, es un problema del entorno virtual de Python.")

input("\nPresione Enter para salir...")

