"""
Ventana principal de la aplicación
Contiene el sidebar y el contenedor de paneles
"""
import customtkinter as ctk
from app.config import *
from app.ui.panel_pedidos import PanelPedidos
from app.ui.panel_inventario import PanelInventario
from app.ui.panel_clientes import PanelClientes
from app.ui.panel_reportes import PanelReportes
from app.ui.panel_servicios import PanelServicios
from app.ui.panel_pedidos_clientes import PanelPedidosClientes
from app.ui.panel_maquinas import PanelMaquinas


class ImprentaApp(ctk.CTk):
    """Ventana principal del Sistema de Gestión de Imprenta"""

    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.title("Sistema Experto - Gestión de Imprenta")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Layout principal: 2 columnas
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variable para controlar el modo
        self.modo_actual = "dark"

        # Crear sidebar
        self._crear_sidebar()

        # Crear contenedor principal
        self.contenedor_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor_principal.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.contenedor_principal.grid_rowconfigure(0, weight=1)
        self.contenedor_principal.grid_columnconfigure(0, weight=1)

        # Panel actual
        self.panel_actual = None

        # Mostrar panel inicial
        self.mostrar_panel_pedidos()

    def _crear_sidebar(self):
        """Crea el menú lateral de navegación"""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Logo/Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="IMPRENTA\nEXPERT",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0",
            font=ctk.CTkFont(size=10)
        )
        self.version_label.grid(row=1, column=0, padx=20, pady=(0, 30))

        # Botones de navegación
        self.btn_pedidos = ctk.CTkButton(
            self.sidebar,
            text="Nuevo Pedido",
            command=self.mostrar_panel_pedidos,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.btn_pedidos.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_lista_pedidos = ctk.CTkButton(
            self.sidebar,
            text="Lista de Pedidos",
            command=self.mostrar_panel_pedidos_clientes,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2
        )
        self.btn_lista_pedidos.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.btn_clientes = ctk.CTkButton(
            self.sidebar,
            text="Clientes",
            command=self.mostrar_panel_clientes,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2
        )
        self.btn_clientes.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.btn_servicios = ctk.CTkButton(
            self.sidebar,
            text="Servicios",
            command=self.mostrar_panel_servicios,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2
        )
        self.btn_servicios.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.btn_inventario = ctk.CTkButton(
            self.sidebar,
            text="Inventario",
            command=self.mostrar_panel_inventario,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2
        )
        self.btn_inventario.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.btn_maquinas = ctk.CTkButton(
            self.sidebar,
            text="Maquinarias",
            command=self.mostrar_panel_maquinas,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2
        )
        self.btn_maquinas.grid(row=7, column=0, padx=20, pady=10, sticky="ew")

        self.btn_reportes = ctk.CTkButton(
            self.sidebar,
            text="Reportes",
            command=self.mostrar_panel_reportes,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2
        )
        self.btn_reportes.grid(row=8, column=0, padx=20, pady=10, sticky="ew")

        # Modo de apariencia
        #self.label_tema = ctk.CTkLabel(
        #    self.sidebar,
        #    text="Tema:",
        #    font=ctk.CTkFont(size=12)
        #)
        #self.label_tema.grid(row=11, column=0, padx=20, pady=(10, 0))
#
        #self.switch_tema = ctk.CTkSwitch(
        #    self.sidebar,
        #    text="Modo Oscuro",
        #    command=self.cambiar_tema,
        #    font=ctk.CTkFont(size=11)
        #)
        #self.switch_tema.grid(row=12, column=0, padx=20, pady=(5, 20))
        #self.switch_tema.select()  # Activado por defecto

    def cambiar_tema(self):
        """Alterna entre modo oscuro y claro"""
        if self.switch_tema.get():
            ctk.set_appearance_mode("dark")
            self.modo_actual = "dark"
        else:
            ctk.set_appearance_mode("light")
            self.modo_actual = "light"

        # Actualizar colores del sidebar según el modo
        self._actualizar_colores_sidebar()

    def _actualizar_colores_sidebar(self):
        """Actualiza los colores del sidebar según el tema"""
        if self.modo_actual == "light":
            # Colores para modo claro
            self.version_label.configure(text_color="gray40")
        else:
            # Colores para modo oscuro
            self.version_label.configure(text_color="gray")

    def _limpiar_panel_actual(self):
        """Elimina el panel actual"""
        if self.panel_actual:
            self.panel_actual.destroy()
            self.panel_actual = None

    def _resaltar_boton(self, boton_activo):
        """Resalta el botón del panel activo"""
        botones = [
            self.btn_pedidos,
            self.btn_lista_pedidos,
            self.btn_clientes,
            self.btn_servicios,
            self.btn_inventario,
            self.btn_maquinas,
            self.btn_reportes
        ]

        for btn in botones:
            if btn == boton_activo:
                btn.configure(fg_color=COLOR_PRIMARY, border_width=0)
            else:
                btn.configure(fg_color="transparent", border_width=2)

    def mostrar_panel_pedidos(self):
        """Muestra el panel de gestión de pedidos"""
        self._limpiar_panel_actual()
        self.panel_actual = PanelPedidos(self.contenedor_principal)
        self.panel_actual.grid(row=0, column=0, sticky="nsew")
        self._resaltar_boton(self.btn_pedidos)

    def mostrar_panel_pedidos_clientes(self):
        """Muestra el panel de lista de pedidos"""
        self._limpiar_panel_actual()
        self.panel_actual = PanelPedidosClientes(self.contenedor_principal)
        self.panel_actual.grid(row=0, column=0, sticky="nsew")
        self._resaltar_boton(self.btn_lista_pedidos)

    def mostrar_panel_clientes(self):
        """Muestra el panel de gestión de clientes"""
        self._limpiar_panel_actual()
        self.panel_actual = PanelClientes(self.contenedor_principal)
        self.panel_actual.grid(row=0, column=0, sticky="nsew")
        self._resaltar_boton(self.btn_clientes)

    def mostrar_panel_servicios(self):
        """Muestra el panel de gestión de servicios"""
        self._limpiar_panel_actual()
        self.panel_actual = PanelServicios(self.contenedor_principal)
        self.panel_actual.grid(row=0, column=0, sticky="nsew")
        self._resaltar_boton(self.btn_servicios)

    def mostrar_panel_inventario(self):
        """Muestra el panel de gestión de inventario"""
        self._limpiar_panel_actual()
        self.panel_actual = PanelInventario(self.contenedor_principal)
        self.panel_actual.grid(row=0, column=0, sticky="nsew")
        self._resaltar_boton(self.btn_inventario)

    def mostrar_panel_maquinas(self):
        """Muestra el panel de gestión de maquinarias"""
        self._limpiar_panel_actual()
        self.panel_actual = PanelMaquinas(self.contenedor_principal)
        self.panel_actual.grid(row=0, column=0, sticky="nsew")
        self._resaltar_boton(self.btn_maquinas)

    def mostrar_panel_reportes(self):
        """Muestra el panel de reportes"""
        self._limpiar_panel_actual()
        self.panel_actual = PanelReportes(self.contenedor_principal)
        self.panel_actual.grid(row=0, column=0, sticky="nsew")
        self._resaltar_boton(self.btn_reportes)

