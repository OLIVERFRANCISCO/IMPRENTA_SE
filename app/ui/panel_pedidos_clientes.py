"""
Panel para visualizar pedidos de clientes
Muestra lista de pedidos con sus detalles, paginación y filtros
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from app.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING
from app.database import consultas
from app.logic.exportacion import exportar_a_csv, exportar_a_excel, exportar_a_pdf


class PanelPedidosClientes(ctk.CTkFrame):
    """
    Panel para visualizar y gestionar pedidos de clientes
    
    Funcionalidades:
    - Lista paginada de pedidos
    - Filtros por estado y fechas
    - Ordenamiento por diferentes campos
    - Cambio de estado de pedidos
    - Visualización de detalles completos
    - Exportación a CSV, Excel y PDF
    """

    # Constantes de clase
    ITEMS_POR_PAGINA = 20
    CAMPO_ORDEN_DEFAULT = 'fecha_ingreso'
    DIRECCION_ORDEN_DEFAULT = 'DESC'
    
    # Iconos Unicode para la interfaz
    ICONOS = {
        'actualizar': '🔄',
        'exportar': '📤',
        'filtro': '🔍',
        'limpiar': '🧹',
        'ver': '👁️',
        'anterior': '◀',
        'siguiente': '▶',
        'ordenar_asc': '▲',
        'ordenar_desc': '▼',
        'calendario': '📅',
        'cliente': '👤',
        'dinero': '💰'
    }

    def __init__(self, parent):
        """Inicializa el panel de pedidos de clientes"""
        super().__init__(parent, fg_color="transparent")
        
        # Configurar layout
        self._configurar_grid()
        
        # Inicializar variables de estado
        self._inicializar_variables()
        
        # Construir interfaz y cargar datos
        self._crear_interfaz()
        self._cargar_pedidos()

    def _configurar_grid(self):
        """Configura el sistema de grid del panel"""
        self.grid_rowconfigure(3, weight=1)  # El área de scroll se expande
        self.grid_columnconfigure(0, weight=1)

    def _inicializar_variables(self):
        """Inicializa las variables de estado del panel"""
        # Variables de paginación
        self.pagina_actual = 1
        self.items_por_pagina = self.ITEMS_POR_PAGINA
        self.pedidos_resultado = {}
        
        # Variables de filtros
        self.filtro_estado = None
        self.filtro_fecha_inicio = None
        self.filtro_fecha_fin = None
        
        # Variables de ordenamiento
        self.orden_campo = self.CAMPO_ORDEN_DEFAULT
        self.orden_dir = self.DIRECCION_ORDEN_DEFAULT
        
        # Cache de estados
        self.estados_disponibles = []

    def _crear_interfaz(self):
        """
        Crea la interfaz completa del panel
        
        Estructura:
        1. Header con título y botones de acción
        2. Barra de filtros
        3. Tabla con encabezados ordenables
        4. Lista scrollable de pedidos
        5. Controles de paginación
        """
        self._crear_header()
        self._crear_barra_filtros()
        self._crear_tabla_encabezados()
        self._crear_contenedor_pedidos()
        self._crear_controles_paginacion()

    def _crear_header(self):
        """Crea el header con título y botones principales"""
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        frame_titulo.grid_columnconfigure(1, weight=1)

        # Título con icono
        self.titulo = ctk.CTkLabel(
            frame_titulo,
            text="📋 Lista de Pedidos",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.titulo.grid(row=0, column=0, sticky="w")

        # Botón actualizar
        self.btn_actualizar = ctk.CTkButton(
            frame_titulo,
            text=f"{self.ICONOS['actualizar']}  Actualizar",
            command=self._cargar_pedidos,
            height=42,
            width=150,
            font=ctk.CTkFont(size=13),
            corner_radius=8,
            hover_color=("gray70", "gray30")
        )
        self.btn_actualizar.grid(row=0, column=2, padx=5)

        # Botón exportar
        self.btn_exportar = ctk.CTkButton(
            frame_titulo,
            text=f"{self.ICONOS['exportar']}  Exportar",
            command=self._mostrar_opciones_exportar,
            height=42,
            width=150,
            font=ctk.CTkFont(size=13),
            fg_color=COLOR_SUCCESS,
            hover_color=("#2d8a4d", "#1f6e3a"),
            corner_radius=8
        )
        self.btn_exportar.grid(row=0, column=3, padx=5)

    def _crear_barra_filtros(self):
        """Crea la barra de filtros con controles de búsqueda y filtrado"""
        # Frame principal de filtros con diseño mejorado
        frame_filtros = ctk.CTkFrame(
            self,
            fg_color=("gray85", "gray20"),
            corner_radius=10
        )
        frame_filtros.grid(row=1, column=0, pady=(0, 15), sticky="ew", padx=10)
        frame_filtros.grid_columnconfigure(5, weight=1)

        # Etiqueta de sección
        label_seccion = ctk.CTkLabel(
            frame_filtros,
            text=f"{self.ICONOS['filtro']} FILTROS",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        label_seccion.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w", columnspan=2)

        # === FILTRO POR ESTADO ===
        ctk.CTkLabel(
            frame_filtros,
            text="Estado:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=0, padx=(15, 5), pady=10, sticky="w")

        # Obtener estados desde la BD
        self.estados_disponibles = consultas.obtener_estados_pedidos()
        nombres_estados = ["Todos"] + [est['nombre'] for est in self.estados_disponibles]

        self.combo_filtro_estado = ctk.CTkComboBox(
            frame_filtros,
            values=nombres_estados,
            command=self._aplicar_filtros,
            width=180,
            height=32,
            corner_radius=8
        )
        self.combo_filtro_estado.grid(row=1, column=1, padx=5, pady=10)
        self.combo_filtro_estado.set("Todos")

        # === FILTRO POR FECHA INICIO ===
        ctk.CTkLabel(
            frame_filtros,
            text=f"{self.ICONOS['calendario']} Desde:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=2, padx=(20, 5), pady=10, sticky="w")
        
        self.entry_fecha_inicio = ctk.CTkEntry(
            frame_filtros,
            width=130,
            height=32,
            placeholder_text="YYYY-MM-DD",
            corner_radius=8
        )
        self.entry_fecha_inicio.grid(row=1, column=3, padx=5, pady=10)

        # === FILTRO POR FECHA FIN ===
        ctk.CTkLabel(
            frame_filtros,
            text=f"{self.ICONOS['calendario']} Hasta:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=1, column=4, padx=(15, 5), pady=10, sticky="w")
        
        self.entry_fecha_fin = ctk.CTkEntry(
            frame_filtros,
            width=130,
            height=32,
            placeholder_text="YYYY-MM-DD",
            corner_radius=8
        )
        self.entry_fecha_fin.grid(row=1, column=5, padx=5, pady=10)

        # === BOTONES DE ACCIÓN ===
        frame_botones = ctk.CTkFrame(frame_filtros, fg_color="transparent")
        frame_botones.grid(row=1, column=6, padx=10, pady=10, columnspan=2)

        # Botón aplicar filtros
        self.btn_aplicar_filtros = ctk.CTkButton(
            frame_botones,
            text=f"{self.ICONOS['filtro']} Aplicar",
            command=self._aplicar_filtros,
            width=110,
            height=32,
            corner_radius=8,
            fg_color=COLOR_PRIMARY
        )
        self.btn_aplicar_filtros.pack(side="left", padx=5)

        # Botón limpiar filtros
        self.btn_limpiar_filtros = ctk.CTkButton(
            frame_botones,
            text=f"{self.ICONOS['limpiar']} Limpiar",
            command=self._limpiar_filtros,
            width=110,
            height=32,
            corner_radius=8,
            fg_color=COLOR_WARNING,
            hover_color=("#d89a14", "#b87d0f")
        )
        self.btn_limpiar_filtros.pack(side="left", padx=5)

    def _crear_tabla_encabezados(self):
        """Crea la tabla de encabezados con ordenamiento"""
        frame_tabla = ctk.CTkFrame(
            self,
            fg_color=("gray80", "gray25"),
            corner_radius=10
        )
        frame_tabla.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))

        # Configuración de columnas: (texto, columna, campo_orden, ancho)
        columnas = [
            ("ID", 0, 'id_pedido', 60),
            (f"{self.ICONOS['cliente']} Cliente", 1, None, 180),
            ("Estado", 2, 'id_estado', 150),
            ("📅 Ingreso", 3, 'fecha_ingreso', 150),
            ("📅 Entrega", 4, 'fecha_entrega_estimada', 150),
            (f"{self.ICONOS['dinero']} Total", 5, 'costo_total', 100),
            ("Acciones", 6, None, 200),
        ]

        # Crear encabezados dinámicamente
        for texto, col, campo, ancho in columnas:
            self._crear_encabezado(frame_tabla, texto, col, campo, ancho)

    def _crear_contenedor_pedidos(self):
        """Crea el contenedor scrollable para la lista de pedidos"""
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            height=400,
            fg_color="transparent",
            corner_radius=10
        )
        self.scroll_frame.grid(row=3, column=0, sticky="nsew", padx=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _crear_controles_paginacion(self):
        """Crea los controles de navegación por páginas"""
        frame_paginacion = ctk.CTkFrame(
            self,
            fg_color=("gray85", "gray20"),
            corner_radius=10
        )
        frame_paginacion.grid(row=4, column=0, pady=15, sticky="ew", padx=10)
        frame_paginacion.grid_columnconfigure(1, weight=1)

        # Botón página anterior
        self.btn_anterior = ctk.CTkButton(
            frame_paginacion,
            text=f"{self.ICONOS['anterior']} Anterior",
            command=self._pagina_anterior,
            width=130,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.btn_anterior.grid(row=0, column=0, padx=15, pady=10)

        # Label indicador de página
        self.label_paginacion = ctk.CTkLabel(
            frame_paginacion,
            text="Página 1 de 1",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_paginacion.grid(row=0, column=1, padx=20)

        # Botón página siguiente
        self.btn_siguiente = ctk.CTkButton(
            frame_paginacion,
            text=f"Siguiente {self.ICONOS['siguiente']}",
            command=self._pagina_siguiente,
            width=130,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        self.btn_siguiente.grid(row=0, column=2, padx=5, sticky="e")

        # Label total de registros
        self.label_total = ctk.CTkLabel(
            frame_paginacion,
            text="Total: 0 pedidos",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        self.label_total.grid(row=0, column=3, padx=15)

    def _crear_encabezado(self, parent, texto, columna, campo_orden, width=100):
        """
        Crea un encabezado de columna con opción de ordenamiento
        
        Args:
            parent: Frame contenedor del encabezado
            texto: Texto a mostrar en el encabezado
            columna: Número de columna en el grid
            campo_orden: Campo de BD para ordenar (None si no es ordenable)
            width: Ancho del encabezado en píxeles
        """
        frame = ctk.CTkFrame(
            parent,
            fg_color=COLOR_PRIMARY,
            corner_radius=6
        )
        frame.grid(row=0, column=columna, padx=2, pady=5, sticky="ew")

        # Label del encabezado
        label = ctk.CTkLabel(
            frame,
            text=texto,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=width,
            height=38
        )
        label.pack(side="left", padx=8)

        # Agregar botones de ordenamiento si es aplicable
        if campo_orden:
            frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
            frame_botones.pack(side="right", padx=5)
            
            # Botón ordenar ascendente
            btn_asc = ctk.CTkButton(
                frame_botones,
                text=self.ICONOS['ordenar_asc'],
                width=28,
                height=28,
                font=ctk.CTkFont(size=11),
                corner_radius=5,
                fg_color=("gray70", "gray40"),
                hover_color=("gray60", "gray35"),
                command=lambda: self._ordenar_por(campo_orden, 'ASC')
            )
            btn_asc.pack(side="left", padx=2)

            # Botón ordenar descendente
            btn_desc = ctk.CTkButton(
                frame_botones,
                text=self.ICONOS['ordenar_desc'],
                width=28,
                height=28,
                font=ctk.CTkFont(size=11),
                corner_radius=5,
                fg_color=("gray70", "gray40"),
                hover_color=("gray60", "gray35"),
                command=lambda: self._ordenar_por(campo_orden, 'DESC')
            )
            btn_desc.pack(side="left", padx=2)

    # ============================================================
    # MÉTODOS DE ORDENAMIENTO Y FILTRADO
    # ============================================================

    def _ordenar_por(self, campo, direccion):
        """
        Ordena los resultados por un campo específico
        
        Args:
            campo: Campo de la BD para ordenar
            direccion: 'ASC' o 'DESC'
        """
        self.orden_campo = campo
        self.orden_dir = direccion
        self.pagina_actual = 1
        self._cargar_pedidos()

    def _aplicar_filtros(self, *args):
        """
        Aplica los filtros seleccionados por el usuario
        
        Recopila los valores de estado y fechas, valida y aplica
        los filtros, luego recarga los pedidos desde la primera página
        """
        # Obtener ID del estado si se seleccionó uno específico
        estado_nombre = self.combo_filtro_estado.get()
        if estado_nombre != "Todos":
            self.filtro_estado = self._obtener_id_estado(estado_nombre)
        else:
            self.filtro_estado = None

        # Obtener y validar fechas
        fecha_inicio = self.entry_fecha_inicio.get().strip()
        fecha_fin = self.entry_fecha_fin.get().strip()

        self.filtro_fecha_inicio = fecha_inicio if fecha_inicio else None
        self.filtro_fecha_fin = fecha_fin if fecha_fin else None

        # Resetear a primera página y cargar
        self.pagina_actual = 1
        self._cargar_pedidos()

    def _limpiar_filtros(self):
        """
        Limpia todos los filtros y resetea la vista
        
        Restaura los valores por defecto de todos los controles
        de filtrado y recarga la lista completa de pedidos
        """
        self.combo_filtro_estado.set("Todos")
        self.entry_fecha_inicio.delete(0, 'end')
        self.entry_fecha_fin.delete(0, 'end')
        
        self.filtro_estado = None
        self.filtro_fecha_inicio = None
        self.filtro_fecha_fin = None
        self.pagina_actual = 1
        
        self._cargar_pedidos()

    def _obtener_id_estado(self, nombre_estado):
        """
        Obtiene el ID de un estado a partir de su nombre
        
        Args:
            nombre_estado: Nombre del estado a buscar
            
        Returns:
            int: ID del estado o None si no se encuentra
        """
        for estado in self.estados_disponibles:
            if estado['nombre'] == nombre_estado:
                return estado['id']
        return None

    # ============================================================
    # MÉTODOS DE CARGA Y VISUALIZACIÓN DE DATOS
    # ============================================================

    def _cargar_pedidos(self):
        """
        Carga los pedidos desde la BD con paginación y filtros aplicados
        
        Consulta la BD con los filtros, ordenamiento y paginación actuales,
        luego actualiza la vista con los resultados
        """
        resultado = consultas.obtener_pedidos_filtrados(
            filtro_estado=self.filtro_estado,
            fecha_ingreso_desde=self.filtro_fecha_inicio,
            fecha_ingreso_hasta=self.filtro_fecha_fin,
            orden_campo=self.orden_campo,
            orden_direccion=self.orden_dir,
            pagina=self.pagina_actual,
            items_por_pagina=self.items_por_pagina
        )

        self.pedidos_resultado = resultado
        self._mostrar_pedidos(resultado['pedidos'])
        self._actualizar_paginacion(resultado)

    def _mostrar_pedidos(self, pedidos):
        """
        Muestra la lista de pedidos en el contenedor scrollable
        
        Args:
            pedidos: Lista de pedidos a mostrar
        """
        # Limpiar contenedor
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Mostrar mensaje si no hay pedidos
        if not pedidos or len(pedidos) == 0:
            self._mostrar_mensaje_vacio()
            return

        # Crear fila para cada pedido
        for pedido in pedidos:
            self._crear_fila_pedido(pedido)

    def _mostrar_mensaje_vacio(self):
        """Muestra un mensaje cuando no hay pedidos para mostrar"""
        frame_vacio = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_vacio.pack(expand=True, fill="both", pady=50)
        
        ctk.CTkLabel(
            frame_vacio,
            text="📭",
            font=ctk.CTkFont(size=48)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            frame_vacio,
            text="No hay pedidos para mostrar",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("gray50", "gray60")
        ).pack()
        
        ctk.CTkLabel(
            frame_vacio,
            text="Intenta ajustar los filtros o crear un nuevo pedido",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray70")
        ).pack(pady=5)

    def _crear_fila_pedido(self, pedido):
        """
        Crea una fila visual con la información completa de un pedido
        
        Args:
            pedido: Diccionario con los datos del pedido
        """
        # Extraer color del estado para la barra lateral
        color_estado = self._get_field(pedido, 'estado_color', '#808080')

        # Frame principal de la fila con diseño mejorado
        frame_pedido = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=("gray90", "gray18"),
            corner_radius=8
        )
        frame_pedido.pack(fill="x", pady=4, padx=5)

        # Barra lateral de color indicando el estado
        barra_color = ctk.CTkFrame(
            frame_pedido,
            fg_color=color_estado,
            width=6,
            corner_radius=8
        )
        barra_color.pack(side="left", fill="y", padx=(0, 8))

        # Contenedor principal de datos
        frame_datos = ctk.CTkFrame(
            frame_pedido,
            fg_color="transparent"
        )
        frame_datos.pack(side="left", fill="x", expand=True, padx=5, pady=8)

        # Fila de información
        fila = ctk.CTkFrame(frame_datos, fg_color="transparent")
        fila.pack(fill="x", padx=5)

        # === COLUMNA: ID ===
        label_id = ctk.CTkLabel(
            fila,
            text=f"#{pedido['id_pedido']}",
            width=60,
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label_id.pack(side="left", padx=5)

        # === COLUMNA: CLIENTE ===
        nombre_cliente = self._get_field(pedido, 'nombre_cliente', 'N/A')
        label_cliente = ctk.CTkLabel(
            fila,
            text=f"{self.ICONOS['cliente']} {nombre_cliente}",
            width=180,
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        label_cliente.pack(side="left", padx=5)

        # === COLUMNA: ESTADO (con selector) ===
        frame_estado = ctk.CTkFrame(
            fila,
            fg_color=color_estado,
            corner_radius=8
        )
        frame_estado.pack(side="left", padx=5)

        nombres_estados = [e['nombre'] for e in self.estados_disponibles]
        estado_nombre = self._get_field(pedido, 'estado_nombre', 'Sin estado') or 'Sin estado'

        combo_estado = ctk.CTkComboBox(
            frame_estado,
            values=nombres_estados,
            width=140,
            height=32,
            corner_radius=6,
            command=lambda choice, pid=pedido['id_pedido']: self._cambiar_estado_pedido(pid, choice)
        )
        combo_estado.pack(padx=5, pady=5)
        combo_estado.set(estado_nombre)

        # === COLUMNA: FECHA INGRESO ===
        fecha_ing = self._formatear_fecha(self._get_field(pedido, 'fecha_ingreso'))
        label_fecha_ing = ctk.CTkLabel(
            fila,
            text=fecha_ing,
            width=150,
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        label_fecha_ing.pack(side="left", padx=5)

        # === COLUMNA: FECHA ENTREGA ===
        fecha_ent = self._formatear_fecha(self._get_field(pedido, 'fecha_entrega_estimada'))
        label_fecha_ent = ctk.CTkLabel(
            fila,
            text=fecha_ent,
            width=150,
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        label_fecha_ent.pack(side="left", padx=5)

        # === COLUMNA: TOTAL ===
        costo_total = self._get_field(pedido, 'costo_total', 0)
        total_texto = f"S/. {float(costo_total):.2f}"
        label_total = ctk.CTkLabel(
            fila,
            text=total_texto,
            width=100,
            anchor="e",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_SUCCESS
        )
        label_total.pack(side="left", padx=5)

        # === COLUMNA: ACCIONES ===
        frame_acciones = ctk.CTkFrame(fila, fg_color="transparent")
        frame_acciones.pack(side="left", padx=5)

        btn_ver = ctk.CTkButton(
            frame_acciones,
            text=f"{self.ICONOS['ver']} Ver",
            command=lambda: self._ver_detalles(pedido['id_pedido']),
            width=110,
            height=32,
            corner_radius=6,
            fg_color=COLOR_PRIMARY,
            font=ctk.CTkFont(size=12)
        )
        btn_ver.pack(side="left", padx=2)

    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================

    def _get_field(self, row, field, default=None):
        """
        Accede de forma segura a campos de un objeto Row de sqlite3
        
        Args:
            row: Objeto Row de sqlite3
            field: Nombre del campo a acceder
            default: Valor por defecto si el campo no existe o es None
            
        Returns:
            Valor del campo o default
        """
        try:
            return row[field] if row[field] is not None else default
        except (KeyError, IndexError):
            return default

    def _formatear_fecha(self, fecha):
        """
        Formatea una fecha ISO a formato DD/MM/YYYY
        
        Args:
            fecha: String de fecha en formato ISO o None
            
        Returns:
            String con fecha formateada o 'N/A'
        """
        if not fecha:
            return 'N/A'
        try:
            return datetime.fromisoformat(fecha).strftime('%d/%m/%Y')
        except:
            return 'N/A'

    # ============================================================
    # MÉTODOS DE ACCIONES SOBRE PEDIDOS
    # ============================================================

    def _cambiar_estado_pedido(self, id_pedido, nuevo_estado_nombre):
        """
        Cambia el estado de un pedido específico
        
        Args:
            id_pedido: ID del pedido a actualizar
            nuevo_estado_nombre: Nombre del nuevo estado
        """
        # Obtener ID del estado desde el nombre
        id_estado = self._obtener_id_estado(nuevo_estado_nombre)

        if id_estado:
            try:
                consultas.actualizar_estado_de_pedido(id_pedido, id_estado)
                messagebox.showinfo(
                    "✅ Éxito",
                    f"Estado del pedido #{id_pedido} actualizado a '{nuevo_estado_nombre}'"
                )
                self._cargar_pedidos()  # Recargar para reflejar cambios
            except Exception as e:
                messagebox.showerror(
                    "❌ Error",
                    f"No se pudo actualizar el estado:\n{str(e)}"
                )

    def _ver_detalles(self, id_pedido):
        """
        Muestra una ventana modal con los detalles completos de un pedido
        
        Args:
            id_pedido: ID del pedido a visualizar
        """
        datos = consultas.obtener_pedido_por_id(id_pedido)
        if not datos:
            messagebox.showerror("❌ Error", "No se encontró el pedido")
            return

        pedido = datos['pedido']
        detalles = datos['detalles']

        # Crear ventana modal de detalles
        ventana = ctk.CTkToplevel(self)
        ventana.title(f"📋 Detalles del Pedido #{id_pedido}")
        ventana.geometry("750x650")
        ventana.transient(self)
        ventana.grab_set()

        # Contenido con scroll
        scroll = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # === SECCIÓN: INFORMACIÓN DEL CLIENTE ===
        self._crear_seccion_cliente(scroll, pedido)

        # === SECCIÓN: INFORMACIÓN DEL PEDIDO ===
        self._crear_seccion_pedido(scroll, pedido)

        # === SECCIÓN: DETALLES DEL PEDIDO ===
        if detalles:
            self._crear_seccion_detalles(scroll, detalles)

        # Botón cerrar
        btn_cerrar = ctk.CTkButton(
            ventana,
            text="✖ Cerrar",
            command=ventana.destroy,
            width=220,
            height=45,
            corner_radius=8,
            fg_color=COLOR_DANGER,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_cerrar.pack(pady=15)

    def _crear_seccion_cliente(self, parent, pedido):
        """Crea la sección de información del cliente"""
        frame_seccion = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"), corner_radius=10)
        frame_seccion.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            frame_seccion,
            text=f"{self.ICONOS['cliente']} INFORMACIÓN DEL CLIENTE",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=15, pady=(15, 10))

        info_cliente = [
            ("Nombre:", pedido['nombre_completo']),
            ("Teléfono:", pedido['telefono'] or 'N/A'),
            ("Email:", pedido['email'] or 'N/A'),
        ]

        for label, valor in info_cliente:
            frame_linea = ctk.CTkFrame(frame_seccion, fg_color="transparent")
            frame_linea.pack(fill="x", padx=15, pady=3)
            
            ctk.CTkLabel(
                frame_linea,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                width=100,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                frame_linea,
                text=valor,
                font=ctk.CTkFont(size=13),
                anchor="w"
            ).pack(side="left", padx=10)

        ctk.CTkLabel(frame_seccion, text="").pack(pady=5)  # Espaciado

    def _crear_seccion_pedido(self, parent, pedido):
        """Crea la sección de información del pedido"""
        frame_seccion = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"), corner_radius=10)
        frame_seccion.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            frame_seccion,
            text=f"📦 INFORMACIÓN DEL PEDIDO",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=15, pady=(15, 10))

        saldo = pedido['costo_total'] - pedido['acuenta']

        info_pedido = [
            ("Estado de Pago:", pedido['estado_pago']),
            ("Total:", f"S/. {pedido['costo_total']:.2f}"),
            ("A cuenta:", f"S/. {pedido['acuenta']:.2f}"),
            ("Saldo:", f"S/. {saldo:.2f}"),
        ]

        for label, valor in info_pedido:
            frame_linea = ctk.CTkFrame(frame_seccion, fg_color="transparent")
            frame_linea.pack(fill="x", padx=15, pady=3)
            
            ctk.CTkLabel(
                frame_linea,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                width=120,
                anchor="w"
            ).pack(side="left")
            
            color_texto = COLOR_SUCCESS if "Total" in label or "A cuenta" in label else None
            ctk.CTkLabel(
                frame_linea,
                text=valor,
                font=ctk.CTkFont(size=13, weight="bold" if "S/." in valor else "normal"),
                anchor="w",
                text_color=color_texto
            ).pack(side="left", padx=10)

        ctk.CTkLabel(frame_seccion, text="").pack(pady=5)  # Espaciado

    def _crear_seccion_detalles(self, parent, detalles):
        """Crea la sección de detalles del pedido"""
        frame_seccion = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"), corner_radius=10)
        frame_seccion.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            frame_seccion,
            text="📝 DETALLES DEL PEDIDO",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=15, pady=(15, 10))

        for idx, detalle in enumerate(detalles, 1):
            frame_det = ctk.CTkFrame(
                frame_seccion,
                fg_color=("gray75", "gray30"),
                corner_radius=8
            )
            frame_det.pack(fill="x", padx=15, pady=8)

            # Título del ítem
            ctk.CTkLabel(
                frame_det,
                text=f"Ítem #{idx}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLOR_PRIMARY
            ).pack(anchor="w", padx=10, pady=(8, 5))

            subtotal = detalle['cantidad'] * detalle['precio_unitario']

            info_detalle = [
                ("🛠️ Servicio:", detalle['nombre_servicio']),
                ("📦 Material:", detalle['nombre_material'] or 'N/A'),
                ("📏 Dimensiones:", f"{detalle['ancho']}m x {detalle['alto']}m"),
                ("🔢 Cantidad:", str(detalle['cantidad'])),
                ("💵 Precio unitario:", f"S/. {detalle['precio_unitario']:.2f}"),
                ("💰 Subtotal:", f"S/. {subtotal:.2f}"),
            ]

            for label, valor in info_detalle:
                frame_linea = ctk.CTkFrame(frame_det, fg_color="transparent")
                frame_linea.pack(fill="x", padx=10, pady=2)
                
                ctk.CTkLabel(
                    frame_linea,
                    text=label,
                    font=ctk.CTkFont(size=12),
                    width=130,
                    anchor="w"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    frame_linea,
                    text=valor,
                    font=ctk.CTkFont(size=12, weight="bold" if "Subtotal" in label else "normal"),
                    anchor="w"
                ).pack(side="left")

            ctk.CTkLabel(frame_det, text="").pack(pady=3)  # Espaciado

        ctk.CTkLabel(frame_seccion, text="").pack(pady=5)  # Espaciado

    # ============================================================
    # MÉTODOS DE PAGINACIÓN
    # ============================================================

    def _actualizar_paginacion(self, resultado):
        """
        Actualiza los controles de paginación según los resultados
        
        Args:
            resultado: Diccionario con información de paginación
        """
        pagina_actual = resultado['pagina_actual']
        total_paginas = resultado['total_paginas']
        total_registros = resultado['total']

        # Actualizar labels informativos
        self.label_paginacion.configure(
            text=f"Página {pagina_actual} de {total_paginas}"
        )
        self.label_total.configure(
            text=f"Total: {total_registros} pedido{'s' if total_registros != 1 else ''}"
        )

        # Habilitar/deshabilitar botones según disponibilidad
        self.btn_anterior.configure(
            state="normal" if pagina_actual > 1 else "disabled"
        )
        self.btn_siguiente.configure(
            state="normal" if pagina_actual < total_paginas else "disabled"
        )

    def _pagina_anterior(self):
        """Navega a la página anterior si es posible"""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self._cargar_pedidos()

    def _pagina_siguiente(self):
        """Navega a la página siguiente si es posible"""
        if self.pagina_actual < self.pedidos_resultado['total_paginas']:
            self.pagina_actual += 1
            self._cargar_pedidos()

    # ============================================================
    # MÉTODOS DE EXPORTACIÓN
    # ============================================================

    def _mostrar_opciones_exportar(self):
        """
        Muestra una ventana modal con opciones de exportación
        
        Permite al usuario elegir entre CSV, Excel o PDF para
        exportar la lista de pedidos actual
        """
        ventana = ctk.CTkToplevel(self)
        ventana.title("📤 Exportar Pedidos")
        ventana.geometry("450x380")
        ventana.transient(self)
        ventana.grab_set()

        # Header
        frame_header = ctk.CTkFrame(ventana, fg_color=COLOR_PRIMARY, corner_radius=0)
        frame_header.pack(fill="x")

        ctk.CTkLabel(
            frame_header,
            text="📊 Seleccione el formato de exportación",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=20)

        # Contenedor de opciones
        frame_opciones = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_opciones.pack(fill="both", expand=True, padx=30, pady=20)

        # Configuración de botones de exportación
        formatos = [
            ("📄 Exportar a CSV", "CSV", COLOR_PRIMARY),
            ("📊 Exportar a Excel", "Excel", COLOR_SUCCESS),
            ("📑 Exportar a PDF", "PDF", "#e74c3c"),
        ]

        for texto, formato, color in formatos:
            btn = ctk.CTkButton(
                frame_opciones,
                text=texto,
                command=lambda f=formato: self._exportar_formato(f, ventana),
                width=280,
                height=55,
                corner_radius=8,
                fg_color=color,
                font=ctk.CTkFont(size=15, weight="bold")
            )
            btn.pack(pady=12)

        # Botón cancelar
        ctk.CTkButton(
            ventana,
            text="✖ Cancelar",
            command=ventana.destroy,
            width=280,
            height=45,
            corner_radius=8,
            fg_color=COLOR_DANGER,
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 20))

    def _exportar_formato(self, formato, ventana):
        """
        Ejecuta la exportación en el formato seleccionado
        
        Args:
            formato: Tipo de formato ('CSV', 'Excel', 'PDF')
            ventana: Ventana modal a cerrar tras éxito
        """
        directorio = filedialog.askdirectory(
            title="📁 Seleccionar carpeta de destino"
        )
        
        if not directorio:
            return

        try:
            pedidos = self.pedidos_resultado['pedidos']
            
            # Ejecutar exportación según formato
            if formato == "CSV":
                ruta = exportar_a_csv(pedidos, "pedidos", directorio)
            elif formato == "Excel":
                ruta = exportar_a_excel(pedidos, "pedidos", directorio)
            elif formato == "PDF":
                ruta = exportar_a_pdf(pedidos, "pedidos", directorio)
            else:
                raise ValueError(f"Formato no soportado: {formato}")

            messagebox.showinfo(
                "✅ Éxito",
                f"Archivo exportado exitosamente:\n\n{ruta}"
            )
            ventana.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "❌ Error",
                f"Error al exportar:\n{str(e)}"
            )
