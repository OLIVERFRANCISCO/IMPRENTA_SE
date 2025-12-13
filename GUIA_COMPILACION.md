# 🔧 Guía de Compilación - Sistema Imprenta Expert

## 📋 Requisitos Previos

### Software Necesario
- ✅ Python 3.13 (instalado)
- ✅ Entorno virtual `.venv` (configurado)
- ✅ Todas las dependencias instaladas

### Verificar Instalación
```bash
# Activar entorno virtual
.venv\Scripts\activate

# Verificar cx_Freeze
python -c "import cx_Freeze; print('cx_Freeze:', cx_Freeze.version)"

# Verificar SQLAlchemy
python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"
```

---

## 🚀 Compilación Rápida (Recomendado)

### Método 1: Script Automático
```bash
# Ejecutar el script de compilación
COMPILAR.bat
```

El script automáticamente:
1. Activa el entorno virtual
2. Verifica dependencias
3. Limpia builds anteriores
4. Compila la aplicación
5. Genera el instalador MSI

### Método 2: Manual
```bash
# 1. Activar entorno virtual
.venv\Scripts\activate

# 2. Limpiar builds anteriores (opcional)
rmdir /s /q build dist

# 3. Compilar
python setup.py bdist_msi
```

---

## 📦 Archivos Generados

Después de la compilación exitosa:

```
Imprenta_SE/
├── build/
│   ├── bdist.win-amd64/
│   └── exe.win-amd64-3.13/
│       ├── ImprentaExpert.exe
│       ├── python313.dll
│       ├── lib/
│       └── ...
└── dist/
    └── Sistema Imprenta Expert-1.6.1-amd64.msi  ← INSTALADOR FINAL
```

---

## ✅ Solución de Errores Comunes

### Error 1: `NoSuchModuleError: sqlalchemy.dialects:sqlite`

**Causa:** SQLAlchemy no incluye el dialecto de SQLite en la compilación.

**Solución:** ✅ **YA CORREGIDO** en setup.py

Ahora incluye:
```python
"sqlalchemy",
"sqlalchemy.dialects.sqlite",  # ← CRÍTICO
"sqlalchemy.orm",
"sqlalchemy.ext.declarative",
```

---

### Error 2: `RuntimeError: input(): lost sys.stdin`

**Causa:** `input()` no funciona en aplicaciones empaquetadas sin consola.

**Solución:** ✅ **YA CORREGIDO** en main.py

Ahora detecta si está empaquetado y usa messagebox:
```python
if getattr(sys, 'frozen', False):
    # Versión empaquetada: usar messagebox
    messagebox.showerror(...)
else:
    # Versión desarrollo: usar input()
    input("Presione Enter para salir...")
```

---

### Error 3: `ImportError: cannot import name 'customtkinter'`

**Causa:** CustomTkinter no incluido correctamente.

**Solución:**
```python
# Ya incluido en setup.py
files_to_include = [
    (ctk_path, "lib/customtkinter"),
]
```

**Verificar:**
```bash
# En build/exe.win-amd64-3.13/ debe existir:
lib/customtkinter/
```

---

### Error 4: `FileNotFoundError: base_de_imprenta.db`

**Causa:** Base de datos no incluida en el empaquetado.

**Solución Opción 1:** Incluir en setup.py
```python
files_to_include = [
    (ctk_path, "lib/customtkinter"),
    ("base_de_imprenta.db", "base_de_imprenta.db"),  # ← Agregar si existe
]
```

**Solución Opción 2:** La aplicación crea la BD automáticamente
- La aplicación creará `base_de_imprenta.db` en el primer inicio
- No requiere acción adicional

---

### Error 5: Instalador no se genera

**Verificar:**
```bash
# ¿Tiene permisos de escritura?
# ¿La carpeta dist está bloqueada?
# ¿Hay espacio en disco?

# Probar sin MSI primero
python setup.py build

# Luego crear MSI
python setup.py bdist_msi
```

---

## 🔍 Verificación Post-Compilación

### 1. Probar el Ejecutable Directamente

**Antes de instalar el MSI**, pruebe el ejecutable:

```bash
cd build\exe.win-amd64-3.13
ImprentaExpert.exe
```

**Verificar:**
- ✅ Ventana de login aparece correctamente
- ✅ No hay errores de módulos faltantes
- ✅ Base de datos se crea automáticamente
- ✅ Login funciona con credenciales por defecto

### 2. Revisar Logs de Error

Si hay error, buscar en:
```
%TEMP%\ImprentaExpert.log  (si implementaste logging)
```

### 3. Verificar Dependencias Incluidas

```bash
cd build\exe.win-amd64-3.13\lib

# Debe contener:
customtkinter\
sqlalchemy\
openpyxl\
reportlab\
PIL\
```

---

## 📝 Configuración Avanzada

### Cambiar Versión

