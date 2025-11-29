"""
Script para reparar Tkinter en el entorno virtual
Copia los archivos TCL/TK necesarios desde la instalación de Python
"""
import os
import shutil
from pathlib import Path

print("=== Reparando Tkinter en el entorno virtual ===\n")

# Rutas
python_base = Path(r"C:\Users\OLIVER\AppData\Local\Programs\Python\Python313")
venv_base = Path(r"C:\Users\OLIVER\PycharmProjects\Imprenta_SE\.venv")

# Directorios a copiar
dirs_to_copy = [
    ("tcl", "tcl"),
    ("DLLs", "DLLs"),
]

try:
    # 1. Copiar carpeta tcl
    tcl_source = python_base / "tcl"
    tcl_dest = venv_base / "tcl"

    if tcl_source.exists():
        print(f"1. Copiando carpeta TCL...")
        if tcl_dest.exists():
            print(f"   - Eliminando carpeta antigua...")
            shutil.rmtree(tcl_dest)
        shutil.copytree(tcl_source, tcl_dest)
        print(f"   ✓ TCL copiado correctamente")
    else:
        print(f"   ✗ No se encontró la carpeta TCL en: {tcl_source}")

    # 2. Copiar DLLs necesarias
    dlls_source = python_base / "DLLs"
    dlls_dest = venv_base / "DLLs"

    if dlls_source.exists():
        print(f"\n2. Copiando DLLs de Tkinter...")
        if not dlls_dest.exists():
            dlls_dest.mkdir()

        # Copiar solo las DLLs de TCL/TK
        tcl_dlls = ["tcl86t.dll", "tk86t.dll", "_tkinter.pyd"]
        for dll in tcl_dlls:
            source_file = dlls_source / dll
            dest_file = dlls_dest / dll
            if source_file.exists():
                shutil.copy2(source_file, dest_file)
                print(f"   ✓ {dll}")
            else:
                print(f"   ⚠️ {dll} no encontrado")
    else:
        print(f"   ✗ No se encontró la carpeta DLLs en: {dlls_source}")

    # 3. Crear variable de entorno TCL_LIBRARY
    print(f"\n3. Configurando variables de entorno...")
    tcl_library = venv_base / "tcl" / "tcl8.6"
    if tcl_library.exists():
        # Crear archivo de activación personalizado
        activate_script = venv_base / "Scripts" / "activate_tcl.bat"
        with open(activate_script, "w") as f:
            f.write(f'@echo off\n')
            f.write(f'set TCL_LIBRARY={tcl_library}\n')
            f.write(f'set TK_LIBRARY={venv_base / "tcl" / "tk8.6"}\n')
        print(f"   ✓ Script de activación creado")

    print("\n=== Reparación completada ===")
    print("\nPara que los cambios surtan efecto:")
    print("1. Cierra y vuelve a abrir el terminal")
    print("2. Activa el entorno virtual: .venv\\Scripts\\activate")
    print("3. Ejecuta: python main.py")

except Exception as e:
    print(f"\n✗ Error durante la reparación: {e}")
    import traceback
    traceback.print_exc()

input("\nPresione Enter para salir...")

