"""
Panel de gestión de inventario
Permite ver, agregar y editar materiales
"""
import customtkinter as ctk
from tkinter import messagebox
from app.config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER
)
from app.database import consultas


class PanelInventario(ctk.CTkFrame):
    """Panel para gestionar el inventario de materiales"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, pady=(0, 20), sticky="ew")

        self.titulo = ctk.CTkLabel(
            frame_titulo,
            text="📦 Gestión de Inventario",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.titulo.pack(side="left")

        self.btn_nuevo_material = ctk.CTkButton(
            frame_titulo,
            text="+ Nuevo Material",
            command=self._mostrar_dialogo_material,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS,
            width=180
        )
        self.btn_nuevo_material.pack(side="right", padx=10)

        self.btn_actualizar = ctk.CTkButton(
            frame_titulo,
            text="🔄 Actualizar",
            command=self._cargar_materiales,
            height=40,
            width=140
        )
        self.btn_actualizar.pack(side="right")

        # Frame de alertas
        self.frame_alertas = ctk.CTkFrame(self, fg_color=COLOR_WARNING, corner_radius=10)

        # Contenedor scrollable para la tabla
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self._cargar_materiales()

    def _cargar_materiales(self):
        """Carga y muestra todos los materiales"""
        # Limpiar frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Obtener materiales
        materiales = consultas.obtener_materiales()
        materiales_bajo_stock = consultas.obtener_materiales_bajo_stock()

        # Mostrar alertas si hay materiales bajos
        if materiales_bajo_stock:
            self.frame_alertas.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

            for widget in self.frame_alertas.winfo_children():
                widget.destroy()

            ctk.CTkLabel(
                self.frame_alertas,
                text=f"⚠️ {len(materiales_bajo_stock)} material(es) con stock bajo",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            ).pack(pady=10, padx=15)

            for mat in materiales_bajo_stock:
                texto = f"• {mat['nombre_material']}: {mat['cantidad_stock']} {mat['unidad_medida']} (Mínimo: {mat['stock_minimo']})"
                ctk.CTkLabel(
                    self.frame_alertas,
                    text=texto,
                    text_color="white",
                    font=ctk.CTkFont(size=12)
                ).pack(pady=2, padx=20, anchor="w")
        else:
            self.frame_alertas.grid_forget()

        # Crear encabezados de tabla
        frame_header = ctk.CTkFrame(self.scroll_frame, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        headers = ["Material", "Stock Actual", "Unidad", "Stock Mínimo", "Precio/Unidad", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                frame_header,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=10)

        # Mostrar materiales
        for idx, material in enumerate(materiales):
            self._crear_fila_material(material, idx + 1)

    def _crear_fila_material(self, material, fila):
        """Crea una fila en la tabla con los datos del material"""
        # Determinar color según stock
        if material['cantidad_stock'] <= material['stock_minimo']:
            fg_color = COLOR_DANGER
            text_color = "white"
        elif material['cantidad_stock'] <= material['stock_minimo'] * 1.5:
            fg_color = COLOR_WARNING
            text_color = "white"
        else:
            fg_color = "gray25" if fila % 2 == 0 else "gray20"
            text_color = "white"

        frame_fila = ctk.CTkFrame(self.scroll_frame, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # Nombre
        ctk.CTkLabel(
            frame_fila,
            text=material['nombre_material'],
            font=ctk.CTkFont(size=12),
            text_color=text_color
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Stock actual
        ctk.CTkLabel(
            frame_fila,
            text=str(material['cantidad_stock']),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=text_color
        ).grid(row=0, column=1, padx=10, pady=10)

        # Unidad
        ctk.CTkLabel(
            frame_fila,
            text=material['unidad_medida'],
            text_color=text_color
        ).grid(row=0, column=2, padx=10, pady=10)

        # Stock mínimo
        ctk.CTkLabel(
            frame_fila,
            text=str(material['stock_minimo']),
            text_color=text_color
        ).grid(row=0, column=3, padx=10, pady=10)

        # Precio
        ctk.CTkLabel(
            frame_fila,
            text=f"S/ {material['precio_por_unidad']:.2f}",
            text_color=text_color
        ).grid(row=0, column=4, padx=10, pady=10)

        # Botones de acción
        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=5, padx=10, pady=5)

        btn_editar = ctk.CTkButton(
            frame_acciones,
            text="✏️",
            command=lambda m=material: self._editar_material(m),
            width=40,
            height=30,
            fg_color=COLOR_PRIMARY
        )
        btn_editar.pack(side="left", padx=2)

        btn_agregar_stock = ctk.CTkButton(
            frame_acciones,
            text="+",
            command=lambda m=material: self._agregar_stock(m),
            width=40,
            height=30,
            fg_color=COLOR_SUCCESS
        )
        btn_agregar_stock.pack(side="left", padx=2)

    def _mostrar_dialogo_material(self, material=None):
        """Muestra diálogo para agregar o editar material"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Material" if material is None else "Editar Material")
        dialogo.geometry("500x450")
        dialogo.transient(self)
        dialogo.grab_set()

        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (450 // 2)
        dialogo.geometry(f"+{x}+{y}")

        # Campos
        ctk.CTkLabel(dialogo, text="Nombre del Material:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        entry_nombre = ctk.CTkEntry(dialogo, width=400)
        entry_nombre.pack(pady=5)
        if material:
            entry_nombre.insert(0, material['nombre_material'])

        ctk.CTkLabel(dialogo, text="Cantidad en Stock:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_cantidad = ctk.CTkEntry(dialogo, width=400)
        entry_cantidad.pack(pady=5)
        if material:
            entry_cantidad.insert(0, str(material['cantidad_stock']))

        ctk.CTkLabel(dialogo, text="Unidad de Medida:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        combo_unidad = ctk.CTkComboBox(dialogo, values=["metros", "hojas", "cartuchos", "unidades", "rollos"], width=400)
        combo_unidad.pack(pady=5)
        if material:
            combo_unidad.set(material['unidad_medida'])

        ctk.CTkLabel(dialogo, text="Stock Mínimo:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_stock_min = ctk.CTkEntry(dialogo, width=400)
        entry_stock_min.pack(pady=5)
        if material:
            entry_stock_min.insert(0, str(material['stock_minimo']))
        else:
            entry_stock_min.insert(0, "5")

        ctk.CTkLabel(dialogo, text="Precio por Unidad:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_precio = ctk.CTkEntry(dialogo, width=400)
        entry_precio.pack(pady=5)
        if material:
            entry_precio.insert(0, str(material['precio_por_unidad']))
        else:
            entry_precio.insert(0, "0.00")

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                cantidad = float(entry_cantidad.get())
                unidad = combo_unidad.get()
                stock_min = float(entry_stock_min.get())
                precio = float(entry_precio.get())

                if not nombre:
                    messagebox.showwarning("Validación", "Debe ingresar un nombre")
                    return

                if material:
                    consultas.actualizar_material(
                        material['id_material'],
                        nombre, cantidad, unidad, stock_min, precio
                    )
                    messagebox.showinfo("Éxito", "Material actualizado correctamente")
                else:
                    consultas.guardar_material(nombre, cantidad, unidad, stock_min, precio)
                    messagebox.showinfo("Éxito", "Material agregado correctamente")

                dialogo.destroy()
                self._cargar_materiales()

            except ValueError:
                messagebox.showerror("Error", "Datos inválidos. Verifique los campos numéricos.")

        btn_guardar = ctk.CTkButton(
            dialogo,
            text="💾 Guardar",
            command=guardar,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLOR_SUCCESS
        )
        btn_guardar.pack(pady=20)

    def _editar_material(self, material):
        """Edita un material existente"""
        self._mostrar_dialogo_material(material)

    def _agregar_stock(self, material):
        """Muestra diálogo para agregar stock"""
        dialogo = ctk.CTkInputDialog(
            text=f"¿Cuántos {material['unidad_medida']} desea agregar a '{material['nombre_material']}'?",
            title="Agregar Stock"
        )
        cantidad_texto = dialogo.get_input()

        if cantidad_texto:
            try:
                cantidad = float(cantidad_texto)
                consultas.actualizar_stock_material(material['id_material'], cantidad)
                messagebox.showinfo("Éxito", f"Se agregaron {cantidad} {material['unidad_medida']}")
                self._cargar_materiales()
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida")

