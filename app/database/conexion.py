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

        # 3.1 Tabla de SERVICIOS_MATERIALES (Relación muchos a muchos)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicios_materiales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_servicio INTEGER NOT NULL,
                id_material INTEGER NOT NULL,
                FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio),
                FOREIGN KEY (id_material) REFERENCES materiales(id_material),
                UNIQUE(id_servicio, id_material)
            )
        """)

        # 4. Tabla de ESTADOS_PEDIDOS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estados_pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                color TEXT NOT NULL DEFAULT '#808080'
            )
        """)

        # 5. Tabla de MATERIALES (INVENTARIO)
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

        # 6. Tabla de PEDIDOS (CABECERA)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                fecha_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP,
                fecha_entrega_estimada DATETIME,
                id_estado INTEGER DEFAULT 1,
                estado_pago TEXT DEFAULT 'Pendiente',
                costo_total REAL DEFAULT 0,
                acuenta REAL DEFAULT 0,
                observaciones TEXT,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_estado) REFERENCES estados_pedidos(id)
            )
        """)

        # 7. Tabla de DETALLE_PEDIDO
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

        # 8. Tabla de CONSUMO_MATERIALES (Historial)
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

        # Verificar si ya hay estados de pedidos
        cursor.execute("SELECT COUNT(*) FROM estados_pedidos")
        if cursor.fetchone()[0] == 0:
            # Insertar estados de pedidos con colores
            estados = [
                ("Cotizado", "#9E9E9E"),           # Gris
                ("Confirmado", "#2196F3"),         # Azul
                ("En Diseño", "#FF9800"),          # Naranja
                ("Previsualización Enviada", "#9C27B0"),  # Púrpura
                ("En Preparación", "#FFC107"),     # Amarillo
                ("Listo para Entrega", "#4CAF50"), # Verde
                ("Entregado", "#00C853"),          # Verde Brillante
                ("Cancelado", "#F44336")           # Rojo
            ]
            cursor.executemany("INSERT INTO estados_pedidos (nombre, color) VALUES (?, ?)", estados)

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
                # Materiales para gigantografía
                ("Lona 13 onz", 50.0, "metros", 10.0, 8.5),
                ("Lona 8 onz", 40.0, "metros", 10.0, 6.0),
                ("Vinil con Laminado Mate", 30.0, "metros", 5.0, 12.0),
                ("Vinil con Laminado Brillo", 30.0, "metros", 5.0, 12.5),
                ("Vinil sin Laminado", 35.0, "metros", 5.0, 8.0),
                # Materiales para formatos
                ("Papel Couché 300g", 500, "hojas", 50, 0.5),
                ("Papel Bond 75g", 1000, "hojas", 100, 0.2),
                ("Papel Fotográfico", 200, "hojas", 30, 1.5),
                # Materiales para merchandising
                ("Vinil Adhesivo", 30.0, "metros", 5.0, 6.0),
                ("Vinil Textil", 20.0, "metros", 3.0, 10.0),
                # Consumibles
                ("Tinta Negra", 5, "cartuchos", 1, 45.0),
                ("Tinta Color", 5, "cartuchos", 1, 55.0),
                ("Laminado Mate", 25.0, "metros", 5.0, 7.0),
                ("Laminado Brillo", 25.0, "metros", 5.0, 7.5)
            ]
            cursor.executemany(
                "INSERT INTO materiales (nombre_material, cantidad_stock, unidad_medida, stock_minimo, precio_por_unidad) VALUES (?, ?, ?, ?, ?)",
                materiales
            )

        # Verificar si ya hay relaciones servicios-materiales
        cursor.execute("SELECT COUNT(*) FROM servicios_materiales")
        if cursor.fetchone()[0] == 0:
            # Insertar relaciones de servicios con materiales compatibles
            # Formato: (id_servicio, id_material)
            relaciones = [
                # Gigantografía (id_servicio=1) - puede usar lonas y viniles
                (1, 1),  # Lona 13 onz
                (1, 2),  # Lona 8 onz
                (1, 3),  # Vinil con Laminado Mate
                (1, 4),  # Vinil con Laminado Brillo
                (1, 5),  # Vinil sin Laminado
                # Banner Roll-Up (id_servicio=2) - usa lona principalmente
                (2, 1),  # Lona 13 onz
                (2, 2),  # Lona 8 onz
                # Tarjetas de Presentación (id_servicio=3) - papel couché
                (3, 6),  # Papel Couché 300g
                # Flyers A5 (id_servicio=4) - papel bond o couché
                (4, 6),  # Papel Couché 300g
                (4, 7),  # Papel Bond 75g
                # Tazas Personalizadas (id_servicio=5) - vinil textil
                (5, 10), # Vinil Textil
                # Llaveros (id_servicio=6) - vinil adhesivo
                (6, 9),  # Vinil Adhesivo
            ]
            cursor.executemany(
                "INSERT INTO servicios_materiales (id_servicio, id_material) VALUES (?, ?)",
                relaciones
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

