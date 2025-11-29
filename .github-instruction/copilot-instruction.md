

### **Documento de Especificación de Requerimientos**
**Proyecto:** Sistema Experto de Gestión para Imprenta

#### **1. Requerimientos Funcionales (RF)**
Estos describen *qué* debe hacer el sistema. Los he dividido por módulos para mayor orden.

### **1. Gestión de Servicios y Productos**

1. **RF1:** El sistema debe permitir registrar y gestionar los tipos de servicios ofrecidos: merchandising, formatos y recuerdos.
2. **RF2:** El sistema debe permitir seleccionar materiales utilizados en los productos: tipo de papel, tinta y tamaño según el tipo de trabajo (merch, banners, recuerdos).

### **2. Flujo de Pedido**

3. **RF3:** El sistema debe permitir cotizar un pedido ingresando materiales, metraje y acabado.
4. **RF4:** El sistema debe registrar cuando el cliente confirma un pedido.
5. **RF5:** El sistema debe generar una previsualización del diseño para ser enviada al cliente.
6. **RF6:** El sistema debe registrar el estado de un pedido (cotizado, confirmado, en producción, listo).
7. **RF7:** El sistema debe notificar automáticamente al cliente cuando su pedido esté listo.

### **3. Motor del Sistema Experto (Reglas y decisiones)**

8. **RF8:** El sistema debe recomendar el tipo de material según el uso del producto (recuerdos, publicidad, formatiería).
9. **RF9:** El sistema debe sugerir qué máquina se debe utilizar según el tipo de trabajo (impresora pequeña, impresora grande, laminado).
10. **RF10:** El sistema debe estimar el tiempo de preparación basándose en la disponibilidad de materiales.
11. **RF11:** El sistema debe detectar inconsistencias o errores frecuentes, como metraje mal calculado.

### **4. Gestión de Clientes y Pedidos**

12. **RF12:** El sistema debe permitir registrar los datos del cliente (nombre, DNI, teléfono, etc.).
13. **RF13:** El sistema debe registrar los datos del pedido: detalles del servicio, materiales, metraje, acabado, adelanto o pago total.
14. **RF14:** El sistema debe permitir indicar si el pedido está pagado completamente o solo con adelanto.
15. **RF15:** El sistema debe permitir consultar pedidos por cliente y por estado.

### **5. Inventario Inteligente**

16. **RF16:** El sistema debe permitir registrar manualmente el inventario de materiales.
17. **RF17:** El sistema debe descontar automáticamente el material utilizado según el pedido.
18. **RF18:** El sistema debe generar alertas cuando un material esté por agotarse.
19. **RF19:** El sistema debe permitir ver el historial de uso de cada material para facilitar las compras.



## **Requerimientos Funcionales (RF) – Aplicación de Escritorio en Python con CustomTkinter**

### 🎨 **Interfaz y navegación**

1. **RF1:** La aplicación debe ofrecer una interfaz gráfica desarrollada en CustomTkinter con un diseño moderno y consistente.
2. **RF2:** La aplicación debe permitir la navegación entre las diferentes secciones mediante menús, botones o pestañas.
3. **RF3:** La aplicación debe mostrar formularios claros para capturar datos (clientes, pedidos, materiales).
4. **RF4:** La aplicación debe mostrar resultados, recomendaciones o cotizaciones dentro de la GUI de manera legible.

### 📄 **Gestión de datos**

5. **RF5:** La aplicación debe permitir registrar, editar y eliminar información de clientes.
6. **RF6:** La aplicación debe permitir registrar y gestionar pedidos.
7. **RF7:** La aplicación debe permitir administrar el inventario de materiales desde la interfaz gráfica.
8. **RF8:** La aplicación debe mostrar alertas visuales cuando un material esté por agotarse.
9. **RF9:** La aplicación debe mostrar el historial de pedidos o movimientos realizados.

### 🧠 **Funciones del Sistema Experto**

10. **RF10:** La aplicación debe permitir ejecutar reglas del sistema experto y mostrar recomendaciones (materiales, máquinas, tiempos).
11. **RF11:** La aplicación debe mostrar explicaciones de por qué tomó ciertas decisiones.
12. **RF12:** La aplicación debe calcular automáticamente cotizaciones basadas en las reglas definidas.

