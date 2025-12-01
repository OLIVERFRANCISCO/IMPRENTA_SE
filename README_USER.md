# 🎨 GUÍA RÁPIDA 


**Dónde:** Panel "Lista de Pedidos"

**Cómo usar:**
1. Abre el panel "Lista de Pedidos"
2. Cada pedido tiene un selector desplegable con su estado actual
3. Haz clic en el selector
4. Elige el nuevo estado
5. ✅ El pedido se actualiza automáticamente

**Estados disponibles:**
- 🔵 Cotizado
- 🔷 Confirmado  
- 🟠 En Diseño
- 🟣 Previsualización Enviada
- 🟡 En Preparación
- 🟢 Listo para Entrega
- ✅ Entregado
- 🔴 Cancelado

---

### 2️⃣ Colores Visuales por Estado

**Qué hace:**
Cada pedido tiene una **barra de color** a la izquierda que indica su estado visualmente.

**Beneficios:**
- Identificación rápida del estado
- Interfaz más intuitiva
- Mejor organización visual

---

### 3️⃣ Filtros Avanzados

**Dónde:** Panel "Lista de Pedidos" (parte superior)

#### Filtro por Estado
- Selector con todos los estados disponibles
- "Todos" para ver todos los pedidos

#### Filtro por Fechas
- **Desde:** Fecha de inicio (YYYY-MM-DD)
- **Hasta:** Fecha de fin (YYYY-MM-DD)
- Ejemplo: `2025-12-01`

**Botones:**
- **Aplicar Filtros:** Ejecuta el filtro
- **Limpiar:** Quita todos los filtros

---

### 4️⃣ Ordenamiento de Resultados

**Dónde:** Encabezados de la tabla en "Lista de Pedidos"

**Cómo usar:**
- Haz clic en **▲** para ordenar ascendente (0→9, A→Z, Antiguo→Reciente)
- Haz clic en **▼** para ordenar descendente (9→0, Z→A, Reciente→Antiguo)

**Campos ordenables:**
- ID del pedido
- Fecha de ingreso
- Fecha de entrega
- Costo total
- Estado

---

### 5️⃣ Paginación

**Dónde:** Parte inferior de "Lista de Pedidos"

**Controles:**
- **← Anterior:** Ir a la página anterior
- **Página X de Y:** Indicador de posición
- **Siguiente →:** Ir a la siguiente página
- **Total: X pedidos:** Contador total

**Nota:** Se muestran 20 pedidos por página.

---

### 6️⃣ Materiales Filtrados por Servicio

**Dónde:** Panel "Nuevo Pedido"

**Qué hace:**
Al seleccionar un servicio, el selector de materiales **muestra solo materiales compatibles**.

**Ejemplo:**
- Seleccionas **"Gigantografía"**
- El material muestra solo:
  - Lona 13 onz
  - Lona 8 onz
  - Vinil con Laminado Mate
  - Vinil con Laminado Brillo
  - Vinil sin Laminado

**Beneficios:**
- No te equivocas de material
- Más rápido seleccionar
- Evita errores de producción

---

## 🎯 FLUJO DE TRABAJO RECOMENDADO

### Crear un Pedido
1. **Nuevo Pedido** → Seleccionar cliente
2. Elegir **Servicio** (ej: Gigantografía)
3. El **Material** se filtra automáticamente
4. Seleccionar material compatible
5. Completar dimensiones y cantidad
6. **Guardar** → El pedido inicia en estado "Cotizado"

### Seguimiento del Pedido
1. Ir a **Lista de Pedidos**
2. Buscar el pedido (usar filtros si es necesario)
3. Ver el **color** para identificar el estado
4. **Cambiar estado** según el progreso:
   - Cliente confirma → **"Confirmado"**
   - Inicias diseño → **"En Diseño"**
   - Envías vista previa → **"Previsualización Enviada"**
   - Cliente aprueba → **"En Preparación"**
   - Terminas trabajo → **"Listo para Entrega"**
   - Cliente recoge → **"Entregado"**

### Análisis y Reportes
1. Ir a **Lista de Pedidos**
2. Usar filtros:
   - Estado = "En Preparación" → Ver trabajos pendientes
   - Fechas de la semana → Ver pedidos de la semana
3. Ordenar por:
   - Fecha Entrega (ASC) → Ver entregas próximas
   - Total (DESC) → Ver pedidos más valiosos

---

#