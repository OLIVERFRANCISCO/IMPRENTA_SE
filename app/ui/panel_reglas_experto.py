"""
Panel de Reglas del Sistema Experto
=====================================
Permite al administrador configurar la Base de Conocimientos:
- Asociar máquinas a servicios (con marcador de "recomendada")
- Asociar materiales a servicios (con marcador de "preferido")
- Ver resumen del conocimiento configurado

Este panel es el corazón del sistema experto: aquí el experto humano
(administrador) transfiere su conocimiento al sistema.
"""
import customtkinter as ctk
from tkinter import messagebox
from app.config import COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER
from app.database import consultas
from app.database.conexion import get_session
from sqlalchemy import text


class PanelReglasExperto(ctk.CTkFrame):
    """
    Panel para gestionar las reglas del Sistema Experto
    
    Permite configurar:
    - Qué máquinas pueden realizar qué servicios
    - Qué materiales son válidos para cada servicio
    - Cuáles son las opciones preferidas/recomendadas
    """
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._crear_header()
        self._crear_tabs()
    
    def _crear_header(self):
        """Crea el encabezado del panel"""
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, pady=(0, 20), padx=10, sticky="ew")
        frame_header.grid_columnconfigure(1, weight=1)
        
        # Título principal
        ctk.CTkLabel(
            frame_header,
            text="🧠 Base de Conocimientos",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_PRIMARY
        ).grid(row=0, column=0, sticky="w")
        
        # Subtítulo explicativo
        ctk.CTkLabel(
            frame_header,
            text="Configure aquí las reglas que el sistema usará para hacer recomendaciones automáticas",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Botón de ayuda
        ctk.CTkButton(
            frame_header,
            text="❓ Ayuda",
            command=self._mostrar_ayuda,
            width=100,
            height=35,
            fg_color="gray30"
        ).grid(row=0, column=1, sticky="e")
    
    def _crear_tabs(self):
        """Crea el sistema de pestañas"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Tabs
        self.tab_maquinas = self.tabview.add("🔧 Máquinas por Servicio")
        self.tab_materiales = self.tabview.add("📦 Materiales por Servicio")
        self.tab_resumen = self.tabview.add("📊 Resumen del Conocimiento")
        
        # Configurar cada tab
        self._configurar_tab_maquinas()
        self._configurar_tab_materiales()
        self._configurar_tab_resumen()
    
    # ==================== TAB: MÁQUINAS POR SERVICIO ====================
    
    def _configurar_tab_maquinas(self):
        """Configura la pestaña de asociación máquinas-servicios"""
        self.tab_maquinas.grid_rowconfigure(1, weight=1)
        self.tab_maquinas.grid_columnconfigure(0, weight=1)
        
        # Instrucciones
        frame_instrucciones = ctk.CTkFrame(self.tab_maquinas, fg_color="gray20", corner_radius=10)
        frame_instrucciones.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(
            frame_instrucciones,
            text="💡 Seleccione un servicio y marque las máquinas que pueden realizarlo.\n"
                 "   Use ⭐ para indicar la máquina RECOMENDADA (aparecerá primero en sugerencias).",
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(padx=15, pady=12, anchor="w")
        
        # Frame principal con dos columnas
        frame_contenido = ctk.CTkFrame(self.tab_maquinas, fg_color="transparent")
        frame_contenido.grid(row=1, column=0, sticky="nsew")
        frame_contenido.grid_columnconfigure(1, weight=1)
        frame_contenido.grid_rowconfigure(0, weight=1)
        
        # Columna izquierda: Lista de servicios
        frame_servicios = ctk.CTkFrame(frame_contenido, width=280)
        frame_servicios.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frame_servicios.grid_propagate(False)
        
        ctk.CTkLabel(
            frame_servicios,
            text="📋 Servicios",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10), padx=15, anchor="w")
        
        self.lista_servicios_maq = ctk.CTkScrollableFrame(frame_servicios, fg_color="transparent")
        self.lista_servicios_maq.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Columna derecha: Máquinas disponibles
        frame_maquinas = ctk.CTkFrame(frame_contenido)
        frame_maquinas.grid(row=0, column=1, sticky="nsew")
        frame_maquinas.grid_rowconfigure(1, weight=1)
        frame_maquinas.grid_columnconfigure(0, weight=1)
        
        self.label_servicio_seleccionado_maq = ctk.CTkLabel(
            frame_maquinas,
            text="Seleccione un servicio para ver las máquinas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_servicio_seleccionado_maq.grid(row=0, column=0, pady=15, padx=15, sticky="w")
        
        self.scroll_maquinas = ctk.CTkScrollableFrame(frame_maquinas)
        self.scroll_maquinas.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_maquinas.grid_columnconfigure(0, weight=1)
        
        # Cargar servicios
        self._cargar_servicios_maquinas()
    
    def _cargar_servicios_maquinas(self):
        """Carga la lista de servicios en el panel de máquinas"""
        for widget in self.lista_servicios_maq.winfo_children():
            widget.destroy()
        
        servicios = consultas.obtener_servicios()
        
        for servicio in servicios:
            btn = ctk.CTkButton(
                self.lista_servicios_maq,
                text=servicio['nombre_servicio'],
                command=lambda s=servicio: self._seleccionar_servicio_maq(s),
                fg_color="transparent",
                hover_color="gray30",
                anchor="w",
                height=40
            )
            btn.pack(fill="x", pady=2)
    
    def _seleccionar_servicio_maq(self, servicio):
        """Muestra las máquinas para el servicio seleccionado"""
        self.servicio_actual_maq = servicio
        self.label_servicio_seleccionado_maq.configure(
            text=f"🔧 Máquinas para: {servicio['nombre_servicio']}"
        )
        
        # Limpiar lista actual
        for widget in self.scroll_maquinas.winfo_children():
            widget.destroy()
        
        # Obtener todas las máquinas
        maquinas = consultas.obtener_maquinas()
        
        # Obtener máquinas ya asociadas a este servicio
        maquinas_asociadas = self._obtener_maquinas_servicio(servicio['id_servicio'])
        ids_asociadas = {m['id_maquina'] for m in maquinas_asociadas}
        maquinas_recomendadas = {m['id_maquina'] for m in maquinas_asociadas if m.get('es_recomendada')}
        
        # Crear checkboxes para cada máquina
        for maquina in maquinas:
            self._crear_fila_maquina_servicio(
                maquina, 
                servicio['id_servicio'],
                maquina['id_maquina'] in ids_asociadas,
                maquina['id_maquina'] in maquinas_recomendadas
            )
    
    def _crear_fila_maquina_servicio(self, maquina, id_servicio, esta_asociada, es_recomendada):
        """Crea una fila para asociar/desasociar una máquina"""
        frame_fila = ctk.CTkFrame(self.scroll_maquinas, fg_color="gray25", corner_radius=8)
        frame_fila.pack(fill="x", pady=4, padx=5)
        frame_fila.grid_columnconfigure(1, weight=1)
        
        # Checkbox de asociación
        var_asociada = ctk.BooleanVar(value=esta_asociada)
        chk = ctk.CTkCheckBox(
            frame_fila,
            text="",
            variable=var_asociada,
            command=lambda: self._toggle_maquina_servicio(
                maquina['id_maquina'], id_servicio, var_asociada.get(), var_recomendada
            ),
            width=30
        )
        chk.grid(row=0, column=0, padx=(15, 5), pady=12)
        
        # Nombre de la máquina
        ctk.CTkLabel(
            frame_fila,
            text=f"{maquina['nombre']}",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=1, sticky="w", padx=5)
        
        # Tipo de máquina
        ctk.CTkLabel(
            frame_fila,
            text=f"({maquina['tipo']})",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).grid(row=0, column=2, padx=10)
        
        # Capacidad (si existe)
        capacidad = self._obtener_capacidad_maquina(maquina['id_maquina'])
        if capacidad and capacidad.get('ancho_util_max'):
            ctk.CTkLabel(
                frame_fila,
                text=f"Max: {capacidad['ancho_util_max']}m",
                font=ctk.CTkFont(size=11),
                text_color="#4CAF50"
            ).grid(row=0, column=3, padx=10)
        
        # Botón de recomendada (estrella)
        var_recomendada = ctk.BooleanVar(value=es_recomendada)
        btn_estrella = ctk.CTkButton(
            frame_fila,
            text="⭐" if es_recomendada else "☆",
            width=40,
            height=30,
            fg_color=COLOR_WARNING if es_recomendada else "gray40",
            hover_color=COLOR_WARNING,
            command=lambda: self._toggle_recomendada(
                maquina['id_maquina'], id_servicio, var_recomendada, btn_estrella, var_asociada
            )
        )
        btn_estrella.grid(row=0, column=4, padx=(10, 15), pady=8)
    
    def _toggle_maquina_servicio(self, id_maquina, id_servicio, asociar, var_recomendada):
        """Asocia o desasocia una máquina de un servicio"""
        try:
            if asociar:
                consultas.asociar_servicio_a_maquina(id_maquina, id_servicio)
            else:
                consultas.desasociar_servicio_de_maquina(id_maquina, id_servicio)
                var_recomendada.set(False)
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def _toggle_recomendada(self, id_maquina, id_servicio, var_recomendada, btn, var_asociada):
        """Marca/desmarca una máquina como recomendada"""
        if not var_asociada.get():
            messagebox.showwarning("Atención", "Primero debe asociar la máquina al servicio")
            return
        
        nuevo_valor = not var_recomendada.get()
        var_recomendada.set(nuevo_valor)
        
        try:
            consultas.marcar_maquina_recomendada(id_maquina, id_servicio, nuevo_valor)
            btn.configure(
                text="⭐" if nuevo_valor else "☆",
                fg_color=COLOR_WARNING if nuevo_valor else "gray40"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def _obtener_maquinas_servicio(self, id_servicio):
        """Obtiene las máquinas asociadas a un servicio"""
        session = get_session()
        try:
            result = session.execute(text("""
                SELECT m.id_maquina, m.nombre, ms.es_recomendada
                FROM maquinas m
                JOIN maquinas_servicios ms ON m.id_maquina = ms.id_maquina
                WHERE ms.id_servicio = :id_servicio
            """), {'id_servicio': id_servicio}).fetchall()
            
            return [{'id_maquina': r[0], 'nombre': r[1], 'es_recomendada': bool(r[2])} for r in result]
        finally:
            session.close()
    
    def _obtener_capacidad_maquina(self, id_maquina):
        """Obtiene la capacidad física de una máquina"""
        session = get_session()
        try:
            result = session.execute(text("""
                SELECT ancho_util_max, largo_util_max, velocidad_promedio
                FROM capacidad_maquinas WHERE id_maquina = :id
            """), {'id': id_maquina}).fetchone()
            
            if result:
                return {
                    'ancho_util_max': result[0],
                    'largo_util_max': result[1],
                    'velocidad_promedio': result[2]
                }
            return None
        finally:
            session.close()
    
    # ==================== TAB: MATERIALES POR SERVICIO ====================
    
    def _configurar_tab_materiales(self):
        """Configura la pestaña de asociación materiales-servicios"""
        self.tab_materiales.grid_rowconfigure(1, weight=1)
        self.tab_materiales.grid_columnconfigure(0, weight=1)
        
        # Instrucciones
        frame_instrucciones = ctk.CTkFrame(self.tab_materiales, fg_color="gray20", corner_radius=10)
        frame_instrucciones.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)
        
        ctk.CTkLabel(
            frame_instrucciones,
            text="💡 Seleccione un servicio y marque los materiales válidos para ese servicio.\n"
                 "   Use ⭐ para indicar el material PREFERIDO (se sugerirá primero al cotizar).",
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(padx=15, pady=12, anchor="w")
        
        # Frame principal
        frame_contenido = ctk.CTkFrame(self.tab_materiales, fg_color="transparent")
        frame_contenido.grid(row=1, column=0, sticky="nsew")
        frame_contenido.grid_columnconfigure(1, weight=1)
        frame_contenido.grid_rowconfigure(0, weight=1)
        
        # Columna izquierda: Lista de servicios
        frame_servicios = ctk.CTkFrame(frame_contenido, width=280)
        frame_servicios.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        frame_servicios.grid_propagate(False)
        
        ctk.CTkLabel(
            frame_servicios,
            text="📋 Servicios",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10), padx=15, anchor="w")
        
        self.lista_servicios_mat = ctk.CTkScrollableFrame(frame_servicios, fg_color="transparent")
        self.lista_servicios_mat.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Columna derecha: Materiales disponibles
        frame_materiales = ctk.CTkFrame(frame_contenido)
        frame_materiales.grid(row=0, column=1, sticky="nsew")
        frame_materiales.grid_rowconfigure(1, weight=1)
        frame_materiales.grid_columnconfigure(0, weight=1)
        
        self.label_servicio_seleccionado_mat = ctk.CTkLabel(
            frame_materiales,
            text="Seleccione un servicio para ver los materiales",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_servicio_seleccionado_mat.grid(row=0, column=0, pady=15, padx=15, sticky="w")
        
        self.scroll_materiales = ctk.CTkScrollableFrame(frame_materiales)
        self.scroll_materiales.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_materiales.grid_columnconfigure(0, weight=1)
        
        # Cargar servicios
        self._cargar_servicios_materiales()
    
    def _cargar_servicios_materiales(self):
        """Carga la lista de servicios en el panel de materiales"""
        for widget in self.lista_servicios_mat.winfo_children():
            widget.destroy()
        
        servicios = consultas.obtener_servicios()
        
        for servicio in servicios:
            btn = ctk.CTkButton(
                self.lista_servicios_mat,
                text=servicio['nombre_servicio'],
                command=lambda s=servicio: self._seleccionar_servicio_mat(s),
                fg_color="transparent",
                hover_color="gray30",
                anchor="w",
                height=40
            )
            btn.pack(fill="x", pady=2)
    
    def _seleccionar_servicio_mat(self, servicio):
        """Muestra los materiales para el servicio seleccionado"""
        self.servicio_actual_mat = servicio
        self.label_servicio_seleccionado_mat.configure(
            text=f"📦 Materiales para: {servicio['nombre_servicio']}"
        )
        
        # Limpiar lista actual
        for widget in self.scroll_materiales.winfo_children():
            widget.destroy()
        
        # Obtener todos los materiales
        materiales = consultas.obtener_materiales()
        
        # Obtener materiales ya asociados
        materiales_asociados = self._obtener_materiales_servicio(servicio['id_servicio'])
        ids_asociados = {m['id_material'] for m in materiales_asociados}
        materiales_preferidos = {m['id_material'] for m in materiales_asociados if m.get('es_preferido')}
        
        # Crear checkboxes para cada material
        for material in materiales:
            self._crear_fila_material_servicio(
                material,
                servicio['id_servicio'],
                material['id_material'] in ids_asociados,
                material['id_material'] in materiales_preferidos
            )
    
    def _crear_fila_material_servicio(self, material, id_servicio, esta_asociado, es_preferido):
        """Crea una fila para asociar/desasociar un material"""
        frame_fila = ctk.CTkFrame(self.scroll_materiales, fg_color="gray25", corner_radius=8)
        frame_fila.pack(fill="x", pady=4, padx=5)
        frame_fila.grid_columnconfigure(1, weight=1)
        
        # Checkbox de asociación
        var_asociado = ctk.BooleanVar(value=esta_asociado)
        chk = ctk.CTkCheckBox(
            frame_fila,
            text="",
            variable=var_asociado,
            command=lambda: self._toggle_material_servicio(
                id_servicio, material['id_material'], var_asociado.get(), var_preferido
            ),
            width=30
        )
        chk.grid(row=0, column=0, padx=(15, 5), pady=12)
        
        # Nombre del material
        ctk.CTkLabel(
            frame_fila,
            text=f"{material['nombre_material']}",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=1, sticky="w", padx=5)
        
        # Tipo de material
        tipo = material.get('tipo_material', 'unidad')
        icono_tipo = "📏" if tipo == 'dimension' else "📦"
        ctk.CTkLabel(
            frame_fila,
            text=f"{icono_tipo} {tipo}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).grid(row=0, column=2, padx=10)
        
        # Stock actual
        stock = material.get('cantidad_stock', 0)
        color_stock = COLOR_SUCCESS if stock > 10 else (COLOR_WARNING if stock > 0 else COLOR_DANGER)
        ctk.CTkLabel(
            frame_fila,
            text=f"Stock: {stock}",
            font=ctk.CTkFont(size=11),
            text_color=color_stock
        ).grid(row=0, column=3, padx=10)
        
        # Botón de preferido (estrella)
        var_preferido = ctk.BooleanVar(value=es_preferido)
        btn_estrella = ctk.CTkButton(
            frame_fila,
            text="⭐" if es_preferido else "☆",
            width=40,
            height=30,
            fg_color=COLOR_WARNING if es_preferido else "gray40",
            hover_color=COLOR_WARNING,
            command=lambda: self._toggle_preferido(
                id_servicio, material['id_material'], var_preferido, btn_estrella, var_asociado
            )
        )
        btn_estrella.grid(row=0, column=4, padx=(10, 15), pady=8)
    
    def _toggle_material_servicio(self, id_servicio, id_material, asociar, var_preferido):
        """Asocia o desasocia un material de un servicio"""
        try:
            if asociar:
                consultas.asociar_material_a_servicio(id_servicio, id_material)
            else:
                consultas.desasociar_material_de_servicio(id_servicio, id_material)
                var_preferido.set(False)
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def _toggle_preferido(self, id_servicio, id_material, var_preferido, btn, var_asociado):
        """Marca/desmarca un material como preferido"""
        if not var_asociado.get():
            messagebox.showwarning("Atención", "Primero debe asociar el material al servicio")
            return
        
        nuevo_valor = not var_preferido.get()
        var_preferido.set(nuevo_valor)
        
        try:
            consultas.marcar_material_preferido(id_servicio, id_material, nuevo_valor)
            btn.configure(
                text="⭐" if nuevo_valor else "☆",
                fg_color=COLOR_WARNING if nuevo_valor else "gray40"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
    
    def _obtener_materiales_servicio(self, id_servicio):
        """Obtiene los materiales asociados a un servicio"""
        session = get_session()
        try:
            result = session.execute(text("""
                SELECT m.id_material, m.nombre_material, sm.es_preferido
                FROM materiales m
                JOIN servicios_materiales sm ON m.id_material = sm.id_material
                WHERE sm.id_servicio = :id_servicio
            """), {'id_servicio': id_servicio}).fetchall()
            
            return [{'id_material': r[0], 'nombre': r[1], 'es_preferido': bool(r[2])} for r in result]
        finally:
            session.close()
    
    # ==================== TAB: RESUMEN DEL CONOCIMIENTO ====================
    
    def _configurar_tab_resumen(self):
        """Configura la pestaña de resumen del conocimiento"""
        self.tab_resumen.grid_rowconfigure(1, weight=1)
        self.tab_resumen.grid_columnconfigure(0, weight=1)
        
        # Botón actualizar
        frame_header = ctk.CTkFrame(self.tab_resumen, fg_color="transparent")
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        ctk.CTkButton(
            frame_header,
            text="🔄 Actualizar Resumen",
            command=self._cargar_resumen,
            height=40,
            width=180
        ).pack(side="right")
        
        ctk.CTkLabel(
            frame_header,
            text="Vista general de las reglas configuradas en el sistema",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        ).pack(side="left")
        
        # Contenedor scrollable
        self.scroll_resumen = ctk.CTkScrollableFrame(self.tab_resumen)
        self.scroll_resumen.grid(row=1, column=0, sticky="nsew", padx=5)
        self.scroll_resumen.grid_columnconfigure(0, weight=1)
        
        self._cargar_resumen()
    
    def _cargar_resumen(self):
        """Carga el resumen del conocimiento configurado"""
        for widget in self.scroll_resumen.winfo_children():
            widget.destroy()
        
        servicios = consultas.obtener_servicios()
        
        if not servicios:
            ctk.CTkLabel(
                self.scroll_resumen,
                text="No hay servicios configurados",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).pack(pady=50)
            return
        
        # Estadísticas generales
        frame_stats = ctk.CTkFrame(self.scroll_resumen, fg_color=COLOR_PRIMARY, corner_radius=10)
        frame_stats.pack(fill="x", pady=(0, 20), padx=5)
        
        total_maquinas = len(consultas.obtener_maquinas())
        total_materiales = len(consultas.obtener_materiales())
        total_servicios = len(servicios)
        
        stats_text = (
            f"📊 Estadísticas: {total_servicios} servicios | "
            f"{total_maquinas} máquinas | {total_materiales} materiales"
        )
        ctk.CTkLabel(
            frame_stats,
            text=stats_text,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=15)
        
        # Detalle por servicio
        for servicio in servicios:
            self._crear_tarjeta_servicio(servicio)
    
    def _crear_tarjeta_servicio(self, servicio):
        """Crea una tarjeta con el resumen de un servicio"""
        frame = ctk.CTkFrame(self.scroll_resumen, fg_color="gray20", corner_radius=10)
        frame.pack(fill="x", pady=8, padx=5)
        
        # Título del servicio
        ctk.CTkLabel(
            frame,
            text=f"🛠️ {servicio['nombre_servicio']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Máquinas asociadas
        maquinas = self._obtener_maquinas_servicio(servicio['id_servicio'])
        if maquinas:
            texto_maq = "   🔧 Máquinas: "
            for m in maquinas:
                prefijo = "⭐" if m.get('es_recomendada') else ""
                texto_maq += f"{prefijo}{m['nombre']}, "
            texto_maq = texto_maq.rstrip(", ")
        else:
            texto_maq = "   🔧 Máquinas: ⚠️ Sin configurar"
        
        ctk.CTkLabel(
            frame,
            text=texto_maq,
            font=ctk.CTkFont(size=12),
            text_color="gray" if not maquinas else None
        ).pack(anchor="w", padx=15, pady=2)
        
        # Materiales asociados
        materiales = self._obtener_materiales_servicio(servicio['id_servicio'])
        if materiales:
            texto_mat = "   📦 Materiales: "
            for m in materiales:
                prefijo = "⭐" if m.get('es_preferido') else ""
                texto_mat += f"{prefijo}{m['nombre']}, "
            texto_mat = texto_mat.rstrip(", ")
        else:
            texto_mat = "   📦 Materiales: ⚠️ Sin configurar"
        
        ctk.CTkLabel(
            frame,
            text=texto_mat,
            font=ctk.CTkFont(size=12),
            text_color="gray" if not materiales else None
        ).pack(anchor="w", padx=15, pady=(2, 15))
    
    # ==================== AYUDA ====================
    
    def _mostrar_ayuda(self):
        """Muestra ventana de ayuda"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Ayuda - Base de Conocimientos")
        dialogo.geometry("600x500")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - 300
        y = (dialogo.winfo_screenheight() // 2) - 250
        dialogo.geometry(f"+{x}+{y}")
        
        scroll = ctk.CTkScrollableFrame(dialogo)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        ayuda_texto = """
🧠 ¿QUÉ ES LA BASE DE CONOCIMIENTOS?

Es donde usted, como experto en impresión, le "enseña" al sistema 
qué máquinas y materiales usar para cada servicio.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 MÁQUINAS POR SERVICIO

Aquí define qué máquinas pueden realizar cada servicio:
• ✅ Marque las máquinas compatibles con el servicio
• ⭐ Use la estrella para indicar la máquina RECOMENDADA
  (la que el sistema sugerirá primero)

Ejemplo: Para "Gigantografía" marque el Plotter como recomendado.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 MATERIALES POR SERVICIO

Aquí define qué materiales son válidos para cada servicio:
• ✅ Marque los materiales que se pueden usar
• ⭐ Use la estrella para el material PREFERIDO
  (el que el sistema sugerirá primero)

Ejemplo: Para "Banner Roll-Up" marque Lona 13oz como preferido.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESUMEN

Muestra una vista rápida de todas las reglas configuradas.
Use esto para verificar que todo esté correctamente definido.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 CONSEJOS

1. Configure al menos una máquina y un material por servicio
2. Use las estrellas ⭐ para las opciones más comunes
3. El sistema usará estas reglas automáticamente al cotizar
"""
        
        ctk.CTkLabel(
            scroll,
            text=ayuda_texto,
            font=ctk.CTkFont(size=13),
            justify="left"
        ).pack(anchor="w")
        
        ctk.CTkButton(
            dialogo,
            text="Entendido",
            command=dialogo.destroy,
            height=40,
            width=150
        ).pack(pady=15)
