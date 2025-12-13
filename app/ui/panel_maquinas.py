"""
Panel de gestión de maquinarias
Permite ver, agregar, editar y eliminar máquinas
"""
import customtkinter as ctk
from tkinter import messagebox
from app.config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER
)
from app.database import consultas


class PanelMaquinas(ctk.CTkFrame):
    """Panel para gestionar maquinarias"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título y botones
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        self.titulo = ctk.CTkLabel(
            frame_titulo,
            text="Gestión de Maquinarias",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.titulo.pack(side="left")

        self.btn_nueva_maquina = ctk.CTkButton(
            frame_titulo,
            text="+ Nueva Máquina",
            command=lambda: self._mostrar_dialogo_maquina(),
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS,
            width=180
        )
        self.btn_nueva_maquina.pack(side="right", padx=10)

        self.btn_actualizar = ctk.CTkButton(
            frame_titulo,
            text="Actualizar",
            command=self._cargar_maquinas,
            height=40,
            width=140
        )
        self.btn_actualizar.pack(side="right")

        # Contenedor scrollable
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self._cargar_maquinas()

    def _cargar_maquinas(self):
        """Carga y muestra todas las máquinas"""
        # Limpiar frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obtener máquinas
        maquinas = consultas.obtener_maquinas()

        if not maquinas:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No hay máquinas registradas",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
            return

        # Crear encabezados
        frame_header = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3), weight=1)

        headers = ["ID", "Nombre de la Máquina", "Tipo", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                frame_header,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=10)

        # Mostrar máquinas
        for idx, maquina in enumerate(maquinas):
            self._crear_fila_maquina(maquina, idx + 1)

    def _crear_fila_maquina(self, maquina, fila):
        """Crea una fila con los datos de la máquina"""
        fg_color = "gray25" if fila % 2 == 0 else "gray20"

        frame_fila = ctk.CTkFrame(self.scroll_frame, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # ID
        ctk.CTkLabel(
            frame_fila,
            text=str(maquina['id_maquina']),
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, padx=10, pady=10)

        # Nombre
        ctk.CTkLabel(
            frame_fila,
            text=maquina['nombre'],
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Tipo
        ctk.CTkLabel(
            frame_fila,
            text=maquina['tipo']
        ).grid(row=0, column=2, padx=10, pady=10)

        # Botones
        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=3, padx=10, pady=5)

        btn_servicios = ctk.CTkButton(
            frame_acciones,
            text="🔗 Servicios",
            command=lambda m=maquina: self._gestionar_servicios_maquina(m),
            width=100,
            height=30,
            fg_color="#2196F3"
        )
        btn_servicios.pack(side="left", padx=2)

        btn_editar = ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda m=maquina: self._mostrar_dialogo_maquina(m),
            width=70,
            height=30,
            fg_color=COLOR_PRIMARY
        )
        btn_editar.pack(side="left", padx=2)

        btn_eliminar = ctk.CTkButton(
            frame_acciones,
            text="Eliminar",
            command=lambda m=maquina: self._confirmar_eliminar_maquina(m),
            width=70,
            height=30,
            fg_color=COLOR_DANGER
        )
        btn_eliminar.pack(side="left", padx=2)

    def _mostrar_dialogo_maquina(self, maquina=None):
        """Muestra diálogo para agregar o editar máquina"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nueva Máquina" if maquina is None else "Editar Máquina")
        dialogo.geometry("550x500")
        dialogo.transient(self)
        dialogo.grab_set()

        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (500 // 2)
        dialogo.geometry(f"+{x}+{y}")

        # Contenedor para campos
        frame_campos = ctk.CTkFrame(dialogo)
        frame_campos.pack(fill="both", expand=True, padx=20, pady=20)

        # Campos
        ctk.CTkLabel(frame_campos, text="Nombre de la Máquina:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        entry_nombre = ctk.CTkEntry(frame_campos, width=450)
        entry_nombre.pack(pady=5)
        if maquina:
            entry_nombre.insert(0, maquina['nombre'])

        ctk.CTkLabel(frame_campos, text="Tipo de Máquina:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        combo_tipo = ctk.CTkComboBox(
            frame_campos,
            values=["Pequeño Formato", "Gran Formato", "Acabado", "Sublimación", "Láser"],
            width=450
        )
        combo_tipo.pack(pady=5)
        if maquina:
            combo_tipo.set(maquina['tipo'])
        else:
            combo_tipo.set("Pequeño Formato")
        
        # FASE 3: Campo Sugerencia
        ctk.CTkLabel(frame_campos, text="Sugerencia / Recomendación:", font=ctk.CTkFont(size=12)).pack(pady=(15, 5))
        text_sugerencia = ctk.CTkTextbox(frame_campos, width=450, height=100)
        text_sugerencia.pack(pady=5)
        if maquina:
            text_sugerencia.insert("1.0", maquina.get('sugerencia', ''))
        else:
            text_sugerencia.insert("1.0", "Ej: Ideal para trabajos de alta calidad, soporta materiales rígidos...")

        # Frame de botones
        frame_botones = ctk.CTkFrame(dialogo)
        frame_botones.pack(fill="x", padx=20, pady=10)

        def guardar():
            nombre = entry_nombre.get().strip()
            tipo = combo_tipo.get()
            sugerencia = text_sugerencia.get("1.0", "end-1c").strip()

            if not nombre:
                messagebox.showwarning("Validación", "Debe ingresar un nombre")
                return

            try:
                if maquina:
                    consultas.actualizar_maquina(
                        maquina['id_maquina'],
                        nombre, tipo, sugerencia
                    )
                    messagebox.showinfo("Éxito", "Máquina actualizada correctamente")
                else:
                    consultas.guardar_maquina(nombre, tipo, sugerencia)
                    messagebox.showinfo("Éxito", "Máquina agregada correctamente")

                dialogo.destroy()
                self._cargar_maquinas()

            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=dialogo.destroy,
            height=40,
            width=150,
            fg_color="gray"
        )
        btn_cancelar.pack(side="left", padx=10)

        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="Guardar",
            command=guardar,
            height=40,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS
        )
        btn_guardar.pack(side="right", padx=10)

    def _confirmar_eliminar_maquina(self, maquina):
        """Muestra diálogo de confirmación antes de eliminar"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Confirmar Eliminación")
        dialogo.geometry("450x250")
        dialogo.transient(self)
        dialogo.grab_set()

        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (250 // 2)
        dialogo.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialogo,
            text="¿Está seguro de eliminar esta máquina?",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            dialogo,
            text=f"Máquina: {maquina['nombre']}",
            font=ctk.CTkFont(size=14)
        ).pack(pady=5)

        ctk.CTkLabel(
            dialogo,
            text="Esta acción no se puede deshacer.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=10)

        frame_botones = ctk.CTkFrame(dialogo, fg_color="transparent")
        frame_botones.pack(pady=20)

        def eliminar():
            try:
                consultas.eliminar_maquina(maquina['id_maquina'])
                messagebox.showinfo("Éxito", "Máquina eliminada correctamente")
                dialogo.destroy()
                self._cargar_maquinas()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la máquina: {str(e)}")

        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray"
        )
        btn_cancelar.pack(side="left", padx=10)

        btn_confirmar = ctk.CTkButton(
            frame_botones,
            text="Sí, Eliminar",
            command=eliminar,
            width=120,
            height=40,
            fg_color=COLOR_DANGER
        )
        btn_confirmar.pack(side="left", padx=10)
    
    def _gestionar_servicios_maquina(self, maquina):
        """Diálogo para gestionar servicios asociados a una máquina"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title(f"Servicios - {maquina['nombre']}")
        dialogo.geometry("800x600")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (800 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (600 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        # Frame principal con scroll
        frame_principal = ctk.CTkScrollableFrame(dialogo, fg_color="transparent")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            frame_principal,
            text=f"Gestionar Servicios para: {maquina['nombre']}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 20))
        
        # === SECCIÓN: SERVICIOS ASOCIADOS ===
        frame_asociados = ctk.CTkFrame(frame_principal, fg_color="gray20")
        frame_asociados.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            frame_asociados,
            text="Servicios Asociados",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10, padx=10, anchor="w")
        
        # Lista de servicios asociados
        frame_lista_asociados = ctk.CTkFrame(frame_asociados, fg_color="transparent")
        frame_lista_asociados.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        def cargar_servicios_asociados():
            # Limpiar lista
            for widget in frame_lista_asociados.winfo_children():
                widget.destroy()
            
            servicios = consultas.obtener_servicios_por_maquina(maquina['id_maquina'])
            
            if not servicios:
                ctk.CTkLabel(
                    frame_lista_asociados,
                    text="No hay servicios asociados",
                    text_color="gray"
                ).pack(pady=10)
                return
            
            for servicio in servicios:
                frame_serv = ctk.CTkFrame(frame_lista_asociados, fg_color="gray25")
                frame_serv.pack(fill="x", pady=2)
                
                # Indicador de recomendada
                icono = "⭐" if servicio.get('es_recomendada') else "🔧"
                
                ctk.CTkLabel(
                    frame_serv,
                    text=f"{icono} {servicio['nombre_servicio']} ({servicio['unidad_cobro']})",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left", padx=10, pady=8)
                
                # Botón marcar/desmarcar recomendada
                btn_recomendada = ctk.CTkButton(
                    frame_serv,
                    text="★ Recomendada" if not servicio.get('es_recomendada') else "☆ Normal",
                    command=lambda s=servicio: toggle_recomendada(s),
                    width=120,
                    height=25,
                    fg_color="#FF9800" if not servicio.get('es_recomendada') else "gray"
                )
                btn_recomendada.pack(side="right", padx=2)
                
                # Botón eliminar asociación
                btn_quitar = ctk.CTkButton(
                    frame_serv,
                    text="Quitar",
                    command=lambda s=servicio: quitar_servicio(s),
                    width=70,
                    height=25,
                    fg_color=COLOR_DANGER
                )
                btn_quitar.pack(side="right", padx=2)
        
        def toggle_recomendada(servicio):
            nuevo_estado = not servicio.get('es_recomendada', False)
            if consultas.marcar_maquina_recomendada(maquina['id_maquina'], servicio['id_servicio'], nuevo_estado):
                cargar_servicios_asociados()
        
        def quitar_servicio(servicio):
            if consultas.desasociar_servicio_de_maquina(maquina['id_maquina'], servicio['id_servicio']):
                cargar_servicios_asociados()
                cargar_servicios_disponibles()
                messagebox.showinfo("Éxito", "Servicio desasociado correctamente")
        
        # === SECCIÓN: AGREGAR SERVICIOS ===
        frame_agregar = ctk.CTkFrame(frame_principal, fg_color="gray20")
        frame_agregar.pack(fill="x")
        
        ctk.CTkLabel(
            frame_agregar,
            text="Agregar Servicios",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10, padx=10, anchor="w")
        
        # Combo de servicios disponibles
        frame_combo = ctk.CTkFrame(frame_agregar, fg_color="transparent")
        frame_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        combo_servicios = ctk.CTkComboBox(
            frame_combo,
            values=["Cargando..."],
            width=400
        )
        combo_servicios.pack(side="left", padx=(0, 10))
        
        var_recomendada = ctk.CTkCheckBox(
            frame_combo,
            text="Marcar como recomendada",
            font=ctk.CTkFont(size=12)
        )
        var_recomendada.pack(side="left", padx=10)
        
        btn_agregar = ctk.CTkButton(
            frame_combo,
            text="+ Agregar",
            command=lambda: agregar_servicio(),
            width=100,
            height=32,
            fg_color=COLOR_SUCCESS
        )
        btn_agregar.pack(side="left")
        
        def cargar_servicios_disponibles():
            servicios_disp = consultas.obtener_servicios_disponibles_para_maquina(maquina['id_maquina'])
            if servicios_disp:
                nombres = [f"{s['nombre_servicio']} - {s['unidad_cobro']}" for s in servicios_disp]
                combo_servicios.configure(values=nombres)
                combo_servicios.set(nombres[0])
                combo_servicios._servicios_data = servicios_disp
            else:
                combo_servicios.configure(values=["No hay servicios disponibles"])
                combo_servicios.set("No hay servicios disponibles")
                combo_servicios._servicios_data = []
        
        def agregar_servicio():
            if not hasattr(combo_servicios, '_servicios_data') or not combo_servicios._servicios_data:
                messagebox.showwarning("Advertencia", "No hay servicios disponibles para asociar")
                return
            
            idx = combo_servicios.cget("values").index(combo_servicios.get())
            servicio_sel = combo_servicios._servicios_data[idx]
            es_rec = var_recomendada.get()
            
            if consultas.asociar_servicio_a_maquina(maquina['id_maquina'], servicio_sel['id_servicio'], es_rec):
                cargar_servicios_asociados()
                cargar_servicios_disponibles()
                var_recomendada.deselect()
                messagebox.showinfo("Éxito", "Servicio asociado correctamente")
            else:
                messagebox.showwarning("Advertencia", "El servicio ya está asociado")
        
        # Cargar datos iniciales
        cargar_servicios_asociados()
        cargar_servicios_disponibles()
        
        # Botón cerrar
        ctk.CTkButton(
            dialogo,
            text="Cerrar",
            command=dialogo.destroy,
            width=150,
            height=40,
            fg_color="gray"
        ).pack(pady=10)

