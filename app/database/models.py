"""
Modelos ORM usando SQLAlchemy
Define la estructura de las tablas como clases Python
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

# Base para todos los modelos
Base = declarative_base()


class Cliente(Base):
    """
    Modelo de Cliente
    
    Representa a los clientes de la imprenta
    """
    __tablename__ = 'clientes'
    
    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    nombre_completo = Column(String, nullable=False)
    telefono = Column(String)
    email = Column(String)
    fecha_registro = Column(DateTime, default=datetime.now)
    
    # Relaciones
    pedidos = relationship('Pedido', back_populates='cliente')
    
    def __repr__(self):
        return f"<Cliente(id={self.id_cliente}, nombre='{self.nombre_completo}')>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario para compatibilidad con código existente"""
        return {
            'id_cliente': self.id_cliente,
            'nombre_completo': self.nombre_completo,
            'telefono': self.telefono,
            'email': self.email,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }


class Maquina(Base):
    """
    Modelo de Maquinaria
    
    Representa las máquinas disponibles en la imprenta
    """
    __tablename__ = 'maquinas'
    
    id_maquina = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    
    # FASE 3: Sugerencia/Recomendación de uso
    sugerencia = Column(Text, default='')
    
    # Relaciones
    servicios = relationship('Servicio', back_populates='maquina_sugerida')
    servicios_compatibles = relationship('Servicio', secondary='maquinas_servicios', back_populates='maquinas_compatibles', viewonly=True)
    
    def __repr__(self):
        return f"<Maquina(id={self.id_maquina}, nombre='{self.nombre}', tipo='{self.tipo}')>"
    
    def to_dict(self):
        return {
            'id_maquina': self.id_maquina,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'sugerencia': self.sugerencia if self.sugerencia else ''
        }


class Material(Base):
    """
    Modelo de Material (Inventario)
    
    Representa los materiales disponibles en inventario
    Soporta dos tipos: 'unidad' y 'dimension'
    """
    __tablename__ = 'materiales'
    
    id_material = Column(Integer, primary_key=True, autoincrement=True)
    nombre_material = Column(String, nullable=False)
    
    # NUEVO: Tipo de material ('unidad' o 'dimension')
    tipo_material = Column(String, default='unidad', nullable=False)
    
    # NUEVO: Sugerencia/Recomendación del material
    sugerencia = Column(Text, default='')
    
    # Campos comunes
    cantidad_stock = Column(Float, nullable=False)
    unidad_medida = Column(String, nullable=False)
    stock_minimo = Column(Float, default=5.0)
    precio_por_unidad = Column(Float, default=0.0)
    
    # Para tipo 'dimension' (materiales en rollo/bobina)
    ancho_bobina = Column(Float, default=0.0)  # Ancho disponible en metros
    dimension_minima = Column(Float, default=0.0)  # Dimensión mínima vendible
    dimension_disponible = Column(Float, default=0.0)  # Dimensión total disponible
    
    # Relaciones
    detalles_pedido = relationship('DetallePedido', back_populates='material')
    consumos = relationship('ConsumoMaterial', back_populates='material')
    servicios = relationship('Servicio', secondary='servicios_materiales', back_populates='materiales', viewonly=True)
    
    def __repr__(self):
        return f"<Material(id={self.id_material}, tipo='{self.tipo_material}', nombre='{self.nombre_material}', stock={self.cantidad_stock})>"
    
    def to_dict(self):
        return {
            'id_material': self.id_material,
            'nombre_material': self.nombre_material,
            'tipo_material': self.tipo_material,
            'sugerencia': self.sugerencia if self.sugerencia else '',
            'cantidad_stock': self.cantidad_stock,
            'unidad_medida': self.unidad_medida,
            'stock_minimo': self.stock_minimo,
            'precio_por_unidad': self.precio_por_unidad,
            'ancho_bobina': self.ancho_bobina if self.ancho_bobina else 0.0,
            'dimension_minima': self.dimension_minima if self.dimension_minima else 0.0,
            'dimension_disponible': self.dimension_disponible if self.dimension_disponible else 0.0
        }
    
    def esta_bajo_stock(self):
        """Verifica si el material está por debajo del stock mínimo"""
        if self.tipo_material == 'dimension':
            return self.dimension_disponible <= self.dimension_minima
        else:
            return self.cantidad_stock <= self.stock_minimo


