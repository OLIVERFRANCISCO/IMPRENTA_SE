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
        
        # Ejecutar migraciones antes de crear tablas
        self._ejecutar_migraciones()
        
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

    def _ejecutar_migraciones(self):
        """
        Ejecuta migraciones para actualizar el esquema de bases de datos existentes.
        Agrega columnas nuevas que no existan en la BD.
        """
        from sqlalchemy import text, inspect
        
        with self._engine.connect() as conn:
            inspector = inspect(self._engine)
            
            # Verificar si la tabla servicios existe
            if 'servicios' in inspector.get_table_names():
                columnas_servicios = [col['name'] for col in inspector.get_columns('servicios')]
                
                # Migración: agregar tipo_material a servicios si no existe
                if 'tipo_material' not in columnas_servicios:
                    conn.execute(text("ALTER TABLE servicios ADD COLUMN tipo_material VARCHAR DEFAULT 'unidad'"))
                    conn.commit()
                    print("✅ Migración: columna 'tipo_material' agregada a servicios")
            
            # Verificar si existe la tabla vieja atributos_rollos_impresion y crear la nueva
            if 'atributos_rollos_impresion' in inspector.get_table_names():
                # La tabla vieja existe, pero la nueva será creada por create_all
                # Podríamos migrar datos aquí si fuera necesario
                print("⚠️ Tabla 'atributos_rollos_impresion' detectada (legacy)")

    def _cargar_datos_iniciales(self):
        """
        Carga datos iniciales si las tablas están vacías
        
        Inserta estados de pedidos, máquinas y servicios de ejemplo
        """
        from app.database.models import (
            EstadoPedido, Maquina, Servicio, TipoMaquina, UnidadMedida
        )
        
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
            
            # Cargar unidades de medida si no existen
            if session.query(UnidadMedida).count() == 0:
                unidades = [
                    UnidadMedida(nombre_unidad="Metro Cuadrado", abreviacion="m2", tipo="Area"),
                    UnidadMedida(nombre_unidad="Unidad", abreviacion="unidad", tipo="Conteo"),
                    UnidadMedida(nombre_unidad="Ciento", abreviacion="ciento", tipo="Conteo"),
                    UnidadMedida(nombre_unidad="Metro Lineal", abreviacion="ml", tipo="Longitud"),
                    UnidadMedida(nombre_unidad="Millar", abreviacion="millar", tipo="Conteo"),
                ]
                session.add_all(unidades)
                session.flush()
                print("✅ Unidades de medida inicializadas")
            
            # Cargar tipos de máquinas si no existen
            if session.query(TipoMaquina).count() == 0:
                tipos_maq = [
                    TipoMaquina(nombre_tipo="Pequeño Formato"),
                    TipoMaquina(nombre_tipo="Gran Formato"),
                    TipoMaquina(nombre_tipo="Acabado"),
                    TipoMaquina(nombre_tipo="Corte"),
                ]
                session.add_all(tipos_maq)
                session.flush()
                print("✅ Tipos de máquinas inicializados")

            # Verificar y cargar máquinas
            if session.query(Maquina).count() == 0:
                # Obtener tipos de máquinas
                tipo_peq = session.query(TipoMaquina).filter_by(nombre_tipo="Pequeño Formato").first()
                tipo_gran = session.query(TipoMaquina).filter_by(nombre_tipo="Gran Formato").first()
                tipo_acab = session.query(TipoMaquina).filter_by(nombre_tipo="Acabado").first()
                
                maquinas = [
                    Maquina(nombre="Impresora Láser A3", id_tipo_maquina=tipo_peq.id_tipo_maquina if tipo_peq else 1),
                    Maquina(nombre="Impresora Sublimación", id_tipo_maquina=tipo_peq.id_tipo_maquina if tipo_peq else 1),
                    Maquina(nombre="Plotter HP DesignJet", id_tipo_maquina=tipo_gran.id_tipo_maquina if tipo_gran else 2),
                    Maquina(nombre="Laminadora Manual", id_tipo_maquina=tipo_acab.id_tipo_maquina if tipo_acab else 3)
                ]
                session.add_all(maquinas)
                print("✅ Máquinas inicializadas")
            
            # Verificar y cargar servicios
            if session.query(Servicio).count() == 0:
                # Obtener unidades de cobro
                unidad_m2 = session.query(UnidadMedida).filter_by(abreviacion="m2").first()
                unidad_und = session.query(UnidadMedida).filter_by(abreviacion="unidad").first()
                unidad_ciento = session.query(UnidadMedida).filter_by(abreviacion="ciento").first()
                
                servicios = [
                    Servicio(nombre_servicio="Gigantografía", id_unidad_cobro=unidad_m2.id_unidad if unidad_m2 else 1, precio_base=25.0, id_maquina_sugerida=3),
                    Servicio(nombre_servicio="Banner Roll-Up", id_unidad_cobro=unidad_und.id_unidad if unidad_und else 2, precio_base=80.0, id_maquina_sugerida=3),
                    Servicio(nombre_servicio="Tarjetas de Presentación", id_unidad_cobro=unidad_ciento.id_unidad if unidad_ciento else 3, precio_base=15.0, id_maquina_sugerida=1),
                    Servicio(nombre_servicio="Flyers A5", id_unidad_cobro=unidad_ciento.id_unidad if unidad_ciento else 3, precio_base=20.0, id_maquina_sugerida=1),
                    Servicio(nombre_servicio="Tazas Personalizadas", id_unidad_cobro=unidad_und.id_unidad if unidad_und else 2, precio_base=12.0, id_maquina_sugerida=2),
                    Servicio(nombre_servicio="Llaveros", id_unidad_cobro=unidad_und.id_unidad if unidad_und else 2, precio_base=3.0, id_maquina_sugerida=2)
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
