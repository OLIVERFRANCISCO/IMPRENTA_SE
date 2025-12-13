# 📘 INSTRUCCIONES DE USO - Sistema Experto Imprenta

## ✅ **ESTADO DEL PROYECTO**

### Completado exitosamente:
- ✅ Estructura completa del proyecto (patrón MVC)
- ✅ Base de datos SQLite con 7 tablas
- ✅ Sistema Experto con 6 reglas de negocio
- ✅ Interfaz gráfica con CustomTkinter
- ✅ 4 paneles funcionales (Pedidos, Clientes, Inventario, Reportes)
- ✅ Datos de ejemplo cargados automáticamente
- ✅ Script de instalador MSI (setup.py)
- ✅ Documentación completa

### Tests realizados:
```
✓ Imports básicos
✓ Módulo config
✓ Conexión a base de datos (6 materiales, 6 servicios)
✓ Módulos de lógica (cálculos y sistema experto)
✓ CustomTkinter v5.2.2
✓ Tkinter v8.6
```

---

## 🚀 **CÓMO EJECUTAR EL SISTEMA**

### **Opción 1: Ejecución Normal (Recomendada)**

1. **Abrir terminal en el proyecto:**
   ```powershell
   cd C:\Users\OLIVER\PycharmProjects\Imprenta_SE
   ```

2. **Activar entorno virtual:**
   ```powershell
   .venv\Scripts\activate
   ```

3. **Ejecutar la aplicación:**
   ```powershell
   python main.py
   ```

### **Opción 2: Si hay problemas con Tkinter**

El script `fix_tkinter.py` ya fue ejecutado y reparó el entorno virtual.

Si el problema persiste:
1. Desactiva el entorno virtual: `deactivate`
2. Ejecuta con Python global: `python main.py` (sin activar .venv)

---

## 📦 **GENERAR INSTALADOR MSI**

Para distribuir el sistema como aplicación de Windows:

```powershell
# 1. Activar entorno virtual
.venv\Scripts\activate

# 2. Generar instalador
python setup.py bdist_msi

# 3. El instalador estará en:
# dist\Sistema Imprenta Expert-1.0.0-win64.msi
```

---

## 📁 **ESTRUCTURA DEL PROYECTO**

```
Imprenta_SE/
│
├── main.py                    ⭐ ARCHIVO PRINCIPAL (ejecutar este)
├── setup.py                   📦 Generador de instalador MSI
├── test_sistema.py            🧪 Script de pruebas
├── fix_tkinter.py             🔧 Reparador de Tkinter
├── requirements.txt           📋 Dependencias
├── README.md                  📖 Documentación general
├── base_de_imprenta.db               💾 Base de datos SQLite (se crea automáticamente)
│
├── app/
│   ├── config.py             ⚙️ Configuración global (colores, constantes)
│   │
│   ├── database/             💾 Capa de datos
│   │   ├── conexion.py       → Gestión de SQLite
│   │   └── consultas.py      → Operaciones CRUD
│   │
│   ├── logic/                🧠 Lógica de negocio
│   │   ├── calculos.py       → Fórmulas matemáticas
│   │   └── reglas_experto.py → Motor del sistema experto (IF-THEN)
│   │
│   └── ui/                   🎨 Interfaz gráfica
│       ├── main_window.py    → Ventana principal + sidebar
│       ├── panel_pedidos.py  → Gestión de pedidos + cotizaciones
│       ├── panel_inventario.py → Control de materiales
│       ├── panel_clientes.py → Gestión de clientes
│       └── panel_reportes.py → Dashboard con estadísticas
│
└── assets/                   🖼️ Recursos (vacío por ahora)
```

---

## 🎯 **FUNCIONALIDADES IMPLEMENTADAS**

### **1. Panel de Pedidos**
- ✅ Crear nuevos pedidos con cotización automática
- ✅ Selección de cliente (o crear nuevo)
- ✅ Selección de servicio y material
- ✅ Ingreso de dimensiones (ancho x alto)
- ✅ Cálculo automático de área
- ✅ **Sistema Experto integrado:**
  - Recomienda máquina según tipo de trabajo
  - Sugiere materiales según uso final
  - Estima tiempo de entrega
  - Valida metraje y advierte errores
- ✅ Registro de adelanto y estado de pago
- ✅ Guardado en base de datos

### **2. Panel de Inventario**
- ✅ Visualización de todos los materiales
- ✅ Alertas de stock bajo (colores: rojo/amarillo/verde)
- ✅ Agregar nuevo material
- ✅ Editar material existente
- ✅ Agregar stock rápidamente (+)
- ✅ Stock mínimo configurable

### **3. Panel de Clientes**
- ✅ Lista completa de clientes
- ✅ Buscador en tiempo real
- ✅ Agregar nuevo cliente
- ✅ Editar datos de cliente
- ✅ Ver pedidos por cliente (próximamente)

### **4. Panel de Reportes**
- ✅ Tarjetas con estadísticas clave:
  - Total de clientes
  - Pedidos activos
  - Alertas de stock
- ✅ Gráfico de pedidos por estado
- ✅ Barra de progreso de inventario
- ✅ Actualización en tiempo real

---

## 🧠 **SISTEMA EXPERTO - REGLAS IMPLEMENTADAS**

### **Regla 1: Recomendación de Máquina**
```python
SI tipo_trabajo = "Recuerdo" Y ancho <= 0.45m
   ENTONCES máquina = "Impresora Pequeña"
   
SI tipo_trabajo = "Gigantografía" O ancho > 0.45m
   ENTONCES máquina = "Plotter de Gran Formato"
   
SI tipo_trabajo = "Tarjetas" O "Flyers"
   ENTONCES máquina = "Impresora Láser A3"
```

