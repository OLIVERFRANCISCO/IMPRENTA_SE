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

        # Crear pestañas (tipos_material NO se configura desde aquí)
        self.tab_unidades = self.tabview.add("📏 Unidades")
        self.tab_tipos_maquina = self.tabview.add("🔧 Tipos Máquina")
        self.tab_estados = self.tabview.add("📋 Estados Pedido")
        self.tab_precios = self.tabview.add("💰 Precios Escalonados")
        self.tab_restricciones = self.tabview.add("🔢 Restricciones")

        # Configurar cada pestaña
        self._configurar_tab_unidades()
        self._configurar_tab_tipos_maquina()
        self._configurar_tab_estados()
        self._configurar_tab_precios()
        self._configurar_tab_restricciones()


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

    # ========== PRECIOS ESCALONADOS ==========
    def _configurar_tab_precios(self):
        """Configura la pestaña de precios escalonados"""
        self.tab_precios.grid_rowconfigure(2, weight=1)
        self.tab_precios.grid_columnconfigure(0, weight=1)

        # Descripción
        ctk.CTkLabel(
            self.tab_precios,
            text="💡 Configure precios por cantidad. Ej: Tazas: 1-9 = S/25, 10-99 = S/20, 100+ = S/8",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 10))

        frame_controles = ctk.CTkFrame(self.tab_precios, fg_color="transparent")
        frame_controles.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            frame_controles,
            text="+ Nuevo Precio",
            command=self._dialogo_precio,
            fg_color=COLOR_SUCCESS,
            width=150,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_controles,
            text="🔄 Actualizar",
            command=self._cargar_precios,
            width=120,
            height=35
        ).pack(side="left", padx=5)

        self.scroll_precios = ctk.CTkScrollableFrame(self.tab_precios)
        self.scroll_precios.grid(row=2, column=0, sticky="nsew")
        self.scroll_precios.grid_columnconfigure(0, weight=1)

        self._cargar_precios()

    def _cargar_precios(self):
        """Carga los precios escalonados"""
        for widget in self.scroll_precios.winfo_children():
            widget.destroy()

        precios = consultas.obtener_precios_escalonados()

        if not precios:
            ctk.CTkLabel(
                self.scroll_precios,
                text="No hay precios escalonados configurados.\nEjemplo: Para 'Tazas' configure S/25 (1-9), S/20 (10-99), S/8 (100+)",
                text_color="gray"
            ).pack(pady=20)
            return

        frame_header = ctk.CTkFrame(self.scroll_precios, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        headers = ["Servicio", "Desde", "Hasta", "Precio Unit.", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(frame_header, text=header, font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=i, padx=10, pady=8)

        for idx, precio in enumerate(precios):
            self._crear_fila_precio(precio, idx + 1)

    def _crear_fila_precio(self, precio, fila):
        """Crea una fila para un precio escalonado"""
        fg_color = "gray25" if fila % 2 == 0 else "gray20"
        frame_fila = ctk.CTkFrame(self.scroll_precios, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(frame_fila, text=precio.get('nombre_servicio', 'N/A')).grid(row=0, column=0, padx=10, pady=8)
        ctk.CTkLabel(frame_fila, text=str(precio['cantidad_minima'])).grid(row=0, column=1, padx=10, pady=8)
        ctk.CTkLabel(frame_fila, text=str(precio['cantidad_maxima']) if precio['cantidad_maxima'] else "∞").grid(row=0, column=2, padx=10, pady=8)
        ctk.CTkLabel(frame_fila, text=f"S/ {precio['precio_unitario']:.2f}", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=8)

        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=4, padx=5, pady=5)

        ctk.CTkButton(frame_acciones, text="Editar", command=lambda p=precio: self._dialogo_precio(p), width=60, height=28, fg_color=COLOR_PRIMARY).pack(side="left", padx=2)
        ctk.CTkButton(frame_acciones, text="Eliminar", command=lambda p=precio: self._eliminar_precio(p), width=70, height=28, fg_color=COLOR_DANGER).pack(side="left", padx=2)

    def _dialogo_precio(self, precio=None):
        """Diálogo para crear/editar precio escalonado"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Precio Escalonado" if precio is None else "Editar Precio")
        dialogo.geometry("500x400")
        dialogo.transient(self)
        dialogo.grab_set()

        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (400 // 2)
        dialogo.geometry(f"+{x}+{y}")

        # Servicio
        ctk.CTkLabel(dialogo, text="Servicio:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        servicios = consultas.obtener_servicios()
        servicios_dict = {s['nombre_servicio']: s['id_servicio'] for s in servicios}
        servicios_nombres = list(servicios_dict.keys())
        
        combo_servicio = ctk.CTkComboBox(dialogo, values=servicios_nombres if servicios_nombres else ["Sin servicios"], width=400)
        combo_servicio.pack(pady=5)
        
        if precio and precio.get('nombre_servicio'):
            combo_servicio.set(precio['nombre_servicio'])
        elif servicios_nombres:
            combo_servicio.set(servicios_nombres[0])

        # Cantidad mínima
        ctk.CTkLabel(dialogo, text="Cantidad Mínima:", font=ctk.CTkFont(size=12)).pack(pady=(15, 5))
        entry_min = ctk.CTkEntry(dialogo, width=400, placeholder_text="Ej: 1")
        entry_min.pack(pady=5)
        if precio:
            entry_min.insert(0, str(precio['cantidad_minima']))

        # Cantidad máxima
        ctk.CTkLabel(dialogo, text="Cantidad Máxima (vacío = sin límite):", font=ctk.CTkFont(size=12)).pack(pady=(15, 5))
        entry_max = ctk.CTkEntry(dialogo, width=400, placeholder_text="Ej: 99 (vacío = infinito)")
        entry_max.pack(pady=5)
        if precio and precio['cantidad_maxima']:
            entry_max.insert(0, str(precio['cantidad_maxima']))

        # Precio unitario
        ctk.CTkLabel(dialogo, text="Precio Unitario (S/):", font=ctk.CTkFont(size=12)).pack(pady=(15, 5))
        entry_precio = ctk.CTkEntry(dialogo, width=400, placeholder_text="Ej: 25.00")
        entry_precio.pack(pady=5)
        if precio:
            entry_precio.insert(0, str(precio['precio_unitario']))

        def guardar():
            try:
                servicio_nombre = combo_servicio.get()
                id_servicio = servicios_dict.get(servicio_nombre)
                cant_min = int(entry_min.get())
                cant_max = int(entry_max.get()) if entry_max.get().strip() else None
                precio_unit = float(entry_precio.get())

                if not id_servicio:
                    messagebox.showwarning("Validación", "Seleccione un servicio")
                    return

                if precio:
                    consultas.actualizar_precio_escalonado(precio['id'], cant_min, cant_max, precio_unit)
                    messagebox.showinfo("Éxito", "Precio actualizado")
                else:
                    consultas.guardar_precio_escalonado(id_servicio, cant_min, cant_max, precio_unit)
                    messagebox.showinfo("Éxito", "Precio creado")
                dialogo.destroy()
                self._cargar_precios()
            except ValueError:
                messagebox.showerror("Error", "Verifique los valores numéricos")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialogo, text="💾 Guardar", command=guardar, fg_color=COLOR_SUCCESS, height=40).pack(pady=25)

    def _eliminar_precio(self, precio):
        """Elimina un precio escalonado"""
        if messagebox.askyesno("Confirmar", "¿Eliminar este precio escalonado?"):
            try:
                consultas.eliminar_precio_escalonado(precio['id'])
                messagebox.showinfo("Éxito", "Precio eliminado")
                self._cargar_precios()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # ========== RESTRICCIONES DE CANTIDAD ==========
    def _configurar_tab_restricciones(self):
        """Configura la pestaña de restricciones de cantidad"""
        self.tab_restricciones.grid_rowconfigure(2, weight=1)
        self.tab_restricciones.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.tab_restricciones,
            text="💡 Configure qué cantidades son válidas. Ej: Llaveros solo 25, 50, 100, 200...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 10))

        frame_controles = ctk.CTkFrame(self.tab_restricciones, fg_color="transparent")
        frame_controles.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkButton(
            frame_controles,
            text="+ Nueva Restricción",
            command=self._dialogo_restriccion,
            fg_color=COLOR_SUCCESS,
            width=160,
            height=35
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_controles,
            text="🔄 Actualizar",
            command=self._cargar_restricciones,
            width=120,
            height=35
        ).pack(side="left", padx=5)

        self.scroll_restricciones = ctk.CTkScrollableFrame(self.tab_restricciones)
        self.scroll_restricciones.grid(row=2, column=0, sticky="nsew")
        self.scroll_restricciones.grid_columnconfigure(0, weight=1)

        self._cargar_restricciones()

    def _cargar_restricciones(self):
        """Carga las restricciones de cantidad"""
        for widget in self.scroll_restricciones.winfo_children():
            widget.destroy()

        restricciones = consultas.obtener_restricciones_cantidad()

        if not restricciones:
            ctk.CTkLabel(
                self.scroll_restricciones,
                text="No hay restricciones configuradas.\nEjemplo: 'Llaveros' solo permite 25, 50, 100, 200...",
                text_color="gray"
            ).pack(pady=20)
            return

        frame_header = ctk.CTkFrame(self.scroll_restricciones, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3), weight=1)

        headers = ["Servicio", "Tipo", "Configuración", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(frame_header, text=header, font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=i, padx=10, pady=8)

        for idx, restriccion in enumerate(restricciones):
            self._crear_fila_restriccion(restriccion, idx + 1)

    def _crear_fila_restriccion(self, restriccion, fila):
        """Crea una fila para una restricción"""
        fg_color = "gray25" if fila % 2 == 0 else "gray20"
        frame_fila = ctk.CTkFrame(self.scroll_restricciones, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(frame_fila, text=restriccion.get('nombre_servicio', 'N/A')).grid(row=0, column=0, padx=10, pady=8)
        
        tipo = restriccion['tipo_restriccion']
        tipo_texto = {"lista": "📋 Lista", "multiplo": "🔢 Múltiplo", "rango": "↔️ Rango"}.get(tipo, tipo)
        ctk.CTkLabel(frame_fila, text=tipo_texto).grid(row=0, column=1, padx=10, pady=8)

        # Mostrar configuración según tipo
        if tipo == "lista":
            vals = restriccion.get('valores_permitidos', '')
            config = (vals[:20] + "...") if len(vals) > 20 else vals
        elif tipo == "multiplo":
            config = f"×{restriccion.get('multiplo_base', '')} desde {restriccion.get('multiplo_desde', '')}"
        else:
            config = f"{restriccion.get('cantidad_minima', '')}-{restriccion.get('cantidad_maxima', '')}"
        
        ctk.CTkLabel(frame_fila, text=config, font=ctk.CTkFont(size=11)).grid(row=0, column=2, padx=10, pady=8)

        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkButton(frame_acciones, text="Editar", command=lambda r=restriccion: self._dialogo_restriccion(r), width=60, height=28, fg_color=COLOR_PRIMARY).pack(side="left", padx=2)
        ctk.CTkButton(frame_acciones, text="Eliminar", command=lambda r=restriccion: self._eliminar_restriccion(r), width=70, height=28, fg_color=COLOR_DANGER).pack(side="left", padx=2)

    def _dialogo_restriccion(self, restriccion=None):
        """Diálogo para crear/editar restricción de cantidad"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nueva Restricción" if restriccion is None else "Editar Restricción")
        dialogo.geometry("550x500")
        dialogo.transient(self)
        dialogo.grab_set()

        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (500 // 2)
        dialogo.geometry(f"+{x}+{y}")

        scroll = ctk.CTkScrollableFrame(dialogo)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Servicio
        ctk.CTkLabel(scroll, text="Servicio:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5), anchor="w")
        servicios = consultas.obtener_servicios()
        servicios_dict = {s['nombre_servicio']: s['id_servicio'] for s in servicios}
        servicios_nombres = list(servicios_dict.keys())
        
        combo_servicio = ctk.CTkComboBox(scroll, values=servicios_nombres if servicios_nombres else ["Sin servicios"], width=450)
        combo_servicio.pack(pady=5, anchor="w")
        
        if restriccion and restriccion.get('nombre_servicio'):
            combo_servicio.set(restriccion['nombre_servicio'])
        elif servicios_nombres:
            combo_servicio.set(servicios_nombres[0])

        # Tipo de restricción
        ctk.CTkLabel(scroll, text="Tipo de Restricción:", font=ctk.CTkFont(size=12)).pack(pady=(15, 5), anchor="w")
        tipo_var = tk.StringVar(value=restriccion['tipo_restriccion'] if restriccion else 'lista')
        
        frame_tipos = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_tipos.pack(pady=5, anchor="w")
        
        ctk.CTkRadioButton(frame_tipos, text="📋 Lista", variable=tipo_var, value="lista").pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_tipos, text="🔢 Múltiplo", variable=tipo_var, value="multiplo").pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_tipos, text="↔️ Rango", variable=tipo_var, value="rango").pack(side="left", padx=10)

        # Frame para campos de LISTA
        frame_lista = ctk.CTkFrame(scroll, fg_color="gray20", corner_radius=10)
        ctk.CTkLabel(frame_lista, text="Valores (separados por coma):", font=ctk.CTkFont(size=11)).pack(pady=(10, 5), padx=10, anchor="w")
        entry_valores = ctk.CTkEntry(frame_lista, width=430, placeholder_text="Ej: 25, 50")
        entry_valores.pack(pady=5, padx=10)
        
        ctk.CTkLabel(frame_lista, text="+ Múltiplos de (opcional):", font=ctk.CTkFont(size=11)).pack(pady=(10, 5), padx=10, anchor="w")
        entry_mult_lista = ctk.CTkEntry(frame_lista, width=150, placeholder_text="Ej: 100")
        entry_mult_lista.pack(pady=5, padx=10, anchor="w")
        
        ctk.CTkLabel(frame_lista, text="Múltiplos desde:", font=ctk.CTkFont(size=11)).pack(pady=(5, 5), padx=10, anchor="w")
        entry_mult_desde = ctk.CTkEntry(frame_lista, width=150, placeholder_text="Ej: 100")
        entry_mult_desde.pack(pady=(0, 10), padx=10, anchor="w")

        # Frame para campos de MULTIPLO
        frame_multiplo = ctk.CTkFrame(scroll, fg_color="gray20", corner_radius=10)
        ctk.CTkLabel(frame_multiplo, text="Múltiplo base:", font=ctk.CTkFont(size=11)).pack(pady=(10, 5), padx=10, anchor="w")
        entry_multiplo = ctk.CTkEntry(frame_multiplo, width=150, placeholder_text="Ej: 100")
        entry_multiplo.pack(pady=5, padx=10, anchor="w")
        
        ctk.CTkLabel(frame_multiplo, text="Cantidad mínima:", font=ctk.CTkFont(size=11)).pack(pady=(10, 5), padx=10, anchor="w")
        entry_min_mult = ctk.CTkEntry(frame_multiplo, width=150, placeholder_text="Ej: 100")
        entry_min_mult.pack(pady=(0, 10), padx=10, anchor="w")

        # Frame para campos de RANGO
        frame_rango = ctk.CTkFrame(scroll, fg_color="gray20", corner_radius=10)
        ctk.CTkLabel(frame_rango, text="Cantidad mínima:", font=ctk.CTkFont(size=11)).pack(pady=(10, 5), padx=10, anchor="w")
        entry_min_rango = ctk.CTkEntry(frame_rango, width=150, placeholder_text="Ej: 10")
        entry_min_rango.pack(pady=5, padx=10, anchor="w")
        
        ctk.CTkLabel(frame_rango, text="Cantidad máxima:", font=ctk.CTkFont(size=11)).pack(pady=(10, 5), padx=10, anchor="w")
        entry_max_rango = ctk.CTkEntry(frame_rango, width=150, placeholder_text="Ej: 1000")
        entry_max_rango.pack(pady=(0, 10), padx=10, anchor="w")

        # Prellenar valores si es edición
        if restriccion:
            if restriccion.get('valores_permitidos'):
                entry_valores.insert(0, restriccion['valores_permitidos'])
            if restriccion.get('multiplo_base'):
                entry_mult_lista.insert(0, str(restriccion['multiplo_base']))
                entry_multiplo.insert(0, str(restriccion['multiplo_base']))
            if restriccion.get('multiplo_desde'):
                entry_mult_desde.insert(0, str(restriccion['multiplo_desde']))
                entry_min_mult.insert(0, str(restriccion['multiplo_desde']))
            if restriccion.get('cantidad_minima'):
                entry_min_rango.insert(0, str(restriccion['cantidad_minima']))
            if restriccion.get('cantidad_maxima'):
                entry_max_rango.insert(0, str(restriccion['cantidad_maxima']))

        def cambiar_tipo(*args):
            frame_lista.pack_forget()
            frame_multiplo.pack_forget()
            frame_rango.pack_forget()
            
            if tipo_var.get() == "lista":
                frame_lista.pack(pady=10, fill="x")
            elif tipo_var.get() == "multiplo":
                frame_multiplo.pack(pady=10, fill="x")
            else:
                frame_rango.pack(pady=10, fill="x")

        tipo_var.trace_add("write", cambiar_tipo)
        cambiar_tipo()

        def guardar():
            try:
                servicio_nombre = combo_servicio.get()
                id_servicio = servicios_dict.get(servicio_nombre)
                tipo = tipo_var.get()

                if not id_servicio:
                    messagebox.showwarning("Validación", "Seleccione un servicio")
                    return

                valores_permitidos = None
                multiplo_base = None
                multiplo_desde = None
                cantidad_minima = None
                cantidad_maxima = None

                if tipo == "lista":
                    valores_permitidos = entry_valores.get().strip()
                    if entry_mult_lista.get().strip():
                        multiplo_base = int(entry_mult_lista.get())
                    if entry_mult_desde.get().strip():
                        multiplo_desde = int(entry_mult_desde.get())
                elif tipo == "multiplo":
                    multiplo_base = int(entry_multiplo.get())
                    multiplo_desde = int(entry_min_mult.get()) if entry_min_mult.get().strip() else multiplo_base
                else:
                    cantidad_minima = int(entry_min_rango.get())
                    cantidad_maxima = int(entry_max_rango.get())

                if restriccion:
                    consultas.actualizar_restriccion_cantidad(
                        restriccion['id'], tipo, valores_permitidos,
                        multiplo_base, multiplo_desde, cantidad_minima, cantidad_maxima, None
                    )
                    messagebox.showinfo("Éxito", "Restricción actualizada")
                else:
                    consultas.guardar_restriccion_cantidad(
                        id_servicio, tipo, valores_permitidos,
                        multiplo_base, multiplo_desde, cantidad_minima, cantidad_maxima, None
                    )
                    messagebox.showinfo("Éxito", "Restricción creada")
                dialogo.destroy()
                self._cargar_restricciones()
            except ValueError:
                messagebox.showerror("Error", "Verifique los valores numéricos")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(scroll, text="💾 Guardar", command=guardar, fg_color=COLOR_SUCCESS, height=40, width=150).pack(pady=20)

    def _eliminar_restriccion(self, restriccion):
        """Elimina una restricción de cantidad"""
        if messagebox.askyesno("Confirmar", "¿Eliminar esta restricción?"):
            try:
                consultas.eliminar_restriccion_cantidad(restriccion['id'])
                messagebox.showinfo("Éxito", "Restricción eliminada")
                self._cargar_restricciones()
            except Exception as e:
                messagebox.showerror("Error", str(e))
