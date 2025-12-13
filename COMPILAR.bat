@echo off
REM ============================================
REM Script para compilar el Sistema Imprenta Expert
REM ============================================

echo.
echo ============================================
echo  COMPILADOR - Sistema Imprenta Expert
echo ============================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo ERROR: No se encuentra main.py
    echo Asegurese de ejecutar este script desde el directorio raiz del proyecto
    pause
    exit /b 1
)

REM Activar entorno virtual
echo [1/5] Activando entorno virtual...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo OK - Entorno virtual activado
) else (
    echo ADVERTENCIA: No se encontro .venv, usando Python global
)

echo.
echo [2/5] Verificando dependencias...
python -c "import customtkinter, sqlalchemy, openpyxl, reportlab" 2>nul
if errorlevel 1 (
    echo ERROR: Faltan dependencias
    echo Instalando dependencias...
    pip install -r requirements.txt
)
echo OK - Dependencias verificadas

echo.
echo [3/5] Limpiando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
echo OK - Limpieza completada

echo.
echo [4/5] Compilando aplicacion (esto puede tardar 2-5 minutos)...
python setup.py bdist_msi

if errorlevel 1 (
    echo.
    echo ============================================
    echo ERROR: La compilacion fallo
    echo ============================================
    echo.
    echo Posibles causas:
    echo - cx_Freeze no instalado: pip install cx_Freeze
    echo - Dependencias faltantes: pip install -r requirements.txt
    echo - Error en el codigo: Revise los mensajes de error arriba
    echo.
    pause
    exit /b 1
)

echo OK - Compilacion exitosa

echo.
echo [5/5] Verificando instalador generado...
if exist "dist\*.msi" (
    echo OK - Instalador MSI creado exitosamente
    echo.
    echo ============================================
    echo  COMPILACION COMPLETADA
    echo ============================================
    echo.
    echo El instalador se encuentra en:
    for %%f in (dist\*.msi) do echo   - %%f
    echo.
    echo Puede ejecutar el instalador para probar la aplicacion
    echo.
) else (
    echo ERROR: No se encontro el archivo MSI
    echo Revise los mensajes de error arriba
    pause
    exit /b 1
)

echo Desea abrir la carpeta dist? (S/N)
set /p abrir="> "
if /i "%abrir%"=="S" (
    explorer dist
)

echo.
echo Presione cualquier tecla para salir...
pause >nul