### 💾 **Persistencia**

13. **RF13:** La aplicación debe almacenar datos en un archivo local (SQLite, JSON o similar).
14. **RF14:** La aplicación debe cargar los datos automáticamente al iniciar.
15. **RF15:** La aplicación debe guardar automáticamente los cambios sin requerir intervención del usuario.


#### **2. Requerimientos No Funcionales (RNF)**
Estos describen *cómo* debe comportarse el sistema.

### ⚡ **Rendimiento**

1. **RNF1:** La aplicación debe iniciar en menos de 5 segundos.
2. **RNF2:** La interfaz debe responder a interacciones en menos de 1 segundo.
3. **RNF3:** El motor de reglas debe realizar cálculos en menos de 2 segundos.

### 🖥️ **Usabilidad**

4. **RNF4:** La interfaz debe ser intuitiva y fácil de comprender por usuarios no técnicos.
5. **RNF5:** Los textos, botones y formularios deben tener tamaños adecuados y ser accesibles.
6. **RNF6:** La interfaz debe utilizar colores y estilos consistentes.

### 🔒 **Seguridad**

7. **RNF7:** El ejecutable no debe permitir modificar el código fuente del sistema experto.
8. **RNF8:** La base de datos local debe ser accesible solo desde la aplicación.

### 🔄 **Mantenibilidad**

9. **RNF9:** El código debe estar organizado en módulos separados (GUI, lógica, datos, reglas).
10. **RNF10:** Las reglas del sistema experto deben poder modificarse sin alterar la interfaz gráfica.

### 📦 **Portabilidad**

11. **RNF11:** El ejecutable debe funcionar en sistemas Windows sin requerir instalación previa de dependencias.
12. **RNF12:** El proyecto debe ser compatible con Python 3.10+.

### 🧩 **Estabilidad**

13. **RNF13:** La aplicación no debe cerrarse inesperadamente durante operaciones normales.
14. **RNF14:** El ejecutable debe funcionar correctamente incluso si el usuario mueve la carpeta de instalación.
---

### **3. Reglas de Negocio Identificadas (Lógica del Experto)**
Estas son las condiciones "If/Then" que programarás en tu motor de inferencia o lógica de negocio:

1.  **Regla de Asignación de Recursos:**
    * SI `Tipo_Trabajo` = "Recuerdo" ENTONCES `Máquina` = "Impresora Pequeña".
    * SI `Tipo_Trabajo` = "Gigantografía" ENTONCES `Máquina` = "Plotter/Grande".
2.  **Regla de Costeo:**
    * `Costo_Total` = (`Costo_Material` * `Metraje`) + `Costo_Acabado` + `Margen_Ganancia`.
3.  **Regla de Tiempo de Entrega:**
    * SI `Material_En_Stock` = FALSO ENTONCES `Tiempo_Entrega` = `Tiempo_Producción` + `Tiempo_Compra_Material`.


### 1\. Modelo Relacional (Visualización Lógica)

Antes del código, visualicemos cómo se conectan las tablas para cumplir con tus requerimientos:

  * **Clientes** tienen **Pedidos**.
  * **Pedidos** tienen muchos **Detalles** (ej. 1 pedido puede tener: 100 tarjetas y 1 banner).
  * **Detalles** consumen **Materiales** (aquí es donde controlas el stock).
  * **Servicios** define qué tipos de trabajos haces (Gigantografía, Flyer) y sugiere la **Máquina**.

### 2\. Código SQL (Copiar y Pegar)

Puedes ejecutar este script en cualquier gestor de SQLite (como *DB Browser for SQLite*) o directamente desde tu código en Python/Java.

