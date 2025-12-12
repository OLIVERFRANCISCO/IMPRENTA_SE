"""
Script de Prueba del Sistema de Autenticación
Valida el funcionamiento correcto de roles, usuarios y permisos
"""
import sys
import os

# Agregar el directorio raíz al path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.database.conexion import DatabaseConnection
from app.database import consultas_auth
from app.logic.auth_service import auth_service


def test_creacion_roles():
    """Prueba 1: Creación de roles"""
    print("\n=== PRUEBA 1: Creación de Roles ===")
    
    try:
        roles = consultas_auth.obtener_roles()
        print(f"✓ Roles existentes: {len(roles)}")
        for rol in roles:
            print(f"  - {rol['nombre_rol']} (ID: {rol['id']})")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_creacion_usuarios():
    """Prueba 2: Creación de usuarios"""
    print("\n=== PRUEBA 2: Gestión de Usuarios ===")
    
    try:
        usuarios = consultas_auth.obtener_usuarios()
        print(f"✓ Usuarios existentes: {len(usuarios)}")
        for usuario in usuarios:
            print(f"  - {usuario['username']} ({usuario['nombre_rol']}) - Activo: {usuario['activo']}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_autenticacion():
    """Prueba 3: Autenticación de usuario"""
    print("\n=== PRUEBA 3: Autenticación ===")
    
    try:
        # Intentar login con admin
        usuario = consultas_auth.autenticar_usuario('admin', 'admin123')
        if usuario:
            print(f"✓ Login exitoso: {usuario['username']}")
            print(f"  - Rol: {usuario['nombre_rol']}")
            print(f"  - ID: {usuario['id']}")
            
            # Establecer sesión
            auth_service.login(usuario)
            print(f"✓ Sesión establecida")
            return True
        else:
            print("✗ Login fallido")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_permisos():
    """Prueba 4: Verificación de permisos"""
    print("\n=== PRUEBA 4: Verificación de Permisos ===")
    
    try:
        if not auth_service.is_authenticated():
            print("✗ No hay sesión activa")
            return False
        
        # Verificar si es admin
        print(f"✓ Usuario actual: {auth_service.get_username()}")
        print(f"✓ Es admin: {auth_service.is_admin()}")
        
        # Verificar permisos en diferentes paneles
        paneles_prueba = [
            'panel_pedidos',
            'panel_clientes',
            'panel_inventario',
            'panel_admin'
        ]
        
        for panel in paneles_prueba:
            puede_ver = auth_service.puede_ver_panel(panel)
            puede_crear = auth_service.puede_crear(panel)
            puede_editar = auth_service.puede_editar(panel)
            puede_eliminar = auth_service.puede_eliminar(panel)
            
            print(f"\n  Panel: {panel}")
            print(f"    Ver: {puede_ver} | Crear: {puede_crear} | Editar: {puede_editar} | Eliminar: {puede_eliminar}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_gestion_permisos():
    """Prueba 5: Configuración de permisos por rol"""
    print("\n=== PRUEBA 5: Configuración de Permisos ===")
    
    try:
        # Obtener rol empleado
        roles = consultas_auth.obtener_roles()
        rol_empleado = None
        for rol in roles:
            if rol['nombre_rol'].lower() == 'empleado':
                rol_empleado = rol
                break
        
        if not rol_empleado:
            print("✗ Rol 'empleado' no encontrado")
            return False
        
        # Obtener permisos del rol
        permisos = consultas_auth.obtener_permisos_por_rol(rol_empleado['id'])
        print(f"✓ Permisos del rol '{rol_empleado['nombre_rol']}': {len(permisos)}")
        
        # Agrupar por panel
        permisos_por_panel = {}
        for permiso in permisos:
            panel = permiso['panel']
            if panel not in permisos_por_panel:
                permisos_por_panel[panel] = []
            permisos_por_panel[panel].append(permiso['permiso'])
        
        for panel, perms in permisos_por_panel.items():
            print(f"  - {panel}: {', '.join(perms)}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_usuario_empleado():
    """Prueba 6: Crear y probar usuario empleado"""
    print("\n=== PRUEBA 6: Usuario Empleado ===")
    
    try:
        # Buscar rol empleado
        roles = consultas_auth.obtener_roles()
        rol_empleado_id = None
        for rol in roles:
            if rol['nombre_rol'].lower() == 'empleado':
                rol_empleado_id = rol['id']
                break
        
        if not rol_empleado_id:
            print("✗ Rol empleado no encontrado")
            return False
        
        # Verificar si ya existe usuario test
        usuarios = consultas_auth.obtener_usuarios()
        usuario_existe = any(u['username'] == 'empleado_test' for u in usuarios)
        
        if not usuario_existe:
            # Crear usuario de prueba
            id_usuario = consultas_auth.crear_usuario('empleado_test', 'test123', rol_empleado_id)
            print(f"✓ Usuario 'empleado_test' creado (ID: {id_usuario})")
        else:
            print("✓ Usuario 'empleado_test' ya existe")
        
        # Intentar login
        usuario = consultas_auth.autenticar_usuario('empleado_test', 'test123')
        if usuario:
            print(f"✓ Login exitoso como empleado")
            
            # Cerrar sesión admin y abrir como empleado
            auth_service.logout()
            auth_service.login(usuario)
            
            # Verificar permisos limitados
            print(f"✓ Permisos limitados:")
            print(f"  - Puede ver pedidos: {auth_service.puede_ver_panel('panel_pedidos')}")
            print(f"  - Puede crear pedidos: {auth_service.puede_crear('panel_pedidos')}")
            print(f"  - Puede ver admin: {auth_service.puede_ver_panel('panel_admin')}")
            print(f"  - Es admin: {auth_service.is_admin()}")
            
            # Restaurar sesión admin
            admin = consultas_auth.autenticar_usuario('admin', 'admin123')
            auth_service.login(admin)
            
            return True
        else:
            print("✗ Login de empleado fallido")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("PRUEBAS DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 60)
    
    try:
        # Inicializar base de datos
        db = DatabaseConnection()
        print("✓ Base de datos inicializada")
        
        # Ejecutar pruebas
        resultados = []
        resultados.append(("Creación de Roles", test_creacion_roles()))
        resultados.append(("Gestión de Usuarios", test_creacion_usuarios()))
        resultados.append(("Autenticación", test_autenticacion()))
        resultados.append(("Verificación de Permisos", test_permisos()))
        resultados.append(("Configuración de Permisos", test_gestion_permisos()))
        resultados.append(("Usuario Empleado", test_usuario_empleado()))
        
        # Resumen
        print("\n" + "=" * 60)
        print("RESUMEN DE PRUEBAS")
        print("=" * 60)
        
        exitosas = 0
        for nombre, resultado in resultados:
            estado = "✓ PASS" if resultado else "✗ FAIL"
            print(f"{estado} - {nombre}")
            if resultado:
                exitosas += 1
        
        print(f"\nResultado: {exitosas}/{len(resultados)} pruebas exitosas")
        
        if exitosas == len(resultados):
            print("\n✓ TODAS LAS PRUEBAS PASARON")
        else:
            print("\n⚠ ALGUNAS PRUEBAS FALLARON")
        
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpiar sesión
        auth_service.logout()
        print("\n✓ Sesión cerrada")


if __name__ == "__main__":
    main()
