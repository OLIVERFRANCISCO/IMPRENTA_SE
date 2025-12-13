"""
Script de Migración - Fase 5
Actualiza el esquema de la base de datos con las columnas agregadas en Fases 1-5

Ejecutar: python migrar_fase_5.py
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "base_de_imprenta.db"

def migrar_base_datos():
    """Aplica las migraciones necesarias para Fases 1-5"""
    
    if not DB_PATH.exists():
        print("❌ No se encontró la base de datos. Ejecuta main.py primero.")
        return False
    
    print("🔄 Iniciando migración de base de datos...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Lista de columnas a agregar
        migraciones = [
            # FASE 1: Columnas de materiales
            {
                'tabla': 'materiales',
                'columna': 'tipo_material',
                'tipo': 'VARCHAR DEFAULT "unidad"',
                'descripcion': 'Tipo de material (unidad/dimension)'
            },
            {
                'tabla': 'materiales',
                'columna': 'sugerencia',
                'tipo': 'TEXT DEFAULT ""',
                'descripcion': 'Sugerencia de uso del material'
            },
            {
                'tabla': 'materiales',
                'columna': 'ancho_bobina',
                'tipo': 'REAL DEFAULT 0.0',
                'descripcion': 'Ancho de bobina en metros'
            },
            {
                'tabla': 'materiales',
                'columna': 'dimension_minima',
                'tipo': 'REAL DEFAULT 0.0',
                'descripcion': 'Dimensión mínima vendible'
            },
            {
                'tabla': 'materiales',
                'columna': 'dimension_disponible',
                'tipo': 'REAL DEFAULT 0.0',
                'descripcion': 'Dimensión total disponible'
            },
            
            # FASE 3: Columna de máquinas
            {
                'tabla': 'maquinas',
                'columna': 'sugerencia',
                'tipo': 'TEXT DEFAULT ""',
                'descripcion': 'Sugerencia de uso de la máquina'
            }
        ]
        
        cambios_realizados = 0
        
        for migracion in migraciones:
            tabla = migracion['tabla']
            columna = migracion['columna']
            tipo = migracion['tipo']
            descripcion = migracion['descripcion']
            
            # Verificar si la columna ya existe
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas_existentes = [col[1] for col in cursor.fetchall()]
            
            if columna not in columnas_existentes:
                print(f"  ➕ Agregando columna '{columna}' a tabla '{tabla}'")
                print(f"     Descripción: {descripcion}")
                
                try:
                    cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
                    cambios_realizados += 1
                    print(f"     ✅ Columna agregada exitosamente")
                except sqlite3.Error as e:
                    print(f"     ⚠️ Error al agregar columna: {e}")
            else:
                print(f"  ✓ Columna '{columna}' ya existe en '{tabla}'")
        
        # Verificar y crear tablas de relación si no existen
        
        # Tabla servicios_materiales (Fase 2)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='servicios_materiales'
        """)
        if not cursor.fetchone():
            print("  ➕ Creando tabla 'servicios_materiales'")
            cursor.execute("""
                CREATE TABLE servicios_materiales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_servicio INTEGER NOT NULL,
                    id_material INTEGER NOT NULL,
                    es_preferido INTEGER DEFAULT 0,
                    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio),
                    FOREIGN KEY (id_material) REFERENCES materiales(id_material),
                    UNIQUE(id_servicio, id_material)
                )
            """)
            cambios_realizados += 1
            print("     ✅ Tabla creada exitosamente")
        else:
            print("  ✓ Tabla 'servicios_materiales' ya existe")
            
            # Verificar si tiene la columna es_preferido
            cursor.execute("PRAGMA table_info(servicios_materiales)")
            columnas_sm = [col[1] for col in cursor.fetchall()]
            
            if 'es_preferido' not in columnas_sm:
                print("  ➕ Agregando columna 'es_preferido' a tabla 'servicios_materiales'")
                cursor.execute("ALTER TABLE servicios_materiales ADD COLUMN es_preferido INTEGER DEFAULT 0")
                cambios_realizados += 1
                print("     ✅ Columna agregada exitosamente")
            else:
                print("  ✓ Columna 'es_preferido' ya existe en 'servicios_materiales'")
        
        # Tabla maquinas_servicios (Fase 3)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='maquinas_servicios'
        """)
        if not cursor.fetchone():
            print("  ➕ Creando tabla 'maquinas_servicios'")
            cursor.execute("""
                CREATE TABLE maquinas_servicios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_maquina INTEGER NOT NULL,
                    id_servicio INTEGER NOT NULL,
                    es_recomendada INTEGER DEFAULT 0,
                    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
                    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio),
                    UNIQUE(id_maquina, id_servicio)
                )
            """)
            cambios_realizados += 1
            print("     ✅ Tabla creada exitosamente")
        else:
            print("  ✓ Tabla 'maquinas_servicios' ya existe")
            
            # Verificar si tiene la columna es_recomendada
            cursor.execute("PRAGMA table_info(maquinas_servicios)")
            columnas_ms = [col[1] for col in cursor.fetchall()]
            
            if 'es_recomendada' not in columnas_ms:
                print("  ➕ Agregando columna 'es_recomendada' a tabla 'maquinas_servicios'")
                cursor.execute("ALTER TABLE maquinas_servicios ADD COLUMN es_recomendada INTEGER DEFAULT 0")
                cambios_realizados += 1
                print("     ✅ Columna agregada exitosamente")
            else:
                print("  ✓ Columna 'es_recomendada' ya existe en 'maquinas_servicios'")
        
        conn.commit()
        conn.close()
        
        if cambios_realizados > 0:
            print(f"\n✅ Migración completada: {cambios_realizados} cambio(s) aplicado(s)")
        else:
            print("\n✅ Base de datos ya está actualizada")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN DE BASE DE DATOS - FASES 1-5")
    print("=" * 60)
    print()
    
    exito = migrar_base_datos()
    
    if exito:
        print("\n🎉 Migración exitosa. Ahora puedes ejecutar: python main.py")
    else:
        print("\n⚠️ Migración falló. Revisa los errores arriba.")
    
    print()
    input("Presiona Enter para salir...")