class EstadoPedido(Base):
    """
    Modelo de Estado de Pedido
    
    Representa los diferentes estados que puede tener un pedido
    """
    __tablename__ = 'estados_pedidos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False, unique=True)
    color = Column(String, nullable=False, default='#808080')
    
    # Relaciones
    pedidos = relationship('Pedido', back_populates='estado')
    
    def __repr__(self):
        return f"<EstadoPedido(id={self.id}, nombre='{self.nombre}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'color': self.color
        }


class MaquinaServicio(Base):
    """
    Tabla de asociación entre Maquinas y Servicios (N:N)
    
    Permite definir qué máquinas son compatibles con cada servicio
    """
    __tablename__ = 'maquinas_servicios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_maquina = Column(Integer, ForeignKey('maquinas.id_maquina'), nullable=False)
    id_servicio = Column(Integer, ForeignKey('servicios.id_servicio'), nullable=False)
    es_recomendada = Column(Integer, default=0)  # 0=normal, 1=recomendada
    
    # Restricción única para evitar duplicados
    __table_args__ = (UniqueConstraint('id_maquina', 'id_servicio', name='uq_maquina_servicio'),)
    
    def __repr__(self):
        return f"<MaquinaServicio(maquina={self.id_maquina}, servicio={self.id_servicio})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_maquina': self.id_maquina,
            'id_servicio': self.id_servicio,
            'es_recomendada': bool(self.es_recomendada)
        }


class ServicioMaterial(Base):
    """
    Tabla de asociación entre Servicios y Materiales (N:N)
    
    Permite definir qué materiales son compatibles con cada servicio
    """
    __tablename__ = 'servicios_materiales'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_servicio = Column(Integer, ForeignKey('servicios.id_servicio'), nullable=False)
    id_material = Column(Integer, ForeignKey('materiales.id_material'), nullable=False)
    es_preferido = Column(Integer, default=0)  # 0=normal, 1=preferido
    
    # Restricción única para evitar duplicados
    __table_args__ = (UniqueConstraint('id_servicio', 'id_material', name='uq_servicio_material'),)
    
    def __repr__(self):
        return f"<ServicioMaterial(servicio={self.id_servicio}, material={self.id_material})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_servicio': self.id_servicio,
            'id_material': self.id_material,
            'es_preferido': bool(self.es_preferido)
        }


class Servicio(Base):
    """
    Modelo de Servicio
    
    Representa los servicios ofrecidos por la imprenta
    """
    __tablename__ = 'servicios'
    
    id_servicio = Column(Integer, primary_key=True, autoincrement=True)
    nombre_servicio = Column(String, nullable=False)
    unidad_cobro = Column(String, nullable=False)
    precio_base = Column(Float, default=0.0)
    id_maquina_sugerida = Column(Integer, ForeignKey('maquinas.id_maquina'))
    
    # Relaciones
    maquina_sugerida = relationship('Maquina', back_populates='servicios')
    detalles_pedido = relationship('DetallePedido', back_populates='servicio')
    materiales = relationship('Material', secondary='servicios_materiales', back_populates='servicios', viewonly=True)
    maquinas_compatibles = relationship('Maquina', secondary='maquinas_servicios', back_populates='servicios_compatibles', viewonly=True)
    
    def __repr__(self):
        return f"<Servicio(id={self.id_servicio}, nombre='{self.nombre_servicio}')>"
    
    def to_dict(self):
        return {
            'id_servicio': self.id_servicio,
            'nombre_servicio': self.nombre_servicio,
            'unidad_cobro': self.unidad_cobro,
            'precio_base': self.precio_base,
            'id_maquina_sugerida': self.id_maquina_sugerida,
            'nombre_maquina': self.maquina_sugerida.nombre if self.maquina_sugerida else None,
            'tipo_maquina': self.maquina_sugerida.tipo if self.maquina_sugerida else None
        }


