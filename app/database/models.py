"""
Modelos ORM Normalizados (V2) - Sistema Experto de Imprenta
Basado en esquema 3FN/BCNF para separar lógica de negocio, inventario y definiciones.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ==========================================
# 1. TABLAS DE METADATOS (CATÁLOGOS)
# ==========================================

class UnidadMedida(Base):
    """
    Catálogo de unidades de medida.
    Ej: Metros, Unidades, Cientos, m2
    """
    __tablename__ = 'unidades_medida'
    
    id_unidad = Column(Integer, primary_key=True, autoincrement=True)
    nombre_unidad = Column(String, unique=True, nullable=False)  # Ej: Metro Cuadrado
    abreviacion = Column(String, nullable=False)  # Ej: m2
    tipo = Column(String, nullable=False)  # Ej: Area, Longitud, Conteo
    factor_conversion = Column(Float, default=1.0) # Para conversiones base si fuera necesario

    # Relaciones
    materiales = relationship('Material', back_populates='unidad_inventario')
    servicios = relationship('Servicio', back_populates='unidad_cobro')
    
    def __repr__(self):
        return f"<UnidadMedida(id={self.id_unidad}, nombre='{self.nombre_unidad}')>"
    
    def to_dict(self):
        return {
            'id_unidad': self.id_unidad,
            'nombre_unidad': self.nombre_unidad,
            'abreviacion': self.abreviacion,
            'tipo': self.tipo,
            'factor_conversion': self.factor_conversion
        }

class TipoMaterial(Base):
    """
    Categorización de materiales.
    Ej: Papel, Vinilo, Lona, Tinta, Rígido
    """
    __tablename__ = 'tipos_materiales'
    
    id_tipo_material = Column(Integer, primary_key=True, autoincrement=True)
    nombre_tipo = Column(String, unique=True, nullable=False)
    
    materiales = relationship('Material', back_populates='tipo_material')
    
    def __repr__(self):
        return f"<TipoMaterial(id={self.id_tipo_material}, nombre='{self.nombre_tipo}')>"
    
    def to_dict(self):
        return {
            'id_tipo_material': self.id_tipo_material,
            'nombre_tipo': self.nombre_tipo
        }

class TipoMaquina(Base):
    """
    Categorización de maquinaria.
    Ej: Plotter de Corte, Impresora Laser, Offset
    """
    __tablename__ = 'tipos_maquinas'
    
    id_tipo_maquina = Column(Integer, primary_key=True, autoincrement=True)
    nombre_tipo = Column(String, unique=True, nullable=False)
    
    maquinas = relationship('Maquina', back_populates='tipo_maquina')
    
    def __repr__(self):
        return f"<TipoMaquina(id={self.id_tipo_maquina}, nombre='{self.nombre_tipo}')>"
    
    def to_dict(self):
        return {
            'id_tipo_maquina': self.id_tipo_maquina,
            'nombre_tipo': self.nombre_tipo
        }

# ==========================================
# 2. TABLAS DE RECURSOS (MÁQUINAS Y MATERIALES)
# ==========================================

class Maquina(Base):
    """
    Máquinas físicas disponibles en el taller.
    """
    __tablename__ = 'maquinas'
    
    id_maquina = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, nullable=False)
    id_tipo_maquina = Column(Integer, ForeignKey('tipos_maquinas.id_tipo_maquina'), nullable=False)
    sugerencia = Column(Text) # Notas para el operador o el sistema experto
    
    # Relaciones
    tipo_maquina = relationship('TipoMaquina', back_populates='maquinas')
    capacidad = relationship('CapacidadMaquina', uselist=False, back_populates='maquina')
    servicios_compatibles = relationship('MaquinaServicio', back_populates='maquina')
    
    def __repr__(self):
        return f"<Maquina(id={self.id_maquina}, nombre='{self.nombre}')>"
    
    def to_dict(self):
        """Diccionario compatible con models.py para no romper UI"""
        return {
            'id_maquina': self.id_maquina,
            'nombre': self.nombre,
            'tipo': self.tipo_maquina.nombre_tipo if self.tipo_maquina else None,
            'id_tipo_maquina': self.id_tipo_maquina,
            'sugerencia': self.sugerencia if self.sugerencia else ''
        }

class CapacidadMaquina(Base):
    """
    CONOCIMIENTO TÉCNICO: Restricciones físicas de cada máquina.
    El sistema experto usa esto para decidir si un trabajo cabe en la máquina.
    """
    __tablename__ = 'capacidad_maquinas'
    
    id_capacidad = Column(Integer, primary_key=True, autoincrement=True)
    id_maquina = Column(Integer, ForeignKey('maquinas.id_maquina'), unique=True, nullable=False)
    
    # Restricciones Físicas (El "Cerebro" de la validación)
    ancho_util_max = Column(Float, default=0.0) # En metros. 0 si no aplica.
    largo_util_max = Column(Float, default=0.0) # En metros. 0 si es infinito (rollo).
    velocidad_promedio = Column(Float, default=0.0) # Unidades/hora (para estimar tiempos)
    
    maquina = relationship('Maquina', back_populates='capacidad')
    
    def to_dict(self):
        return {
            'id_capacidad': self.id_capacidad,
            'id_maquina': self.id_maquina,
            'ancho_util_max': self.ancho_util_max,
            'largo_util_max': self.largo_util_max,
            'velocidad_promedio': self.velocidad_promedio
        }

class Material(Base):
    """
    Catálogo de productos/insumos (No incluye stock, solo definición).
    """
    __tablename__ = 'materiales'
    
    id_material = Column(Integer, primary_key=True, autoincrement=True)
    nombre_material = Column(String, nullable=False)
    id_tipo_material = Column(Integer, ForeignKey('tipos_materiales.id_tipo_material'), nullable=False)
    id_unidad_inventario = Column(Integer, ForeignKey('unidades_medida.id_unidad'), nullable=False)
    sugerencia = Column(Text)
    
    # Relaciones
    tipo_material = relationship('TipoMaterial', back_populates='materiales')
    unidad_inventario = relationship('UnidadMedida', back_populates='materiales')
    inventario = relationship('InventarioMaterial', uselist=False, back_populates='material')
    atributos_rollo = relationship('AtributoRolloImpresion', uselist=False, back_populates='material')
    servicios_compatibles = relationship('ServicioMaterial', back_populates='material')
    
    def __repr__(self):
        return f"<Material(id={self.id_material}, nombre='{self.nombre_material}')>"
    
    def to_dict(self):
        """Diccionario compatible con models.py para no romper UI"""
        # Obtener datos de inventario si existen
        inv = self.inventario
        rollo = self.atributos_rollo
        return {
            'id_material': self.id_material,
            'nombre_material': self.nombre_material,
            'tipo_material': self.tipo_material.nombre_tipo if self.tipo_material else 'unidad',
            'sugerencia': self.sugerencia if self.sugerencia else '',
            'cantidad_stock': inv.cantidad_stock if inv else 0.0,
            'unidad_medida': self.unidad_inventario.abreviacion if self.unidad_inventario else '',
            'stock_minimo': inv.stock_minimo if inv else 5.0,
            'precio_por_unidad': inv.precio_compra_promedio if inv else 0.0,
            'ancho_bobina': rollo.ancho_fijo_rollo if rollo else 0.0,
            'dimension_minima': 0.0,
            'dimension_disponible': inv.cantidad_stock if inv else 0.0
        }
    
    def esta_bajo_stock(self):
        """Verifica si el material está por debajo del stock mínimo"""
        if self.inventario:
            return self.inventario.cantidad_stock <= self.inventario.stock_minimo
        return False

class InventarioMaterial(Base):
    """
    Estado actual del stock y costos.
    """
    __tablename__ = 'inventario_materiales'
    
    id_inventario = Column(Integer, primary_key=True, autoincrement=True)
    id_material = Column(Integer, ForeignKey('materiales.id_material'), unique=True, nullable=False)
    
    cantidad_stock = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=5.0)
    precio_compra_promedio = Column(Float, default=0.0) # Costo para la empresa
    
    material = relationship('Material', back_populates='inventario')
    
    def to_dict(self):
        return {
            'id_inventario': self.id_inventario,
            'id_material': self.id_material,
            'cantidad_stock': self.cantidad_stock,
            'stock_minimo': self.stock_minimo,
            'precio_compra_promedio': self.precio_compra_promedio
        }

class AtributoRolloImpresion(Base):
    """
    Atributos específicos para materiales que vienen en rollo (Lonas, Vinilos).
    """
    __tablename__ = 'atributos_rollos_impresion'
    
    id_atributo = Column(Integer, primary_key=True, autoincrement=True)
    id_material = Column(Integer, ForeignKey('materiales.id_material'), unique=True, nullable=False)
    
    ancho_fijo_rollo = Column(Float, nullable=False) # El ancho físico del rollo
    es_rollo_continuo = Column(Boolean, default=True)
    
    material = relationship('Material', back_populates='atributos_rollo')
    
    def to_dict(self):
        return {
            'id_atributo': self.id_atributo,
            'id_material': self.id_material,
            'ancho_fijo_rollo': self.ancho_fijo_rollo,
            'es_rollo_continuo': self.es_rollo_continuo
        }

# ==========================================
# 3. SERVICIOS Y REGLAS DE NEGOCIO
# ==========================================

class Servicio(Base):
    """
    Servicios que se venden al cliente.
    """
    __tablename__ = 'servicios'
    
    id_servicio = Column(Integer, primary_key=True, autoincrement=True)
    nombre_servicio = Column(String, nullable=False)
    id_unidad_cobro = Column(Integer, ForeignKey('unidades_medida.id_unidad'), nullable=False)
    precio_base = Column(Float, default=0.0) # Precio de venta base
    
    # Sugerencia por defecto (opcional, el sistema experto debería inferirlo, pero sirve de fallback)
    id_maquina_sugerida = Column(Integer, ForeignKey('maquinas.id_maquina'), nullable=True)
    
    # Relaciones
    unidad_cobro = relationship('UnidadMedida', back_populates='servicios')
    maquina_sugerida = relationship('Maquina', foreign_keys=[id_maquina_sugerida])
    maquinas_validas = relationship('MaquinaServicio', back_populates='servicio')
    materiales_validos = relationship('ServicioMaterial', back_populates='servicio')
    detalles_pedido = relationship('DetallePedido', back_populates='servicio')
    
    def __repr__(self):
        return f"<Servicio(id={self.id_servicio}, nombre='{self.nombre_servicio}')>"
    
    def to_dict(self):
        """Diccionario compatible con models.py para no romper UI"""
        return {
            'id_servicio': self.id_servicio,
            'nombre_servicio': self.nombre_servicio,
            'unidad_cobro': self.unidad_cobro.abreviacion if self.unidad_cobro else '',
            'precio_base': self.precio_base,
            'id_maquina_sugerida': self.id_maquina_sugerida,
            'nombre_maquina': self.maquina_sugerida.nombre if self.maquina_sugerida else None,
            'tipo_maquina': self.maquina_sugerida.tipo_maquina.nombre_tipo if self.maquina_sugerida and self.maquina_sugerida.tipo_maquina else None
        }

class MaquinaServicio(Base):
    """
    REGLA: Qué máquinas pueden realizar qué servicio.
    """
    __tablename__ = 'maquinas_servicios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_maquina = Column(Integer, ForeignKey('maquinas.id_maquina'), nullable=False)
    id_servicio = Column(Integer, ForeignKey('servicios.id_servicio'), nullable=False)
    es_recomendada = Column(Boolean, default=False) # Preferencia del experto
    
    __table_args__ = (UniqueConstraint('id_maquina', 'id_servicio'),)
    
    maquina = relationship('Maquina', back_populates='servicios_compatibles')
    servicio = relationship('Servicio', back_populates='maquinas_validas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_maquina': self.id_maquina,
            'id_servicio': self.id_servicio,
            'es_recomendada': bool(self.es_recomendada)
        }

class ServicioMaterial(Base):
    """
    REGLA: Qué materiales son válidos para un servicio.
    """
    __tablename__ = 'servicios_materiales'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_servicio = Column(Integer, ForeignKey('servicios.id_servicio'), nullable=False)
    id_material = Column(Integer, ForeignKey('materiales.id_material'), nullable=False)
    es_preferido = Column(Boolean, default=False)
    
    __table_args__ = (UniqueConstraint('id_servicio', 'id_material'),)
    
    servicio = relationship('Servicio', back_populates='materiales_validos')
    material = relationship('Material', back_populates='servicios_compatibles')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_servicio': self.id_servicio,
            'id_material': self.id_material,
            'es_preferido': bool(self.es_preferido)
        }

# ==========================================
# 4. TRANSACCIONALES (PEDIDOS)
# ==========================================

class Cliente(Base):
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
        return {
            'id_cliente': self.id_cliente,
            'nombre_completo': self.nombre_completo,
            'telefono': self.telefono,
            'email': self.email,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

class EstadoPedido(Base):
    __tablename__ = 'estados_pedidos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)
    color = Column(String, default='#808080')
    
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

class Pedido(Base):
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
    __tablename__ = 'detalle_pedidos'
    
    id_detalle = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey('pedidos.id_pedido'), nullable=False)
    id_servicio = Column(Integer, ForeignKey('servicios.id_servicio'), nullable=False)
    
    # Elecciones específicas para este ítem
    id_material = Column(Integer, ForeignKey('materiales.id_material'))
    
    descripcion = Column(Text)
    
    # Dimensiones del trabajo (Input del usuario) - Compatible con viejo esquema
    ancho = Column(Float, default=0.0)
    alto = Column(Float, default=0.0)
    
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Float, nullable=False, default=0.0)
    
    # Relaciones
    pedido = relationship('Pedido', back_populates='detalles')
    servicio = relationship('Servicio', back_populates='detalles_pedido')
    material = relationship('Material')
    consumos = relationship('ConsumoMaterial', back_populates='detalle', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<DetallePedido(id={self.id_detalle}, pedido={self.id_pedido}, cantidad={self.cantidad})>"
    
    def to_dict(self):
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
    __tablename__ = 'consumo_materiales'
    
    id_consumo = Column(Integer, primary_key=True, autoincrement=True)
    id_detalle = Column(Integer, ForeignKey('detalle_pedidos.id_detalle'), nullable=False)
    id_material = Column(Integer, ForeignKey('materiales.id_material'), nullable=False)
    cantidad_usada = Column(Float, nullable=False)
    fecha_consumo = Column(DateTime, default=datetime.now)
    
    # Relaciones
    detalle = relationship('DetallePedido', back_populates='consumos')
    material = relationship('Material')
    
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


# ==========================================
# 5. USUARIOS Y PERMISOS
# ==========================================

class Rol(Base):
    """Roles del sistema (Admin, Operador, etc.)"""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre_rol = Column(String, nullable=False, unique=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
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
    """Usuarios del sistema con autenticación"""
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    rol_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    ultimo_acceso = Column(DateTime, nullable=True)
    activo = Column(Integer, default=1)
    
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
        """Verifica si el usuario tiene permiso para realizar una acción en un panel"""
        if self.rol and self.rol.es_admin():
            return True
        if self.rol:
            for permiso in self.rol.permisos:
                if permiso.panel == panel and permiso.permiso == accion:
                    return True
        return False
    
    def obtener_paneles_permitidos(self):
        """Retorna lista de paneles a los que tiene acceso"""
        if self.rol and self.rol.es_admin():
            return ['todos']
        paneles = set()
        if self.rol:
            for permiso in self.rol.permisos:
                paneles.add(permiso.panel)
        return list(paneles)


class Permiso(Base):
    """Permisos por rol y panel"""
    __tablename__ = 'permisos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rol_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    panel = Column(String, nullable=False)
    permiso = Column(String, nullable=False)
    
    __table_args__ = (UniqueConstraint('rol_id', 'panel', 'permiso'),)
    
    rol = relationship('Rol', back_populates='permisos')
    
    def __repr__(self):
        return f"<Permiso(rol_id={self.rol_id}, panel='{self.panel}', permiso='{self.permiso}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'rol_id': self.rol_id,
            'panel': self.panel,
            'permiso': self.permiso,
            'nombre_rol': self.rol.nombre_rol if self.rol else None
        }
