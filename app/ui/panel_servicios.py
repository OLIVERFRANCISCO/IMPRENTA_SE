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

        btn_editar = ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda s=servicio: self._editar_servicio(s),
            width=80,
            height=30,
            fg_color=COLOR_PRIMARY
        )
        btn_editar.pack(side="left", padx=2)

        btn_eliminar = ctk.CTkButton(
            frame_acciones,
            text="Eliminar",
            command=lambda s=servicio: self._confirmar_eliminar_servicio(s),
            width=80,
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
        combo_unidad = ctk.CTkComboBox(dialogo, values=["m2", "cm2", "unidad", "ciento", "docena", "metro", "hora"], width=450)
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
            text="Sí, Eliminar",
            command=eliminar,
            width=120,
            height=40,
            fg_color=COLOR_DANGER
        )
        btn_confirmar.pack(side="left", padx=10)

