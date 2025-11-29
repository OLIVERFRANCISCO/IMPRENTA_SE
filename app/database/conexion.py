"""
Módulo de conexión a la base de datos SQLite
Crea las tablas si no existen y gestiona la conexión
"""
import sqlite3
from pathlib import Path
from app.config import DB_PATH


class DatabaseConnection:
    """Clase singleton para gestionar la conexión a SQLite"""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def get_connection(self):
        """Retorna la conexión a la base de datos"""
        if self._connection is None:
            self._connection = sqlite3.connect(str(DB_PATH), check_same_thread=False)
            self._connection.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
            self._inicializar_db()
        return self._connection

    def _inicializar_db(self):
        """Crea las tablas si no existen"""
        cursor = self._connection.cursor()

        # 1. Tabla de CLIENTES
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Tabla de MAQUINAS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maquinas (
                id_maquina INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL
            )
        """)

        # 3. Tabla de SERVICIOS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicios (
                id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_servicio TEXT NOT NULL,
                unidad_cobro TEXT NOT NULL,
                precio_base REAL DEFAULT 0,
                id_maquina_sugerida INTEGER,
                FOREIGN KEY (id_maquina_sugerida) REFERENCES maquinas(id_maquina)
            )
        """)

        # 4. Tabla de MATERIALES (INVENTARIO)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materiales (
                id_material INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_material TEXT NOT NULL,
                cantidad_stock REAL NOT NULL,
                unidad_medida TEXT NOT NULL,
                stock_minimo REAL DEFAULT 5,
                precio_por_unidad REAL DEFAULT 0
            )
        """)

        # 5. Tabla de PEDIDOS (CABECERA)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                fecha_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_entrega_estimada DATETIME,
                estado_pedido TEXT DEFAULT 'Cotizado',
                estado_pago TEXT DEFAULT 'Pendiente',
                costo_total REAL DEFAULT 0,
                acuenta REAL DEFAULT 0,
                observaciones TEXT,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
            )
        """)

        # 6. Tabla de DETALLE_PEDIDO
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalles_pedido (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER NOT NULL,
                id_servicio INTEGER NOT NULL,
                id_material INTEGER,
                descripcion TEXT,
                ancho REAL DEFAULT 0,
                alto REAL DEFAULT 0,
                cantidad INTEGER NOT NULL DEFAULT 1,
                precio_unitario REAL NOT NULL,
                FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
                FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio),
                FOREIGN KEY (id_material) REFERENCES materiales(id_material)
            )
        """)

        # 7. Tabla de CONSUMO_MATERIALES (Historial)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consumo_materiales (
                id_consumo INTEGER PRIMARY KEY AUTOINCREMENT,
                id_detalle INTEGER NOT NULL,
                id_material INTEGER NOT NULL,
                cantidad_usada REAL NOT NULL,
                fecha_consumo DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_detalle) REFERENCES detalles_pedido(id_detalle),
                FOREIGN KEY (id_material) REFERENCES materiales(id_material)
            )
        """)

        self._connection.commit()
        self._cargar_datos_iniciales()

    def _cargar_datos_iniciales(self):
        """Carga datos de ejemplo si las tablas están vacías"""
        cursor = self._connection.cursor()

        # Verificar si ya hay máquinas
        cursor.execute("SELECT COUNT(*) FROM maquinas")
        if cursor.fetchone()[0] == 0:
            # Insertar máquinas de ejemplo
            maquinas = [
                ("Impresora Láser A3", "Pequeño Formato"),
                ("Impresora Sublimación", "Pequeño Formato"),
                ("Plotter HP DesignJet", "Gran Formato"),
                ("Laminadora Manual", "Acabado")
            ]
            cursor.executemany("INSERT INTO maquinas (nombre, tipo) VALUES (?, ?)", maquinas)

        # Verificar si ya hay servicios
        cursor.execute("SELECT COUNT(*) FROM servicios")
        if cursor.fetchone()[0] == 0:
            # Insertar servicios de ejemplo
            servicios = [
                ("Gigantografía", "m2", 25.0, 3),
                ("Banner Roll-Up", "unidad", 80.0, 3),
                ("Tarjetas de Presentación", "ciento", 15.0, 1),
                ("Flyers A5", "ciento", 20.0, 1),
                ("Tazas Personalizadas", "unidad", 12.0, 2),
                ("Llaveros", "unidad", 3.0, 2)
            ]
            cursor.executemany(
                "INSERT INTO servicios (nombre_servicio, unidad_cobro, precio_base, id_maquina_sugerida) VALUES (?, ?, ?, ?)",
                servicios
            )

        # Verificar si ya hay materiales
        cursor.execute("SELECT COUNT(*) FROM materiales")
        if cursor.fetchone()[0] == 0:
            # Insertar materiales de ejemplo
            materiales = [
                ("Lona 13oz", 50.0, "metros", 10.0, 8.5),
                ("Vinil Adhesivo", 30.0, "metros", 5.0, 6.0),
                ("Papel Couché 300g", 500, "hojas", 50, 0.5),
                ("Papel Bond 75g", 1000, "hojas", 100, 0.2),
                ("Tinta Negra", 5, "cartuchos", 1, 45.0),
                ("Tinta Color", 5, "cartuchos", 1, 55.0)
            ]
            cursor.executemany(
                "INSERT INTO materiales (nombre_material, cantidad_stock, unidad_medida, stock_minimo, precio_por_unidad) VALUES (?, ?, ?, ?, ?)",
                materiales
            )

        self._connection.commit()

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self._connection:
            self._connection.close()
            self._connection = None


# Función de conveniencia para obtener la conexión
def get_db():
    """Retorna la conexión a la base de datos"""
    db = DatabaseConnection()
    return db.get_connection()

