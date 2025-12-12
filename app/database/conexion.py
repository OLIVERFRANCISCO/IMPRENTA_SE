"""
Módulo de conexión a la base de datos SQLite usando SQLAlchemy ORM
Gestiona la sesión y configuración de la base de datos
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from app.config import DB_PATH
from app.database.models import Base


class DatabaseConnection:
    """
    Clase singleton para gestionar la conexión con SQLAlchemy ORM
    
    Proporciona acceso a la sesión de base de datos y maneja
    la inicialización de tablas y datos
    """

    _instance = None
    _engine = None
    _session_factory = None
    _Session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa el engine y session factory de SQLAlchemy"""
        # Crear engine con SQLite
        self._engine = create_engine(
            f'sqlite:///{DB_PATH}',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=False  # Cambiar a True para debug SQL
        )
        
        # Habilitar foreign keys en SQLite
        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        # Crear todas las tablas definidas en los modelos
        Base.metadata.create_all(self._engine)
        
        # Configurar session factory con scoped_session para thread safety
        self._session_factory = sessionmaker(bind=self._engine)
        self._Session = scoped_session(self._session_factory)
        
        # Cargar datos iniciales si la BD está vacía
        self._cargar_datos_iniciales()

    def get_session(self):
        """
        Retorna una sesión de SQLAlchemy
        
        Returns:
            Session: Sesión de SQLAlchemy para operaciones ORM
        """
        return self._Session()

    def get_engine(self):
        """
        Retorna el engine de SQLAlchemy
        
        Returns:
            Engine: Engine de SQLAlchemy
        """
        return self._engine

    @contextmanager
    def session_scope(self):
        """
        Context manager para manejar transacciones de forma segura
        
        Uso:
            with db.session_scope() as session:
                cliente = session.query(Cliente).first()
                
        Yields:
            Session: Sesión que hace commit automático al salir
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def remove_session(self):
        """Remueve la sesión actual del registro de scoped_session"""
        self._Session.remove()

    def _cargar_datos_iniciales(self):
        """
        Carga datos iniciales si las tablas están vacías
        
        Inserta estados de pedidos, máquinas y servicios de ejemplo
        """
        from app.database.models import EstadoPedido, Maquina, Servicio
        
        with self.session_scope() as session:
            # Verificar y cargar estados de pedidos
            if session.query(EstadoPedido).count() == 0:
                estados = [
                    EstadoPedido(nombre="Cotizado", color="#9E9E9E"),
                    EstadoPedido(nombre="Confirmado", color="#2196F3"),
                    EstadoPedido(nombre="En Diseño", color="#FF9800"),
                    EstadoPedido(nombre="Previsualización Enviada", color="#9C27B0"),
                    EstadoPedido(nombre="En Preparación", color="#FFC107"),
                    EstadoPedido(nombre="Listo para Entrega", color="#4CAF50"),
                    EstadoPedido(nombre="Entregado", color="#00C853"),
                    EstadoPedido(nombre="Cancelado", color="#F44336")
                ]
                session.add_all(estados)
                print("✅ Estados de pedidos inicializados")
            
            # Verificar y cargar máquinas
            if session.query(Maquina).count() == 0:
                maquinas = [
                    Maquina(nombre="Impresora Láser A3", tipo="Pequeño Formato"),
                    Maquina(nombre="Impresora Sublimación", tipo="Pequeño Formato"),
                    Maquina(nombre="Plotter HP DesignJet", tipo="Gran Formato"),
                    Maquina(nombre="Laminadora Manual", tipo="Acabado")
                ]
                session.add_all(maquinas)
                print("✅ Máquinas inicializadas")
            
            # Verificar y cargar servicios
            if session.query(Servicio).count() == 0:
                servicios = [
                    Servicio(nombre_servicio="Gigantografía", unidad_cobro="m2", precio_base=25.0, id_maquina_sugerida=3),
                    Servicio(nombre_servicio="Banner Roll-Up", unidad_cobro="unidad", precio_base=80.0, id_maquina_sugerida=3),
                    Servicio(nombre_servicio="Tarjetas de Presentación", unidad_cobro="ciento", precio_base=15.0, id_maquina_sugerida=1),
                    Servicio(nombre_servicio="Flyers A5", unidad_cobro="ciento", precio_base=20.0, id_maquina_sugerida=1),
                    Servicio(nombre_servicio="Tazas Personalizadas", unidad_cobro="unidad", precio_base=12.0, id_maquina_sugerida=2),
                    Servicio(nombre_servicio="Llaveros", unidad_cobro="unidad", precio_base=3.0, id_maquina_sugerida=2)
                ]
                session.add_all(servicios)
                print("✅ Servicios inicializados")

    def close(self):
        """Cierra todas las conexiones y limpia recursos"""
        if self._Session:
            self._Session.remove()
        if self._engine:
            self._engine.dispose()
        print("✅ Conexión de base de datos cerrada")


# Función de conveniencia para obtener la sesión
def get_session():
    """
    Retorna una sesión de SQLAlchemy
    
    Returns:
        Session: Sesión de SQLAlchemy para operaciones ORM
    """
    db = DatabaseConnection()
    return db.get_session()


# Función antigua mantenida para compatibilidad (deprecated)
def get_db():
    """
    Retorna una sesión de SQLAlchemy (deprecated)
    
    Esta función se mantiene para compatibilidad con código antiguo
    Se recomienda usar get_session() en su lugar
    
    Returns:
        Session: Sesión de SQLAlchemy
    """
    return get_session()