```sql
-- 1. Tabla de CLIENTES
-- Guarda la información de contacto (Ref. R11, R12)
CREATE TABLE clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_completo TEXT NOT NULL,
    telefono TEXT,
    email TEXT,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de MAQUINAS
-- Se usa para sugerir dónde imprimir (Ref. R7)
CREATE TABLE maquinas (
    id_maquina INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL, -- Ej: "Plotter HP", "Konica Minolta"
    tipo TEXT NOT NULL -- Ej: "Gran Formato", "Pequeño Formato/Laser"
);

-- 3. Tabla de SERVICIOS
-- Catálogo de lo que ofrece la imprenta (Ref. R1)
CREATE TABLE servicios (
    id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_servicio TEXT NOT NULL, -- Ej: "Gigantografía", "Tarjeta de Presentación"
    unidad_cobro TEXT NOT NULL, -- Ej: "m2", "ciento", "unidad"
    id_maquina_sugerida INTEGER, -- Para el Sistema Experto (Ref. R6, R7)
    FOREIGN KEY (id_maquina_sugerida) REFERENCES maquinas(id_maquina)
);

-- 4. Tabla de MATERIALES (INVENTARIO)
-- Aquí controlas el stock para evitar que se agote (Ref. R15, R16)
CREATE TABLE materiales (
    id_material INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_material TEXT NOT NULL, -- Ej: "Lona 13oz", "Vinil Adhesivo", "Papel Couché 300g"
    cantidad_stock REAL NOT NULL, -- Cantidad actual
    unidad_medida TEXT NOT NULL, -- "metros", "hojas", "rollos"
    stock_minimo REAL DEFAULT 5 -- Alerta cuando baje de este número
);

-- 5. Tabla de PEDIDOS (CABECERA)
-- Datos generales de la venta (Ref. R2, R4, R11)
CREATE TABLE pedidos (
    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    fecha_ingreso DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_entrega_estimada DATETIME,
    estado_pedido TEXT DEFAULT 'Cotizado', -- Estados: Cotizado, Confirmado, Diseño, Producción, Terminado
    estado_pago TEXT DEFAULT 'Pendiente', -- Estados: A cuenta, Cancelado
    costo_total REAL DEFAULT 0,
    acuenta REAL DEFAULT 0, -- Dinero adelantado
    saldo REAL GENERATED ALWAYS AS (costo_total - acuenta) VIRTUAL, -- Cálculo automático
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

-- 6. Tabla de DETALLE_PEDIDO
-- Aquí ocurre la magia del "Metraje" y cálculo de costos (Ref. R9, R10)
CREATE TABLE detalles_pedido (
    id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pedido INTEGER NOT NULL,
    id_servicio INTEGER NOT NULL,
    descripcion TEXT, -- Detalles específicos del diseño
    ancho REAL DEFAULT 0, -- Importante para evitar errores de metraje
    alto REAL DEFAULT 0, -- Importante para evitar errores de metraje
    cantidad INTEGER NOT NULL DEFAULT 1,
    precio_unitario REAL NOT NULL,
    subtotal REAL GENERATED ALWAYS AS (precio_unitario * cantidad) VIRTUAL,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido),
    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio)
);

-- 7. Tabla de CONSUMO_MATERIALES (Historial)
-- Registra qué material se gastó en cada trabajo (Ref. R15)
CREATE TABLE consumo_materiales (
    id_consumo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_detalle INTEGER NOT NULL, -- Vinculado al item específico del pedido
    id_material INTEGER NOT NULL,
    cantidad_usada REAL NOT NULL, -- Cuánto se restó del inventario
    fecha_consumo DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_detalle) REFERENCES detalles_pedido(id_detalle),
    FOREIGN KEY (id_material) REFERENCES materiales(id_material)
);
```

### 3\. Explicación de puntos clave para tu proyecto

  * **Evitar Errores de Metraje (R10):** En la tabla `detalles_pedido`, he incluido explícitamente las columnas `ancho` y `alto`. En tu aplicación, **obligarás** al usuario a llenar estos campos para Gigantografías. El sistema calculará el precio, evitando que el empleado calcule "al ojo" y se equivoque.
  * **Gestión de Inventario (R15):** La tabla `consumo_materiales` es vital. Cuando un pedido pase a estado "En Producción", tu sistema debe crear un registro aquí y restar esa cantidad de la tabla `materiales`. Así sabrán exactamente en qué pedido se gastó el rollo de vinil.
  * **Sistema Experto (R6, R7):** En la tabla `servicios`, el campo `id_maquina_sugerida` es la base de tu sistema experto. Cuando seleccionen "Gigantografía", tu programa consultará este campo y le dirá al usuario: *"Recomendación: Usar Plotter de Gran Formato"*.