En `setup.py`:
```python
setup(
    name="Sistema Imprenta Expert",
    version="1.6.1",  # ← Cambiar aquí
    ...
)
```

### Agregar Icono

1. Crear/obtener archivo `.ico`
2. Colocarlo en raíz del proyecto: `icon.ico`
3. Actualizar `setup.py`:

```python
executables = [
    Executable(
        "main.py",
        base=base,
        target_name="ImprentaExpert.exe",
        icon="icon.ico",  # ← Agregar ruta
        ...
    )
]

bdist_msi_options = {
    ...,
    "install_icon": "icon.ico",  # ← Agregar ruta
}
```

### Incluir Archivos Adicionales

En `setup.py`:
```python
files_to_include = [
    (ctk_path, "lib/customtkinter"),
    ("assets/", "assets/"),  # Carpeta completa
    ("config.ini", "config.ini"),  # Archivo individual
    ("base_de_imprenta.db", "base_de_imprenta.db"),  # Base de datos
]
```

### Cambiar Ubicación de Instalación

En `setup.py`:
```python
bdist_msi_options = {
    "initial_target_dir": r"[ProgramFilesFolder]\TuEmpresa\ImprentaSE",
    ...
}
```

---

## 🎯 Mejores Prácticas

### Antes de Compilar

1. ✅ Probar la aplicación en modo desarrollo
   ```bash
   python main.py
   ```

2. ✅ Verificar que no hay errores
   ```bash
   python -m py_compile main.py
   ```

3. ✅ Limpiar cache de Python
   ```bash
   python -c "import compileall, pathlib; compileall.compile_dir('.', force=True)"
   ```

4. ✅ Actualizar versión en setup.py

### Durante la Compilación

- ⏱️ Proceso tarda 2-5 minutos (normal)
- 🔍 Revisar advertencias (warnings) pero pueden ignorarse
- ❌ Errores deben resolverse antes de continuar

### Después de Compilar

1. ✅ Probar ejecutable directamente (build/)
2. ✅ Instalar MSI en máquina de prueba
3. ✅ Verificar todas las funcionalidades
4. ✅ Probar en Windows limpio (sin Python instalado)

---

## 📊 Checklist de Compilación

```
Pre-Compilación:
[ ] Entorno virtual activado
[ ] Todas las dependencias instaladas
[ ] Aplicación funciona en desarrollo
[ ] Versión actualizada en setup.py
[ ] Sin errores de sintaxis

Compilación:
[ ] Script COMPILAR.bat ejecutado O comando manual
[ ] Sin errores durante build
[ ] Carpeta build/ generada
[ ] Carpeta dist/ generada
[ ] Archivo .msi presente en dist/

Post-Compilación:
[ ] Ejecutable probado desde build/
[ ] MSI instalado en máquina de prueba
[ ] Login funciona correctamente
[ ] Base de datos se crea automáticamente
[ ] Todas las funcionalidades operativas
[ ] Sin errores de módulos faltantes

Distribución:
[ ] MSI renombrado apropiadamente
[ ] Documentación incluida
[ ] Instrucciones de instalación claras
```

---

## 🛠️ Comandos Útiles

```bash
# Ver información del build
python setup.py --help

# Solo compilar (sin MSI)
python setup.py build

# Compilar y crear MSI
python setup.py bdist_msi

# Ver todas las opciones de cx_Freeze
python -c "from cx_Freeze import setup; help(setup)"

# Limpiar todo
rmdir /s /q build dist

# Ver tamaño del instalador
dir dist\*.msi
```

---

## 📞 Soporte

Si encuentra problemas no listados aquí:

1. Verificar versiones:
   ```bash
   python --version
   pip list | findstr "cx_Freeze sqlalchemy customtkinter"
   ```

2. Buscar en logs de compilación:
   - Mensajes de error específicos
   - Módulos faltantes
   - Advertencias críticas

3. Recursos:
   - [Documentación cx_Freeze](https://cx-freeze.readthedocs.io/)
   - [SQLAlchemy + cx_Freeze](https://github.com/marcelotduarte/cx_Freeze/issues)
   - [CustomTkinter GitHub](https://github.com/TomSchimansky/CustomTkinter)

---

## 📈 Historial de Cambios

### v1.6.1 (Actual)
- ✅ Corregido: Error `NoSuchModuleError: sqlalchemy.dialects:sqlite`
- ✅ Corregido: Error `RuntimeError: input(): lost sys.stdin`
- ✅ Agregado: SQLAlchemy y dialectos en setup.py
- ✅ Agregado: Manejo de errores en aplicación empaquetada
- ✅ Agregado: Script COMPILAR.bat automático

### v1.6.0
- Sistema de autenticación completo
- Panel de perfil de usuario
- Panel de reglas del sistema experto
- Toggles show/hide en contraseñas

---

**Última actualización:** Diciembre 2025  
**Versión del sistema:** 1.6.1  
**Plataforma:** Windows 10/11 (64-bit)
