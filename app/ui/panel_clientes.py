"""
Panel de gestión de clientes
Permite ver, agregar y editar clientes
"""
import customtkinter as ctk
from tkinter import messagebox
from app.config import (
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS
)
from app.database import consultas


class PanelClientes(ctk.CTkFrame):
    """Panel para gestionar clientes"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título y botones
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        self.titulo = ctk.CTkLabel(
            frame_titulo,
            text="Gestión de Clientes",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.titulo.pack(side="left")

        self.btn_nuevo_cliente = ctk.CTkButton(
            frame_titulo,
            text="+ Nuevo Cliente",
            command=self._mostrar_dialogo_cliente,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS,
            width=180
        )
        self.btn_nuevo_cliente.pack(side="right", padx=10)

        self.btn_actualizar = ctk.CTkButton(
            frame_titulo,
            text="Actualizar",
            command=self._cargar_clientes,
            height=40,
            width=140
        )
        self.btn_actualizar.pack(side="right")

        # Buscador
        frame_buscar = ctk.CTkFrame(self, fg_color="transparent")
        frame_buscar.grid(row=1, column=0, pady=(0, 10), sticky="ew")

        self.entry_buscar = ctk.CTkEntry(
            frame_buscar,
            placeholder_text="Buscar cliente...",
            width=400,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_buscar.pack(side="left", padx=10)
        self.entry_buscar.bind("<KeyRelease>", self._filtrar_clientes)

        # Contenedor scrollable
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=2, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self._cargar_clientes()

    def _cargar_clientes(self):
        """Carga y muestra todos los clientes"""
        # Limpiar frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obtener clientes
        self.clientes = consultas.obtener_clientes()

        if not self.clientes:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No hay clientes registrados",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            ).pack(pady=50)
            return

        # Crear encabezados
        frame_header = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        headers = ["ID", "Nombre Completo", "Teléfono", "Email", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                frame_header,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=10)

        # Mostrar clientes
        for idx, cliente in enumerate(self.clientes):
            self._crear_fila_cliente(cliente, idx + 1)

    def _crear_fila_cliente(self, cliente, fila):
        """Crea una fila con los datos del cliente"""
        fg_color = "gray25" if fila % 2 == 0 else "gray20"

        frame_fila = ctk.CTkFrame(self.scroll_frame, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # ID
        ctk.CTkLabel(
            frame_fila,
            text=str(cliente['id_cliente']),
            font=ctk.CTkFont(size=12)
        ).grid(row=0, column=0, padx=10, pady=10)

        # Nombre
        ctk.CTkLabel(
            frame_fila,
            text=cliente['nombre_completo'],
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Teléfono
        ctk.CTkLabel(
            frame_fila,
            text=cliente['telefono'] or "-"
        ).grid(row=0, column=2, padx=10, pady=10)

        # Email
        ctk.CTkLabel(
            frame_fila,
            text=cliente['email'] or "-"
        ).grid(row=0, column=3, padx=10, pady=10)

        # Botones
        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=4, padx=10, pady=5)

        btn_editar = ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda c=cliente: self._editar_cliente(c),
            width=80,
            height=30,
            fg_color=COLOR_PRIMARY
        )
        btn_editar.pack(side="left", padx=2)

        btn_pedidos = ctk.CTkButton(
            frame_acciones,
            text="Pedidos",
            command=lambda c=cliente: self._ver_pedidos_cliente(c),
            width=90,
            height=30,
            fg_color=COLOR_SECONDARY
        )
        btn_pedidos.pack(side="left", padx=2)

    def _filtrar_clientes(self, event=None):
        """Filtra clientes según el texto de búsqueda"""
        busqueda = self.entry_buscar.get().lower()

        # Limpiar tabla
        for widget in self.scroll_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        # Filtrar y mostrar
        clientes_filtrados = [
            c for c in self.clientes
            if busqueda in c['nombre_completo'].lower() or
               busqueda in (c['telefono'] or "").lower() or
               busqueda in (c['email'] or "").lower()
        ]

        for idx, cliente in enumerate(clientes_filtrados):
            self._crear_fila_cliente(cliente, idx)

    def _mostrar_dialogo_cliente(self, cliente=None):
        """Muestra diálogo para agregar o editar cliente"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Cliente" if cliente is None else "Editar Cliente")
        dialogo.geometry("500x400")
        dialogo.transient(self)
        dialogo.grab_set()

        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (400 // 2)
        dialogo.geometry(f"+{x}+{y}")

        # Campos
        ctk.CTkLabel(dialogo, text="Nombre Completo:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        entry_nombre = ctk.CTkEntry(dialogo, width=400)
        entry_nombre.pack(pady=5)
        if cliente:
            entry_nombre.insert(0, cliente['nombre_completo'])

        ctk.CTkLabel(dialogo, text="Teléfono:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_telefono = ctk.CTkEntry(dialogo, width=400, placeholder_text="Opcional")
        entry_telefono.pack(pady=5)
        if cliente and cliente['telefono']:
            entry_telefono.insert(0, cliente['telefono'])

        ctk.CTkLabel(dialogo, text="Email:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_email = ctk.CTkEntry(dialogo, width=400, placeholder_text="Opcional")
        entry_email.pack(pady=5)
        if cliente and cliente['email']:
            entry_email.insert(0, cliente['email'])

        def guardar():
            nombre = entry_nombre.get().strip()
            telefono = entry_telefono.get().strip()
            email = entry_email.get().strip()

            if not nombre:
                messagebox.showwarning("Validación", "Debe ingresar un nombre")
                return

            try:
                if cliente:
                    consultas.actualizar_cliente(
                        cliente['id_cliente'],
                        nombre, telefono, email
                    )
                    messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                else:
                    consultas.guardar_cliente(nombre, telefono, email)
                    messagebox.showinfo("Éxito", "Cliente agregado correctamente")

                dialogo.destroy()
                self._cargar_clientes()

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

    def _editar_cliente(self, cliente):
        """Edita un cliente existente"""
        self._mostrar_dialogo_cliente(cliente)

    def _ver_pedidos_cliente(self, cliente):
        """Muestra los pedidos de un cliente"""
        messagebox.showinfo(
            "Pedidos",
            f"Funcionalidad próximamente:\nMostrar pedidos de {cliente['nombre_completo']}"
        )