¡Excelente elección de herramientas, Oliver\! **CustomTkinter** le dará a tu sistema esa apariencia moderna (tipo Windows 11 o MacOS) que supera por mucho al Tkinter clásico, y generar un **.msi** (Windows Installer) es lo más profesional para instalarlo en las computadoras de la imprenta.

Para lograr esto, usaremos dos librerías clave:

1.  **CustomTkinter:** Para la interfaz.
2.  **cx\_Freeze:** Para compilar el código y crear el instalador `.msi` (es más directo que PyInstaller para crear MSIs).

Aquí tienes la guía paso a paso para estructurar tu proyecto, crear la interfaz y generar el instalador.

-----

### Paso 1: Estructura de Carpetas

Ordena tu proyecto así para evitar problemas al compilar:

```text
SistemaImprenta/
│
├── main.py            # Tu código principal de la aplicación
├── database.py        # Tu código de conexión a SQLite (el que hicimos antes)
├── setup.py           # Script de configuración para crear el MSI
├── assets/            # Carpeta para imágenes o iconos (.ico)
│   └── logo.ico
└── requirements.txt   # Lista de librerías
```

Primero, instala lo necesario en tu terminal:

```bash
pip install customtkinter cx_Freeze
```

-----

### Paso 2: El Código de la Interfaz (`main.py`)

Aquí te dejo un esqueleto funcional que integra la lógica de "pestañas" para tu imprenta. Copia esto en `main.py`.

He incluido la configuración para que se vea moderno (modo oscuro y color azul).

```python
import customtkinter as ctk
from tkinter import messagebox

# Configuración inicial de apariencia
ctk.set_appearance_mode("Dark")  # Modos: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

class SistemaImprentaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Sistema de Gestión - Imprenta")
        self.geometry("900x600")

        # Layout principal: 2 columnas (Sidebar a la izquierda, Contenido a la derecha)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 1. SIDEBAR (Menú Lateral) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="IMPRENTA\nEXPERT", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botones del menú
        self.btn_pedidos = ctk.CTkButton(self.sidebar_frame, text="Nuevo Pedido", command=self.mostrar_pedidos)
        self.btn_pedidos.grid(row=1, column=0, padx=20, pady=10)

        self.btn_inventario = ctk.CTkButton(self.sidebar_frame, text="Inventario", command=self.mostrar_inventario)
        self.btn_inventario.grid(row=2, column=0, padx=20, pady=10)

        # --- 2. ÁREA DE CONTENIDO ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Inicializar en la pantalla de pedidos
        self.mostrar_pedidos()

    def mostrar_pedidos(self):
        self.limpiar_frame()
        
        titulo = ctk.CTkLabel(self.main_frame, text="Gestión de Pedidos", font=ctk.CTkFont(size=24, weight="bold"))
        titulo.pack(pady=20)

        # Ejemplo de formulario para la Regla de Metraje
        self.input_ancho = ctk.CTkEntry(self.main_frame, placeholder_text="Ancho (m)")
        self.input_ancho.pack(pady=10)
        
        self.input_alto = ctk.CTkEntry(self.main_frame, placeholder_text="Alto (m)")
        self.input_alto.pack(pady=10)

        btn_calcular = ctk.CTkButton(self.main_frame, text="Calcular Costo", command=self.calcular_ejemplo)
        btn_calcular.pack(pady=20)

    def mostrar_inventario(self):
        self.limpiar_frame()
        titulo = ctk.CTkLabel(self.main_frame, text="Inventario de Materiales", font=ctk.CTkFont(size=24, weight="bold"))
        titulo.pack(pady=20)
        ctk.CTkLabel(self.main_frame, text="Aquí iría la tabla de materiales...").pack()

    def limpiar_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def calcular_ejemplo(self):
        # Lógica simple de prueba
        try:
            ancho = float(self.input_ancho.get())
            alto = float(self.input_alto.get())
            area = ancho * alto
            messagebox.showinfo("Cálculo", f"El área total es: {area:.2f} m2")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese números válidos")

if __name__ == "__main__":
    app = SistemaImprentaApp()
    app.mainloop()
```