class Pedido(Base):
    """
    Modelo de Pedido (Cabecera)
    
    Representa un pedido realizado por un cliente
    """
    __tablename__ = 'pedidos'
    
    id_pedido = Column(Integer, primary_key=True, autoincrement=True)
    id_cliente = Column(Integer, ForeignKey('clientes.id_cliente'), nullable=False)
    fecha_ingreso = Column(DateTime, default=datetime.now)
    fecha_entrega_estimada = Column(DateTime)
    id_estado = Column(Integer, ForeignKey('estados_pedidos.id'))
    estado_pago = Column(String, default='Pendiente')
    costo_total = Column(Float, default=0.0)
    acuenta = Column(Float, default=0.0)
    observaciones = Column(Text)
    
    # Relaciones
    cliente = relationship('Cliente', back_populates='pedidos')
    estado = relationship('EstadoPedido', back_populates='pedidos')
    detalles = relationship('DetallePedido', back_populates='pedido', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Pedido(id={self.id_pedido}, cliente_id={self.id_cliente}, total={self.costo_total})>"
    
    def to_dict(self):
        """Convierte a diccionario con información completa"""
        return {
            'id_pedido': self.id_pedido,
            'id_cliente': self.id_cliente,
            'nombre_cliente': self.cliente.nombre_completo if self.cliente else None,
            'nombre_completo': self.cliente.nombre_completo if self.cliente else None,
            'telefono': self.cliente.telefono if self.cliente else None,
            'email': self.cliente.email if self.cliente else None,
            'fecha_ingreso': self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
            'fecha_entrega_estimada': self.fecha_entrega_estimada.isoformat() if self.fecha_entrega_estimada else None,
            'id_estado': self.id_estado,
            'estado_nombre': self.estado.nombre if self.estado else None,
            'estado_color': self.estado.color if self.estado else '#808080',
            'estado_pago': self.estado_pago,
            'costo_total': self.costo_total,
            'acuenta': self.acuenta,
            'observaciones': self.observaciones
        }
    
    def calcular_saldo(self):
        """Calcula el saldo pendiente"""
        return self.costo_total - self.acuenta


class DetallePedido(Base):
    """
    Modelo de Detalle de Pedido
    
    Representa los ítems individuales de un pedido
    """
    __tablename__ = 'detalle_pedidos'
    
    id_detalle = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey('pedidos.id_pedido'), nullable=False)
    id_servicio = Column(Integer, ForeignKey('servicios.id_servicio'), nullable=False)
    id_material = Column(Integer, ForeignKey('materiales.id_material'))
    descripcion = Column(Text)
    ancho = Column(Float, nullable=False)
    alto = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    
    # Relaciones
    pedido = relationship('Pedido', back_populates='detalles')
    servicio = relationship('Servicio', back_populates='detalles_pedido')
    material = relationship('Material', back_populates='detalles_pedido')
    consumos = relationship('ConsumoMaterial', back_populates='detalle', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<DetallePedido(id={self.id_detalle}, pedido={self.id_pedido}, cantidad={self.cantidad})>"
    
    def to_dict(self):
        """Convierte a diccionario con información completa"""
        return {
            'id_detalle': self.id_detalle,
            'id_pedido': self.id_pedido,
            'id_servicio': self.id_servicio,
            'nombre_servicio': self.servicio.nombre_servicio if self.servicio else None,
            'id_material': self.id_material,
            'nombre_material': self.material.nombre_material if self.material else None,
            'descripcion': self.descripcion,
            'ancho': self.ancho,
            'alto': self.alto,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario
        }
    
    def calcular_subtotal(self):
        """Calcula el subtotal del detalle"""
        return self.cantidad * self.precio_unitario


class ConsumoMaterial(Base):
    """
    Modelo de Consumo de Material
    
    Registra el consumo de materiales en la producción
    """
    __tablename__ = 'consumo_materiales'
    
    id_consumo = Column(Integer, primary_key=True, autoincrement=True)
    id_detalle = Column(Integer, ForeignKey('detalle_pedidos.id_detalle'), nullable=False)
    id_material = Column(Integer, ForeignKey('materiales.id_material'), nullable=False)
    cantidad_usada = Column(Float, nullable=False)
    fecha_consumo = Column(DateTime, default=datetime.now)
    
    # Relaciones
    detalle = relationship('DetallePedido', back_populates='consumos')
    material = relationship('Material', back_populates='consumos')
    
    def __repr__(self):
        return f"<ConsumoMaterial(id={self.id_consumo}, material={self.id_material}, cantidad={self.cantidad_usada})>"
    
    def to_dict(self):
        return {
            'id_consumo': self.id_consumo,
            'id_detalle': self.id_detalle,
            'id_material': self.id_material,
            'nombre_material': self.material.nombre_material if self.material else None,
            'cantidad_usada': self.cantidad_usada,
            'fecha_consumo': self.fecha_consumo.isoformat() if self.fecha_consumo else None
        }


class Rol(Base):
    """
    Modelo de Rol
    
    Define roles de usuario con permisos configurables
    """
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_rol = Column(String, nullable=False, unique=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relaciones
    usuarios = relationship('Usuario', back_populates='rol')
    permisos = relationship('Permiso', back_populates='rol', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Rol(id={self.id}, nombre='{self.nombre_rol}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre_rol': self.nombre_rol,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'total_usuarios': len(self.usuarios) if self.usuarios else 0,
            'total_permisos': len(self.permisos) if self.permisos else 0
        }
    
    def es_admin(self):
        """Verifica si es el rol de administrador"""
        return self.nombre_rol.lower() == 'admin'


class Usuario(Base):
    """
    Modelo de Usuario
    
    Representa usuarios del sistema con autenticación y roles
    """
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    rol_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    ultimo_acceso = Column(DateTime, nullable=True)
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo
    
    # Relaciones
    rol = relationship('Rol', back_populates='usuarios')
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', rol='{self.rol.nombre_rol if self.rol else None}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'rol_id': self.rol_id,
            'nombre_rol': self.rol.nombre_rol if self.rol else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
            'activo': bool(self.activo)
        }
    
    def tiene_permiso(self, panel, accion):
        """
        Verifica si el usuario tiene permiso para realizar una acción en un panel
        
        Args:
            panel: Nombre del panel (ej: 'panel_clientes')
            accion: Acción a realizar (crear, editar, eliminar, ver)
            
        Returns:
            bool: True si tiene permiso
        """
        if self.rol and self.rol.es_admin():
            return True  # Admin tiene todos los permisos
        
        if self.rol:
            for permiso in self.rol.permisos:
                if permiso.panel == panel and permiso.permiso == accion:
                    return True
        return False
    
    def obtener_paneles_permitidos(self):
        """Retorna lista de paneles a los que tiene acceso"""
        if self.rol and self.rol.es_admin():
            # Admin tiene acceso a todo
            return ['todos']
        
        paneles = set()
        if self.rol:
            for permiso in self.rol.permisos:
                paneles.add(permiso.panel)
        return list(paneles)


class Permiso(Base):
    """
    Modelo de Permiso
    
    Define qué acciones puede realizar un rol en cada panel
    """
    __tablename__ = 'permisos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rol_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    panel = Column(String, nullable=False)  # Nombre del panel (ej: 'panel_clientes')
    permiso = Column(String, nullable=False)  # Tipo de permiso: crear, editar, eliminar, ver
    
    # Relaciones
    rol = relationship('Rol', back_populates='permisos')
    
    # Constraint único para evitar permisos duplicados
    __table_args__ = (
        UniqueConstraint('rol_id', 'panel', 'permiso', name='_rol_panel_permiso_uc'),
    )
    
    def __repr__(self):
        return f"<Permiso(rol_id={self.rol_id}, panel='{self.panel}', permiso='{self.permiso}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'rol_id': self.rol_id,
            'panel': self.panel,
            'permiso': self.permiso
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'rol_id': self.rol_id,
            'panel': self.panel,
            'permiso': self.permiso,
            'nombre_rol': self.rol.nombre_rol if self.rol else None
        }
