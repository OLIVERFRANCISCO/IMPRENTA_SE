"""
Widget de búsqueda con autocompletado
Permite buscar y seleccionar clientes con sugerencias en tiempo real
"""
import customtkinter as ctk
from app.database import consultas


class AutocompleteEntry(ctk.CTkFrame):
    """Entry con autocompletado para seleccionar clientes"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent")

        self.cliente_seleccionado = None
        self.sugerencias_activas = []

        # Entry principal
        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="Escriba nombre o apellido del cliente...",
            width=kwargs.get('width', 300)
        )
        self.entry.pack()
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusOut>", self._on_focus_out)

        # Frame de sugerencias (inicialmente oculto)
        self.sugerencias_frame = ctk.CTkScrollableFrame(
            self,
            width=kwargs.get('width', 300),
            height=150,
            fg_color="gray20"
        )

        self.sugerencias_visible = False

    def _on_key_release(self, event):
        """Actualiza sugerencias al escribir"""
        texto = self.entry.get().strip().lower()

        if len(texto) < 2:
            self._ocultar_sugerencias()
            return

        # Buscar clientes que coincidan
        clientes = consultas.obtener_clientes()
        coincidencias = [
            c for c in clientes
            if texto in c['nombre_completo'].lower()
        ]

        if coincidencias:
            self._mostrar_sugerencias(coincidencias)
        else:
            self._ocultar_sugerencias()

    def _mostrar_sugerencias(self, clientes):
        """Muestra lista de sugerencias"""
        # Limpiar sugerencias anteriores
        for widget in self.sugerencias_frame.winfo_children():
            widget.destroy()

        self.sugerencias_activas = clientes

        # Crear botones de sugerencias
        for cliente in clientes[:10]:  # Máximo 10 sugerencias
            btn = ctk.CTkButton(
                self.sugerencias_frame,
                text=cliente['nombre_completo'],
                command=lambda c=cliente: self._seleccionar_cliente(c),
                fg_color="transparent",
                hover_color="gray30",
                anchor="w",
                height=35
            )
            btn.pack(fill="x", padx=5, pady=2)

        # Mostrar frame de sugerencias
        if not self.sugerencias_visible:
            self.sugerencias_frame.pack(pady=(5, 0))
            self.sugerencias_visible = True

    def _ocultar_sugerencias(self):
        """Oculta las sugerencias"""
        if self.sugerencias_visible:
            self.sugerencias_frame.pack_forget()
            self.sugerencias_visible = False

    def _seleccionar_cliente(self, cliente):
        """Selecciona un cliente de las sugerencias"""
        self.cliente_seleccionado = cliente
        self.entry.delete(0, "end")
        self.entry.insert(0, cliente['nombre_completo'])
        self._ocultar_sugerencias()

    def _on_focus_out(self, event):
        """Oculta sugerencias al perder foco (con delay para permitir clicks)"""
        self.after(200, self._ocultar_sugerencias)

    def get(self):
        """Retorna el texto del entry"""
        return self.entry.get()

    def get_cliente_seleccionado(self):
        """Retorna el cliente seleccionado o None"""
        return self.cliente_seleccionado

    def clear(self):
        """Limpia el entry"""
        self.entry.delete(0, "end")
        self.cliente_seleccionado = None