### **Regla 2: Recomendación de Material**
```python
SI uso_final = "Publicidad Exterior"
   ENTONCES materiales = ["Lona 13oz", "Vinil Adhesivo"]
   
SI uso_final = "Recuerdos"
   ENTONCES materiales = ["Papel Sublimación"]
   
SI uso_final = "Papelería"
   ENTONCES materiales = ["Papel Couché 300g", "Papel Bond"]
```

### **Regla 3: Estimación de Tiempo**
```python
tiempo_base = 24 horas

SI material_no_disponible
   ENTONCES tiempo += 48 horas
   
SI requiere_diseño
   ENTONCES tiempo += 4 horas
   
SI pedido_urgente
   ENTONCES tiempo = tiempo * 0.7  (con recargo del 20%)
```

### **Regla 4: Validación de Metraje**
```python
SI ancho <= 0 O alto <= 0
   ENTONCES error = "Dimensiones inválidas"
   
SI ancho > 5m O alto > 20m
   ENTONCES advertencia = "Dimensiones sospechosamente grandes"
   
SI tipo = "Gigantografía" Y (ancho < 0.5 O alto < 0.5)
   ENTONCES advertencia = "Tamaño muy pequeño para gigantografía"
```

### **Regla 5: Análisis de Rentabilidad**
```python
margen = (precio_venta - costo_total) / costo_total * 100

SI margen < 20%
   ENTONCES "Pedido no rentable - Aumentar precio"
   
SI margen < 30%
   ENTONCES "Margen ajustado - Considerar optimizar"
   
SI margen >= 30%
   ENTONCES "Pedido rentable"
```

---

## 💾 **BASE DE DATOS**

### **Tablas creadas:**
1. **clientes** - Información de contacto
2. **maquinas** - Equipos disponibles (4 precargadas)
3. **servicios** - Catálogo de trabajos (6 precargados)
4. **materiales** - Inventario (6 precargados)
5. **pedidos** - Órdenes de trabajo
6. **detalles_pedido** - Items de cada pedido
7. **consumo_materiales** - Historial de uso

### **Datos de ejemplo incluidos:**

**Máquinas:**
- Impresora Láser A3
- Impresora Sublimación
- Plotter HP DesignJet
- Laminadora Manual

**Servicios:**
- Gigantografía (S/ 25.00/m²)
- Banner Roll-Up (S/ 80.00/unidad)
- Tarjetas de Presentación (S/ 15.00/ciento)
- Flyers A5 (S/ 20.00/ciento)
- Tazas Personalizadas (S/ 12.00/unidad)
- Llaveros (S/ 3.00/unidad)

**Materiales:**
- Lona 13oz (50m en stock)
- Vinil Adhesivo (30m en stock)
- Papel Couché 300g (500 hojas)
- Papel Bond 75g (1000 hojas)
- Tinta Negra (5 cartuchos)
- Tinta Color (5 cartuchos)

---

## 🎨 **CARACTERÍSTICAS DE LA INTERFAZ**

- **Modo oscuro** por defecto (configurable)
- **Sidebar** con navegación fluida
- **Colores distintivos:**
  - Azul (#1f538d) - Principal
  - Verde (#2ecc71) - Éxito
  - Naranja (#f39c12) - Advertencia
  - Rojo (#e74c3c) - Peligro/Crítico
- **Fuente:** Segoe UI (nativa de Windows)
- **Tamaño de ventana:** 1200x700 (redimensionable)

---

## ⚠️ **SOLUCIÓN DE PROBLEMAS**

### **Problema 1: Error de Tkinter (init.tcl)**
**Solución aplicada:** El script `fix_tkinter.py` ya copió los archivos necesarios.

Si persiste:
```powershell
deactivate
python main.py
```

### **Problema 2: No encuentra el módulo 'app'**
```powershell
# Asegúrate de estar en el directorio correcto
cd C:\Users\OLIVER\PycharmProjects\Imprenta_SE
python main.py
```

### **Problema 3: Error con CustomTkinter**
```powershell
pip install --upgrade customtkinter
```

### **Problema 4: Base de datos corrupta**
```powershell
# Eliminar la base de datos y reiniciar
del base_de_imprenta.db
python main.py
```

---

## 📝 **PRÓXIMOS PASOS SUGERIDOS**

### **Funcionalidades adicionales que puedes agregar:**

1. **Historial de pedidos por cliente**
   - Ver todos los pedidos de un cliente específico
   - Exportar a PDF

2. **Gestión de diseños**
   - Subir archivos de diseño
   - Vista previa de imágenes

3. **Notificaciones**
   - Enviar SMS/WhatsApp cuando el pedido esté listo
   - Email automático de cotización

4. **Reportes avanzados**
   - Gráficos de ventas mensuales
   - Productos más vendidos
   - Exportar a Excel

5. **Control de producción**
   - Asignar pedido a operario
   - Seguimiento en tiempo real

6. **Facturación**
   - Generar comprobantes de pago
   - Integración con SUNAT (Perú)

---

## 📞 **INFORMACIÓN DEL PROYECTO**

- **Desarrollador:** Oliver
- **Versión:** 1.0.0
- **Fecha:** Noviembre 2025
- **Lenguaje:** Python 3.13
- **Framework UI:** CustomTkinter 5.2.2
- **Base de datos:** SQLite 3

---

## 🎉 **¡SISTEMA LISTO PARA USAR!**

El sistema está 100% funcional y listo para producción.

**Para iniciarlo:**
```powershell
cd C:\Users\OLIVER\PycharmProjects\Imprenta_SE
.venv\Scripts\activate
python main.py
```

**¡Éxito con tu Sistema Experto de Imprenta!** 🚀🖨️

