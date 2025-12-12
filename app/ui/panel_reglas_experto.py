"""
Panel de Gestión de Reglas del Sistema Experto
CRUD completo de reglas IF-THEN
Solo accesible para administradores
"""
import customtkinter as ctk
import json
from tkinter import messagebox
from app.config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER
)
from app.database import consultas_reglas
from app.logic.auth_service import auth_service, require_admin


class PanelReglasExperto(ctk.CTkFrame):
    """
    Panel para administrar reglas del sistema experto
    Solo administradores pueden crear, editar o eliminar reglas
    """
    
    # Categorías disponibles
    CATEGORIAS = [
        'maquina',
        'material',
        'tiempo',
        'metraje',
        'acabado',
        'rentabilidad',
        'integradora'
    ]
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Verificar que sea admin
        if not auth_service.is_admin():
            self._mostrar_acceso_denegado()
            return
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._crear_header()
        self._crear_barra_filtros()
        self._crear_tabla()
        self._cargar_reglas()
    
    def _mostrar_acceso_denegado(self):
        """Muestra mensaje de acceso denegado"""
        ctk.CTkLabel(
            self,
            text="🚫 Acceso Denegado",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_DANGER
        ).pack(expand=True)
        
        ctk.CTkLabel(
            self,
            text="Solo los administradores pueden gestionar reglas del sistema experto",
            font=ctk.CTkFont(size=14)
        ).pack()
    
    def _crear_header(self):
        """Crea el encabezado del panel"""
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, pady=(0, 20), padx=10, sticky="ew")
        frame_header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_header,
            text="⚙️ Reglas del Sistema Experto",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_PRIMARY
        ).grid(row=0, column=0, sticky="w")
        
        # Botones de acción
        frame_botones = ctk.CTkFrame(frame_header, fg_color="transparent")
        frame_botones.grid(row=0, column=1, sticky="e")
        
        ctk.CTkButton(
            frame_botones,
            text="➕ Nueva Regla",
            command=self._crear_regla,
            height=40,
            width=150,
            fg_color=COLOR_SUCCESS
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_botones,
            text="🔄 Actualizar",
            command=self._cargar_reglas,
            height=40,
            width=120
        ).pack(side="left", padx=5)
    
    def _crear_barra_filtros(self):
        """Crea la barra de filtros"""
        frame_filtros = ctk.CTkFrame(self, fg_color=("gray85", "gray20"))
        frame_filtros.grid(row=1, column=0, pady=(0, 10), padx=10, sticky="ew")
        
        ctk.CTkLabel(
            frame_filtros,
            text="Filtrar por categoría:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=10)
        
        self.combo_categoria = ctk.CTkComboBox(
            frame_filtros,
            values=["Todas"] + self.CATEGORIAS,
            command=self._cargar_reglas,
            width=180
        )
        self.combo_categoria.set("Todas")
        self.combo_categoria.pack(side="left", padx=5)
        
        # Switch para mostrar inactivas
        self.switch_inactivas = ctk.CTkSwitch(
            frame_filtros,
            text="Mostrar reglas inactivas",
            command=self._cargar_reglas
        )
        self.switch_inactivas.pack(side="left", padx=20)
        
        # Estadísticas
        self.label_stats = ctk.CTkLabel(
            frame_filtros,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.label_stats.pack(side="right", padx=10)
    
    def _crear_tabla(self):
        """Crea la tabla de reglas"""
        self.scroll_reglas = ctk.CTkScrollableFrame(self)
        self.scroll_reglas.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_reglas.grid_columnconfigure(0, weight=1)
    
    def _cargar_reglas(self, *args):
        """Carga y muestra las reglas"""
        # Limpiar tabla
        for widget in self.scroll_reglas.winfo_children():
            widget.destroy()
        
        # Obtener filtros
        categoria_filtro = self.combo_categoria.get()
        categoria = None if categoria_filtro == "Todas" else categoria_filtro
        solo_activas = not self.switch_inactivas.get()
        
        # Obtener reglas
        reglas = consultas_reglas.obtener_reglas(
            categoria=categoria,
            solo_activas=solo_activas
        )
        
        if not reglas:
            ctk.CTkLabel(
                self.scroll_reglas,
                text="No hay reglas registradas",
                font=ctk.CTkFont(size=14)
            ).pack(pady=20)
            self.label_stats.configure(text="0 reglas")
            return
        
        # Actualizar estadísticas
        self.label_stats.configure(text=f"{len(reglas)} reglas")
        
        # Encabezados
        frame_header = ctk.CTkFrame(self.scroll_reglas, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        headers = ["#", "Número", "Nombre", "Categoría", "Prioridad", "Estado", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                frame_header,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=10)
        
        # Filas de reglas
        for idx, regla in enumerate(reglas):
            self._crear_fila_regla(regla, idx + 1)
    
    def _crear_fila_regla(self, regla, fila):
        """Crea una fila con datos de regla"""
        color = "gray25" if fila % 2 == 0 else "gray20"
        frame_fila = ctk.CTkFrame(self.scroll_reglas, fg_color=color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        # Índice
        ctk.CTkLabel(frame_fila, text=str(fila)).grid(row=0, column=0, padx=10, pady=10)
        
        # Número de regla
        ctk.CTkLabel(
            frame_fila,
            text=regla['numero_regla'],
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, padx=10, pady=10)
        
        # Nombre
        nombre_corto = regla['nombre'][:40] + "..." if len(regla['nombre']) > 40 else regla['nombre']
        ctk.CTkLabel(frame_fila, text=nombre_corto).grid(row=0, column=2, padx=10, pady=10)
        
        # Categoría
        ctk.CTkLabel(
            frame_fila,
            text=regla['categoria'].capitalize(),
            text_color=COLOR_PRIMARY
        ).grid(row=0, column=3, padx=10, pady=10)
        
        # Prioridad
        ctk.CTkLabel(frame_fila, text=str(regla['prioridad'])).grid(row=0, column=4, padx=10, pady=10)
        
        # Estado
        estado_text = "✓ Activa" if regla['activa'] else "✗ Inactiva"
        estado_color = COLOR_SUCCESS if regla['activa'] else "gray"
        ctk.CTkLabel(
            frame_fila,
            text=estado_text,
            text_color=estado_color,
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=5, padx=10, pady=10)
        
        # Acciones
        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=6, padx=10, pady=5)
        
        ctk.CTkButton(
            frame_acciones,
            text="👁️",
            command=lambda r=regla: self._ver_regla(r),
            width=40,
            height=30,
            fg_color="gray"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            frame_acciones,
            text="✏️",
            command=lambda r=regla: self._editar_regla(r),
            width=40,
            height=30,
            fg_color=COLOR_PRIMARY
        ).pack(side="left", padx=2)
        
        # Botón activar/desactivar
        if regla['activa']:
            ctk.CTkButton(
                frame_acciones,
                text="⏸️",
                command=lambda r=regla: self._cambiar_estado_regla(r, False),
                width=40,
                height=30,
                fg_color=COLOR_WARNING
            ).pack(side="left", padx=2)
        else:
            ctk.CTkButton(
                frame_acciones,
                text="▶️",
                command=lambda r=regla: self._cambiar_estado_regla(r, True),
                width=40,
                height=30,
                fg_color=COLOR_SUCCESS
            ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            frame_acciones,
            text="🗑️",
            command=lambda r=regla: self._eliminar_regla(r),
            width=40,
            height=30,
            fg_color=COLOR_DANGER
        ).pack(side="left", padx=2)
    
    def _crear_regla(self):
        """Muestra diálogo para crear nueva regla"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nueva Regla del Sistema Experto")
        dialogo.geometry("700x800")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (800 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        # Scroll frame
        scroll = ctk.CTkScrollableFrame(dialogo)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            scroll,
            text="➕ Nueva Regla",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)
        
        # Número de regla
        ctk.CTkLabel(scroll, text="Número de Regla *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_numero = ctk.CTkEntry(scroll, width=620, height=40, placeholder_text="Ej: REGLA-01")
        entry_numero.pack(padx=10, pady=(5, 15))
        
        # Nombre
        ctk.CTkLabel(scroll, text="Nombre *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_nombre = ctk.CTkEntry(scroll, width=620, height=40, placeholder_text="Nombre descriptivo")
        entry_nombre.pack(padx=10, pady=(5, 15))
        
        # Categoría
        ctk.CTkLabel(scroll, text="Categoría *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        combo_categoria = ctk.CTkComboBox(scroll, values=self.CATEGORIAS, width=620, height=40)
        combo_categoria.set(self.CATEGORIAS[0])
        combo_categoria.pack(padx=10, pady=(5, 15))
        
        # Descripción
        ctk.CTkLabel(scroll, text="Descripción *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        text_descripcion = ctk.CTkTextbox(scroll, width=620, height=100)
        text_descripcion.pack(padx=10, pady=(5, 15))
        
        # Condiciones (IF)
        ctk.CTkLabel(scroll, text="Condiciones (IF) - JSON *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        text_condiciones = ctk.CTkTextbox(scroll, width=620, height=120)
        text_condiciones.insert("1.0", '{\n  "campo": "valor",\n  "operador": "=="\n}')
        text_condiciones.pack(padx=10, pady=(5, 15))
        
        # Acciones (THEN)
        ctk.CTkLabel(scroll, text="Acciones (THEN) - JSON *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        text_acciones = ctk.CTkTextbox(scroll, width=620, height=120)
        text_acciones.insert("1.0", '{\n  "accion": "resultado",\n  "valor": "salida"\n}')
        text_acciones.pack(padx=10, pady=(5, 15))
        
        # Prioridad
        ctk.CTkLabel(scroll, text="Prioridad (1-10) *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_prioridad = ctk.CTkEntry(scroll, width=620, height=40, placeholder_text="1 = más alta, 10 = más baja")
        entry_prioridad.insert(0, "5")
        entry_prioridad.pack(padx=10, pady=(5, 15))
        
        # Activa
        switch_activa = ctk.CTkSwitch(scroll, text="Regla activa")
        switch_activa.select()
        switch_activa.pack(padx=10, pady=(5, 15), anchor="w")
        
        # Label error
        label_error = ctk.CTkLabel(scroll, text="", text_color=COLOR_DANGER, wraplength=600)
        label_error.pack(pady=10)
        
        def guardar():
            numero = entry_numero.get().strip()
            nombre = entry_nombre.get().strip()
            categoria = combo_categoria.get()
            descripcion = text_descripcion.get("1.0", "end").strip()
            condiciones = text_condiciones.get("1.0", "end").strip()
            acciones = text_acciones.get("1.0", "end").strip()
            prioridad = entry_prioridad.get().strip()
            activa = switch_activa.get()
            
            # Validaciones
            if not numero or not nombre or not descripcion or not condiciones or not acciones:
                label_error.configure(text="❌ Todos los campos obligatorios deben completarse")
                return
            
            # Validar JSON
            try:
                json.loads(condiciones)
                json.loads(acciones)
            except json.JSONDecodeError as e:
                label_error.configure(text=f"❌ JSON inválido: {str(e)}")
                return
            
            # Validar prioridad
            try:
                prioridad_int = int(prioridad)
                if prioridad_int < 1 or prioridad_int > 10:
                    raise ValueError()
            except:
                label_error.configure(text="❌ La prioridad debe ser un número entre 1 y 10")
                return
            
            # Crear regla
            try:
                id_usuario = auth_service.get_id_usuario()
                consultas_reglas.crear_regla(
                    numero_regla=numero,
                    categoria=categoria,
                    nombre=nombre,
                    descripcion=descripcion,
                    condiciones=condiciones,
                    acciones=acciones,
                    prioridad=prioridad_int,
                    activa=activa,
                    creada_por=id_usuario
                )
                
                dialogo.destroy()
                self._cargar_reglas()
                messagebox.showinfo("Éxito", f"Regla '{numero}' creada correctamente")
            except Exception as e:
                label_error.configure(text=f"❌ {str(e)}")
        
        # Botones
        frame_btn = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_btn.pack(pady=15)
        
        ctk.CTkButton(
            frame_btn,
            text="✓ Guardar",
            command=guardar,
            width=150,
            height=40,
            fg_color=COLOR_SUCCESS
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_btn,
            text="✗ Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray"
        ).pack(side="left", padx=5)
    
    def _ver_regla(self, regla):
        """Muestra detalles completos de la regla"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title(f"Detalles - {regla['numero_regla']}")
        dialogo.geometry("700x700")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (700 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        scroll = ctk.CTkScrollableFrame(dialogo)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        ctk.CTkLabel(
            scroll,
            text=f"👁️ {regla['numero_regla']}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(pady=15)
        
        # Función helper para crear secciones
        def crear_seccion(titulo, contenido):
            frame = ctk.CTkFrame(scroll, fg_color=("gray85", "gray20"))
            frame.pack(fill="x", pady=10, padx=10)
            
            ctk.CTkLabel(
                frame,
                text=titulo,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", padx=15, pady=(10, 5))
            
            ctk.CTkLabel(
                frame,
                text=contenido,
                font=ctk.CTkFont(size=12),
                wraplength=620,
                justify="left"
            ).pack(anchor="w", padx=15, pady=(0, 10))
        
        crear_seccion("Nombre:", regla['nombre'])
        crear_seccion("Categoría:", regla['categoria'].capitalize())
        crear_seccion("Descripción:", regla['descripcion'])
        
        # Formatear JSON
        try:
            condiciones_formateadas = json.dumps(json.loads(regla['condiciones']), indent=2, ensure_ascii=False)
        except:
            condiciones_formateadas = regla['condiciones']
        
        try:
            acciones_formateadas = json.dumps(json.loads(regla['acciones']), indent=2, ensure_ascii=False)
        except:
            acciones_formateadas = regla['acciones']
        
        crear_seccion("Condiciones (IF):", condiciones_formateadas)
        crear_seccion("Acciones (THEN):", acciones_formateadas)
        crear_seccion("Prioridad:", f"{regla['prioridad']} (1 = más alta)")
        crear_seccion("Estado:", "✓ Activa" if regla['activa'] else "✗ Inactiva")
        
        # Botón cerrar
        ctk.CTkButton(
            scroll,
            text="Cerrar",
            command=dialogo.destroy,
            width=150,
            height=40
        ).pack(pady=20)
    
    def _editar_regla(self, regla):
        """Muestra diálogo para editar regla"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title(f"Editar - {regla['numero_regla']}")
        dialogo.geometry("700x800")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (800 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        scroll = ctk.CTkScrollableFrame(dialogo)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            scroll,
            text=f"✏️ Editar Regla",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)
        
        # Campos (prellenados)
        ctk.CTkLabel(scroll, text="Número de Regla *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_numero = ctk.CTkEntry(scroll, width=620, height=40)
        entry_numero.insert(0, regla['numero_regla'])
        entry_numero.pack(padx=10, pady=(5, 15))
        
        ctk.CTkLabel(scroll, text="Nombre *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_nombre = ctk.CTkEntry(scroll, width=620, height=40)
        entry_nombre.insert(0, regla['nombre'])
        entry_nombre.pack(padx=10, pady=(5, 15))
        
        ctk.CTkLabel(scroll, text="Categoría *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        combo_categoria = ctk.CTkComboBox(scroll, values=self.CATEGORIAS, width=620, height=40)
        combo_categoria.set(regla['categoria'])
        combo_categoria.pack(padx=10, pady=(5, 15))
        
        ctk.CTkLabel(scroll, text="Descripción *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        text_descripcion = ctk.CTkTextbox(scroll, width=620, height=100)
        text_descripcion.insert("1.0", regla['descripcion'])
        text_descripcion.pack(padx=10, pady=(5, 15))
        
        # Formatear JSON para mostrar
        try:
            condiciones_formateadas = json.dumps(json.loads(regla['condiciones']), indent=2, ensure_ascii=False)
        except:
            condiciones_formateadas = regla['condiciones']
        
        try:
            acciones_formateadas = json.dumps(json.loads(regla['acciones']), indent=2, ensure_ascii=False)
        except:
            acciones_formateadas = regla['acciones']
        
        ctk.CTkLabel(scroll, text="Condiciones (IF) - JSON *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        text_condiciones = ctk.CTkTextbox(scroll, width=620, height=120)
        text_condiciones.insert("1.0", condiciones_formateadas)
        text_condiciones.pack(padx=10, pady=(5, 15))
        
        ctk.CTkLabel(scroll, text="Acciones (THEN) - JSON *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        text_acciones = ctk.CTkTextbox(scroll, width=620, height=120)
        text_acciones.insert("1.0", acciones_formateadas)
        text_acciones.pack(padx=10, pady=(5, 15))
        
        ctk.CTkLabel(scroll, text="Prioridad (1-10) *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_prioridad = ctk.CTkEntry(scroll, width=620, height=40)
        entry_prioridad.insert(0, str(regla['prioridad']))
        entry_prioridad.pack(padx=10, pady=(5, 15))
        
        switch_activa = ctk.CTkSwitch(scroll, text="Regla activa")
        if regla['activa']:
            switch_activa.select()
        switch_activa.pack(padx=10, pady=(5, 15), anchor="w")
        
        label_error = ctk.CTkLabel(scroll, text="", text_color=COLOR_DANGER, wraplength=600)
        label_error.pack(pady=10)
        
        def guardar():
            numero = entry_numero.get().strip()
            nombre = entry_nombre.get().strip()
            categoria = combo_categoria.get()
            descripcion = text_descripcion.get("1.0", "end").strip()
            condiciones = text_condiciones.get("1.0", "end").strip()
            acciones = text_acciones.get("1.0", "end").strip()
            prioridad = entry_prioridad.get().strip()
            activa = switch_activa.get()
            
            if not numero or not nombre or not descripcion or not condiciones or not acciones:
                label_error.configure(text="❌ Todos los campos obligatorios deben completarse")
                return
            
            try:
                json.loads(condiciones)
                json.loads(acciones)
            except json.JSONDecodeError as e:
                label_error.configure(text=f"❌ JSON inválido: {str(e)}")
                return
            
            try:
                prioridad_int = int(prioridad)
                if prioridad_int < 1 or prioridad_int > 10:
                    raise ValueError()
            except:
                label_error.configure(text="❌ La prioridad debe ser un número entre 1 y 10")
                return
            
            try:
                consultas_reglas.actualizar_regla(
                    id_regla=regla['id'],
                    numero_regla=numero,
                    categoria=categoria,
                    nombre=nombre,
                    descripcion=descripcion,
                    condiciones=condiciones,
                    acciones=acciones,
                    prioridad=prioridad_int,
                    activa=activa
                )
                
                dialogo.destroy()
                self._cargar_reglas()
                messagebox.showinfo("Éxito", "Regla actualizada correctamente")
            except Exception as e:
                label_error.configure(text=f"❌ {str(e)}")
        
        frame_btn = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_btn.pack(pady=15)
        
        ctk.CTkButton(
            frame_btn,
            text="✓ Guardar",
            command=guardar,
            width=150,
            height=40,
            fg_color=COLOR_SUCCESS
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_btn,
            text="✗ Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray"
        ).pack(side="left", padx=5)
    
    def _cambiar_estado_regla(self, regla, activa):
        """Activa o desactiva una regla"""
        accion = "activar" if activa else "desactivar"
        if messagebox.askyesno(
            "Confirmar",
            f"¿Está seguro de {accion} la regla '{regla['numero_regla']}'?"
        ):
            try:
                consultas_reglas.activar_desactivar_regla(regla['id'], activa)
                self._cargar_reglas()
                messagebox.showinfo("Éxito", f"Regla {accion}da correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo {accion} la regla:\n{str(e)}")
    
    def _eliminar_regla(self, regla):
        """Elimina una regla"""
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar la regla '{regla['numero_regla']}'?\n\n"
            "Esta acción no se puede deshacer."
        ):
            try:
                consultas_reglas.eliminar_regla(regla['id'])
                self._cargar_reglas()
                messagebox.showinfo("Éxito", "Regla eliminada correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la regla:\n{str(e)}")
