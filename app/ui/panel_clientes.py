"""
Panel de gestión de clientes mejorado
Permite ver, agregar y editar clientes con interfaz visual mejorada
"""
import customtkinter as ctk
from tkinter import messagebox

from app.config import (
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COLOR_TEXT,
    COLOR_BG_LIGHT,
    COLOR_BG_DARK
)
from app.database import consultas


class IconoSVG:
    """Clase helper para crear iconos SVG simples como texto Unicode"""
    CLIENTE = "👤"
    AGREGAR = "➕"
    ACTUALIZAR = "🔄"
    BUSCAR = "🔍"
    EDITAR = "✏️"
    PEDIDOS = "📦"
    TELEFONO = "📱"
    EMAIL = "📧"
    ID = "🆔"
    GUARDAR = "💾"
    EXITO = "✓"
    ERROR = "✗"
    ALERTA = "⚠"
    ELIMINAR = "🗑️"


class PanelClientes(ctk.CTkFrame):
    """Panel principal para gestión de clientes con diseño mejorado"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # Configuración de la grilla principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Variables de estado
        self.clientes = []
        self.clientes_filtrados = []

        self._crear_encabezado()
        self._crear_barra_busqueda()
        self._crear_tabla_clientes()
        self._cargar_clientes()

    # ==================== CONSTRUCCIÓN DE UI ====================

    def _crear_encabezado(self):
        """Crea el encabezado del panel con título y botones de acción"""
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, pady=(0, 20), padx=10, sticky="ew")
        frame_header.grid_columnconfigure(1, weight=1)

        # Título con icono
        titulo = ctk.CTkLabel(
            frame_header,
            text=f"{IconoSVG.CLIENTE} Gestión de Clientes",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        titulo.grid(row=0, column=0, sticky="w")

        # Botón actualizar
        self.btn_actualizar = ctk.CTkButton(
            frame_header,
            text=f"{IconoSVG.ACTUALIZAR} Actualizar",
            command=self._cargar_clientes,
            height=40,
            width=140,
            font=ctk.CTkFont(size=14),
            fg_color=COLOR_SECONDARY,
            hover_color="#4b5563",
            corner_radius=8
        )
        self.btn_actualizar.grid(row=0, column=2, padx=5)

        # Botón nuevo cliente
        self.btn_nuevo_cliente = ctk.CTkButton(
            frame_header,
            text=f"{IconoSVG.AGREGAR} Nuevo Cliente",
            command=self._mostrar_dialogo_cliente,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            width=180,
            corner_radius=8
        )
        self.btn_nuevo_cliente.grid(row=0, column=3, padx=5)

    def _crear_barra_busqueda(self):
        """Crea la barra de búsqueda con icono"""
        frame_buscar = ctk.CTkFrame(self, fg_color="transparent")
        frame_buscar.grid(row=1, column=0, pady=(0, 20), padx=10, sticky="ew")

        # Contenedor para barra de búsqueda estilizada
        frame_busqueda = ctk.CTkFrame(frame_buscar, corner_radius=12)
        frame_busqueda.pack(fill="x", padx=10)

        # Icono de búsqueda
        label_icono = ctk.CTkLabel(
            frame_busqueda,
            text=f"{IconoSVG.BUSCAR}",
            font=ctk.CTkFont(size=16),
            width=40
        )
        label_icono.pack(side="left", padx=(15, 0))

        # Campo de búsqueda
        self.entry_buscar = ctk.CTkEntry(
            frame_busqueda,
            placeholder_text="Buscar por nombre, teléfono o email...",
            height=40,
            font=ctk.CTkFont(size=14),
            border_width=0,
            fg_color="transparent"
        )
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.entry_buscar.bind("<KeyRelease>", self._filtrar_clientes)

    def _crear_tabla_clientes(self):
        """Crea el contenedor de la tabla de clientes"""
        # Frame para encabezados de tabla
        self.frame_encabezados = ctk.CTkFrame(self, fg_color=COLOR_PRIMARY, corner_radius=8)
        self.frame_encabezados.grid(row=2, column=0, padx=10, sticky="ew")
        self.frame_encabezados.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Encabezados de tabla
        headers = [
            (f"{IconoSVG.ID} ID", 0),
            (f"{IconoSVG.CLIENTE} Nombre Completo", 1),
            (f"{IconoSVG.TELEFONO} Teléfono", 2),
            (f"{IconoSVG.EMAIL} Email", 3),
            ("Acciones", 4)
        ]

        for text, col in headers:
            ctk.CTkLabel(
                self.frame_encabezados,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=col, padx=10, pady=12)

        # Contenedor scrollable para filas de clientes
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            border_width=1,
            border_color="#374151"
        )
        self.scroll_frame.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _crear_fila_cliente(self, cliente, fila):
        """Crea una fila estilizada para mostrar un cliente"""
        # Color de fondo alternado
        fg_color = COLOR_BG_DARK

        frame_fila = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=fg_color,
            corner_radius=6
        )
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # ID
        ctk.CTkLabel(
            frame_fila,
            text=str(cliente['id_cliente']),
            font=ctk.CTkFont(size=12, family="monospace"),
            text_color=COLOR_TEXT
        ).grid(row=0, column=0, padx=10, pady=10)

        # Nombre
        ctk.CTkLabel(
            frame_fila,
            text=cliente['nombre_completo'],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_TEXT
        ).grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Teléfono
        telefono_texto = cliente['telefono'] or f"{IconoSVG.TELEFONO} No especificado"
        ctk.CTkLabel(
            frame_fila,
            text=telefono_texto,
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT if cliente['telefono'] else "#6b7280"
        ).grid(row=0, column=2, padx=10, pady=10)

        # Email
        email_texto = cliente['email'] or f"{IconoSVG.EMAIL} No especificado"
        ctk.CTkLabel(
            frame_fila,
            text=email_texto,
            font=ctk.CTkFont(size=12),
            text_color=COLOR_TEXT if cliente['email'] else "#6b7280"
        ).grid(row=0, column=3, padx=10, pady=10)

        # Botones de acción
        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=4, padx=10, pady=5)

        # Botón Editar
        btn_editar = ctk.CTkButton(
            frame_acciones,
            text=f"{IconoSVG.EDITAR} Editar",
            command=lambda c=cliente: self._editar_cliente(c),
            width=90,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_PRIMARY,
            hover_color="#2563eb",
            corner_radius=6
        )
        btn_editar.pack(side="left", padx=2)

        # Botón Pedidos
        btn_pedidos = ctk.CTkButton(
            frame_acciones,
            text=f"{IconoSVG.PEDIDOS} Pedidos",
            command=lambda c=cliente: self._ver_pedidos_cliente(c),
            width=100,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color=COLOR_SECONDARY,
            hover_color="#4b5563",
            corner_radius=6
        )
        btn_pedidos.pack(side="left", padx=2)

    # ==================== OBTENCIÓN DE DATOS ====================

    def _cargar_clientes(self):
        """Carga y muestra todos los clientes"""
        # Limpiar tabla
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obtener clientes desde la base de datos
        try:
            self.clientes = consultas.obtener_clientes()
            self.clientes_filtrados = self.clientes.copy()

            if not self.clientes:
                self._mostrar_mensaje_vacio()
                return

            # Mostrar clientes en tabla
            for idx, cliente in enumerate(self.clientes_filtrados):
                self._crear_fila_cliente(cliente, idx)

        except Exception as e:
            self._mostrar_error_carga(e)

    def _mostrar_mensaje_vacio(self):
        """Muestra mensaje cuando no hay clientes"""
        frame_vacio = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_vacio.pack(pady=50)

        ctk.CTkLabel(
            frame_vacio,
            text="📭 No hay clientes registrados",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#6b7280"
        ).pack(pady=10)

        ctk.CTkLabel(
            frame_vacio,
            text="Haz clic en 'Nuevo Cliente' para agregar el primero",
            font=ctk.CTkFont(size=14),
            text_color="#9ca3af"
        ).pack(pady=5)

    def _mostrar_error_carga(self, error):
        """Muestra mensaje de error al cargar clientes"""
        frame_error = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_error.pack(pady=50)

        ctk.CTkLabel(
            frame_error,
            text=f"{IconoSVG.ERROR} Error al cargar clientes",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_TEXT
        ).pack(pady=10)

        ctk.CTkLabel(
            frame_error,
            text=str(error),
            font=ctk.CTkFont(size=12),
            text_color="#9ca3af"
        ).pack(pady=5)

    # ==================== FILTRADO Y BÚSQUEDA ====================

    def _filtrar_clientes(self, event=None):
        """Filtra clientes según el texto de búsqueda en tiempo real"""
        busqueda = self.entry_buscar.get().lower().strip()

        # Limpiar tabla
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not busqueda:
            self.clientes_filtrados = self.clientes
        else:
            # Filtrar clientes por criterios
            self.clientes_filtrados = [
                cliente for cliente in self.clientes
                if (busqueda in cliente['nombre_completo'].lower() or
                    busqueda in (cliente['telefono'] or "").lower() or
                    busqueda in (cliente['email'] or "").lower())
            ]

        # Mostrar resultados o mensaje de no encontrados
        if not self.clientes_filtrados:
            self._mostrar_sin_resultados(busqueda)
        else:
            for idx, cliente in enumerate(self.clientes_filtrados):
                self._crear_fila_cliente(cliente, idx)

    def _mostrar_sin_resultados(self, busqueda):
        """Muestra mensaje cuando no se encuentran resultados"""
        frame_sin_resultados = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_sin_resultados.pack(pady=50)

        ctk.CTkLabel(
            frame_sin_resultados,
            text=f"{IconoSVG.BUSCAR} Sin resultados",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#6b7280"
        ).pack(pady=10)

        ctk.CTkLabel(
            frame_sin_resultados,
            text=f"No se encontraron clientes para: '{busqueda}'",
            font=ctk.CTkFont(size=14),
            text_color="#9ca3af"
        ).pack(pady=5)

    # ==================== DIÁLOGOS DE CLIENTE ====================

    def _mostrar_dialogo_cliente(self, cliente=None):
        """Muestra diálogo modal para agregar o editar cliente"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Cliente" if not cliente else "Editar Cliente")
        dialogo.geometry("500x500")
        dialogo.resizable(False, False)
        dialogo.transient(self)
        dialogo.grab_set()

        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (450 // 2)
        dialogo.geometry(f"+{x}+{y}")

        # Contenedor principal
        frame = ctk.CTkFrame(dialogo, corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        titulo_texto = f"{IconoSVG.AGREGAR} Nuevo Cliente" if not cliente else f"{IconoSVG.EDITAR} Editar Cliente"
        ctk.CTkLabel(
            frame,
            text=titulo_texto,
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(10, 30))

        # Campo Nombre Completo
        ctk.CTkLabel(
            frame,
            text=f"{IconoSVG.CLIENTE} Nombre Completo *",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=30)

        entry_nombre = ctk.CTkEntry(
            frame,
            width=400,
            height=40,
            placeholder_text="Ingrese nombre completo",
            corner_radius=8
        )
        entry_nombre.pack(padx=30, pady=(5, 15))
        entry_nombre.focus()

        if cliente:
            entry_nombre.insert(0, cliente['nombre_completo'])

        # Campo Teléfono
        ctk.CTkLabel(
            frame,
            text=f"{IconoSVG.TELEFONO} Teléfono",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=30)

        entry_telefono = ctk.CTkEntry(
            frame,
            width=400,
            height=40,
            placeholder_text="Opcional",
            corner_radius=8
        )
        entry_telefono.pack(padx=30, pady=(5, 15))

        if cliente and cliente['telefono']:
            entry_telefono.insert(0, cliente['telefono'])

        # Campo Email
        ctk.CTkLabel(
            frame,
            text=f"{IconoSVG.EMAIL} Email",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=30)

        entry_email = ctk.CTkEntry(
            frame,
            width=400,
            height=40,
            placeholder_text="Opcional",
            corner_radius=8
        )
        entry_email.pack(padx=30, pady=(5, 25))

        if cliente and cliente['email']:
            entry_email.insert(0, cliente['email'])

        # Label de error
        label_error = ctk.CTkLabel(
            frame,
            text="",
            text_color="#dc2626",
            font=ctk.CTkFont(size=11)
        )
        label_error.pack(pady=(0, 15))

        def guardar_cliente():
            """Valida y guarda los datos del cliente"""
            nombre = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            email = entry_email.get().strip()

            # Validaciones
            if not nombre:
                label_error.configure(text=f"{IconoSVG.ERROR} El nombre es obligatorio")
                return

            if telefono and (not telefono.isdigit() or len(telefono) < 9):
                label_error.configure(text=f"{IconoSVG.ERROR} Teléfono inválido (mínimo 9 dígitos)")
                return

            if email and "@" not in email:
                label_error.configure(text=f"{IconoSVG.ERROR} Email inválido")
                return

            try:
                # Guardar en base de datos
                if cliente:
                    consultas.actualizar_cliente(
                        cliente['id_cliente'],
                        nombre,
                        telefono if telefono else None,
                        email if email else None
                    )
                    mensaje = f"{IconoSVG.EXITO} Cliente actualizado correctamente"
                else:
                    consultas.guardar_cliente(
                        nombre,
                        telefono if telefono else None,
                        email if email else None
                    )
                    mensaje = f"{IconoSVG.EXITO} Cliente agregado correctamente"

                # Cerrar diálogo y actualizar tabla
                dialogo.destroy()
                messagebox.showinfo("Éxito", mensaje)
                self._cargar_clientes()

            except Exception as e:
                label_error.configure(text=f"{IconoSVG.ERROR} Error al guardar: {str(e)}")

        # Botones
        frame_btn = ctk.CTkFrame(frame, fg_color="transparent")
        frame_btn.pack(pady=10)

        ctk.CTkButton(
            frame_btn,
            text=f"{IconoSVG.GUARDAR} Guardar",
            command=guardar_cliente,
            width=180,
            height=40,
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            corner_radius=8
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_btn,
            text=f"{IconoSVG.ERROR} Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray",
            hover_color="#6b7280",
            corner_radius=8
        ).pack(side="left", padx=5)

        # Permitir guardar con Enter
        entry_email.bind("<Return>", lambda e: guardar_cliente())

    # ==================== ACCIONES PRINCIPALES ====================

    def _editar_cliente(self, cliente):
        """Inicia la edición de un cliente existente"""
        self._mostrar_dialogo_cliente(cliente)

    def _ver_pedidos_cliente(self, cliente):
        """Muestra los pedidos de un cliente (funcionalidad futura)"""
        # TODO: Implementar vista detallada de pedidos del cliente
        messagebox.showinfo(
            f"{IconoSVG.PEDIDOS} Pedidos de {cliente['nombre_completo']}",
            f"ID Cliente: {cliente['id_cliente']}\n"
            f"Nombre: {cliente['nombre_completo']}\n\n"
            "Funcionalidad de visualización de pedidos\n"
            "está en desarrollo y estará disponible pronto."
        )