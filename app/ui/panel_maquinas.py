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

        btn_editar = ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda m=maquina: self._mostrar_dialogo_maquina(m),
            width=80,
            height=30,
            fg_color=COLOR_PRIMARY
        )
        btn_editar.pack(side="left", padx=2)

        btn_eliminar = ctk.CTkButton(
            frame_acciones,
            text="Eliminar",
            command=lambda m=maquina: self._confirmar_eliminar_maquina(m),
            width=80,
            height=30,
            fg_color=COLOR_DANGER
        )
        btn_eliminar.pack(side="left", padx=2)

    def _mostrar_dialogo_maquina(self, maquina=None):
        """Muestra diálogo para agregar o editar máquina"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nueva Máquina" if maquina is None else "Editar Máquina")
        dialogo.geometry("500x350")
        dialogo.transient(self)
        dialogo.grab_set()

        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (350 // 2)
        dialogo.geometry(f"+{x}+{y}")

        # Contenedor para campos
        frame_campos = ctk.CTkFrame(dialogo)
        frame_campos.pack(fill="both", expand=True, padx=20, pady=20)

        # Campos
        ctk.CTkLabel(frame_campos, text="Nombre de la Máquina:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        entry_nombre = ctk.CTkEntry(frame_campos, width=400)
        entry_nombre.pack(pady=5)
        if maquina:
            entry_nombre.insert(0, maquina['nombre'])

        ctk.CTkLabel(frame_campos, text="Tipo de Máquina:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        combo_tipo = ctk.CTkComboBox(
            frame_campos,
            values=["Pequeño Formato", "Gran Formato", "Acabado", "Sublimación", "Láser"],
            width=400
        )
        combo_tipo.pack(pady=5)
        if maquina:
            combo_tipo.set(maquina['tipo'])
        else:
            combo_tipo.set("Pequeño Formato")

        # Frame de botones
        frame_botones = ctk.CTkFrame(dialogo)
        frame_botones.pack(fill="x", padx=20, pady=10)

        def guardar():
            nombre = entry_nombre.get().strip()
            tipo = combo_tipo.get()

            if not nombre:
                messagebox.showwarning("Validación", "Debe ingresar un nombre")
                return

            try:
                if maquina:
                    consultas.actualizar_maquina(
                        maquina['id_maquina'],
                        nombre, tipo
                    )
                    messagebox.showinfo("Éxito", "Máquina actualizada correctamente")
                else:
                    consultas.guardar_maquina(nombre, tipo)
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

