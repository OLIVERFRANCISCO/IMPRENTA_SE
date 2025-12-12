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
from app.ui.login_window import mostrar_login
from app.database.conexion import DatabaseConnection
from app.database import consultas_auth


def inicializar_datos_auth():
    """
    Inicializa roles y usuario admin por defecto si no existen
    """
    try:
        # Verificar si ya existen roles
        roles_existentes = consultas_auth.obtener_roles()
        
        if not roles_existentes:
            print("Inicializando sistema de autenticación...")
            
            # Crear rol admin
            id_admin = consultas_auth.crear_rol('admin')
            print("✓ Rol 'admin' creado")
            
            # Crear rol empleado
            id_empleado = consultas_auth.crear_rol('empleado')
            print("✓ Rol 'empleado' creado")
            
            # Crear usuario admin por defecto
            consultas_auth.crear_usuario('admin', 'admin123', id_admin)
            print("✓ Usuario administrador creado (admin/admin123)")
            
            # Configurar permisos básicos para empleado
            permisos_empleado = {
                'panel_pedidos_clientes': ['ver'],
                'panel_clientes': ['ver'],
                'panel_servicios': ['ver'],
                'panel_inventario': ['ver'],
                'panel_reportes': ['ver']
            }
            consultas_auth.configurar_permisos_rol(id_empleado, permisos_empleado)
            print("✓ Permisos de empleado configurados")
            
            print("✓ Sistema de autenticación inicializado")
        else:
            print("✓ Sistema de autenticación ya configurado")
            
    except Exception as e:
        print(f"⚠ Advertencia al inicializar autenticación: {e}")


def main():
    """Función principal que inicia la aplicación"""
    try:
        # Inicializar la base de datos (ORM)
        db = DatabaseConnection()
        print("✓ Base de datos inicializada correctamente")
        
        # Inicializar datos de autenticación
        inicializar_datos_auth()
        
        # Mostrar ventana de login
        print("Esperando autenticación...")
        if not mostrar_login():
            print("✗ Login cancelado o fallido")
            return
        
        print("✓ Login exitoso")
        
        # Crear y ejecutar la aplicación principal
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
        # Limpiar sesiones al salir
        try:
            from app.database import get_session
            from app.logic.auth_service import auth_service
            auth_service.logout()
            print("✓ Sesión cerrada correctamente")
        except:
            pass


if __name__ == "__main__":
    main()

