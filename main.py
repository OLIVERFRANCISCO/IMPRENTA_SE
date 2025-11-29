"""
Sistema Experto de Gestión para Imprenta
Punto de entrada de la aplicación

Autor: Oliver
Versión: 1.0.0
"""
import sys
import os

# Agregar el directorio raíz al path para imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.ui.main_window import ImprentaApp
from app.database.conexion import DatabaseConnection


def main():
    """Función principal que inicia la aplicación"""
    try:
        # Inicializar la base de datos
        db = DatabaseConnection()
        db.get_connection()
        print("✓ Base de datos inicializada correctamente")

        # Crear y ejecutar la aplicación
        app = ImprentaApp()
        print("✓ Interfaz gráfica cargada")
        print("✓ Sistema iniciado correctamente")

        # Iniciar el loop principal
        app.mainloop()

    except Exception as e:
        print(f"✗ Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        input("Presione Enter para salir...")
    finally:
        # Cerrar conexión a la base de datos al salir
        try:
            db = DatabaseConnection()
            db.close()
            print("✓ Conexión a base de datos cerrada")
        except:
            pass


if __name__ == "__main__":
    main()

