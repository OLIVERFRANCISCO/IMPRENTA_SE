"""
Ventana principal de la aplicación
Contiene el sidebar y el contenedor de paneles
"""
import customtkinter as ctk
from tkinter import messagebox
from app.config import *
from app.logic.auth_service import auth_service
from app.ui.panel_pedidos import PanelPedidos
from app.ui.panel_inventario import PanelInventario
from app.ui.panel_clientes import PanelClientes
from app.ui.panel_reportes import PanelReportes
from app.ui.panel_servicios import PanelServicios
from app.ui.panel_pedidos_clientes import PanelPedidosClientes
from app.ui.panel_maquinas import PanelMaquinas
from app.ui.panel_admin import PanelAdmin
from app.ui.panel_perfil import PanelPerfil
from app.ui.panel_reglas_experto import PanelReglasExperto
from app.ui.panel_configuracion import PanelConfiguracion


class ImprentaApp(ctk.CTk):
    """
    Ventana principal del Sistema de Gestión de Imprenta
    
    Clase principal que gestiona la interfaz de usuario, incluyendo
    el menú lateral de navegación y el área de contenido principal.
    """

    # Constantes de la clase para mejor organización
    SIDEBAR_WIDTH = 240
    LOGO_FONT_SIZE = 32
    VERSION = "v1.0.0"
    
    # Iconos SVG para cada sección (Unicode)
    ICONOS = {
        'pedido': '📋',
        'lista': '📊',
        'cliente': '👥',
        'servicio': '🛠️',
        'inventario': '📦',
        'maquina': '⚙️',
        'reporte': '📈',
        'admin': '⚙️',
        'perfil': '👤',
        'reglas': '🧠',
        'config': '🔧',
    }
    
    # Mapeo de paneles a identificadores para permisos
    PANEL_IDS = {
        'btn_pedidos': 'panel_pedidos',
        'btn_pedidos_clientes': 'panel_pedidos_clientes',
        'btn_clientes': 'panel_clientes',
        'btn_servicios': 'panel_servicios',
        'btn_inventario': 'panel_inventario',
        'btn_maquinas': 'panel_maquinas',
        'btn_reportes': 'panel_reportes',
        'btn_reglas': 'panel_reglas',
        'btn_config': 'panel_config',
        'btn_admin': 'panel_admin',
        'btn_perfil': None,  # No requiere permisos, disponible para todos
    }

    def __init__(self):
        """Inicializa la ventana principal y sus componentes"""
        super().__init__()
        
        # Verificar autenticación
        if not auth_service.is_authenticated():
            messagebox.showerror("Error", "Debe iniciar sesión primero")
            self.destroy()
            return
        
        # Configuración inicial
        self._configurar_ventana()
        self._configurar_tema()
        self._configurar_layout()
        
        # Variables de estado
        self.modo_actual = "dark"
        self.panel_actual = None
        self.botones_navegacion = {}
        
        # Construir interfaz
        self._crear_sidebar()
        self._crear_contenedor_principal()
        
        # Mostrar panel inicial permitido
        self._mostrar_panel_inicial()

    def _configurar_ventana(self):
        """Configura las propiedades básicas de la ventana"""
        self.title("Sistema Experto - Gestión de Imprenta")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

    def _configurar_tema(self):
        """Aplica el tema visual de la aplicación"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _configurar_layout(self):
        """Configura el layout de grid principal (sidebar + contenido)"""
        self.grid_columnconfigure(1, weight=1)  # Columna del contenido se expande
        self.grid_rowconfigure(0, weight=1)     # Fila principal se expande
    
    def _crear_contenedor_principal(self):
        """Crea el área de contenido donde se muestran los paneles"""
        self.contenedor_principal = ctk.CTkFrame(
            self, 
            fg_color="transparent",
            corner_radius=15
        )
        self.contenedor_principal.grid(
            row=0, 
            column=1, 
            padx=20, 
            pady=20, 
            sticky="nsew"
        )
        self.contenedor_principal.grid_rowconfigure(0, weight=1)
        self.contenedor_principal.grid_columnconfigure(0, weight=1)

    def _crear_sidebar(self):
        """
        Crea el menú lateral de navegación con logo, versión y botones
        
        El sidebar contiene:
        - Header con logo y versión
        - Botones de navegación organizados (con scroll vertical)
        - Espaciado optimizado para mejor UX
        """
        # Crear frame del sidebar con diseño mejorado y scroll vertical
        self.sidebar = ctk.CTkScrollableFrame(
            self, 
            width=self.SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=("gray90", "gray15")  # Color adaptativo según tema
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        
        # === HEADER DEL SIDEBAR ===
        self._crear_header_sidebar()
        
        # === SECCIÓN DE NAVEGACIÓN ===
        self._crear_botones_navegacion()
        
        # === FOOTER DEL SIDEBAR ===
        self._crear_footer_sidebar()

    def _crear_header_sidebar(self):
        """Crea el header del sidebar con logo, usuario y versión"""
        # Frame contenedor del header
        header_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Logo principal con diseño mejorado
        self.logo_label = ctk.CTkLabel(
            header_frame,
            text="IMPRENTA\nEXPERT",
            font=ctk.CTkFont(size=self.LOGO_FONT_SIZE, weight="bold"),
            text_color=COLOR_PRIMARY,
            justify="center"
        )
        self.logo_label.pack(pady=(0, 5))
        
        # Etiqueta de versión con mejor estilo
        self.version_label = ctk.CTkLabel(
            header_frame,
            text=self.VERSION,
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        )
        self.version_label.pack()
        
        # Información del usuario logueado
        usuario_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=("gray80", "gray20"),
            corner_radius=10
        )
        usuario_frame.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="ew")
        
        username = auth_service.get_username()
        rol = auth_service.get_usuario_actual().get('nombre_rol', 'Usuario')
        
        ctk.CTkLabel(
            usuario_frame,
            text=f"👤 {username}",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(8, 2))
        
        ctk.CTkLabel(
            usuario_frame,
            text=rol,
            font=ctk.CTkFont(size=10),
            text_color=COLOR_PRIMARY
        ).pack(pady=(0, 8))
        
        # Separador visual
        separador = ctk.CTkFrame(
            self.sidebar,
            height=2,
            fg_color=("gray70", "gray30")
        )
        separador.grid(row=2, column=0, padx=30, pady=(10, 20), sticky="ew")

    def _crear_botones_navegacion(self):
        """
        Crea todos los botones de navegación del sidebar
        Solo muestra botones para paneles con permisos
        """
        # Configuración de botones: (texto, icono, comando, fila, panel_id)
        config_botones = [
            ("Nuevo Pedido", self.ICONOS['pedido'], self.mostrar_panel_pedidos, 3, 'panel_pedidos'),
            ("Lista de Pedidos", self.ICONOS['lista'], self.mostrar_panel_pedidos_clientes, 4, 'panel_pedidos_clientes'),
            ("Clientes", self.ICONOS['cliente'], self.mostrar_panel_clientes, 5, 'panel_clientes'),
            ("Servicios", self.ICONOS['servicio'], self.mostrar_panel_servicios, 6, 'panel_servicios'),
            ("Inventario", self.ICONOS['inventario'], self.mostrar_panel_inventario, 7, 'panel_inventario'),
            ("Maquinarias", self.ICONOS['maquina'], self.mostrar_panel_maquinas, 8, 'panel_maquinas'),
            ("Reportes", self.ICONOS['reporte'], self.mostrar_panel_reportes, 9, 'panel_reportes'),
        ]
        
        # Agregar panel de reglas del sistema experto (solo admin)
        if auth_service.is_admin():
            config_botones.append(
                ("Base de Conocimientos", self.ICONOS['reglas'], self.mostrar_panel_reglas, 10, 'panel_reglas')
            )
        
        # Agregar panel de configuración (solo admin)
        if auth_service.is_admin():
            config_botones.append(
                ("Configuración", self.ICONOS['config'], self.mostrar_panel_configuracion, 11, 'panel_config')
            )
        
        # Agregar panel de admin solo si es admin
        if auth_service.is_admin():
            config_botones.append(
                ("Administración", self.ICONOS['admin'], self.mostrar_panel_admin, 12, 'panel_admin')
            )
        
        # Agregar perfil (disponible para todos)
        config_botones.append(
            ("Mi Perfil", self.ICONOS['perfil'], self.mostrar_panel_perfil, 13, None)
        )
        
        # Crear botones solo si tiene permiso para verlos
        for texto, icono, comando, fila, panel_id in config_botones:
            # Verificar permiso de ver panel (None = disponible para todos)
            if panel_id is None or auth_service.puede_ver_panel(panel_id):
                boton = self._crear_boton_navegacion(texto, icono, comando)
                boton.grid(row=fila, column=0, padx=20, pady=8, sticky="ew")
                
                # Guardar referencia del botón usando el nombre del comando
                nombre_boton = comando.__name__.replace('mostrar_panel_', 'btn_')
                self.botones_navegacion[nombre_boton] = boton

    def _crear_boton_navegacion(self, texto, icono, comando):
        """
        Crea un botón de navegación individual con estilo consistente
        
        Args:
            texto: Texto a mostrar en el botón
            icono: Icono unicode/emoji para el botón
            comando: Función a ejecutar al hacer clic
            
        Returns:
            CTkButton: Botón configurado
        """
        return ctk.CTkButton(
            self.sidebar,
            text=f"{icono}  {texto}",
            command=comando,
            height=45,
            font=ctk.CTkFont(size=14, weight="normal"),
            fg_color="transparent",
            border_width=2,
            border_color=("gray70", "gray30"),
            hover_color=("gray80", "gray25"),
            anchor="w",  # Alinear texto a la izquierda
            corner_radius=10
        )
    
    def _crear_footer_sidebar(self):
        """Crea el footer del sidebar con botón de cerrar sesión"""
        # Footer frame para información adicional o controles
        footer_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        footer_frame.grid(row=14, column=0, padx=20, pady=20, sticky="ew")
        
        # Botón de cerrar sesión
        self.btn_logout = ctk.CTkButton(
            footer_frame,
            text="Cerrar Sesión",
            command=self._cerrar_sesion,
            height=40,
            fg_color=COLOR_DANGER,
            hover_color=("red", "darkred"),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_logout.pack(fill="x")
        
        # Información del sistema
        info_label = ctk.CTkLabel(
            footer_frame,
            text="Sistema Activo",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray60")
        )
        info_label.pack(pady=(10, 0))

    def _limpiar_panel_actual(self):
        """
        Elimina el panel actual del contenedor principal
        Libera memoria destruyendo el widget anterior
        """
        if self.panel_actual:
            self.panel_actual.destroy()
            self.panel_actual = None

    def _resaltar_boton(self, boton_activo):
        """
        Actualiza el estilo visual de los botones de navegación
        
        El botón activo se resalta con el color primario,
        mientras que los demás mantienen el estilo transparente
        
        Args:
            boton_activo: Botón que debe mostrarse como activo
        """
        for nombre, boton in self.botones_navegacion.items():
            if boton == boton_activo:
                # Estilo para botón activo
                boton.configure(
                    fg_color=COLOR_PRIMARY,
                    border_width=0,
                    font=ctk.CTkFont(size=14, weight="bold")
                )
            else:
                # Estilo para botones inactivos
                boton.configure(
                    fg_color="transparent",
                    border_width=2,
                    font=ctk.CTkFont(size=14, weight="normal")
                )

    # ============================================================
    # MÉTODOS DE NAVEGACIÓN ENTRE PANELES
    # ============================================================
    
    def _mostrar_panel(self, clase_panel, nombre_boton):
        """
        Método genérico para mostrar un panel y actualizar la UI
        
        Este método centraliza la lógica común de cambio de panel,
        reduciendo duplicación de código
        
        Args:
            clase_panel: Clase del panel a instanciar
            nombre_boton: Clave del botón en el diccionario de navegación
        """
        self._limpiar_panel_actual()
        self.panel_actual = clase_panel(self.contenedor_principal)
        self.panel_actual.grid(row=0, column=0, sticky="nsew")
        
        if nombre_boton in self.botones_navegacion:
            self._resaltar_boton(self.botones_navegacion[nombre_boton])

    def mostrar_panel_pedidos(self):
        """Muestra el panel para crear nuevos pedidos"""
        self._mostrar_panel(PanelPedidos, 'btn_pedidos')

    def mostrar_panel_pedidos_clientes(self):
        """Muestra el panel con la lista completa de pedidos"""
        self._mostrar_panel(PanelPedidosClientes, 'btn_pedidos_clientes')

    def mostrar_panel_clientes(self):
        """Muestra el panel de gestión de clientes"""
        self._mostrar_panel(PanelClientes, 'btn_clientes')

    def mostrar_panel_servicios(self):
        """Muestra el panel de gestión de servicios ofrecidos"""
        self._mostrar_panel(PanelServicios, 'btn_servicios')

    def mostrar_panel_inventario(self):
        """Muestra el panel de control de inventario y materiales"""
        self._mostrar_panel(PanelInventario, 'btn_inventario')

    def mostrar_panel_maquinas(self):
        """Muestra el panel de gestión de maquinarias"""
        self._mostrar_panel(PanelMaquinas, 'btn_maquinas')

    def mostrar_panel_reportes(self):
        """Muestra el panel de generación de reportes y estadísticas"""
        self._mostrar_panel(PanelReportes, 'btn_reportes')
    
    def mostrar_panel_reglas(self):
        """Muestra el panel de reglas del sistema experto (solo admin)"""
        if not auth_service.is_admin():
            messagebox.showerror("Acceso Denegado", "Solo los administradores pueden configurar las reglas")
            return
        self._mostrar_panel(PanelReglasExperto, 'btn_reglas')
    
    def mostrar_panel_configuracion(self):
        """Muestra el panel de configuración del sistema (solo admin)"""
        if not auth_service.is_admin():
            messagebox.showerror("Acceso Denegado", "Solo los administradores pueden acceder a configuración")
            return
        self._mostrar_panel(PanelConfiguracion, 'btn_config')
    
    def mostrar_panel_admin(self):
        """Muestra el panel de administración (solo admin)"""
        if not auth_service.is_admin():
            messagebox.showerror("Acceso Denegado", "Solo los administradores pueden acceder a este panel")
            return
        self._mostrar_panel(PanelAdmin, 'btn_admin')
    
    def mostrar_panel_perfil(self):
        """Muestra el panel de perfil de usuario (todos)"""
        self._mostrar_panel(PanelPerfil, 'btn_perfil')
    
    def _mostrar_panel_inicial(self):
        """Muestra el primer panel al que el usuario tiene acceso"""
        # Lista de métodos en orden de prioridad
        paneles_orden = [
            ('panel_pedidos', self.mostrar_panel_pedidos),
            ('panel_pedidos_clientes', self.mostrar_panel_pedidos_clientes),
            ('panel_clientes', self.mostrar_panel_clientes),
            ('panel_servicios', self.mostrar_panel_servicios),
            ('panel_inventario', self.mostrar_panel_inventario),
            ('panel_maquinas', self.mostrar_panel_maquinas),
            ('panel_reportes', self.mostrar_panel_reportes),
        ]
        
        # Admins van directo a administración si no tienen otros permisos
        if auth_service.is_admin():
            self.mostrar_panel_admin()
            return
        
        # Buscar primer panel con permiso
        for panel_id, metodo in paneles_orden:
            if auth_service.puede_ver_panel(panel_id):
                metodo()
                return
        
        # Si no tiene permisos para nada, mostrar mensaje
        messagebox.showwarning(
            "Sin Permisos",
            "No tiene permisos para acceder a ningún panel.\nContacte al administrador."
        )
    
    def _cerrar_sesion(self):
        """Cierra la sesión actual y vuelve al login"""
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro de cerrar sesión?"):
            auth_service.logout()
            self.destroy()
            # Importar aquí para evitar importación circular
            from app.ui.login_window import mostrar_login
            if mostrar_login():
                # Si login exitoso, crear nueva ventana principal
                nueva_ventana = ImprentaApp()
                nueva_ventana.mainloop()

