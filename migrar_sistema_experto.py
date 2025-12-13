"""
Script de Migración: Sistema CRUD → Sistema Experto Normalizado
================================================================
Este script migra la base de datos actual a la nueva estructura normalizada (3FN/BCNF).

CAMBIOS PRINCIPALES:
1. Separa definición de material de inventario (Material → Material + InventarioMaterial)
2. Crea tablas de metadatos (UnidadMedida, TipoMaterial, TipoMaquina)
3. Agrega capacidades físicas a máquinas (CapacidadMaquina)
4. Vincula servicios a unidades de medida estándar

EJECUTAR: python migrar_sistema_experto.py
"""
import os
import sys
import shutil
from datetime import datetime

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import DB_PATH


def backup_database():
    """Crea respaldo de la BD antes de migrar"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = DB_PATH.parent / f'backup_pre_migracion_{timestamp}.db'
    
    if os.path.exists(DB_PATH):
        shutil.copy(DB_PATH, backup_path)
        print(f"✅ Backup creado: {backup_path}")
        return True
    return False


def get_engine():
    """Crea engine de SQLAlchemy"""
    return create_engine(f'sqlite:///{DB_PATH}', echo=False)


def migrar_estructura():
    """Migra la estructura de la BD a la nueva versión normalizada"""
    engine = get_engine()
    
    with engine.connect() as conn:
        # ============================================
        # PASO 1: Crear tablas de metadatos
        # ============================================
        print("\n📦 Paso 1: Creando tablas de metadatos...")
        
        # Tabla: unidades_medida
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS unidades_medida (
                id_unidad INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_unidad TEXT UNIQUE NOT NULL,
                abreviacion TEXT NOT NULL,
                tipo TEXT NOT NULL,
                factor_conversion REAL DEFAULT 1.0
            )
        """))
        
        # Insertar unidades básicas
        unidades = [
            ('Metro Cuadrado', 'm²', 'Area', 1.0),
            ('Metro Lineal', 'm', 'Longitud', 1.0),
            ('Unidad', 'u', 'Conteo', 1.0),
            ('Decena', 'dec', 'Conteo', 10.0),
            ('Ciento', 'cto', 'Conteo', 100.0),
            ('Millar', 'mil', 'Conteo', 1000.0),
        ]
        for u in unidades:
            try:
                conn.execute(text("""
                    INSERT OR IGNORE INTO unidades_medida (nombre_unidad, abreviacion, tipo, factor_conversion)
                    VALUES (:nombre, :abrev, :tipo, :factor)
                """), {'nombre': u[0], 'abrev': u[1], 'tipo': u[2], 'factor': u[3]})
            except Exception:
                pass
        
        # Tabla: tipos_materiales
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tipos_materiales (
                id_tipo_material INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_tipo TEXT UNIQUE NOT NULL
            )
        """))
        
        tipos_material = ['Lona', 'Vinilo', 'Papel', 'Cartulina', 'Acrílico', 'MDF', 'PVC', 'Tela', 'Otro']
        for tipo in tipos_material:
            try:
                conn.execute(text("INSERT OR IGNORE INTO tipos_materiales (nombre_tipo) VALUES (:tipo)"), {'tipo': tipo})
            except Exception:
                pass
        
        # Tabla: tipos_maquinas
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tipos_maquinas (
                id_tipo_maquina INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_tipo TEXT UNIQUE NOT NULL
            )
        """))
        
        tipos_maquina = ['Plotter de Impresión', 'Plotter de Corte', 'Impresora Láser', 
                        'Impresora UV', 'Sublimación', 'Grabadora Láser', 'Laminadora', 'Otro']
        for tipo in tipos_maquina:
            try:
                conn.execute(text("INSERT OR IGNORE INTO tipos_maquinas (nombre_tipo) VALUES (:tipo)"), {'tipo': tipo})
            except Exception:
                pass
        
        conn.commit()
        print("   ✓ Tablas de metadatos creadas")
        
        # ============================================
        # PASO 2: Migrar estructura de MAQUINAS
        # ============================================
        print("\n🔧 Paso 2: Normalizando máquinas...")
        
        # Verificar si la columna id_tipo_maquina ya existe
        result = conn.execute(text("PRAGMA table_info(maquinas)")).fetchall()
        columns = [col[1] for col in result]
        
        if 'id_tipo_maquina' not in columns:
            # Agregar columna de FK a tipos_maquinas
            conn.execute(text("ALTER TABLE maquinas ADD COLUMN id_tipo_maquina INTEGER DEFAULT 8"))
            
            # Mapear tipos existentes
            mapeo_tipos = {
                'pequeño formato': 3,  # Impresora Láser
                'gran formato': 1,     # Plotter de Impresión
                'acabado': 7,          # Laminadora
                'pequeño': 3,
                'grande': 1,
            }
            
            # Obtener máquinas existentes y mapear
            maquinas = conn.execute(text("SELECT id_maquina, tipo FROM maquinas")).fetchall()
            for maq in maquinas:
                tipo_lower = (maq[1] or '').lower()
                id_tipo = 8  # Default: Otro
                for key, val in mapeo_tipos.items():
                    if key in tipo_lower:
                        id_tipo = val
                        break
                conn.execute(text("UPDATE maquinas SET id_tipo_maquina = :id_tipo WHERE id_maquina = :id_maq"),
                           {'id_tipo': id_tipo, 'id_maq': maq[0]})
        
        # Crear tabla de capacidades
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS capacidad_maquinas (
                id_capacidad INTEGER PRIMARY KEY AUTOINCREMENT,
                id_maquina INTEGER UNIQUE NOT NULL,
                ancho_util_max REAL DEFAULT 0.0,
                largo_util_max REAL DEFAULT 0.0,
                velocidad_promedio REAL DEFAULT 0.0,
                FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina)
            )
        """))
        
        # Insertar capacidades por defecto basadas en tipo
        maquinas = conn.execute(text("SELECT id_maquina, id_tipo_maquina FROM maquinas")).fetchall()
        for maq in maquinas:
            # Valores por defecto según tipo
            capacidades = {
                1: (1.60, 50.0, 5.0),   # Plotter Impresión: 1.60m ancho
                2: (0.60, 10.0, 10.0),  # Plotter Corte
                3: (0.45, 0.30, 50.0),  # Láser A3: 45cm
                4: (2.50, 1.30, 2.0),   # UV gran formato
                5: (0.33, 0.48, 30.0),  # Sublimación A3
                6: (0.60, 0.40, 5.0),   # Grabadora
                7: (1.60, 100.0, 20.0), # Laminadora
                8: (1.0, 1.0, 10.0),    # Otro
            }
            cap = capacidades.get(maq[1], (1.0, 1.0, 10.0))
            try:
                conn.execute(text("""
                    INSERT OR IGNORE INTO capacidad_maquinas (id_maquina, ancho_util_max, largo_util_max, velocidad_promedio)
                    VALUES (:id_maq, :ancho, :largo, :vel)
                """), {'id_maq': maq[0], 'ancho': cap[0], 'largo': cap[1], 'vel': cap[2]})
            except Exception:
                pass
        
        conn.commit()
        print("   ✓ Máquinas normalizadas con capacidades físicas")
        
        # ============================================
        # PASO 3: Migrar estructura de MATERIALES
        # ============================================
        print("\n📄 Paso 3: Normalizando materiales...")
        
        result = conn.execute(text("PRAGMA table_info(materiales)")).fetchall()
        columns = [col[1] for col in result]
        
        if 'id_tipo_material' not in columns:
            conn.execute(text("ALTER TABLE materiales ADD COLUMN id_tipo_material INTEGER DEFAULT 9"))
            conn.execute(text("ALTER TABLE materiales ADD COLUMN id_unidad_inventario INTEGER DEFAULT 1"))
            
            # Mapear materiales existentes
            mapeo_materiales = {
                'lona': 1, 'vinilo': 2, 'vinil': 2, 'papel': 3, 'cartulina': 4,
                'acrilico': 5, 'acrílico': 5, 'mdf': 6, 'pvc': 7, 'tela': 8
            }
            
            materiales = conn.execute(text("SELECT id_material, nombre_material, tipo_material FROM materiales")).fetchall()
            for mat in materiales:
                nombre_lower = (mat[1] or '').lower()
                tipo_exist = (mat[2] or '').lower()
                id_tipo = 9  # Default: Otro
                
                for key, val in mapeo_materiales.items():
                    if key in nombre_lower or key in tipo_exist:
                        id_tipo = val
                        break
                
                # Determinar unidad de inventario
                id_unidad = 1  # m² por defecto
                if 'unidad' in tipo_exist:
                    id_unidad = 3  # Unidad
                
                conn.execute(text("""
                    UPDATE materiales SET id_tipo_material = :id_tipo, id_unidad_inventario = :id_unidad 
                    WHERE id_material = :id_mat
                """), {'id_tipo': id_tipo, 'id_unidad': id_unidad, 'id_mat': mat[0]})
        
        # Crear tabla de inventario separada
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS inventario_materiales (
                id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
                id_material INTEGER UNIQUE NOT NULL,
                cantidad_stock REAL DEFAULT 0.0,
                stock_minimo REAL DEFAULT 5.0,
                precio_compra_promedio REAL DEFAULT 0.0,
                FOREIGN KEY (id_material) REFERENCES materiales(id_material)
            )
        """))
        
        # Migrar datos de stock existentes a nueva tabla
        materiales = conn.execute(text("""
            SELECT id_material, cantidad_stock, stock_minimo, precio_por_unidad 
            FROM materiales
        """)).fetchall()
        
        for mat in materiales:
            try:
                conn.execute(text("""
                    INSERT OR IGNORE INTO inventario_materiales 
                    (id_material, cantidad_stock, stock_minimo, precio_compra_promedio)
                    VALUES (:id_mat, :stock, :min, :precio)
                """), {'id_mat': mat[0], 'stock': mat[1] or 0, 'min': mat[2] or 5, 'precio': mat[3] or 0})
            except Exception:
                pass
        
        # Crear tabla de atributos de rollos
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS atributos_rollos_impresion (
                id_atributo INTEGER PRIMARY KEY AUTOINCREMENT,
                id_material INTEGER UNIQUE NOT NULL,
                ancho_fijo_rollo REAL DEFAULT 0.0,
                es_rollo_continuo INTEGER DEFAULT 1,
                FOREIGN KEY (id_material) REFERENCES materiales(id_material)
            )
        """))
        
        # Migrar datos de rollos existentes
        materiales_rollo = conn.execute(text("""
            SELECT id_material, ancho_bobina 
            FROM materiales 
            WHERE tipo_material = 'dimension' OR ancho_bobina > 0
        """)).fetchall()
        
        for mat in materiales_rollo:
            if mat[1] and mat[1] > 0:
                try:
                    conn.execute(text("""
                        INSERT OR IGNORE INTO atributos_rollos_impresion 
                        (id_material, ancho_fijo_rollo, es_rollo_continuo)
                        VALUES (:id_mat, :ancho, 1)
                    """), {'id_mat': mat[0], 'ancho': mat[1]})
                except Exception:
                    pass
        
        conn.commit()
        print("   ✓ Materiales normalizados (definición separada de inventario)")
        
        # ============================================
        # PASO 4: Normalizar SERVICIOS
        # ============================================
        print("\n🛠️ Paso 4: Normalizando servicios...")
        
        result = conn.execute(text("PRAGMA table_info(servicios)")).fetchall()
        columns = [col[1] for col in result]
        
        if 'id_unidad_cobro' not in columns:
            conn.execute(text("ALTER TABLE servicios ADD COLUMN id_unidad_cobro INTEGER DEFAULT 3"))
            
            # Mapear unidades de texto a IDs
            mapeo_unidades = {
                'm2': 1, 'm²': 1, 'metro cuadrado': 1,
                'm': 2, 'metro': 2, 'metro lineal': 2,
                'unidad': 3, 'u': 3, 'und': 3,
                'decena': 4, 'dec': 4,
                'ciento': 5, 'cto': 5,
                'millar': 6, 'mil': 6,
            }
            
            servicios = conn.execute(text("SELECT id_servicio, unidad_cobro FROM servicios")).fetchall()
            for srv in servicios:
                unidad_lower = (srv[1] or '').lower()
                id_unidad = 3  # Default: Unidad
                
                for key, val in mapeo_unidades.items():
                    if key in unidad_lower:
                        id_unidad = val
                        break
                
                conn.execute(text("UPDATE servicios SET id_unidad_cobro = :id_unidad WHERE id_servicio = :id_srv"),
                           {'id_unidad': id_unidad, 'id_srv': srv[0]})
        
        conn.commit()
        print("   ✓ Servicios normalizados con unidades de medida estándar")
        
        # ============================================
        # PASO 5: Agregar campos a detalle_pedidos
        # ============================================
        print("\n📋 Paso 5: Actualizando detalle de pedidos...")
        
        result = conn.execute(text("PRAGMA table_info(detalle_pedidos)")).fetchall()
        columns = [col[1] for col in result]
        
        if 'id_maquina_asignada' not in columns:
            conn.execute(text("ALTER TABLE detalle_pedidos ADD COLUMN id_maquina_asignada INTEGER"))
        
        # Renombrar columnas si es necesario (en SQLite hay que recrear la tabla)
        # Por simplicidad, dejamos las columnas existentes como alias
        
        conn.commit()
        print("   ✓ Detalle de pedidos actualizado")
        
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        
        # Mostrar resumen
        print("\n📊 RESUMEN DE LA MIGRACIÓN:")
        
        count = conn.execute(text("SELECT COUNT(*) FROM unidades_medida")).fetchone()[0]
        print(f"   • Unidades de medida: {count}")
        
        count = conn.execute(text("SELECT COUNT(*) FROM tipos_materiales")).fetchone()[0]
        print(f"   • Tipos de materiales: {count}")
        
        count = conn.execute(text("SELECT COUNT(*) FROM tipos_maquinas")).fetchone()[0]
        print(f"   • Tipos de máquinas: {count}")
        
        count = conn.execute(text("SELECT COUNT(*) FROM capacidad_maquinas")).fetchone()[0]
        print(f"   • Capacidades de máquinas registradas: {count}")
        
        count = conn.execute(text("SELECT COUNT(*) FROM inventario_materiales")).fetchone()[0]
        print(f"   • Registros de inventario: {count}")


def main():
    print("="*60)
    print("  MIGRACIÓN A SISTEMA EXPERTO NORMALIZADO")
    print("  Base de Conocimientos para Imprenta")
    print("="*60)
    
    # Verificar que existe la BD
    if not os.path.exists(DB_PATH):
        print("❌ Error: No se encontró la base de datos en:", DB_PATH)
        return
    
    print(f"\n📁 Base de datos: {DB_PATH}")
    
    # Crear backup
    print("\n🔒 Creando respaldo de seguridad...")
    if not backup_database():
        print("⚠️ No se pudo crear backup (BD no existe)")
    
    # Ejecutar migración
    try:
        migrar_estructura()
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎉 ¡Migración completada!")
    print("\n📌 PRÓXIMOS PASOS:")
    print("   1. Revisar datos en panel de administración")
    print("   2. Ajustar capacidades de máquinas (ancho_util_max)")
    print("   3. Verificar materiales asignados a servicios")
    print("   4. El sistema experto ahora consultará la BD para inferir")


if __name__ == "__main__":
    main()
