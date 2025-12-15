"""
Panel de gestión de pedidos mejorado
Permite crear cotizaciones y gestionar pedidos con interfaz visual mejorada
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

from app.config import *
from app.database import consultas
from app.logic import calculos
from app.logic.motor_inferencia import analizar_pedido_experto
from app.ui.widgets import AutocompleteEntry


class IconoSVG:
    """Clase helper para crear iconos SVG simples como texto Unicode"""
    USUARIO = "👤"
    SERVICIO = "📦"
    MATERIAL = "🎨"
    DIMENSION = "📏"
    CANTIDAD = "🔢"
    PRECIO = "💰"
    GUARDAR = "💾"
    LIMPIAR = "🔄"
    CALCULAR = "🧮"
    ROLLO = "🎯"
    RECOMENDACION = "💡"
    EXITO = "✓"
    ERROR = "✗"
    ALERTA = "⚠"
    PDF = "📄"


class PanelPedidos(ctk.CTkFrame):
    """Panel principal para gestión de pedidos con diseño mejorado"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # Configuración de la grilla principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Variables de estado
        self.servicio_actual = None
        self.rollo_seleccionado = None

        self._crear_encabezado()
        self._crear_contenedor_principal()
        self._crear_formulario()

    # ==================== CONSTRUCCIÓN DE UI ====================

    def _crear_encabezado(self):
        """Crea el encabezado del panel con título y botones de acción"""
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, pady=(0, 20), padx=10, sticky="ew")
        frame_header.grid_columnconfigure(1, weight=1)

        # Título con icono
        titulo = ctk.CTkLabel(
            frame_header,
            text=f"{IconoSVG.SERVICIO} Gestión de Pedidos",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        titulo.grid(row=0, column=0, sticky="w")

        # Botón exportar PDF
        # self.btn_exportar = ctk.CTkButton(
        #     frame_header,
        #     text=f"{IconoSVG.PDF} Exportar PDF",
        #     command=self._exportar_cotizacion_pdf,
        #     height=40,
        #     width=150,
        #     fg_color=COLOR_WARNING,
        #     hover_color="#d97706"
        # )
        # self.btn_exportar.grid(row=0, column=2, padx=5)

    def _crear_contenedor_principal(self):
        """Crea el contenedor scrollable principal"""
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _crear_formulario(self):
        """Crea el formulario completo organizado en secciones"""
        self._crear_seccion_cliente()
        self._crear_seccion_servicio()
        self._crear_seccion_dimensiones()
        self._crear_seccion_rollo_automatico()
        self._crear_seccion_recomendaciones()
        self._crear_seccion_costos()
        self._crear_botones_accion()

    def _crear_seccion_cliente(self):
        """Sección: Datos del Cliente"""
        frame = self._crear_frame_seccion(0, f"{IconoSVG.USUARIO} Datos del Cliente")

        # Cliente con autocompletado
        self._crear_campo_label(frame, "Cliente:", 1, 0)
        self.autocomplete_cliente = AutocompleteEntry(frame, width=350)
        self.autocomplete_cliente.grid(row=1, column=1, padx=15, pady=8, sticky="w")

        # Botón nuevo cliente
        self.btn_nuevo_cliente = ctk.CTkButton(
            frame,
            text=f"{IconoSVG.EXITO} Nuevo Cliente",
            command=self._mostrar_dialogo_cliente,
            width=160,
            height=36,
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            corner_radius=8
        )
        self.btn_nuevo_cliente.grid(row=1, column=2, padx=10, pady=8)

    def _crear_seccion_servicio(self):
        """Sección: Detalles del Servicio"""
        frame = self._crear_frame_seccion(1, f"{IconoSVG.SERVICIO} Detalles del Servicio")

        # Servicio
        self._crear_campo_label(frame, "Servicio:", 1, 0)
        self.combo_servicio = ctk.CTkComboBox(
            frame,
            values=self._obtener_nombres_servicios(),
            width=350,
            height=36,
            command=self._al_seleccionar_servicio,
            corner_radius=8
        )
        self.combo_servicio.grid(row=1, column=1, padx=15, pady=8, sticky="w")
        self.combo_servicio.set("Seleccionar servicio...")

        # Material (con referencias para ocultar/mostrar)
        self.label_material = self._crear_campo_label(frame, f"{IconoSVG.MATERIAL} Material:", 2, 0)
        self.combo_material = ctk.CTkComboBox(
            frame,
            values=self._obtener_nombres_materiales(),
            width=350,
            height=36,
            command=self._al_cambiar_material,
            corner_radius=8
        )
        self.combo_material.grid(row=2, column=1, padx=15, pady=8, sticky="w")

        # Descripción
        self.label_descripcion = self._crear_campo_label(frame, "Descripción:", 3, 0)
        self.entry_descripcion = ctk.CTkEntry(
            frame,
            width=500,
            height=36,
            placeholder_text="Detalles del trabajo...",
            corner_radius=8
        )
        self.entry_descripcion.grid(row=3, column=1, columnspan=2, padx=15, pady=8, sticky="w")

    def _crear_seccion_dimensiones(self):
        """Sección: Dimensiones y Cantidad"""
        frame = self._crear_frame_seccion(2, f"{IconoSVG.DIMENSION} Dimensiones y Cantidad")

        # Contenedor para campos en fila
        frame_campos = ctk.CTkFrame(frame, fg_color="transparent")
        frame_campos.grid(row=1, column=0, columnspan=3, padx=15, pady=10, sticky="ew")

        # Ancho
        self.label_ancho = ctk.CTkLabel(frame_campos, text="Ancho (m):", font=ctk.CTkFont(size=13))
        self.label_ancho.grid(row=0, column=0, padx=(0, 10), sticky="w")
        self.entry_ancho = ctk.CTkEntry(frame_campos, width=120, height=36, placeholder_text="0.00", corner_radius=8)
        self.entry_ancho.grid(row=0, column=1, padx=(0, 20))
        self.entry_ancho.bind("<KeyRelease>", self._validar_ancho_tiempo_real)

        # Alto
        self.label_alto = ctk.CTkLabel(frame_campos, text="Alto (m):", font=ctk.CTkFont(size=13))
        self.label_alto.grid(row=0, column=2, padx=(0, 10), sticky="w")
        self.entry_alto = ctk.CTkEntry(frame_campos, width=120, height=36, placeholder_text="0.00", corner_radius=8)
        self.entry_alto.grid(row=0, column=3, padx=(0, 20))
        self.entry_alto.bind("<KeyRelease>", self._al_cambiar_dimensiones)

        # Cantidad
        self.label_cantidad = ctk.CTkLabel(frame_campos, text=f"{IconoSVG.CANTIDAD} Cantidad:", font=ctk.CTkFont(size=13))
        self.label_cantidad.grid(row=0, column=4, padx=(0, 10), sticky="w")
        self.entry_cantidad = ctk.CTkEntry(frame_campos, width=120, height=36, placeholder_text="1", corner_radius=8)
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.grid(row=0, column=5)
        self.entry_cantidad.bind("<KeyRelease>", self._al_cambiar_cantidad)

        # Área calculada y Precio unitario
        frame_info = ctk.CTkFrame(frame, fg_color="transparent")
        frame_info.grid(row=2, column=0, columnspan=3, padx=15, pady=10, sticky="ew")

        self.label_area = ctk.CTkLabel(
            frame_info,
            text="Área: 0.00 m²",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.label_area.grid(row=0, column=0, padx=(0, 30), sticky="w")

        ctk.CTkLabel(frame_info, text=f"{IconoSVG.PRECIO} Precio Unitario:", font=ctk.CTkFont(size=13)).grid(row=0, column=1, padx=(0, 10), sticky="w")
        self.entry_precio_unitario = ctk.CTkEntry(frame_info, width=140, height=36, placeholder_text="0.00", corner_radius=8)
        self.entry_precio_unitario.grid(row=0, column=2)
        self.entry_precio_unitario.bind("<KeyRelease>", self._al_cambiar_precio)

    def _crear_seccion_rollo_automatico(self):
        """Sección: Selección Automática de Rollo"""
        self.frame_rollo_info = ctk.CTkFrame(self.scroll_frame, fg_color="#1a472a", corner_radius=12)
        self.frame_rollo_info.grid(row=3, column=0, pady=15, padx=10, sticky="ew")

        # Título
        titulo_rollo = ctk.CTkLabel(
            self.frame_rollo_info,
            text=f"{IconoSVG.ROLLO} Rollo Seleccionado Automáticamente",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        titulo_rollo.grid(row=0, column=0, pady=(15, 10), padx=20, sticky="w")

        # Contenido
        self.label_rollo_seleccionado = ctk.CTkLabel(
            self.frame_rollo_info,
            text="Ingrese dimensiones y seleccione material para ver recomendación...",
            font=ctk.CTkFont(size=12),
            text_color="white",
            wraplength=750,
            justify="left"
        )
        self.label_rollo_seleccionado.grid(row=1, column=0, pady=(0, 15), padx=20, sticky="w")

        # Ocultar inicialmente
        self.frame_rollo_info.grid_remove()

    def _crear_seccion_recomendaciones(self):
        """Sección: Recomendaciones del Sistema Experto"""
        frame = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_PRIMARY, corner_radius=12)
        frame.grid(row=4, column=0, pady=15, padx=10, sticky="ew")

        # Título
        titulo = ctk.CTkLabel(
            frame,
            text=f"{IconoSVG.RECOMENDACION} Recomendaciones del Sistema Experto",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        titulo.grid(row=0, column=0, pady=(15, 10), padx=20, sticky="w")

        # Contenido scrollable
        self.label_recomendaciones = ctk.CTkTextbox(
            frame,
            width=750,
            height=200,
            font=ctk.CTkFont(size=12),
            fg_color="#2d3748",
            corner_radius=8,
            wrap="word"
        )
        self.label_recomendaciones.grid(row=1, column=0, pady=(0, 15), padx=20, sticky="ew")
        self.label_recomendaciones.insert("1.0", "Complete los datos para obtener recomendaciones...")
        self.label_recomendaciones.configure(state="disabled")

    def _crear_seccion_costos(self):
        """Sección: Cotización y Costos"""
        frame = self._crear_frame_seccion(5, f"{IconoSVG.PRECIO} Cotización")

        # Precio total destacado
        self.label_precio = ctk.CTkLabel(
            frame,
            text="Precio Total: S/ 0.00",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_SUCCESS
        )
        self.label_precio.grid(row=1, column=0, columnspan=2, pady=15, padx=15, sticky="w")

        # Adelanto y Estado de pago
        frame_pago = ctk.CTkFrame(frame, fg_color="transparent")
        frame_pago.grid(row=2, column=0, columnspan=2, padx=15, pady=10, sticky="ew")

        self._crear_campo_label(frame_pago, "Adelanto (S/):", 0, 0)
        self.entry_adelanto = ctk.CTkEntry(frame_pago, width=150, height=36, placeholder_text="0.00", corner_radius=8)
        self.entry_adelanto.insert(0, "0")
        self.entry_adelanto.grid(row=0, column=1, padx=(10, 30), sticky="w")

        self._crear_campo_label(frame_pago, "Estado de Pago:", 0, 2)
        self.combo_estado_pago = ctk.CTkComboBox(
            frame_pago,
            values=ESTADOS_PAGO,
            width=200,
            height=36,
            corner_radius=8
        )
        self.combo_estado_pago.grid(row=0, column=3, padx=10, sticky="w")
        self.combo_estado_pago.set("Pendiente")

    def _crear_botones_accion(self):
        """Crea los botones de acción principales"""
        frame_botones = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_botones.grid(row=6, column=0, pady=30, padx=10, sticky="ew")

        # Botón Calcular
        self.btn_calcular = ctk.CTkButton(
            frame_botones,
            text=f"{IconoSVG.CALCULAR} Calcular Cotización",
            command=self._calcular_cotizacion,
            height=50,
            width=260,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLOR_PRIMARY,
            hover_color="#2563eb",
            corner_radius=10
        )
        self.btn_calcular.pack(side="left", padx=10)

        # Botón Guardar
        self.btn_guardar = ctk.CTkButton(
            frame_botones,
            text=f"{IconoSVG.GUARDAR} Guardar Pedido",
            command=self._guardar_pedido,
            height=50,
            width=260,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            corner_radius=10
        )
        self.btn_guardar.pack(side="left", padx=10)

        # Botón Limpiar
        self.btn_limpiar = ctk.CTkButton(
            frame_botones,
            text=f"{IconoSVG.LIMPIAR} Limpiar",
            command=self._limpiar_formulario,
            height=50,
            width=160,
            font=ctk.CTkFont(size=16),
            fg_color="gray",
            hover_color="#6b7280",
            corner_radius=10
        )
        self.btn_limpiar.pack(side="left", padx=10)

    # ==================== HELPERS DE UI ====================

    def _crear_frame_seccion(self, row, titulo):
        """Crea un frame de sección con título"""
        frame = ctk.CTkFrame(self.scroll_frame, corner_radius=12)
        frame.grid(row=row, column=0, pady=12, padx=10, sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        # Título de sección
        ctk.CTkLabel(
            frame,
            text=titulo,
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=(15, 10), sticky="w", padx=20)

        return frame

    def _crear_campo_label(self, parent, texto, row, col):
        """Crea una etiqueta de campo estilizada"""
        label = ctk.CTkLabel(
            parent,
            text=texto,
            font=ctk.CTkFont(size=13)
        )
        label.grid(row=row, column=col, padx=15, pady=8, sticky="w")
        return label

    # ==================== OBTENCIÓN DE DATOS ====================

    def _obtener_nombres_clientes(self):
        """Obtiene nombres de clientes desde la base de datos"""
        return [c['nombre_completo'] for c in consultas.obtener_clientes()]

    def _obtener_nombres_servicios(self):
        """Obtiene nombres de servicios desde la base de datos"""
        return [s['nombre_servicio'] for s in consultas.obtener_servicios()]

    def _obtener_nombres_materiales(self):
        """Obtiene nombres de materiales desde la base de datos"""
        return [m['nombre_material'] for m in consultas.obtener_materiales()]

    # ==================== DIÁLOGOS ====================

    def _mostrar_dialogo_cliente(self):
        """Muestra diálogo modal para registro rápido de cliente"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Registro Rápido de Cliente")
        dialogo.geometry("480x320")
        dialogo.resizable(False, False)
        dialogo.transient(self)
        dialogo.grab_set()

        # Contenedor principal
        frame = ctk.CTkFrame(dialogo, corner_radius=15)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        ctk.CTkLabel(
            frame,
            text=f"{IconoSVG.USUARIO} Nuevo Cliente",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(15, 25))

        # Campo Nombre
        ctk.CTkLabel(frame, text="Nombre Completo *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=30)
        entry_nombre = ctk.CTkEntry(frame, width=400, height=40, placeholder_text="Ingrese nombre completo", corner_radius=8)
        entry_nombre.pack(padx=30, pady=(5, 15))
        entry_nombre.focus()

        # Campo Celular
        ctk.CTkLabel(frame, text="Número de Celular *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=30)
        entry_celular = ctk.CTkEntry(frame, width=400, height=40, placeholder_text="Mínimo 9 dígitos", corner_radius=8)
        entry_celular.pack(padx=30, pady=(5, 15))

        # Label de error
        label_error = ctk.CTkLabel(frame, text="", text_color=COLOR_DANGER, font=ctk.CTkFont(size=11))
        label_error.pack(pady=(0, 10))

        def guardar():
            """Valida y guarda el cliente"""
            nombre = entry_nombre.get().strip()
            celular = entry_celular.get().strip()

            if not nombre:
                label_error.configure(text=f"{IconoSVG.ERROR} El nombre es obligatorio")
                return

            if not celular or len(celular) < 9:
                label_error.configure(text=f"{IconoSVG.ERROR} El celular debe tener al menos 9 dígitos")
                return

            try:
                id_cliente = consultas.guardar_cliente(nombre, celular)
                if id_cliente:
                    dialogo.destroy()
                    self.autocomplete_cliente.entry.delete(0, "end")
                    self.autocomplete_cliente.entry.insert(0, nombre)
                    cliente = consultas.obtener_cliente_por_id(id_cliente)
                    self.autocomplete_cliente.cliente_seleccionado = cliente
                    messagebox.showinfo("Éxito", f"{IconoSVG.EXITO} Cliente '{nombre}' registrado correctamente")
            except Exception as e:
                label_error.configure(text=f"{IconoSVG.ERROR} Error: {str(e)}")

        # Botones
        frame_btn = ctk.CTkFrame(frame, fg_color="transparent")
        frame_btn.pack(pady=15)

        ctk.CTkButton(
            frame_btn, text=f"{IconoSVG.EXITO} Guardar", command=guardar,
            width=180, height=40, fg_color=COLOR_SUCCESS, corner_radius=8
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_btn, text=f"{IconoSVG.ERROR} Cancelar", command=dialogo.destroy,
            width=120, height=40, fg_color="gray", corner_radius=8
        ).pack(side="left", padx=5)

        entry_celular.bind("<Return>", lambda e: guardar())

    # ==================== EVENTOS Y LÓGICA ====================

    def _al_seleccionar_servicio(self, choice):
        """Maneja la selección de servicio y aplica lógica adaptativa"""
        if choice == "Seleccionar servicio...":
            return

        # Buscar y almacenar servicio actual
        for servicio in consultas.obtener_servicios():
            if servicio['nombre_servicio'] == choice:
                self.servicio_actual = servicio
                break

        # FASE 2: Filtrar materiales compatibles según asociaciones
        if self.servicio_actual:
            materiales = consultas.obtener_materiales_por_servicio(self.servicio_actual['id_servicio'])
            if materiales:
                # Ordenar: preferidos primero
                materiales_ordenados = sorted(materiales, key=lambda m: not m.get('es_preferido', False))
                nombres = []
                for m in materiales_ordenados:
                    prefijo = "⭐ " if m.get('es_preferido') else ""
                    nombres.append(f"{prefijo}{m['nombre_material']}")
                
                self.combo_material.configure(values=nombres)
                self.combo_material.set(nombres[0])
                self._materiales_filtrados = materiales_ordenados
            else:
                # Si no hay materiales asociados, mostrar todos
                self.combo_material.configure(values=self._obtener_nombres_materiales())
                self._materiales_filtrados = None

        self._aplicar_logica_servicio(choice)

    def _aplicar_logica_servicio(self, nombre_servicio):
        """RQ-03, RQ-08: Aplica reglas de UI según tipo de servicio"""
        nombre_lower = nombre_servicio.lower()

        # RQ-03: Determinar si mostrar dimensiones según tipo_material del servicio
        mostrar_dimensiones = False

        if self.servicio_actual:
            # Usar el campo tipo_material para determinar si requiere dimensiones
            tipo_material = self.servicio_actual.get('tipo_material', 'unidad')
            mostrar_dimensiones = tipo_material == 'dimension'

        # RQ-02: Mostrar/ocultar panel de dimensiones dinámicamente
        widgets_dimension = [self.label_ancho, self.entry_ancho, self.label_alto, self.entry_alto, self.label_area]
        for widget in widgets_dimension:
            if mostrar_dimensiones:
                widget.grid()
            else:
                widget.grid_remove()

        # Lógica especial para llaveros
        es_llavero = "llavero" in nombre_lower
        if es_llavero:
            self.label_material.grid_remove()
            self.combo_material.grid_remove()
            self.label_descripcion.configure(text="Descripción *", text_color=COLOR_DANGER)
            self.entry_descripcion.configure(placeholder_text="Obligatorio: Especifique características")
        else:
            self.label_material.grid()
            self.combo_material.grid()
            self.label_descripcion.configure(text="Descripción:", text_color="white")
            self.entry_descripcion.configure(placeholder_text="Detalles del trabajo...")

        # Aplicar actualización adicional de campos
        self._actualizar_campos_producto(nombre_servicio)

    def _actualizar_campos_producto(self, nombre_servicio):
        """Actualiza campos específicos según tipo de producto"""
        nombre_lower = nombre_servicio.lower()

        # Flyers/Tarjetas: cambiar a "Millares"
        if "flyer" in nombre_lower or "tarjeta" in nombre_lower:
            self.label_cantidad.configure(text=f"{IconoSVG.CANTIDAD} Millares:")
        else:
            self.label_cantidad.configure(text=f"{IconoSVG.CANTIDAD} Cantidad:")

        # Tazas: precio automático
        if "taza" in nombre_lower:
            self.entry_precio_unitario.configure(state="disabled")
        else:
            self.entry_precio_unitario.configure(state="normal")

    def _al_cambiar_material(self, choice):
        """Maneja cambio de material y selecciona rollo automáticamente"""
        self._seleccionar_rollo_automaticamente()

    def _al_cambiar_cantidad(self, event=None):
        """Valida cantidad y calcula precios según reglas de negocio"""
        servicio = self.combo_servicio.get()
        if servicio == "Seleccionar servicio...":
            return

        try:
            cantidad = int(self.entry_cantidad.get() or 0)
            if cantidad <= 0:
                return

            # Validar restricciones para llaveros
            es_valido, mensaje, cantidad_sugerida = calculos.validar_restricciones_cantidad(servicio, cantidad)
            if not es_valido:
                if messagebox.askyesno("Cantidad Inválida", f"{mensaje}\n\n¿Ajustar a {cantidad_sugerida}?"):
                    self.entry_cantidad.delete(0, "end")
                    self.entry_cantidad.insert(0, str(cantidad_sugerida))
                    cantidad = cantidad_sugerida

            # Calcular precio sugerido para tazas
            precio = calculos.calcular_precio_sugerido(servicio, cantidad)
            if precio:
                self.entry_precio_unitario.configure(state="normal")
                self.entry_precio_unitario.delete(0, "end")
                self.entry_precio_unitario.insert(0, f"{precio:.2f}")
                self.entry_precio_unitario.configure(state="disabled")

            self._calcular_total_automatico()
        except ValueError:
            pass

    def _al_cambiar_precio(self, event=None):
        """Recalcula total al cambiar precio unitario"""
        self._calcular_total_automatico()

    def _calcular_total_automatico(self):
        """Calcula y muestra el total automáticamente"""
        try:
            servicio = self.combo_servicio.get()
            if servicio == "Seleccionar servicio...":
                return

            cantidad = float(self.entry_cantidad.get() or 0)
            precio_unit = float(self.entry_precio_unitario.get() or 0)

            # Convertir millares si aplica
            if "flyer" in servicio.lower() or "tarjeta" in servicio.lower():
                cantidad = calculos.convertir_millares_a_unidades(cantidad)

            total = cantidad * precio_unit
            self.label_precio.configure(text=f"Precio Total: S/ {total:.2f}")
        except ValueError:
            pass

    def _validar_ancho_tiempo_real(self, event=None):
        """Valida ancho y muestra recomendaciones de optimización"""
        try:
            servicio = self.combo_servicio.get()
            if servicio == "Seleccionar servicio...":
                return

            ancho = float(self.entry_ancho.get() or 0)
            if ancho <= 0:
                return

            # Validar optimización usando el Sistema Experto
            alto = float(self.entry_alto.get() or 0)
            id_servicio = self.servicio_actual.get('id_servicio') if self.servicio_actual else None
            resultado_opt = calculos.validar_optimizacion_impresion(
                ancho=ancho,
                alto=alto,
                nombre_servicio=servicio,
                id_servicio=id_servicio
            )
            if resultado_opt.get('requiere_optimizacion') and resultado_opt.get('mensaje'):
                messagebox.showwarning(f"{IconoSVG.ALERTA} Optimización Recomendada", resultado_opt['mensaje'])

            self._al_cambiar_dimensiones()
            self._seleccionar_rollo_automaticamente()
        except ValueError:
            pass

    def _al_cambiar_dimensiones(self, event=None):
        """Calcula y muestra el área"""
        try:
            ancho = float(self.entry_ancho.get() or 0)
            alto = float(self.entry_alto.get() or 0)

            if ancho > 0 and alto > 0:
                area = calculos.calcular_area(ancho, alto)
                self.label_area.configure(text=f"Área: {area:.2f} m²")
            else:
                self.label_area.configure(text="Área: 0.00 m²")
        except ValueError:
            self.label_area.configure(text="Área: 0.00 m²")

    def _seleccionar_rollo_automaticamente(self):
        """Selecciona rollo óptimo según dimensiones y material"""
        try:
            ancho_str = self.entry_ancho.get()
            material_nombre = self.combo_material.get()

            if not ancho_str or not material_nombre:
                self.frame_rollo_info.grid_remove()
                return

            # FASE 2: Limpiar prefijos de preferido
            material_limpio = material_nombre.replace("⭐ ", "").strip()
            
            ancho = float(ancho_str)
            materiales_disp = consultas.obtener_materiales_por_tipo_y_ancho(material_limpio)

            if not materiales_disp:
                self.frame_rollo_info.grid_remove()
                return

            rollo_optimo = calculos.seleccionar_rollo_optimo(ancho, material_limpio, materiales_disp)

            if rollo_optimo:
                self.rollo_seleccionado = rollo_optimo
                alto = float(self.entry_alto.get() or 0)

                verificacion = calculos.verificar_disponibilidad_lineal(
                    rollo_optimo['id_material'],
                    alto,
                    consultas.obtener_rollo_por_id
                )

                color = "#1a472a" if verificacion['puede_continuar'] else "#7a1a1a"
                self.frame_rollo_info.configure(fg_color=color)

                mensaje = (
                    f"{IconoSVG.EXITO} Material: {rollo_optimo['nombre_material']}\n"
                    f"{IconoSVG.EXITO} Ancho de rollo: {rollo_optimo['ancho_bobina']:.2f} m\n"
                    f"{IconoSVG.EXITO} Ancho necesario (con margen): {rollo_optimo['ancho_necesario']:.2f} m\n"
                    f"{IconoSVG.EXITO} Stock disponible: {rollo_optimo['cantidad_stock']:.2f} m\n\n"
                    f"{verificacion['mensaje']}"
                )

                self.label_rollo_seleccionado.configure(text=mensaje)
                self.frame_rollo_info.grid()
            else:
                self.rollo_seleccionado = None
                self.frame_rollo_info.configure(fg_color="#7a1a1a")

                mensaje = (
                    f"{IconoSVG.ERROR} No hay rollo disponible\n\n"
                    f"No existe un rollo de '{material_limpio}' suficientemente ancho.\n"
                    f"Ancho requerido: {ancho + 0.05:.2f} m"
                )

                self.label_rollo_seleccionado.configure(text=mensaje)
                self.frame_rollo_info.grid()

        except (ValueError, Exception) as e:
            self.frame_rollo_info.grid_remove()

    # ==================== ACCIONES PRINCIPALES ====================

    def _calcular_cotizacion(self):
        """RQ-09: Calcula cotización con validación unificada de dimensiones según unidad de medida"""
        try:
            if self.combo_servicio.get() == "Seleccionar servicio...":
                messagebox.showwarning(f"{IconoSVG.ALERTA} Validación", "Debe seleccionar un servicio")
                return

            # RQ-01, RQ-04: Verificar si requiere dimensiones según unidad de medida
            unidades_espaciales = ['m', 'cm', 'm2', 'cm2']
            requiere_dimensiones = False

            if self.servicio_actual:
                # Acceso seguro a la unidad de cobro
                unidad = self.servicio_actual.get('unidad_cobro', '') if isinstance(self.servicio_actual, dict) else ''
                if unidad:
                    unidad = unidad.strip().lower()
                    # RQ-01: Solo requiere dimensiones si la unidad coincide exactamente
                    requiere_dimensiones = unidad in unidades_espaciales

            # RQ-04: Obtener dimensiones solo si el servicio las requiere
            if requiere_dimensiones:
                ancho = float(self.entry_ancho.get() or 0)
                alto = float(self.entry_alto.get() or 0)
                # RQ-01: Validar solo cuando las dimensiones son obligatorias
                if ancho <= 0 or alto <= 0:
                    messagebox.showwarning(f"{IconoSVG.ALERTA} Validación", "El servicio seleccionado requiere dimensiones válidas")
                    return
            else:
                # RQ-04: Ignorar dimensiones completamente para servicios sin unidad espacial
                ancho, alto = 1.0, 1.0

            cantidad = int(self.entry_cantidad.get() or 1)
            servicio = self.combo_servicio.get()

            # Análisis del sistema experto (Motor de Inferencia Dinámico)
            id_servicio = self.servicio_actual.get('id_servicio') if self.servicio_actual else None
            analisis = analizar_pedido_experto(
                id_servicio=id_servicio,
                ancho=ancho,
                alto=alto,
                cantidad=cantidad
            )

            # Formatear recomendaciones
            texto = self._formatear_recomendaciones(analisis)
            self.label_recomendaciones.configure(state="normal")
            self.label_recomendaciones.delete("1.0", "end")
            self.label_recomendaciones.insert("1.0", texto)
            self.label_recomendaciones.configure(state="disabled")

            # Calcular precio según tipo de servicio
            if requiere_dimensiones:
                area = calculos.calcular_area(ancho, alto)
                precio_total = calculos.calcular_costo_total(area * 25.0 * cantidad, 0)
            else:
                # Acceso seguro al precio base del servicio
                precio_base = self.servicio_actual.get('precio_base', 0) if isinstance(self.servicio_actual, dict) else 0
                precio_total = precio_base * cantidad

            self.label_precio.configure(text=f"Precio Total: S/ {precio_total:.2f}")
            messagebox.showinfo(f"{IconoSVG.EXITO} Cotización", "Cotización calculada exitosamente")

        except ValueError as e:
            messagebox.showerror(f"{IconoSVG.ERROR} Error", f"Datos inválidos: {str(e)}")

    def _formatear_recomendaciones(self, analisis):
        """Formatea el análisis del sistema experto (Motor de Inferencia)"""
        texto = f"{IconoSVG.RECOMENDACION} MAQUINA RECOMENDADA\n"
        
        # Máquina recomendada
        maq = analisis.get('recomendacion_maquina', {})
        if maq.get('nombre'):
            texto += f"{maq['nombre']}\n"
            texto += f"{maq.get('explicacion', '')}\n"
            # Mostrar origen de la inferencia
            origen = maq.get('origen_inferencia', '')
            if origen == 'bd_servicio':
                texto += "(Basado en reglas del servicio)\n"
            elif origen == 'bd_capacidad':
                texto += "(Basado en capacidad fisica)\n"
        else:
            texto += "No hay maquina disponible\n"
        
        texto += "\n"
        
        # Material recomendado
        texto += f"{IconoSVG.MATERIAL} MATERIAL SUGERIDO\n"
        mat = analisis.get('recomendacion_material', {})
        if mat.get('nombre'):
            texto += f"{mat['nombre']}\n"
            texto += f"{mat.get('explicacion', '')}\n"
            # Alternativas
            alternativas = mat.get('alternativas', [])
            if alternativas:
                texto += "Alternativas: "
                texto += ", ".join([a['nombre'] for a in alternativas[:3]])
                texto += "\n"
        else:
            texto += "Sin materiales configurados para este servicio\n"
        
        texto += "\n"
        
        # Tiempo estimado
        texto += f"{IconoSVG.CALCULAR} TIEMPO ESTIMADO\n"
        tiempo = analisis.get('tiempo_estimado', {})
        texto += f"Produccion: {tiempo.get('horas_estimadas', 0):.1f} horas\n"
        texto += f"{tiempo.get('explicacion', '')}\n"
        
        # Alertas y advertencias
        alertas = analisis.get('alertas', [])
        errores = analisis.get('errores', [])
        
        if errores:
            texto += f"\n{IconoSVG.ERROR} ERRORES\n"
            for err in errores:
                texto += f"* {err}\n"
        
        if alertas:
            texto += f"\n{IconoSVG.ALERTA} ADVERTENCIAS\n"
            for alerta in alertas:
                texto += f"* {alerta}\n"
        
        # Resumen
        resumen = analisis.get('resumen', {})
        if resumen:
            texto += f"\n--- RESUMEN ---\n"
            texto += f"Area: {resumen.get('area_m2', 0)} m2\n"
            texto += f"Cantidad: {resumen.get('cantidad', 1)}\n"
        
        return texto

    def _guardar_pedido(self):
        """Guarda el pedido en la base de datos"""
        try:
            # Validaciones
            cliente = self.autocomplete_cliente.get_cliente_seleccionado()
            if not cliente:
                messagebox.showwarning(f"{IconoSVG.ALERTA} Validación", "Debe seleccionar un cliente")
                return

            if self.combo_servicio.get() == "Seleccionar servicio...":
                messagebox.showwarning(f"{IconoSVG.ALERTA} Validación", "Debe seleccionar un servicio")
                return

            # Validar descripción para llaveros
            if "llavero" in self.combo_servicio.get().lower():
                if not self.entry_descripcion.get().strip():
                    messagebox.showwarning(f"{IconoSVG.ALERTA} Validación", "La descripción es obligatoria para llaveros")
                    return

            # Obtener material (limpiar prefijos de preferido)
            material_nombre = self.combo_material.get().replace("⭐ ", "").strip()
            
            # Obtener precio
            precio_texto = self.label_precio.cget("text")
            precio_total = float(precio_texto.split("S/ ")[1])

            if precio_total == 0:
                messagebox.showwarning(f"{IconoSVG.ALERTA} Validación", "Debe calcular la cotización primero")
                return

            adelanto = float(self.entry_adelanto.get() or 0)
            fecha_entrega = datetime.now() + timedelta(days=3)

            # Validar fecha/hora
            es_valida, msg = calculos.validar_fecha_hora_entrega_completa(
                fecha_entrega,
                HORAS_MINIMAS_ANTICIPACION,
                HORA_ENTREGA_MINIMA,
                HORA_ENTREGA_MAXIMA
            )

            if not es_valida:
                messagebox.showerror(f"{IconoSVG.ERROR} Validación", msg)
                return

            # Guardar
            id_pedido = consultas.guardar_pedido(
                id_cliente=cliente['id_cliente'],
                fecha_entrega=fecha_entrega,
                estado="Cotizado",
                estado_pago=self.combo_estado_pago.get(),
                costo_total=precio_total,
                acuenta=adelanto,
                observaciones=self.entry_descripcion.get()
            )

            messagebox.showinfo(f"{IconoSVG.EXITO} Éxito", f"Pedido #{id_pedido} guardado correctamente")
            self._limpiar_formulario()

        except Exception as e:
            messagebox.showerror(f"{IconoSVG.ERROR} Error", f"Error al guardar: {str(e)}")

    def _limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.autocomplete_cliente.clear()
        self.combo_servicio.set("Seleccionar servicio...")
        self.entry_descripcion.delete(0, "end")
        self.entry_ancho.delete(0, "end")
        self.entry_alto.delete(0, "end")
        self.entry_cantidad.delete(0, "end")
        self.entry_cantidad.insert(0, "1")
        self.entry_adelanto.delete(0, "end")
        self.entry_adelanto.insert(0, "0")
        self.combo_estado_pago.set("Pendiente")
        self.label_area.configure(text="Área: 0.00 m²")
        self.label_precio.configure(text="Precio Total: S/ 0.00")
        self.label_recomendaciones.configure(state="normal")
        self.label_recomendaciones.delete("1.0", "end")
        self.label_recomendaciones.insert("1.0", "Complete los datos para obtener recomendaciones...")
        self.label_recomendaciones.configure(state="disabled")
        self.frame_rollo_info.grid_remove()

    # ==================== EXPORTACIÓN PDF ====================

    def _exportar_cotizacion_pdf(self):
        """Exporta la cotización actual a PDF"""
        try:
            # Validar que haya cotización
            if "S/ 0.00" in self.label_precio.cget("text"):
                messagebox.showwarning(f"{IconoSVG.ALERTA} Exportar", "No hay cotización para exportar. Calcule primero.")
                return

            # Seleccionar archivo
            archivo = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=f"Cotizacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            if not archivo:
                return

            # Crear PDF
            c = canvas.Canvas(archivo, pagesize=letter)
            width, height = letter

            # Título
            c.setFont("Helvetica-Bold", 24)
            c.drawString(50, height - 50, "COTIZACIÓN")

            # Datos del cliente
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 100, "CLIENTE:")
            c.setFont("Helvetica", 12)
            cliente = self.autocomplete_cliente.entry.get()
            c.drawString(70, height - 120, cliente if cliente else "No especificado")

            # Servicio
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 160, "SERVICIO:")
            c.setFont("Helvetica", 12)
            c.drawString(70, height - 180, self.combo_servicio.get())

            # Material
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 220, "MATERIAL:")
            c.setFont("Helvetica", 12)
            c.drawString(70, height - 240, self.combo_material.get())

            # Dimensiones
            ancho = self.entry_ancho.get()
            alto = self.entry_alto.get()
            if ancho and alto:
                c.setFont("Helvetica-Bold", 14)
                c.drawString(50, height - 280, "DIMENSIONES:")
                c.setFont("Helvetica", 12)
                c.drawString(70, height - 300, f"Ancho: {ancho} m  |  Alto: {alto} m")

            # Cantidad
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 340, "CANTIDAD:")
            c.setFont("Helvetica", 12)
            c.drawString(70, height - 360, self.entry_cantidad.get())

            # Precio
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 420, "PRECIO TOTAL:")
            c.setFont("Helvetica-Bold", 24)
            c.setFillColorRGB(0, 0.6, 0)
            c.drawString(70, height - 450, self.label_precio.cget("text").replace("Precio Total: ", ""))

            # Footer
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica", 10)
            c.drawString(50, 50, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            c.drawString(50, 35, "Sistema de Gestión de Imprenta v2.0")

            c.save()

            messagebox.showinfo(f"{IconoSVG.EXITO} Exportar", f"PDF generado exitosamente:\n{archivo}")

        except Exception as e:
            messagebox.showerror(f"{IconoSVG.ERROR} Error", f"Error al exportar PDF: {str(e)}")

