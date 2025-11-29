"""
Script de configuración para crear el instalador MSI
Ejecutar: python setup.py bdist_msi
"""
import sys
import os
from cx_Freeze import setup, Executable

# ========== CONFIGURACIÓN CRÍTICA ==========
# Localizar los archivos de customtkinter
try:
    import customtkinter
    ctk_path = os.path.dirname(customtkinter.__file__)
except ImportError:
    print("ERROR: CustomTkinter no está instalado")
    print("Ejecute: pip install customtkinter")
    sys.exit(1)

# ========== ARCHIVOS A INCLUIR ==========
files_to_include = [
    (ctk_path, "lib/customtkinter"),
    # Agregar aquí otros archivos si es necesario:
    # ("assets/", "assets/"),
    # ("imprenta.db", "imprenta.db"),
]

# ========== OPCIONES DE COMPILACIÓN ==========
build_exe_options = {
    "packages": [
        "os",
        "sys",
        "customtkinter",
        "sqlite3",
        "tkinter",
        "datetime",
        "pathlib",
        "PIL",  # Pillow, requerido por CustomTkinter
        "darkdetect",  # Requerido por CustomTkinter
    ],
    "include_files": files_to_include,
    "excludes": ["matplotlib", "numpy", "pandas"],  # Excluir paquetes pesados innecesarios
    "include_msvcr": True,  # Incluir runtime de Visual C++
    "optimize": 2,  # Nivel de optimización
}

# ========== CONFIGURACIÓN DEL INSTALADOR MSI ==========
bdist_msi_options = {
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\SistemaImprentaExpert",
    "upgrade_code": "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}",  # ID único (no cambiar)
    "install_icon": None,  # Agregar ruta al icono .ico si tienes uno
}

# ========== CONFIGURACIÓN DEL EJECUTABLE ==========
# Para Python 3.13, cx_Freeze requiere un enfoque diferente
base = None
if sys.platform == "win32":
    # En Python 3.13, Win32GUI debe ser especificado sin el prefijo "legacy/"
    base = "gui"  # Oculta la consola negra (alternativa a Win32GUI)

executables = [
    Executable(
        "main.py",
        base=base,
        target_name="ImprentaExpert.exe",
        icon=None,  # Agregar ruta al icono .ico si tienes uno
        shortcut_name="Sistema Imprenta Expert",
        shortcut_dir="DesktopFolder"
    )
]

# ========== SETUP ==========
setup(
    name="Sistema Imprenta Expert",
    version="1.0.0",
    description="Sistema Experto de Gestión para Imprenta",
    author="Oliver",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options
    },
    executables=executables
)