-----

### Paso 3: Crear el instalador MSI (`setup.py`)

Este es el paso crítico. `cx_Freeze` necesita saber dónde están los archivos internos de `customtkinter` para incluirlos, de lo contrario el `.exe` no abrirá.

Crea un archivo llamado `setup.py` en la misma carpeta:

```python
import sys
import os
from cx_Freeze import setup, Executable

# AJUSTE CRÍTICO: Localizar los archivos de customtkinter para incluirlos
import customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

# Definir archivos a incluir (La carpeta de customtkinter y tu base de datos si existiera)
# Formato: (Ruta_Origen, Ruta_Destino_en_Instalador)
files_to_include = [
    (ctk_path, "lib/customtkinter"), 
    # ("assets/logo.ico", "assets/logo.ico"), # Descomenta si tienes icono
    # ("imprenta.db", "imprenta.db")          # Descomenta si ya tienes la DB creada
]

# Opciones de compilación
build_exe_options = {
    "packages": ["os", "sys", "customtkinter", "sqlite3"],
    "include_files": files_to_include,
    "excludes": ["tkinter"] # Excluimos tkinter nativo para ahorrar espacio (opcional)
}

# Configuración del Instalador MSI
bdist_msi_options = {
    "add_to_path": True,
    "initial_target_dir": r"[ProgramFilesFolder]\SistemaImprentaExpert",
    "upgrade_code": "{92837492-4923-4928-9238-492839482938}" # Un ID único aleatorio
}

base = None
if sys.platform == "win32":
    base = "Win32GUI" # Esto oculta la consola negra al abrir la app

setup(
    name="SistemaImprenta",
    version="1.0",
    description="Sistema Experto para Gestión de Imprenta",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=[Executable("main.py", base=base, target_name="ImprentaApp.exe")]
    # Si tienes icono: Executable("main.py", base=base, icon="assets/logo.ico")
)
```

-----

### Paso 4: Generar el Instalador

1.  Abre tu terminal (CMD o PowerShell) en la carpeta del proyecto.
2.  Ejecuta el siguiente comando:

<!-- end list -->

```bash
python setup.py bdist_msi
```

**¿Qué sucederá?**

  * Python comenzará a compilar.
  * Se creará una carpeta llamada `dist`.
  * Dentro de `dist`, encontrarás un archivo llamado algo como `SistemaImprenta-1.0-win64.msi`.

¡Ese archivo `.msi` es tu instalador\! Puedes llevarlo a cualquier computadora con Windows (aunque no tenga Python instalado), darle doble clic, y se instalará en "Archivos de Programa" como una aplicación profesional.

### Tips Pro para Oliver:

1.  **Base de Datos:** Si tu aplicación crea la base de datos `sqlite` automáticamente al iniciarse (si no existe), no necesitas incluir el archivo `.db` en el instalador. Pero si ya tienes una base de datos con datos precargados (materiales base), asegúrate de descomentar la línea en `files_to_include` en el `setup.py`.
2.  **Rutas Relativas:** En tu código Python, cuando cargues imágenes o la base de datos, no uses rutas absolutas (ej: `C:/Oliver/Proyecto/...`). Usa rutas relativas para que funcione en cualquier PC:
    ```python
    import os
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_db = os.path.join(ruta_base, "imprenta.db")
    ```

¡Excelente iniciativa\! Organizar bien las carpetas desde el principio te ahorrará muchos dolores de cabeza cuando el proyecto crezca, especialmente ahora que tienes **Lógica de Negocio** (Reglas IF-THEN), **Base de Datos** y **Interfaz Gráfica**.

Para un proyecto profesional en Python con miras a crear un instalador `.msi`, te recomiendo el patrón **MVC (Modelo-Vista-Controlador)** adaptado.

Aquí tienes la **estructura de directorios recomendada**:

