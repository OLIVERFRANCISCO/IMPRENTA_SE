"""
Panel de gestión de pedidos
Permite crear cotizaciones y gestionar pedidos
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from app.config import *
from app.database import consultas
from app.logic import calculos, reglas_experto
from app.ui.widgets import AutocompleteEntry


class PanelPedidos(ctk.CTkFrame):
    """Panel para crear y gestionar pedidos"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título
        self.titulo = ctk.CTkLabel(
            self,
            text="Gestión de Pedidos",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.titulo.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Contenedor con scroll
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self._crear_formulario()

    def _crear_formulario(self):
        """Crea el formulario de nuevo pedido"""

        # ===== SECCIÓN 1: DATOS DEL CLIENTE =====
        frame_cliente = ctk.CTkFrame(self.scroll_frame)
        frame_cliente.grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        frame_cliente.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_cliente,
            text="Datos del Cliente",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=10, sticky="w", padx=15)

        # Selector de cliente con autocompletado
        ctk.CTkLabel(frame_cliente, text="Cliente:").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.autocomplete_cliente = AutocompleteEntry(
            frame_cliente,
            width=300
        )
        self.autocomplete_cliente.grid(row=1, column=1, padx=15, pady=5, sticky="w")

        # Botón nuevo cliente
        self.btn_nuevo_cliente = ctk.CTkButton(
            frame_cliente,
            text="+ Nuevo Cliente",
            command=self._mostrar_dialogo_cliente,
            width=150,
            fg_color=COLOR_SUCCESS
        )
        self.btn_nuevo_cliente.grid(row=1, column=2, padx=10, pady=5)

        # ===== SECCIÓN 2: DATOS DEL SERVICIO =====
        frame_servicio = ctk.CTkFrame(self.scroll_frame)
        frame_servicio.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
        frame_servicio.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_servicio,
            text="Detalles del Servicio",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=10, sticky="w", padx=15)

        # Tipo de servicio
        ctk.CTkLabel(frame_servicio, text="Servicio:").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.combo_servicio = ctk.CTkComboBox(
            frame_servicio,
            values=self._obtener_nombres_servicios(),
            width=300,
            command=self._al_seleccionar_servicio
        )
        self.combo_servicio.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        self.combo_servicio.set("Seleccionar servicio...")

        # Material
        ctk.CTkLabel(frame_servicio, text="Material:").grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.combo_material = ctk.CTkComboBox(
            frame_servicio,
            values=self._obtener_nombres_materiales(),
            width=300
        )
        self.combo_material.grid(row=2, column=1, padx=15, pady=5, sticky="w")

        # Descripción
        ctk.CTkLabel(frame_servicio, text="Descripción:").grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.entry_descripcion = ctk.CTkEntry(frame_servicio, width=400, placeholder_text="Detalles del trabajo...")
        self.entry_descripcion.grid(row=3, column=1, padx=15, pady=5, sticky="w")

        # ===== SECCIÓN 3: DIMENSIONES Y CANTIDAD =====
        frame_dimensiones = ctk.CTkFrame(self.scroll_frame)
        frame_dimensiones.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(
            frame_dimensiones,
            text="Dimensiones y Cantidad",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=4, pady=10, sticky="w", padx=15)

        # Ancho
        ctk.CTkLabel(frame_dimensiones, text="Ancho (m):").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.entry_ancho = ctk.CTkEntry(frame_dimensiones, width=120, placeholder_text="0.00")
        self.entry_ancho.grid(row=1, column=1, padx=5, pady=5)
        self.entry_ancho.bind("<KeyRelease>", self._al_cambiar_dimensiones)

        # Alto
        ctk.CTkLabel(frame_dimensiones, text="Alto (m):").grid(row=1, column=2, padx=15, pady=5, sticky="w")
        self.entry_alto = ctk.CTkEntry(frame_dimensiones, width=120, placeholder_text="0.00")
        self.entry_alto.grid(row=1, column=3, padx=5, pady=5)
        self.entry_alto.bind("<KeyRelease>", self._al_cambiar_dimensiones)

        # Cantidad
        ctk.CTkLabel(frame_dimensiones, text="Cantidad:").grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.entry_cantidad = ctk.CTkEntry(frame_dimensiones, width=120, placeholder_text="1")
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.grid(row=2, column=1, padx=5, pady=5)
        self.entry_cantidad.bind("<KeyRelease>", self._al_cambiar_dimensiones)

        # Área calculada
        self.label_area = ctk.CTkLabel(
            frame_dimensiones,
            text="Área: 0.00 m²",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLOR_PRIMARY
        )
        self.label_area.grid(row=2, column=2, columnspan=2, padx=15, pady=5, sticky="w")

        # ===== SECCIÓN 4: RECOMENDACIONES DEL SISTEMA EXPERTO =====
        self.frame_recomendaciones = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_PRIMARY)
        self.frame_recomendaciones.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(
            self.frame_recomendaciones,
            text="Recomendaciones del Sistema Experto",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).grid(row=0, column=0, pady=10, sticky="w", padx=15)

        self.label_recomendaciones = ctk.CTkLabel(
            self.frame_recomendaciones,
            text="Complete los datos para obtener recomendaciones...",
            font=ctk.CTkFont(size=12),
            text_color="white",
            justify="left"
        )
        self.label_recomendaciones.grid(row=1, column=0, pady=10, padx=15, sticky="w")

        # ===== SECCIÓN 5: COSTOS =====
        frame_costos = ctk.CTkFrame(self.scroll_frame)
        frame_costos.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

        ctk.CTkLabel(
            frame_costos,
            text="Cotización",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=2, pady=10, sticky="w", padx=15)

        # Precio calculado
        self.label_precio = ctk.CTkLabel(
            frame_costos,
            text="Precio Total: S/ 0.00",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLOR_SUCCESS
        )
        self.label_precio.grid(row=1, column=0, columnspan=2, pady=10, padx=15, sticky="w")

        # Adelanto
        ctk.CTkLabel(frame_costos, text="Adelanto:").grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.entry_adelanto = ctk.CTkEntry(frame_costos, width=150, placeholder_text="0.00")
        self.entry_adelanto.insert(0, "0")
        self.entry_adelanto.grid(row=2, column=1, padx=15, pady=5, sticky="w")

        # Estado de pago
        ctk.CTkLabel(frame_costos, text="Estado de pago:").grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.combo_estado_pago = ctk.CTkComboBox(
            frame_costos,
            values=ESTADOS_PAGO,
            width=200
        )
        self.combo_estado_pago.grid(row=3, column=1, padx=15, pady=5, sticky="w")
        self.combo_estado_pago.set("Pendiente")

        # ===== BOTONES DE ACCIÓN =====
        frame_botones = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_botones.grid(row=5, column=0, pady=20, padx=10, sticky="ew")

        self.btn_calcular = ctk.CTkButton(
            frame_botones,
            text="Calcular Cotización",
            command=self._calcular_cotizacion,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLOR_PRIMARY,
            width=250
        )
        self.btn_calcular.pack(side="left", padx=10)

        self.btn_guardar = ctk.CTkButton(
            frame_botones,
            text="Guardar Pedido",
            command=self._guardar_pedido,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLOR_SUCCESS,
            width=250
        )
        self.btn_guardar.pack(side="left", padx=10)

        self.btn_limpiar = ctk.CTkButton(
            frame_botones,
            text="Limpiar",
            command=self._limpiar_formulario,
            height=50,
            font=ctk.CTkFont(size=16),
            fg_color="gray",
            width=150
        )
        self.btn_limpiar.pack(side="left", padx=10)

    def _obtener_nombres_clientes(self):
        """Obtiene los nombres de los clientes para el combobox"""
        clientes = consultas.obtener_clientes()
        return [f"{c['nombre_completo']}" for c in clientes]

    def _obtener_nombres_servicios(self):
        """Obtiene los nombres de los servicios"""
        servicios = consultas.obtener_servicios()
        return [s['nombre_servicio'] for s in servicios]

    def _obtener_nombres_materiales(self):
        """Obtiene los nombres de los materiales"""
        materiales = consultas.obtener_materiales()
        return [m['nombre_material'] for m in materiales]

    def _mostrar_dialogo_cliente(self):
        """Muestra diálogo para agregar nuevo cliente"""
        dialogo = ctk.CTkInputDialog(
            text="Ingrese el nombre completo del cliente:",
            title="Nuevo Cliente"
        )
        nombre = dialogo.get_input()

        if nombre:
            id_cliente = consultas.guardar_cliente(nombre)
            messagebox.showinfo("Éxito", f"Cliente '{nombre}' registrado correctamente")
            # Actualizar el entry con el nuevo cliente
            self.autocomplete_cliente.entry.delete(0, "end")
            self.autocomplete_cliente.entry.insert(0, nombre)
            # Cargar el cliente recién creado
            cliente = consultas.obtener_cliente_por_id(id_cliente)
            self.autocomplete_cliente.cliente_seleccionado = cliente

    def _al_seleccionar_servicio(self, choice):
        """Se ejecuta al seleccionar un servicio"""
        if choice == "Seleccionar servicio...":
            return

        # Obtener ID del servicio seleccionado
        servicios = consultas.obtener_servicios()
        id_servicio = None
        for servicio in servicios:
            if servicio['nombre_servicio'] == choice:
                id_servicio = servicio['id_servicio']
                break

        if id_servicio:
            # Filtrar materiales compatibles con este servicio
            materiales_filtrados = consultas.obtener_materiales_por_servicio(id_servicio)

            if materiales_filtrados:
                nombres_materiales = [mat['nombre_material'] for mat in materiales_filtrados]
                self.combo_material.configure(values=nombres_materiales)
                if nombres_materiales:
                    self.combo_material.set(nombres_materiales[0])
            else:
                # Si no hay materiales específicos, mostrar todos
                self.combo_material.configure(values=self._obtener_nombres_materiales())
                messagebox.showinfo("Información",
                    f"No hay materiales específicos configurados para {choice}.\nSe muestran todos los materiales disponibles.")

    def _al_cambiar_dimensiones(self, event=None):
        """Se ejecuta al escribir en los campos de dimensiones"""
        try:
            ancho = float(self.entry_ancho.get() or 0)
            alto = float(self.entry_alto.get() or 0)

            if ancho > 0 and alto > 0:
                area = calculos.calcular_area(ancho, alto)
                self.label_area.configure(text=f"Área: {area} m²")
        except ValueError:
            self.label_area.configure(text="Área: 0.00 m²")

    def _calcular_cotizacion(self):
        """Calcula la cotización y muestra recomendaciones"""
        try:
            # Validar datos básicos
            if self.combo_servicio.get() == "Seleccionar servicio...":
                messagebox.showwarning("Validación", "Debe seleccionar un servicio")
                return

            ancho = float(self.entry_ancho.get() or 0)
            alto = float(self.entry_alto.get() or 0)
            cantidad = int(self.entry_cantidad.get() or 1)

            if ancho <= 0 or alto <= 0:
                messagebox.showwarning("Validación", "Debe ingresar dimensiones válidas")
                return

            # Obtener análisis del sistema experto
            servicio_nombre = self.combo_servicio.get()
            cantidad = int(self.entry_cantidad.get() or 1)

            analisis = reglas_experto.analizar_pedido_completo(
                tipo_trabajo=servicio_nombre,
                ancho=ancho,
                alto=alto,
                cantidad=cantidad,
                material_disponible=True,
                requiere_diseño=False,
                es_urgente=False
            )

            # Mostrar recomendaciones
            texto_recomendaciones = f"""
Máquina: {analisis['maquina']['maquina_recomendada']}
   {analisis['maquina']['explicacion']}

Materiales recomendados:
"""
            for mat in analisis['material']['materiales_recomendados']:
                texto_recomendaciones += f"   - {mat['nombre']}: {mat['razon']}\n"

            # Información de tiempo y cola
            texto_recomendaciones += f"\n--- TIEMPO DE ENTREGA ---"
            texto_recomendaciones += f"\nTiempo de producción: {analisis['tiempo']['horas_estimadas']:.1f} horas"
            texto_recomendaciones += f"\nDías hábiles: {analisis['tiempo']['dias_habiles']}"
            texto_recomendaciones += f"\nFecha de entrega: {analisis['tiempo']['fecha_entrega'].strftime('%d/%m/%Y a las %H:%M')}"

            # Estado de la cola
            info_cola = analisis['tiempo']['info_cola']
            texto_recomendaciones += f"\n\n--- ESTADO DE PRODUCCIÓN ---"
            texto_recomendaciones += f"\nPedidos pendientes: {info_cola['pedidos_pendientes']}"
            texto_recomendaciones += f"\nHoras en cola: {info_cola['horas_en_cola']:.1f}h"
            texto_recomendaciones += f"\nEstado: {info_cola['estado_produccion']}"

            # Detalles del cálculo
            texto_recomendaciones += f"\n\n{analisis['tiempo']['detalles_calculo']}"

            # Advertencias
            if analisis['validacion_metraje']['advertencias']:
                texto_recomendaciones += "\n\n--- ADVERTENCIAS ---"
                for adv in analisis['validacion_metraje']['advertencias']:
                    texto_recomendaciones += f"\n{adv}"

            if analisis['tiempo']['alertas']:
                for alerta in analisis['tiempo']['alertas']:
                    texto_recomendaciones += f"\n{alerta}"

            self.label_recomendaciones.configure(text=texto_recomendaciones)

            # Calcular precio
            area = calculos.calcular_area(ancho, alto)
            precio_m2 = 25.0  # Precio base por m2
            precio_total = calculos.calcular_costo_total(area * precio_m2 * cantidad, 0)

            self.label_precio.configure(text=f"Precio Total: S/ {precio_total:.2f}")

            messagebox.showinfo("Cotización", "Cotización calculada exitosamente")

        except ValueError as e:
            messagebox.showerror("Error", f"Datos inválidos: {str(e)}")

    def _guardar_pedido(self):
        """Guarda el pedido en la base de datos"""
        try:
            # Validaciones
            cliente = self.autocomplete_cliente.get_cliente_seleccionado()
            if not cliente:
                messagebox.showwarning("Validación", "Debe seleccionar un cliente de las sugerencias")
                return

            if self.combo_servicio.get() == "Seleccionar servicio...":
                messagebox.showwarning("Validación", "Debe seleccionar un servicio")
                return

            # Obtener precio del label (quitar el texto "Precio Total: S/ ")
            precio_texto = self.label_precio.cget("text")
            precio_total = float(precio_texto.split("S/ ")[1])

            if precio_total == 0:
                messagebox.showwarning("Validación", "Debe calcular la cotización primero")
                return

            # Obtener adelanto
            adelanto = float(self.entry_adelanto.get() or 0)

            # Calcular fecha de entrega (ejemplo: 3 días)
            fecha_entrega = datetime.now() + timedelta(days=3)

            # Guardar pedido
            id_pedido = consultas.guardar_pedido(
                id_cliente=cliente['id_cliente'],
                fecha_entrega=fecha_entrega,
                estado="Cotizado",
                estado_pago=self.combo_estado_pago.get(),
                costo_total=precio_total,
                acuenta=adelanto,
                observaciones=self.entry_descripcion.get()
            )

            messagebox.showinfo("Éxito", f"Pedido #{id_pedido} guardado correctamente")
            self._limpiar_formulario()

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

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
        self.label_recomendaciones.configure(text="Complete los datos para obtener recomendaciones...")

