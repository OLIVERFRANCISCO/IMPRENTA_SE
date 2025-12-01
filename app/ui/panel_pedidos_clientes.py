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
    """Panel para visualizar y gestionar pedidos con paginación"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Variables de paginación y filtros
        self.pagina_actual = 1
        self.items_por_pagina = 20
        self.filtro_estado = None
        self.filtro_fecha_inicio = None
        self.filtro_fecha_fin = None
        self.orden_campo = 'fecha_ingreso'
        self.orden_dir = 'DESC'

        self._crear_interfaz()
        self._cargar_pedidos()

    def _crear_interfaz(self):
        """Crea la interfaz completa"""

        # ===== TÍTULO Y BOTONES PRINCIPALES =====
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        frame_titulo.grid_columnconfigure(1, weight=1)

        self.titulo = ctk.CTkLabel(
            frame_titulo,
            text="Lista de Pedidos",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.titulo.grid(row=0, column=0, sticky="w")

        self.btn_actualizar = ctk.CTkButton(
            frame_titulo,
            text="Actualizar",
            command=self._cargar_pedidos,
            height=40,
            width=140
        )
        self.btn_actualizar.grid(row=0, column=2, padx=5)

        self.btn_exportar = ctk.CTkButton(
            frame_titulo,
            text="Exportar",
            command=self._mostrar_opciones_exportar,
            height=40,
            width=140,
            fg_color=COLOR_SUCCESS
        )
        self.btn_exportar.grid(row=0, column=3, padx=5)

        # ===== FILTROS =====
        frame_filtros = ctk.CTkFrame(self)
        frame_filtros.grid(row=1, column=0, pady=(0, 10), sticky="ew", padx=10)
        frame_filtros.grid_columnconfigure(5, weight=1)

        # Filtro por estado
        ctk.CTkLabel(frame_filtros, text="Estado:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=0, padx=(10, 5), pady=10, sticky="w"
        )

        # Obtener estados desde la BD
        self.estados_disponibles = consultas.obtener_estados_pedidos()
        nombres_estados = ["Todos"] + [est['nombre'] for est in self.estados_disponibles]

        self.combo_filtro_estado = ctk.CTkComboBox(
            frame_filtros,
            values=nombres_estados,
            command=self._aplicar_filtros,
            width=180
        )
        self.combo_filtro_estado.grid(row=0, column=1, padx=5, pady=10)
        self.combo_filtro_estado.set("Todos")

        # Filtro por fecha inicio
        ctk.CTkLabel(frame_filtros, text="Desde:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=2, padx=(20, 5), pady=10, sticky="w"
        )
        self.entry_fecha_inicio = ctk.CTkEntry(frame_filtros, width=120, placeholder_text="YYYY-MM-DD")
        self.entry_fecha_inicio.grid(row=0, column=3, padx=5, pady=10)

        # Filtro por fecha fin
        ctk.CTkLabel(frame_filtros, text="Hasta:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=4, padx=(10, 5), pady=10, sticky="w"
        )
        self.entry_fecha_fin = ctk.CTkEntry(frame_filtros, width=120, placeholder_text="YYYY-MM-DD")
        self.entry_fecha_fin.grid(row=0, column=5, padx=5, pady=10)

        # Botón aplicar filtros
        self.btn_aplicar_filtros = ctk.CTkButton(
            frame_filtros,
            text="Aplicar Filtros",
            command=self._aplicar_filtros,
            width=120,
            height=32
        )
        self.btn_aplicar_filtros.grid(row=0, column=6, padx=10, pady=10)

        # Botón limpiar filtros
        self.btn_limpiar_filtros = ctk.CTkButton(
            frame_filtros,
            text="Limpiar",
            command=self._limpiar_filtros,
            width=100,
            height=32,
            fg_color=COLOR_WARNING
        )
        self.btn_limpiar_filtros.grid(row=0, column=7, padx=5, pady=10)

        # ===== TABLA CON ENCABEZADOS =====
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Encabezados con ordenamiento
        self._crear_encabezado(frame_tabla, "ID", 0, 'id_pedido', width=60)
        self._crear_encabezado(frame_tabla, "Cliente", 1, None, width=180)
        self._crear_encabezado(frame_tabla, "Estado", 2, 'id_estado', width=150)
        self._crear_encabezado(frame_tabla, "Fecha Ingreso", 3, 'fecha_ingreso', width=150)
        self._crear_encabezado(frame_tabla, "Fecha Entrega", 4, 'fecha_entrega_estimada', width=150)
        self._crear_encabezado(frame_tabla, "Total", 5, 'costo_total', width=100)
        self._crear_encabezado(frame_tabla, "Acciones", 6, None, width=200)

        # ===== CONTENEDOR SCROLLABLE PARA PEDIDOS =====
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=400)
        self.scroll_frame.grid(row=3, column=0, sticky="nsew", padx=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # ===== CONTROLES DE PAGINACIÓN =====
        frame_paginacion = ctk.CTkFrame(self)
        frame_paginacion.grid(row=4, column=0, pady=10, sticky="ew", padx=10)
        frame_paginacion.grid_columnconfigure(2, weight=1)

        self.btn_anterior = ctk.CTkButton(
            frame_paginacion,
            text="← Anterior",
            command=self._pagina_anterior,
            width=120
        )
        self.btn_anterior.grid(row=0, column=0, padx=5)

        self.label_paginacion = ctk.CTkLabel(
            frame_paginacion,
            text="Página 1 de 1",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.label_paginacion.grid(row=0, column=1, padx=20)

        self.btn_siguiente = ctk.CTkButton(
            frame_paginacion,
            text="Siguiente →",
            command=self._pagina_siguiente,
            width=120
        )
        self.btn_siguiente.grid(row=0, column=2, padx=5, sticky="e")

        self.label_total = ctk.CTkLabel(
            frame_paginacion,
            text="Total: 0 pedidos",
            font=ctk.CTkFont(size=12)
        )
        self.label_total.grid(row=0, column=3, padx=20)

    def _crear_encabezado(self, parent, texto, columna, campo_orden, width=100):
        """Crea un encabezado con opción de ordenamiento"""
        frame = ctk.CTkFrame(parent, fg_color=COLOR_PRIMARY)
        frame.grid(row=0, column=columna, padx=2, pady=2, sticky="ew")

        label = ctk.CTkLabel(
            frame,
            text=texto,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=width,
            height=35
        )
        label.pack(side="left", padx=5)

        # Si tiene campo de ordenamiento, agregar botones
        if campo_orden:
            btn_asc = ctk.CTkButton(
                frame,
                text="▲",
                width=25,
                height=25,
                command=lambda: self._ordenar_por(campo_orden, 'ASC')
            )
            btn_asc.pack(side="left", padx=2)

            btn_desc = ctk.CTkButton(
                frame,
                text="▼",
                width=25,
                height=25,
                command=lambda: self._ordenar_por(campo_orden, 'DESC')
            )
            btn_desc.pack(side="left", padx=2)

    def _ordenar_por(self, campo, direccion):
        """Ordena los resultados por un campo específico"""
        self.orden_campo = campo
        self.orden_dir = direccion
        self.pagina_actual = 1
        self._cargar_pedidos()

    def _aplicar_filtros(self, *args):
        """Aplica los filtros seleccionados"""
        # Obtener ID del estado si se seleccionó uno
        estado_nombre = self.combo_filtro_estado.get()
        if estado_nombre != "Todos":
            estados = consultas.obtener_estados_pedidos()
            for estado in estados:
                if estado['nombre'] == estado_nombre:
                    self.filtro_estado = estado['id']
                    break
        else:
            self.filtro_estado = None

        # Obtener fechas
        fecha_inicio = self.entry_fecha_inicio.get().strip()
        fecha_fin = self.entry_fecha_fin.get().strip()

        self.filtro_fecha_inicio = fecha_inicio if fecha_inicio else None
        self.filtro_fecha_fin = fecha_fin if fecha_fin else None

        # Resetear a primera página y cargar
        self.pagina_actual = 1
        self._cargar_pedidos()

    def _limpiar_filtros(self):
        """Limpia todos los filtros"""
        self.combo_filtro_estado.set("Todos")
        self.entry_fecha_inicio.delete(0, 'end')
        self.entry_fecha_fin.delete(0, 'end')
        self.filtro_estado = None
        self.filtro_fecha_inicio = None
        self.filtro_fecha_fin = None
        self.pagina_actual = 1
        self._cargar_pedidos()

    def _cargar_pedidos(self):
        """Carga los pedidos con paginación y filtros"""
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
        """Muestra la lista de pedidos en la tabla"""
        # Limpiar frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not pedidos or len(pedidos) == 0:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No hay pedidos para mostrar",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
            return

        for pedido in pedidos:
            self._crear_fila_pedido(pedido)

    def _crear_fila_pedido(self, pedido):
        """Crea una fila con la información del pedido"""
        # Función auxiliar para acceder de forma segura a sqlite3.Row
        def get_field(row, field, default=None):
            try:
                return row[field] if row[field] is not None else default
            except (KeyError, IndexError):
                return default

        # Frame principal de la fila con color del estado
        color_estado = get_field(pedido, 'estado_color', '#808080')

        frame_pedido = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_pedido.pack(fill="x", pady=2, padx=5)

        # Barra de color del estado
        barra_color = ctk.CTkFrame(frame_pedido, fg_color=color_estado, width=8)
        barra_color.pack(side="left", fill="y")

        # Contenedor de datos
        frame_datos = ctk.CTkFrame(frame_pedido)
        frame_datos.pack(side="left", fill="x", expand=True, padx=5)

        # Fila de información
        fila = ctk.CTkFrame(frame_datos, fg_color="transparent")
        fila.pack(fill="x", pady=5, padx=10)

        # ID
        ctk.CTkLabel(fila, text=f"#{pedido['id_pedido']}", width=60, anchor="w").pack(side="left", padx=5)

        # Cliente
        nombre_cliente = get_field(pedido, 'nombre_cliente', 'N/A')
        ctk.CTkLabel(fila, text=nombre_cliente, width=180, anchor="w").pack(side="left", padx=5)

        # Estado con selector
        frame_estado = ctk.CTkFrame(fila, fg_color=color_estado, corner_radius=6)
        frame_estado.pack(side="left", padx=5)

        nombres_estados = [e['nombre'] for e in self.estados_disponibles]

        combo_estado = ctk.CTkComboBox(
            frame_estado,
            values=nombres_estados,
            width=140,
            command=lambda choice, pid=pedido['id_pedido']: self._cambiar_estado_pedido(pid, choice)
        )
        combo_estado.pack(padx=5, pady=3)
        estado_nombre = get_field(pedido, 'estado_nombre', 'Sin estado') or 'Sin estado'
        combo_estado.set(estado_nombre)

        # Fecha ingreso
        fecha_ingreso = get_field(pedido, 'fecha_ingreso')
        if fecha_ingreso:
            try:
                fecha_ing = datetime.fromisoformat(fecha_ingreso).strftime('%d/%m/%Y')
            except:
                fecha_ing = 'N/A'
        else:
            fecha_ing = 'N/A'
        ctk.CTkLabel(fila, text=fecha_ing, width=150, anchor="w").pack(side="left", padx=5)

        # Fecha entrega
        fecha_entrega = get_field(pedido, 'fecha_entrega_estimada')
        if fecha_entrega:
            try:
                fecha_ent = datetime.fromisoformat(fecha_entrega).strftime('%d/%m/%Y')
            except:
                fecha_ent = 'N/A'
        else:
            fecha_ent = 'N/A'
        ctk.CTkLabel(fila, text=fecha_ent, width=150, anchor="w").pack(side="left", padx=5)

        # Total
        costo_total = get_field(pedido, 'costo_total', 0)
        total_texto = f"S/. {float(costo_total):.2f}"
        ctk.CTkLabel(fila, text=total_texto, width=100, anchor="e", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        # Botones de acción
        frame_acciones = ctk.CTkFrame(fila, fg_color="transparent")
        frame_acciones.pack(side="left", padx=5)

        btn_ver = ctk.CTkButton(
            frame_acciones,
            text="Ver Detalles",
            command=lambda: self._ver_detalles(pedido['id_pedido']),
            width=100,
            height=28,
            fg_color=COLOR_PRIMARY
        )
        btn_ver.pack(side="left", padx=2)

    def _cambiar_estado_pedido(self, id_pedido, nuevo_estado_nombre):
        """Cambia el estado de un pedido"""
        # Obtener ID del estado
        id_estado = None
        for estado in self.estados_disponibles:
            if estado['nombre'] == nuevo_estado_nombre:
                id_estado = estado['id']
                break

        if id_estado:
            try:
                consultas.actualizar_estado_de_pedido(id_pedido, id_estado)
                messagebox.showinfo("Éxito", f"Estado del pedido #{id_pedido} actualizado a '{nuevo_estado_nombre}'")
                self._cargar_pedidos()  # Recargar para ver los cambios
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el estado: {str(e)}")

    def _ver_detalles(self, id_pedido):
        """Muestra los detalles completos de un pedido"""
        datos = consultas.obtener_pedido_por_id(id_pedido)
        if not datos:
            messagebox.showerror("Error", "No se encontró el pedido")
            return

        pedido = datos['pedido']
        detalles = datos['detalles']

        # Crear ventana de detalles
        ventana = ctk.CTkToplevel(self)
        ventana.title(f"Detalles del Pedido #{id_pedido}")
        ventana.geometry("700x600")
        ventana.transient(self)
        ventana.grab_set()

        # Contenido con scroll
        scroll = ctk.CTkScrollableFrame(ventana)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Información del cliente
        ctk.CTkLabel(scroll, text="INFORMACIÓN DEL CLIENTE", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))
        ctk.CTkLabel(scroll, text=f"Nombre: {pedido['nombre_completo']}").pack(anchor="w")
        ctk.CTkLabel(scroll, text=f"Teléfono: {pedido['telefono'] or 'N/A'}").pack(anchor="w")
        ctk.CTkLabel(scroll, text=f"Email: {pedido['email'] or 'N/A'}").pack(anchor="w")

        # Información del pedido
        ctk.CTkLabel(scroll, text="\nINFORMACIÓN DEL PEDIDO", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(10, 10))
        # ctk.CTkLabel(scroll, text=f"Estado: {pedido['estado_nombre']}").pack(anchor="w")
        ctk.CTkLabel(scroll, text=f"Estado de Pago: {pedido['estado_pago']}").pack(anchor="w")
        ctk.CTkLabel(scroll, text=f"Total: S/. {pedido['costo_total']:.2f}").pack(anchor="w")
        ctk.CTkLabel(scroll, text=f"A cuenta: S/. {pedido['acuenta']:.2f}").pack(anchor="w")
        saldo = pedido['costo_total'] - pedido['acuenta']
        ctk.CTkLabel(scroll, text=f"Saldo: S/. {saldo:.2f}").pack(anchor="w")

        # Detalles del pedido
        if detalles:
            ctk.CTkLabel(scroll, text="\nDETALLES DEL PEDIDO", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(10, 10))
            for detalle in detalles:
                frame_det = ctk.CTkFrame(scroll)
                frame_det.pack(fill="x", pady=5)

                info = f"Servicio: {detalle['nombre_servicio']}\n"
                info += f"Material: {detalle['nombre_material'] or 'N/A'}\n"
                info += f"Dimensiones: {detalle['ancho']}m x {detalle['alto']}m\n"
                info += f"Cantidad: {detalle['cantidad']}\n"
                info += f"Precio unitario: S/. {detalle['precio_unitario']:.2f}\n"
                subtotal = detalle['cantidad'] * detalle['precio_unitario']
                info += f"Subtotal: S/. {subtotal:.2f}"

                ctk.CTkLabel(frame_det, text=info, justify="left").pack(padx=10, pady=5, anchor="w")

        # Botón cerrar
        ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy, width=200, height=40).pack(pady=20)

    def _actualizar_paginacion(self, resultado):
        """Actualiza los controles de paginación"""
        pagina_actual = resultado['pagina_actual']
        total_paginas = resultado['total_paginas']
        total_registros = resultado['total']

        self.label_paginacion.configure(text=f"Página {pagina_actual} de {total_paginas}")
        self.label_total.configure(text=f"Total: {total_registros} pedidos")

        # Habilitar/deshabilitar botones
        self.btn_anterior.configure(state="normal" if pagina_actual > 1 else "disabled")
        self.btn_siguiente.configure(state="normal" if pagina_actual < total_paginas else "disabled")

    def _pagina_anterior(self):
        """Va a la página anterior"""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self._cargar_pedidos()

    def _pagina_siguiente(self):
        """Va a la página siguiente"""
        if self.pagina_actual < self.pedidos_resultado['total_paginas']:
            self.pagina_actual += 1
            self._cargar_pedidos()

    def _mostrar_opciones_exportar(self):
        """Muestra opciones de exportación"""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Exportar Pedidos")
        ventana.geometry("400x300")
        ventana.transient(self)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana,
            text="Seleccione el formato de exportación",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)

        def exportar_formato(formato):
            directorio = filedialog.askdirectory(title="Seleccionar carpeta de destino")
            if not directorio:
                return

            try:
                pedidos = self.pedidos_resultado['pedidos']
                if formato == "CSV":
                    ruta = exportar_a_csv(pedidos, "pedidos", directorio)
                elif formato == "Excel":
                    ruta = exportar_a_excel(pedidos, "pedidos", directorio)
                elif formato == "PDF":
                    ruta = exportar_a_pdf(pedidos, "pedidos", directorio)

                messagebox.showinfo("Éxito", f"Archivo exportado exitosamente en:\n{ruta}")
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")

        ctk.CTkButton(
            ventana,
            text="Exportar a CSV",
            command=lambda: exportar_formato("CSV"),
            width=250,
            height=50
        ).pack(pady=10)

        ctk.CTkButton(
            ventana,
            text="Exportar a Excel",
            command=lambda: exportar_formato("Excel"),
            width=250,
            height=50
        ).pack(pady=10)

        ctk.CTkButton(
            ventana,
            text="Exportar a PDF",
            command=lambda: exportar_formato("PDF"),
            width=250,
            height=50
        ).pack(pady=10)

        ctk.CTkButton(
            ventana,
            text="Cancelar",
            command=ventana.destroy,
            width=250,
            height=40,
            fg_color=COLOR_DANGER
        ).pack(pady=20)
