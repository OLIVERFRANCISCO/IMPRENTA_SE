"""
Panel de Configuración del Sistema
Permite gestionar catálogos: Unidades de Medida, Tipos de Máquina, Estados de Pedido
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, colorchooser
from app.config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER
)
from app.database import consultas


class PanelConfiguracion(ctk.CTkFrame):
    """Panel para configurar catálogos del sistema"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        self.titulo = ctk.CTkLabel(
            frame_titulo,
            text="⚙️ Configuración del Sistema",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.titulo.pack(side="left")

        # Tabview para las diferentes secciones
        self.tabview = ctk.CTkTabview(self, corner_radius=15)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Crear pestañas
        self.tab_unidades = self.tabview.add("📏 Unidades de Medida")
        self.tab_tipos_maquina = self.tabview.add("🔧 Tipos de Máquina")
        self.tab_tipos_material = self.tabview.add("📦 Tipos de Material")
        self.tab_estados = self.tabview.add("📋 Estados de Pedido")

        # Configurar cada pestaña
        self._configurar_tab_unidades()
        self._configurar_tab_tipos_maquina()
        self._configurar_tab_tipos_material()
        self._configurar_tab_estados()

    # ========== UNIDADES DE MEDIDA ==========
    def _configurar_tab_unidades(self):
        """Configura la pestaña de unidades de medida"""
        self.tab_unidades.grid_rowconfigure(1, weight=1)
        self.tab_unidades.grid_columnconfigure(0, weight=1)

        # Frame de controles
        frame_controles = ctk.CTkFrame(self.tab_unidades, fg_color="transparent")
        frame_controles.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            frame_controles,
            text="+ Nueva Unidad",
            command=self._dialogo_unidad,
            fg_color=COLOR_SUCCESS,
            width=150,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_controles,
            text="🔄 Actualizar",
            command=self._cargar_unidades,
            width=120,
            height=35
        ).pack(side="left", padx=5)

        # Frame scrollable para la lista
        self.scroll_unidades = ctk.CTkScrollableFrame(self.tab_unidades)
        self.scroll_unidades.grid(row=1, column=0, sticky="nsew")
        self.scroll_unidades.grid_columnconfigure(0, weight=1)

        self._cargar_unidades()

    def _cargar_unidades(self):
        """Carga las unidades de medida"""
        for widget in self.scroll_unidades.winfo_children():
            widget.destroy()

        unidades = consultas.obtener_unidades_medida()

        if not unidades:
            ctk.CTkLabel(
                self.scroll_unidades,
                text="No hay unidades registradas",
                text_color="gray"
            ).pack(pady=20)
            return

        # Encabezados
        frame_header = ctk.CTkFrame(self.scroll_unidades, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3), weight=1)

        headers = ["Nombre", "Abreviación", "Tipo", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                frame_header,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=8)

        # Filas
        for idx, unidad in enumerate(unidades):
            self._crear_fila_unidad(unidad, idx + 1)

    def _crear_fila_unidad(self, unidad, fila):
        """Crea una fila para una unidad"""
        fg_color = "gray25" if fila % 2 == 0 else "gray20"
        frame_fila = ctk.CTkFrame(self.scroll_unidades, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(frame_fila, text=unidad['nombre_unidad']).grid(row=0, column=0, padx=10, pady=8)
        ctk.CTkLabel(frame_fila, text=unidad['abreviacion'], font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=8)
        ctk.CTkLabel(frame_fila, text=unidad['tipo']).grid(row=0, column=2, padx=10, pady=8)

        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda u=unidad: self._dialogo_unidad(u),
            width=60,
            height=28,
            fg_color=COLOR_PRIMARY
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            frame_acciones,
            text="Eliminar",
            command=lambda u=unidad: self._eliminar_unidad(u),
            width=70,
            height=28,
            fg_color=COLOR_DANGER
        ).pack(side="left", padx=2)

    def _dialogo_unidad(self, unidad=None):
        """Diálogo para crear/editar unidad"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nueva Unidad" if unidad is None else "Editar Unidad")
        dialogo.geometry("450x350")
        dialogo.transient(self)
        dialogo.grab_set()

        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (350 // 2)
        dialogo.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialogo, text="Nombre de la Unidad:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        entry_nombre = ctk.CTkEntry(dialogo, width=350, placeholder_text="Ej: Metro Cuadrado")
        entry_nombre.pack(pady=5)
        if unidad:
            entry_nombre.insert(0, unidad['nombre_unidad'])

        ctk.CTkLabel(dialogo, text="Abreviación:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_abrev = ctk.CTkEntry(dialogo, width=350, placeholder_text="Ej: m², unid, kg")
        entry_abrev.pack(pady=5)
        if unidad:
            entry_abrev.insert(0, unidad['abreviacion'])

        ctk.CTkLabel(dialogo, text="Tipo de Unidad:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        combo_tipo = ctk.CTkComboBox(
            dialogo,
            values=["Área", "Longitud", "Conteo", "Volumen", "Peso", "Tiempo"],
            width=350
        )
        combo_tipo.pack(pady=5)
        if unidad:
            combo_tipo.set(unidad['tipo'])
        else:
            combo_tipo.set("Conteo")

        def guardar():
            nombre = entry_nombre.get().strip()
            abrev = entry_abrev.get().strip()
            tipo = combo_tipo.get()

            if not nombre or not abrev:
                messagebox.showwarning("Validación", "Complete todos los campos")
                return

            try:
                if unidad:
                    consultas.actualizar_unidad_medida(unidad['id_unidad'], nombre, abrev, tipo)
                    messagebox.showinfo("Éxito", "Unidad actualizada correctamente")
                else:
                    consultas.guardar_unidad_medida(nombre, abrev, tipo)
                    messagebox.showinfo("Éxito", "Unidad creada correctamente")
                dialogo.destroy()
                self._cargar_unidades()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(
            dialogo,
            text="💾 Guardar",
            command=guardar,
            fg_color=COLOR_SUCCESS,
            height=40,
            width=150
        ).pack(pady=25)

    def _eliminar_unidad(self, unidad):
        """Elimina una unidad de medida"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar la unidad '{unidad['nombre_unidad']}'?"):
            try:
                consultas.eliminar_unidad_medida(unidad['id_unidad'])
                messagebox.showinfo("Éxito", "Unidad eliminada")
                self._cargar_unidades()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ========== TIPOS DE MÁQUINA ==========
    def _configurar_tab_tipos_maquina(self):
        """Configura la pestaña de tipos de máquina"""
        self.tab_tipos_maquina.grid_rowconfigure(1, weight=1)
        self.tab_tipos_maquina.grid_columnconfigure(0, weight=1)

        frame_controles = ctk.CTkFrame(self.tab_tipos_maquina, fg_color="transparent")
        frame_controles.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            frame_controles,
            text="+ Nuevo Tipo",
            command=self._dialogo_tipo_maquina,
            fg_color=COLOR_SUCCESS,
            width=150,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_controles,
            text="🔄 Actualizar",
            command=self._cargar_tipos_maquina,
            width=120,
            height=35
        ).pack(side="left", padx=5)

        self.scroll_tipos_maquina = ctk.CTkScrollableFrame(self.tab_tipos_maquina)
        self.scroll_tipos_maquina.grid(row=1, column=0, sticky="nsew")
        self.scroll_tipos_maquina.grid_columnconfigure(0, weight=1)

        self._cargar_tipos_maquina()

    def _cargar_tipos_maquina(self):
        """Carga los tipos de máquina"""
        for widget in self.scroll_tipos_maquina.winfo_children():
            widget.destroy()

        tipos = consultas.obtener_tipos_maquina()

        if not tipos:
            ctk.CTkLabel(
                self.scroll_tipos_maquina,
                text="No hay tipos registrados",
                text_color="gray"
            ).pack(pady=20)
            return

        frame_header = ctk.CTkFrame(self.scroll_tipos_maquina, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame_header, text="Nombre del Tipo", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=0, padx=10, pady=8)
        ctk.CTkLabel(frame_header, text="Acciones", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=1, padx=10, pady=8)

        for idx, tipo in enumerate(tipos):
            self._crear_fila_tipo_maquina(tipo, idx + 1)

    def _crear_fila_tipo_maquina(self, tipo, fila):
        """Crea una fila para un tipo de máquina"""
        fg_color = "gray25" if fila % 2 == 0 else "gray20"
        frame_fila = ctk.CTkFrame(self.scroll_tipos_maquina, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame_fila, text=tipo['nombre_tipo'], font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=8)

        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda t=tipo: self._dialogo_tipo_maquina(t),
            width=60,
            height=28,
            fg_color=COLOR_PRIMARY
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            frame_acciones,
            text="Eliminar",
            command=lambda t=tipo: self._eliminar_tipo_maquina(t),
            width=70,
            height=28,
            fg_color=COLOR_DANGER
        ).pack(side="left", padx=2)

    def _dialogo_tipo_maquina(self, tipo=None):
        """Diálogo para crear/editar tipo de máquina"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Tipo" if tipo is None else "Editar Tipo")
        dialogo.geometry("400x200")
        dialogo.transient(self)
        dialogo.grab_set()

        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (200 // 2)
        dialogo.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialogo, text="Nombre del Tipo:", font=ctk.CTkFont(size=12)).pack(pady=(30, 5))
        entry_nombre = ctk.CTkEntry(dialogo, width=300, placeholder_text="Ej: Gran Formato, Láser, UV")
        entry_nombre.pack(pady=5)
        if tipo:
            entry_nombre.insert(0, tipo['nombre_tipo'])

        def guardar():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Validación", "Ingrese un nombre")
                return
            try:
                if tipo:
                    consultas.actualizar_tipo_maquina(tipo['id_tipo_maquina'], nombre)
                    messagebox.showinfo("Éxito", "Tipo actualizado")
                else:
                    consultas.guardar_tipo_maquina(nombre)
                    messagebox.showinfo("Éxito", "Tipo creado")
                dialogo.destroy()
                self._cargar_tipos_maquina()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialogo, text="💾 Guardar", command=guardar, fg_color=COLOR_SUCCESS, height=40).pack(pady=20)

    def _eliminar_tipo_maquina(self, tipo):
        """Elimina un tipo de máquina"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar el tipo '{tipo['nombre_tipo']}'?"):
            try:
                consultas.eliminar_tipo_maquina(tipo['id_tipo_maquina'])
                messagebox.showinfo("Éxito", "Tipo eliminado")
                self._cargar_tipos_maquina()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ========== TIPOS DE MATERIAL ==========
    def _configurar_tab_tipos_material(self):
        """Configura la pestaña de tipos de material"""
        self.tab_tipos_material.grid_rowconfigure(1, weight=1)
        self.tab_tipos_material.grid_columnconfigure(0, weight=1)

        frame_controles = ctk.CTkFrame(self.tab_tipos_material, fg_color="transparent")
        frame_controles.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            frame_controles,
            text="+ Nuevo Tipo",
            command=self._dialogo_tipo_material,
            fg_color=COLOR_SUCCESS,
            width=150,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_controles,
            text="🔄 Actualizar",
            command=self._cargar_tipos_material,
            width=120,
            height=35
        ).pack(side="left", padx=5)

        self.scroll_tipos_material = ctk.CTkScrollableFrame(self.tab_tipos_material)
        self.scroll_tipos_material.grid(row=1, column=0, sticky="nsew")
        self.scroll_tipos_material.grid_columnconfigure(0, weight=1)

        self._cargar_tipos_material()

    def _cargar_tipos_material(self):
        """Carga los tipos de material"""
        for widget in self.scroll_tipos_material.winfo_children():
            widget.destroy()

        tipos = consultas.obtener_tipos_material()

        if not tipos:
            ctk.CTkLabel(
                self.scroll_tipos_material,
                text="No hay tipos registrados",
                text_color="gray"
            ).pack(pady=20)
            return

        frame_header = ctk.CTkFrame(self.scroll_tipos_material, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame_header, text="Nombre del Tipo", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=0, padx=10, pady=8)
        ctk.CTkLabel(frame_header, text="Acciones", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=1, padx=10, pady=8)

        for idx, tipo in enumerate(tipos):
            self._crear_fila_tipo_material(tipo, idx + 1)

    def _crear_fila_tipo_material(self, tipo, fila):
        """Crea una fila para un tipo de material"""
        fg_color = "gray25" if fila % 2 == 0 else "gray20"
        frame_fila = ctk.CTkFrame(self.scroll_tipos_material, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame_fila, text=tipo['nombre_tipo'], font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=8)

        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda t=tipo: self._dialogo_tipo_material(t),
            width=60,
            height=28,
            fg_color=COLOR_PRIMARY
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            frame_acciones,
            text="Eliminar",
            command=lambda t=tipo: self._eliminar_tipo_material(t),
            width=70,
            height=28,
            fg_color=COLOR_DANGER
        ).pack(side="left", padx=2)

    def _dialogo_tipo_material(self, tipo=None):
        """Diálogo para crear/editar tipo de material"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Tipo" if tipo is None else "Editar Tipo")
        dialogo.geometry("400x200")
        dialogo.transient(self)
        dialogo.grab_set()

        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (200 // 2)
        dialogo.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialogo, text="Nombre del Tipo:", font=ctk.CTkFont(size=12)).pack(pady=(30, 5))
        entry_nombre = ctk.CTkEntry(dialogo, width=300, placeholder_text="Ej: Papel, Vinilo, Lona, Tinta")
        entry_nombre.pack(pady=5)
        if tipo:
            entry_nombre.insert(0, tipo['nombre_tipo'])

        def guardar():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("Validación", "Ingrese un nombre")
                return
            try:
                if tipo:
                    consultas.actualizar_tipo_material(tipo['id_tipo_material'], nombre)
                    messagebox.showinfo("Éxito", "Tipo actualizado")
                else:
                    consultas.guardar_tipo_material(nombre)
                    messagebox.showinfo("Éxito", "Tipo creado")
                dialogo.destroy()
                self._cargar_tipos_material()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialogo, text="💾 Guardar", command=guardar, fg_color=COLOR_SUCCESS, height=40).pack(pady=20)

    def _eliminar_tipo_material(self, tipo):
        """Elimina un tipo de material"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar el tipo '{tipo['nombre_tipo']}'?"):
            try:
                consultas.eliminar_tipo_material(tipo['id_tipo_material'])
                messagebox.showinfo("Éxito", "Tipo eliminado")
                self._cargar_tipos_material()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ========== ESTADOS DE PEDIDO ==========
    def _configurar_tab_estados(self):
        """Configura la pestaña de estados de pedido"""
        self.tab_estados.grid_rowconfigure(1, weight=1)
        self.tab_estados.grid_columnconfigure(0, weight=1)

        frame_controles = ctk.CTkFrame(self.tab_estados, fg_color="transparent")
        frame_controles.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            frame_controles,
            text="+ Nuevo Estado",
            command=self._dialogo_estado,
            fg_color=COLOR_SUCCESS,
            width=150,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_controles,
            text="🔄 Actualizar",
            command=self._cargar_estados,
            width=120,
            height=35
        ).pack(side="left", padx=5)

        self.scroll_estados = ctk.CTkScrollableFrame(self.tab_estados)
        self.scroll_estados.grid(row=1, column=0, sticky="nsew")
        self.scroll_estados.grid_columnconfigure(0, weight=1)

        self._cargar_estados()

    def _cargar_estados(self):
        """Carga los estados de pedido"""
        for widget in self.scroll_estados.winfo_children():
            widget.destroy()

        estados = consultas.obtener_estados_pedidos()

        if not estados:
            ctk.CTkLabel(
                self.scroll_estados,
                text="No hay estados registrados",
                text_color="gray"
            ).pack(pady=20)
            return

        frame_header = ctk.CTkFrame(self.scroll_estados, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(frame_header, text="Nombre", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=0, padx=10, pady=8)
        ctk.CTkLabel(frame_header, text="Color", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=1, padx=10, pady=8)
        ctk.CTkLabel(frame_header, text="Acciones", font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=2, padx=10, pady=8)

        for idx, estado in enumerate(estados):
            self._crear_fila_estado(estado, idx + 1)

    def _crear_fila_estado(self, estado, fila):
        """Crea una fila para un estado"""
        fg_color = "gray25" if fila % 2 == 0 else "gray20"
        frame_fila = ctk.CTkFrame(self.scroll_estados, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(frame_fila, text=estado['nombre'], font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=10, pady=8)

        # Muestra de color
        frame_color = ctk.CTkFrame(frame_fila, fg_color=estado.get('color', '#808080'), width=60, height=25, corner_radius=5)
        frame_color.grid(row=0, column=1, padx=10, pady=8)

        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda e=estado: self._dialogo_estado(e),
            width=60,
            height=28,
            fg_color=COLOR_PRIMARY
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            frame_acciones,
            text="Eliminar",
            command=lambda e=estado: self._eliminar_estado(e),
            width=70,
            height=28,
            fg_color=COLOR_DANGER
        ).pack(side="left", padx=2)

    def _dialogo_estado(self, estado=None):
        """Diálogo para crear/editar estado"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Estado" if estado is None else "Editar Estado")
        dialogo.geometry("400x280")
        dialogo.transient(self)
        dialogo.grab_set()

        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (280 // 2)
        dialogo.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialogo, text="Nombre del Estado:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        entry_nombre = ctk.CTkEntry(dialogo, width=300, placeholder_text="Ej: En Producción, Entregado")
        entry_nombre.pack(pady=5)
        if estado:
            entry_nombre.insert(0, estado['nombre'])

        # Selector de color
        color_actual = estado.get('color', '#3498db') if estado else '#3498db'
        color_var = tk.StringVar(value=color_actual)

        ctk.CTkLabel(dialogo, text="Color del Estado:", font=ctk.CTkFont(size=12)).pack(pady=(15, 5))
        
        frame_color = ctk.CTkFrame(dialogo, fg_color="transparent")
        frame_color.pack(pady=5)

        muestra_color = ctk.CTkFrame(frame_color, fg_color=color_actual, width=80, height=30, corner_radius=5)
        muestra_color.pack(side="left", padx=10)

        def elegir_color():
            color = colorchooser.askcolor(title="Seleccionar Color", color=color_var.get())
            if color[1]:
                color_var.set(color[1])
                muestra_color.configure(fg_color=color[1])

        ctk.CTkButton(
            frame_color,
            text="🎨 Elegir",
            command=elegir_color,
            width=80,
            height=30
        ).pack(side="left", padx=5)

        def guardar():
            nombre = entry_nombre.get().strip()
            color = color_var.get()
            if not nombre:
                messagebox.showwarning("Validación", "Ingrese un nombre")
                return
            try:
                if estado:
                    consultas.actualizar_estado_pedido(estado['id'], nombre, color)
                    messagebox.showinfo("Éxito", "Estado actualizado")
                else:
                    consultas.guardar_estado_pedido(nombre, color)
                    messagebox.showinfo("Éxito", "Estado creado")
                dialogo.destroy()
                self._cargar_estados()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialogo, text="💾 Guardar", command=guardar, fg_color=COLOR_SUCCESS, height=40).pack(pady=25)

    def _eliminar_estado(self, estado):
        """Elimina un estado de pedido"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar el estado '{estado['nombre']}'?"):
            try:
                consultas.eliminar_estado_pedido(estado['id'])
                messagebox.showinfo("Éxito", "Estado eliminado")
                self._cargar_estados()
            except Exception as e:
                messagebox.showerror("Error", str(e))