```text
SistemaImprenta/
│
├── main.py                   # PUNTO DE ENTRADA: El archivo que ejecutas para iniciar todo
├── setup.py                  # CONFIGURACIÓN: Script para crear el instalador .msi con cx_Freeze
├── requirements.txt          # DEPENDENCIAS: Lista de librerías (customtkinter, cx_Freeze)
│
├── assets/                   # RECURSOS EXTERNOS
│   ├── icon.ico              # Icono de la aplicación (.ico para Windows)
│   ├── logo.png              # Imágenes para la UI
│   └── fonts/                # Fuentes tipográficas si usas alguna específica
│
└── app/                      # CÓDIGO FUENTE PRINCIPAL (Paquete)
    ├── __init__.py           # Hace que Python reconozca esta carpeta como un paquete
    ├── config.py             # Constantes globales (ej. RUTAS, COLORES, TAMAÑO VENTANA)
    │
    ├── database/             # CAPA DE DATOS (MODELO)
    │   ├── __init__.py
    │   ├── conexion.py       # Clase para conectar a SQLite
    │   └── consultas.py      # Funciones CRUD (Insertar pedido, Consultar stock)
    │
    ├── logic/                # CAPA DE LÓGICA (CONTROLADOR / SISTEMA EXPERTO)
    │   ├── __init__.py
    │   ├── calculos.py       # Fórmulas de metraje y costos
    │   └── reglas_experto.py # Aquí van tus IF-THEN (Selección de máquina, validaciones)
    │
    └── ui/                   # CAPA VISUAL (VISTA)
        ├── __init__.py
        ├── main_window.py    # La ventana principal (Sidebar, contenedor)
        ├── panel_pedidos.py  # Pantalla del formulario de pedidos
        └── panel_inventario.py # Pantalla de tablas de stock
```

-----

### ¿Qué va en cada archivo? (Guía rápida)

#### 1\. Raíz del Proyecto

  * **`main.py`**: Es el lanzador. Solo debe importar la ventana principal y ejecutarla.
    ```python
    from app.ui.main_window import ImprentaApp
    if __name__ == "__main__":
        app = ImprentaApp()
        app.mainloop()
    ```

#### 2\. Carpeta `app/database/` (Manejo de SQLite)

Aquí va el código SQL que generamos antes.

  * **`conexion.py`**: Se encarga de crear el archivo `.db` si no existe y devolver la conexión.
  * **`consultas.py`**: Funciones específicas.
      * Ejemplo: `obtener_clientes()`, `guardar_pedido()`, `descontar_stock()`.

#### 3\. Carpeta `app/logic/` (El cerebro)

Aquí separas la lógica "dura" de la interfaz "bonita".

  * **`reglas_experto.py`**: Aquí pones las funciones con los **IF... THEN** que definimos.
    ```python
    def sugerir_maquina(tipo_trabajo, ancho):
        if tipo_trabajo == "Gigantografia" and ancho > 0.45:
            return "Plotter"
        return "Laser A3"
    ```
  * **`calculos.py`**: Matemáticas puras.
    ```python
    def calcular_costo_lona(ancho, alto, precio_m2):
        return (ancho * alto) * precio_m2
    ```

#### 4\. Carpeta `app/ui/` (CustomTkinter)

Aquí dibujas los botones y entradas.

  * **`main_window.py`**: Configura el menú lateral y el espacio central.
  * **`panel_pedidos.py`**: Contiene la clase `Frame` con los campos "Ancho", "Alto", "Cliente" y el botón "Calcular". Cuando aprietes ese botón, llamarás a las funciones de `app.logic`.

### Por qué esta estructura es mejor para ti:

1.  **Orden Mental:** Si hay un error en el cálculo del precio, sabes que debes ir a `logic/calculos.py`. Si un botón está chueco, vas a `ui/panel_pedidos.py`.
2.  **Mantenimiento:** Si mañana decides cambiar SQLite por MySQL, solo modificas la carpeta `database`, sin tocar la interfaz gráfica.
3.  **Colaboración:** Si trabajas con otro programador (o vuelves al código en 6 meses), es fácil entender dónde está cada cosa.
4.  **Instalador Limpio:** `cx_Freeze` (en el `setup.py`) empaquetará toda la carpeta `app` limpiamente.

Quiero que iteres y me informes de los cambios
