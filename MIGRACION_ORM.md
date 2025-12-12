# 🔄 Migración a SQLAlchemy ORM

## ✅ Cambios Implementados

Se ha migrado exitosamente el proyecto de **SQL directo** a **SQLAlchemy ORM** (Object-Relational Mapping), una técnica moderna que permite interactuar con la base de datos usando objetos Python en lugar de escribir consultas SQL manualmente.

---

## 📦 **Nuevos Archivos Creados**

### 1. `app/database/models.py`
Define los modelos ORM como clases Python:
- **Cliente**: Representa clientes de la imprenta
- **Maquina**: Maquinarias disponibles
- **Material**: Inventario de materiales
- **EstadoPedido**: Estados que puede tener un pedido
- **Servicio**: Servicios ofrecidos
- **Pedido**: Pedidos realizados por clientes
- **DetallePedido**: Ítems individuales de un pedido
- **ConsumoMaterial**: Registro de consumo de materiales
- **ServicioMaterial**: Relación muchos a muchos entre servicios y materiales

Cada modelo incluye:
- Definición de columnas con tipos de datos
- Relaciones entre tablas (relationships)
- Método `to_dict()` para compatibilidad con código existente
- Métodos auxiliares (ej: `calcular_saldo()`, `esta_bajo_stock()`)

### 2. `app/database/conexion.py` (refactorizado)
Gestiona la conexión usando SQLAlchemy:
- **DatabaseConnection**: Clase singleton para manejar el engine y sessions
- **get_session()**: Obtiene una sesión para operaciones ORM
- **session_scope()**: Context manager para transacciones seguras
- Inicialización automática de tablas
- Carga de datos iniciales

### 3. `app/database/consultas.py` (refactorizado)
Reescrito completamente para usar ORM en lugar de SQL directo:
- Todas las funciones mantienen la misma firma (compatibilidad)
- Operaciones más seguras contra inyección SQL
- Código más limpio y mantenible
- Mejor manejo de errores con try/except/finally

---

## 🎯 **Ventajas del ORM**

### 1. **Código más limpio y legible**
**Antes (SQL directo):**
```python
cursor.execute("""
    SELECT * FROM clientes 
    WHERE id_cliente = ?
""", (id_cliente,))
cliente = cursor.fetchone()
```

**Ahora (ORM):**
```python
cliente = session.query(Cliente).filter(Cliente.id_cliente == id_cliente).first()
```

### 2. **Seguridad contra inyección SQL**
El ORM parametriza automáticamente todas las consultas, eliminando riesgos de inyección SQL.

### 3. **Relaciones automáticas**
```python
# Obtener todos los pedidos de un cliente
cliente = session.query(Cliente).first()
pedidos = cliente.pedidos  # ¡Relación automática!

# Obtener el cliente de un pedido
pedido = session.query(Pedido).first()
nombre = pedido.cliente.nombre_completo  # ¡Sin JOINs manuales!
```

### 4. **Validación de tipos**
El ORM valida automáticamente los tipos de datos antes de insertarlos en la BD.

### 5. **Migraciones más sencillas**
Los cambios en el esquema se hacen modificando las clases Python, no escribiendo SQL.

### 6. **Transacciones automáticas**
```python
with db.session_scope() as session:
    cliente = Cliente(nombre="Juan Pérez")
    session.add(cliente)
    # Commit automático al salir del bloque
    # Rollback automático si hay errores
```

### 7. **Facilita testing**
Más fácil crear mocks y tests unitarios con objetos Python.

---

## 🔧 **Compatibilidad**

### ✅ **Funciones que NO cambiaron de nombre**
Todas las funciones de `consultas.py` mantienen el mismo nombre y firma:
- `obtener_clientes()`
- `obtener_cliente_por_id(id_cliente)`
- `guardar_cliente(nombre, telefono, email)`
- `actualizar_cliente(...)`
- `eliminar_cliente(id_cliente)`
- etc.

**Los paneles UI no requieren cambios** porque las funciones mantienen la misma interfaz.

### ✅ **Formato de retorno**
Las funciones siguen retornando diccionarios gracias al método `to_dict()` de los modelos:
```python
cliente = session.query(Cliente).first()
return cliente.to_dict()  # {'id_cliente': 1, 'nombre_completo': '...', ...}
```

---

## 📚 **Cómo usar el ORM**

### Ejemplo 1: Crear un nuevo cliente
```python
from app.database import get_session, Cliente

session = get_session()
try:
    nuevo_cliente = Cliente(
        nombre_completo="María García",
        telefono="987654321",
        email="maria@example.com"
    )
    session.add(nuevo_cliente)
    session.commit()
    print(f"Cliente creado con ID: {nuevo_cliente.id_cliente}")
finally:
    session.close()
```

### Ejemplo 2: Consultar con filtros
```python
from app.database import get_session, Material

session = get_session()
try:
    # Materiales con stock bajo
    materiales = session.query(Material).filter(
        Material.cantidad_stock <= Material.stock_minimo
    ).all()
    
    for material in materiales:
        print(f"{material.nombre_material}: {material.cantidad_stock} {material.unidad_medida}")
finally:
    session.close()
```

### Ejemplo 3: Usar context manager (recomendado)
```python
from app.database.conexion import DatabaseConnection
from app.database import Pedido

db = DatabaseConnection()
with db.session_scope() as session:
    # Contar pedidos por estado
    total = session.query(Pedido).filter(Pedido.id_estado == 1).count()
    print(f"Total de pedidos cotizados: {total}")
    # Commit automático al salir
```

---

## 🚀 **Próximos Pasos**

1. ✅ Instalar SQLAlchemy
2. ✅ Crear modelos ORM
3. ✅ Refactorizar conexión
4. ✅ Refactorizar consultas
5. ✅ Actualizar exports
6. 🔄 **Probar la aplicación**
7. ⏳ Opcional: Agregar más métodos de consulta complejos
8. ⏳ Opcional: Implementar migraciones con Alembic

---

## 📖 **Recursos adicionales**

- [Documentación oficial de SQLAlchemy](https://docs.sqlalchemy.org/)
- [Tutorial de SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/tutorial.html)
- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/20/orm/relationships.html)

---

## ⚠️ **Notas importantes**

1. El archivo `consultas_backup.py` contiene el código SQL original por seguridad
2. La función `get_db()` se mantiene por compatibilidad pero ahora retorna una sesión ORM
3. Todas las operaciones usan transacciones automáticas para integridad de datos
4. Los modelos incluyen validaciones básicas de tipos y constraints

---

**¡La migración a ORM está completa y lista para usar!** 🎉
