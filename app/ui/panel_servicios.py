"""
Panel de gestión de servicios
Permite ver, agregar, editar y eliminar servicios
"""
import customtkinter as ctk
from tkinter import messagebox
from app.config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER
)
from app.database import consultas


class PanelServicios(ctk.CTkFrame):
    """Panel para gestionar servicios"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título y botones
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        self.titulo = ctk.CTkLabel(
            frame_titulo,
            text="Gestión de Servicios",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.titulo.pack(side="left")

        self.btn_nuevo_servicio = ctk.CTkButton(
            frame_titulo,
            text="+ Nuevo Servicio",
            command=self._mostrar_dialogo_servicio,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS,
            width=180
        )
        self.btn_nuevo_servicio.pack(side="right", padx=10)

        self.btn_actualizar = ctk.CTkButton(
            frame_titulo,
            text="Actualizar",
            command=self._cargar_servicios,
            height=40,
            width=140
        )
        self.btn_actualizar.pack(side="right")

        # Contenedor scrollable
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self._cargar_servicios()

    def _cargar_servicios(self):
        """Carga y muestra todos los servicios"""
        # Limpiar frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obtener servicios
        servicios = consultas.obtener_servicios()

        if not servicios:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No hay servicios registrados",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
            return

        # Crear encabezados
        frame_header = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        headers = ["ID", "Nombre Servicio", "Unidad", "Precio Base", "Máquina Sugerida", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                frame_header,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=10)

        # Mostrar servicios
        for idx, servicio in enumerate(servicios):
            self._crear_fila_servicio(servicio, idx + 1)

    def _crear_fila_servicio(self, servicio, fila):
        """Crea una fila con los datos del servicio"""
        fg_color = "gray25" if fila % 2 == 0 else "gray20"

        frame_fila = ctk.CTkFrame(self.scroll_frame, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # ID
        ctk.CTkLabel(
            frame_fila,
            text=str(servicio['id_servicio']),
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, padx=10, pady=10)

        # Nombre
        ctk.CTkLabel(
            frame_fila,
            text=servicio['nombre_servicio'],
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Unidad
        ctk.CTkLabel(
            frame_fila,
            text=servicio['unidad_cobro']
        ).grid(row=0, column=2, padx=10, pady=10)

        # Precio
        ctk.CTkLabel(
            frame_fila,
            text=f"S/ {servicio['precio_base']:.2f}"
        ).grid(row=0, column=3, padx=10, pady=10)

        # Máquina
        maquina_texto = servicio['nombre_maquina'] if servicio['nombre_maquina'] else "No asignada"
        ctk.CTkLabel(
            frame_fila,
            text=maquina_texto
        ).grid(row=0, column=4, padx=10, pady=10)

        # Botones
        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=5, padx=10, pady=5)

        btn_materiales = ctk.CTkButton(
            frame_acciones,
            text="🔗 Materiales",
            command=lambda s=servicio: self._gestionar_materiales_servicio(s),
            width=100,
            height=30,
            fg_color="#2196F3"
        )
        btn_materiales.pack(side="left", padx=2)

        btn_editar = ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda s=servicio: self._editar_servicio(s),
            width=70,
            height=30,
            fg_color=COLOR_PRIMARY
        )
        btn_editar.pack(side="left", padx=2)

        btn_eliminar = ctk.CTkButton(
            frame_acciones,
            text="Eliminar",
            command=lambda s=servicio: self._confirmar_eliminar_servicio(s),
            width=70,
            height=30,
            fg_color=COLOR_DANGER
        )
        btn_eliminar.pack(side="left", padx=2)

    def _mostrar_dialogo_servicio(self, servicio=None):
        """Muestra diálogo para agregar o editar servicio"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Servicio" if servicio is None else "Editar Servicio")
        dialogo.geometry("550x500")
        dialogo.transient(self)
        dialogo.grab_set()

        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (500 // 2)
        dialogo.geometry(f"+{x}+{y}")

        # Campos
        ctk.CTkLabel(dialogo, text="Nombre del Servicio:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        entry_nombre = ctk.CTkEntry(dialogo, width=450)
        entry_nombre.pack(pady=5)
        if servicio:
            entry_nombre.insert(0, servicio['nombre_servicio'])

        ctk.CTkLabel(dialogo, text="Unidad de Cobro:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        
        # Obtener unidades de la base de datos
        unidades = consultas.obtener_unidades_medida()
        unidades_nombres = [u['abreviacion'] for u in unidades]
        
        # Fallback si no hay unidades
        if not unidades_nombres:
            unidades_nombres = ["m2", "cm2", "unidad", "ciento", "docena", "metro", "hora"]
        
        combo_unidad = ctk.CTkComboBox(dialogo, values=unidades_nombres, width=450)
        combo_unidad.pack(pady=5)
        if servicio:
            combo_unidad.set(servicio['unidad_cobro'])

        ctk.CTkLabel(dialogo, text="Precio Base (S/):", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_precio = ctk.CTkEntry(dialogo, width=450)
        entry_precio.pack(pady=5)
        if servicio:
            entry_precio.insert(0, str(servicio['precio_base']))
        else:
            entry_precio.insert(0, "0.00")

        ctk.CTkLabel(dialogo, text="Máquina Sugerida:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))

        # Obtener máquinas
        maquinas = consultas.obtener_maquinas()
        maquinas_dict = {f"{m['nombre']} - {m['tipo']}": m['id_maquina'] for m in maquinas}
        maquinas_nombres = list(maquinas_dict.keys())

        combo_maquina = ctk.CTkComboBox(dialogo, values=["Ninguna"] + maquinas_nombres, width=450)
        combo_maquina.pack(pady=5)

        if servicio and servicio['nombre_maquina']:
            nombre_actual = f"{servicio['nombre_maquina']} - {servicio['tipo_maquina']}"
            combo_maquina.set(nombre_actual)
        else:
            combo_maquina.set("Ninguna")

        def guardar():
            nombre = entry_nombre.get().strip()
            unidad = combo_unidad.get()

            try:
                precio = float(entry_precio.get())
            except ValueError:
                messagebox.showerror("Error", "El precio debe ser un número válido")
                return

            if not nombre:
                messagebox.showwarning("Validación", "Debe ingresar un nombre de servicio")
                return

            # Obtener ID de máquina
            maquina_seleccionada = combo_maquina.get()
            id_maquina = maquinas_dict.get(maquina_seleccionada, None) if maquina_seleccionada != "Ninguna" else None

            try:
                if servicio:
                    consultas.actualizar_servicio(
                        servicio['id_servicio'],
                        nombre, unidad, precio, id_maquina
                    )
                    messagebox.showinfo("Éxito", "Servicio actualizado correctamente")
                else:
                    consultas.guardar_servicio(nombre, unidad, precio, id_maquina)
                    messagebox.showinfo("Éxito", "Servicio agregado correctamente")

                dialogo.destroy()
                self._cargar_servicios()

            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        btn_guardar = ctk.CTkButton(
            dialogo,
            text="Guardar",
            command=guardar,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS
        )
        btn_guardar.pack(pady=30)

    def _editar_servicio(self, servicio):
        """Edita un servicio existente"""
        self._mostrar_dialogo_servicio(servicio)

    def _confirmar_eliminar_servicio(self, servicio):
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
            text="¿Está seguro de eliminar este servicio?",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            dialogo,
            text=f"Servicio: {servicio['nombre_servicio']}",
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
                consultas.eliminar_servicio(servicio['id_servicio'])
                messagebox.showinfo("Éxito", "Servicio eliminado correctamente")
                dialogo.destroy()
                self._cargar_servicios()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el servicio: {str(e)}")

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
            text="Eliminar",
            command=eliminar,
            width=120,
            height=40,
            fg_color=COLOR_DANGER
        )
        btn_confirmar.pack(side="left", padx=10)
    
    def _gestionar_materiales_servicio(self, servicio):
        """Diálogo para gestionar materiales asociados a un servicio"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title(f"Materiales - {servicio['nombre_servicio']}")
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
            text=f"Gestionar Materiales para: {servicio['nombre_servicio']}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 20))
        
        # === SECCIÓN: MATERIALES ASOCIADOS ===
        frame_asociados = ctk.CTkFrame(frame_principal, fg_color="gray20")
        frame_asociados.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            frame_asociados,
            text="Materiales Asociados",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10, padx=10, anchor="w")
        
        # Lista de materiales asociados
        frame_lista_asociados = ctk.CTkFrame(frame_asociados, fg_color="transparent")
        frame_lista_asociados.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        def cargar_materiales_asociados():
            # Limpiar lista
            for widget in frame_lista_asociados.winfo_children():
                widget.destroy()
            
            materiales = consultas.obtener_materiales_por_servicio(servicio['id_servicio'])
            
            if not materiales:
                ctk.CTkLabel(
                    frame_lista_asociados,
                    text="No hay materiales asociados",
                    text_color="gray"
                ).pack(pady=10)
                return
            
            for material in materiales:
                frame_mat = ctk.CTkFrame(frame_lista_asociados, fg_color="gray25")
                frame_mat.pack(fill="x", pady=2)
                
                # Indicador de preferido
                icono = "⭐" if material.get('es_preferido') else "📦"
                
                ctk.CTkLabel(
                    frame_mat,
                    text=f"{icono} {material['nombre_material']} ({material['unidad_medida']})",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left", padx=10, pady=8)
                
                # Botón marcar/desmarcar preferido
                btn_preferido = ctk.CTkButton(
                    frame_mat,
                    text="★ Preferido" if not material.get('es_preferido') else "☆ Normal",
                    command=lambda m=material: toggle_preferido(m),
                    width=100,
                    height=25,
                    fg_color="#FF9800" if not material.get('es_preferido') else "gray"
                )
                btn_preferido.pack(side="right", padx=2)
                
                # Botón eliminar asociación
                btn_quitar = ctk.CTkButton(
                    frame_mat,
                    text="Quitar",
                    command=lambda m=material: quitar_material(m),
                    width=70,
                    height=25,
                    fg_color=COLOR_DANGER
                )
                btn_quitar.pack(side="right", padx=2)
        
        def toggle_preferido(material):
            nuevo_estado = not material.get('es_preferido', False)
            if consultas.marcar_material_preferido(servicio['id_servicio'], material['id_material'], nuevo_estado):
                cargar_materiales_asociados()
        
        def quitar_material(material):
            if consultas.desasociar_material_de_servicio(servicio['id_servicio'], material['id_material']):
                cargar_materiales_asociados()
                cargar_materiales_disponibles()
                messagebox.showinfo("Éxito", "Material desasociado correctamente")
        
        # === SECCIÓN: AGREGAR MATERIALES ===
        frame_agregar = ctk.CTkFrame(frame_principal, fg_color="gray20")
        frame_agregar.pack(fill="x")
        
        ctk.CTkLabel(
            frame_agregar,
            text="Agregar Materiales",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10, padx=10, anchor="w")
        
        # Combo de materiales disponibles
        frame_combo = ctk.CTkFrame(frame_agregar, fg_color="transparent")
        frame_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        combo_materiales = ctk.CTkComboBox(
            frame_combo,
            values=["Cargando..."],
            width=400
        )
        combo_materiales.pack(side="left", padx=(0, 10))
        
        var_preferido = ctk.CTkCheckBox(
            frame_combo,
            text="Marcar como preferido",
            font=ctk.CTkFont(size=12)
        )
        var_preferido.pack(side="left", padx=10)
        
        btn_agregar = ctk.CTkButton(
            frame_combo,
            text="+ Agregar",
            command=lambda: agregar_material(),
            width=100,
            height=32,
            fg_color=COLOR_SUCCESS
        )
        btn_agregar.pack(side="left")
        
        def cargar_materiales_disponibles():
            materiales_disp = consultas.obtener_materiales_disponibles_para_servicio(servicio['id_servicio'])
            if materiales_disp:
                nombres = [f"{m['nombre_material']} ({m['tipo_material']})" for m in materiales_disp]
                combo_materiales.configure(values=nombres)
                combo_materiales.set(nombres[0])
                combo_materiales._materiales_data = materiales_disp
            else:
                combo_materiales.configure(values=["No hay materiales disponibles"])
                combo_materiales.set("No hay materiales disponibles")
                combo_materiales._materiales_data = []
        
        def agregar_material():
            if not hasattr(combo_materiales, '_materiales_data') or not combo_materiales._materiales_data:
                messagebox.showwarning("Advertencia", "No hay materiales disponibles para asociar")
                return
            
            idx = combo_materiales.cget("values").index(combo_materiales.get())
            material_sel = combo_materiales._materiales_data[idx]
            es_pref = var_preferido.get()
            
            if consultas.asociar_material_a_servicio(servicio['id_servicio'], material_sel['id_material'], es_pref):
                cargar_materiales_asociados()
                cargar_materiales_disponibles()
                var_preferido.deselect()
                messagebox.showinfo("Éxito", "Material asociado correctamente")
            else:
                messagebox.showwarning("Advertencia", "El material ya está asociado")
        
        # Cargar datos iniciales
        cargar_materiales_asociados()
        cargar_materiales_disponibles()
        
        # Botón cerrar
        ctk.CTkButton(
            dialogo,
            text="Cerrar",
            command=dialogo.destroy,
            width=150,
            height=40,
            fg_color="gray"
        ).pack(pady=10)
    
    def _editar_servicio(self, servicio):
        """Abre el diálogo de edición de servicio"""
        self._mostrar_dialogo_servicio(servicio)
    
    def _confirmar_eliminar_servicio(self, servicio):
        """Muestra confirmación antes de eliminar servicio"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Confirmar Eliminación")
        dialogo.geometry("450x200")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (200 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(
            dialogo,
            text="¿Está seguro de eliminar este servicio?",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            dialogo,
            text=f"Servicio: {servicio['nombre_servicio']}",
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
                consultas.eliminar_servicio(servicio['id_servicio'])
                messagebox.showinfo("Éxito", "Servicio eliminado correctamente")
                dialogo.destroy()
                self._cargar_servicios()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el servicio: {str(e)}")
        
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

