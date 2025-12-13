"""
Panel de gestión de inventario
Permite ver, agregar y editar materiales
"""
import customtkinter as ctk
import tkinter as tk
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
            text="Gestión de Inventario",
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
            text="Actualizar",
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
                text=f"ADVERTENCIA: {len(materiales_bajo_stock)} material(es) con stock bajo",
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
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        headers = ["Material", "Tipo", "Stock/Dim", "Unidad", "Mín.", "Precio", "Sugerencia", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                frame_header,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=8, pady=10)

        # Mostrar materiales
        for idx, material in enumerate(materiales):
            self._crear_fila_material(material, idx + 1)

    def _crear_fila_material(self, material, fila):
        """Crea una fila en la tabla con los datos del material"""
        # Determinar tipo y valores
        tipo = material.get('tipo_material', 'unidad')
        
        # Determinar color según stock (dinámico según tipo)
        if tipo == 'dimension':
            dim_disp = material.get('dimension_disponible', 0.0)
            dim_min = material.get('dimension_minima', 0.0)
            bajo_stock = dim_disp <= dim_min
            medio_stock = dim_disp <= dim_min * 1.5
        else:
            bajo_stock = material['cantidad_stock'] <= material['stock_minimo']
            medio_stock = material['cantidad_stock'] <= material['stock_minimo'] * 1.5
        
        if bajo_stock:
            fg_color = COLOR_DANGER
            text_color = "white"
        elif medio_stock:
            fg_color = COLOR_WARNING
            text_color = "white"
        else:
            fg_color = "gray25" if fila % 2 == 0 else "gray20"
            text_color = "white"

        frame_fila = ctk.CTkFrame(self.scroll_frame, fg_color=fg_color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)

        # Nombre
        ctk.CTkLabel(
            frame_fila,
            text=material['nombre_material'],
            font=ctk.CTkFont(size=11),
            text_color=text_color
        ).grid(row=0, column=0, padx=8, pady=10, sticky="w")

        # Tipo
        tipo_texto = "📦" if tipo == "unidad" else "📏"
        ctk.CTkLabel(
            frame_fila,
            text=tipo_texto,
            font=ctk.CTkFont(size=14),
            text_color=text_color
        ).grid(row=0, column=1, padx=8, pady=10)

        # Stock/Dimensión
        if tipo == 'dimension':
            stock_texto = f"{material.get('dimension_disponible', 0):.1f}"
        else:
            stock_texto = str(material['cantidad_stock'])
        
        ctk.CTkLabel(
            frame_fila,
            text=stock_texto,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=text_color
        ).grid(row=0, column=2, padx=8, pady=10)

        # Unidad
        ctk.CTkLabel(
            frame_fila,
            text=material['unidad_medida'],
            font=ctk.CTkFont(size=10),
            text_color=text_color
        ).grid(row=0, column=3, padx=8, pady=10)

        # Mínimo
        if tipo == 'dimension':
            min_texto = f"{material.get('dimension_minima', 0):.1f}"
        else:
            min_texto = str(material['stock_minimo'])
        
        ctk.CTkLabel(
            frame_fila,
            text=min_texto,
            font=ctk.CTkFont(size=10),
            text_color=text_color
        ).grid(row=0, column=4, padx=8, pady=10)

        # Precio
        ctk.CTkLabel(
            frame_fila,
            text=f"S/ {material['precio_por_unidad']:.2f}",
            font=ctk.CTkFont(size=10),
            text_color=text_color
        ).grid(row=0, column=5, padx=8, pady=10)

        # Sugerencia (truncada)
        sugerencia = material.get('sugerencia', '-')
        sugerencia_corta = sugerencia[:25] + "..." if len(sugerencia) > 25 else sugerencia
        ctk.CTkLabel(
            frame_fila,
            text=sugerencia_corta,
            font=ctk.CTkFont(size=9, slant="italic"),
            text_color=text_color
        ).grid(row=0, column=6, padx=8, pady=10, sticky="w")

        # Botones de acción
        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=7, padx=8, pady=5)

        btn_editar = ctk.CTkButton(
            frame_acciones,
            text="Editar",
            command=lambda m=material: self._editar_material(m),
            width=60,
            height=30,
            fg_color=COLOR_PRIMARY
        )
        btn_editar.pack(side="left", padx=2)

        btn_agregar_stock = ctk.CTkButton(
            frame_acciones,
            text="+ Stock",
            command=lambda m=material: self._agregar_stock(m),
            width=70,
            height=30,
            fg_color=COLOR_SUCCESS
        )
        btn_agregar_stock.pack(side="left", padx=2)

        btn_eliminar = ctk.CTkButton(
            frame_acciones,
            text="Eliminar",
            command=lambda m=material: self._confirmar_eliminar_material(m),
            width=70,
            height=30,
            fg_color=COLOR_DANGER
        )
        btn_eliminar.pack(side="left", padx=2)

    def _mostrar_dialogo_material(self, material=None):
        """Muestra diálogo para agregar o editar material"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Material / Rollo" if material is None else "Editar Material")
        dialogo.geometry("550x800")
        dialogo.transient(self)
        dialogo.grab_set()

        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (800 // 2)
        dialogo.geometry(f"+{x}+{y}")

        # === TIPO DE MATERIAL ===
        ctk.CTkLabel(dialogo, text="Tipo de Material:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(15, 5))
        
        tipo_var = tk.StringVar(value=material.get('tipo_material', 'unidad') if material else 'unidad')
        
        frame_tipo = ctk.CTkFrame(dialogo, fg_color="transparent")
        frame_tipo.pack(pady=5)
        
        radio_unidad = ctk.CTkRadioButton(
            frame_tipo, 
            text="📦 Unidad (stock tradicional)", 
            variable=tipo_var, 
            value="unidad",
            font=ctk.CTkFont(size=12)
        )
        radio_unidad.pack(side="left", padx=15)
        
        radio_dimension = ctk.CTkRadioButton(
            frame_tipo, 
            text="📏 Dimensión (rollos/bobinas)", 
            variable=tipo_var, 
            value="dimension",
            font=ctk.CTkFont(size=12)
        )
        radio_dimension.pack(side="left", padx=15)

        # Campos
        ctk.CTkLabel(dialogo, text="Nombre del Material:", font=ctk.CTkFont(size=12)).pack(pady=(20, 5))
        entry_nombre = ctk.CTkEntry(dialogo, width=450, placeholder_text="Ej: Lona 13oz, Vinil Adhesivo")
        entry_nombre.pack(pady=5)
        if material:
            entry_nombre.insert(0, material['nombre_material'])

        # === CAMPOS DINÁMICOS SEGÚN TIPO ===
        
        # Frame para campos de UNIDAD
        frame_unidad = ctk.CTkFrame(dialogo, fg_color="transparent")
        
        ctk.CTkLabel(frame_unidad, text="Cantidad en Stock:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_cantidad = ctk.CTkEntry(frame_unidad, width=450, placeholder_text="Cantidad disponible")
        entry_cantidad.pack(pady=5)
        
        ctk.CTkLabel(frame_unidad, text="Stock Mínimo:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_stock_min = ctk.CTkEntry(frame_unidad, width=450, placeholder_text="Cantidad mínima recomendada")
        entry_stock_min.pack(pady=5)
        
        # Frame para campos de DIMENSIÓN
        frame_dimension = ctk.CTkFrame(dialogo, fg_color="transparent")
        
        ctk.CTkLabel(frame_dimension, text="Ancho de Bobina (metros):", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_ancho_bobina = ctk.CTkEntry(frame_dimension, width=450, placeholder_text="Ej: 1.10, 1.50, 1.60")
        entry_ancho_bobina.pack(pady=5)
        
        ctk.CTkLabel(frame_dimension, text="Dimensión Disponible:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_dimension_disponible = ctk.CTkEntry(frame_dimension, width=450, placeholder_text="Metros/m² disponibles")
        entry_dimension_disponible.pack(pady=5)
        
        ctk.CTkLabel(frame_dimension, text="Dimensión Mínima:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_dimension_minima = ctk.CTkEntry(frame_dimension, width=450, placeholder_text="Dimensión mínima para alerta")
        entry_dimension_minima.pack(pady=5)
        
        # Prellenar valores si es edición
        if material:
            if material.get('tipo_material') == 'dimension':
                entry_ancho_bobina.insert(0, str(material.get('ancho_bobina', 0.0)))
                entry_dimension_disponible.insert(0, str(material.get('dimension_disponible', 0.0)))
                entry_dimension_minima.insert(0, str(material.get('dimension_minima', 0.0)))
            else:
                entry_cantidad.insert(0, str(material['cantidad_stock']))
                entry_stock_min.insert(0, str(material['stock_minimo']))
        else:
            entry_cantidad.insert(0, "0")
            entry_stock_min.insert(0, "5")
            entry_ancho_bobina.insert(0, "0")
            entry_dimension_disponible.insert(0, "0")
            entry_dimension_minima.insert(0, "0")
        
        # Función para mostrar/ocultar campos según tipo
        def cambiar_tipo(*args):
            if tipo_var.get() == "unidad":
                frame_dimension.pack_forget()
                frame_unidad.pack(pady=5)
            else:
                frame_unidad.pack_forget()
                frame_dimension.pack(pady=5)
        
        tipo_var.trace_add("write", cambiar_tipo)
        cambiar_tipo()  # Inicializar

        # === CAMPOS COMUNES ===
        ctk.CTkLabel(dialogo, text="Unidad de Medida:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        
        # Obtener unidades de la base de datos
        unidades = consultas.obtener_unidades_medida()
        unidades_dict = {u['abreviacion']: u['id_unidad'] for u in unidades}
        unidades_nombres = [u['abreviacion'] for u in unidades]
        
        # Fallback si no hay unidades
        if not unidades_nombres:
            unidades_nombres = ["metros", "unidades", "m²"]
        
        combo_unidad = ctk.CTkComboBox(dialogo, values=unidades_nombres, width=450)
        combo_unidad.pack(pady=5)
        if material:
            combo_unidad.set(material['unidad_medida'])
        else:
            combo_unidad.set(unidades_nombres[0] if unidades_nombres else "metros")

        ctk.CTkLabel(dialogo, text="Precio por Unidad:", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))
        entry_precio = ctk.CTkEntry(dialogo, width=450, placeholder_text="Precio en soles")
        entry_precio.pack(pady=5)
        if material:
            entry_precio.insert(0, str(material['precio_por_unidad']))
        else:
            entry_precio.insert(0, "0.00")
        
        # === CAMPO SUGERENCIA ===
        ctk.CTkLabel(dialogo, text="Sugerencia / Recomendación:", font=ctk.CTkFont(size=12)).pack(pady=(15, 5))
        text_sugerencia = ctk.CTkTextbox(dialogo, width=450, height=80)
        text_sugerencia.pack(pady=5)
        if material:
            text_sugerencia.insert("1.0", material.get('sugerencia', ''))
        else:
            text_sugerencia.insert("1.0", "Ej: Ideal para exteriores, resistente al agua...")

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                unidad = combo_unidad.get()
                precio = float(entry_precio.get())
                tipo = tipo_var.get()
                sugerencia = text_sugerencia.get("1.0", "end-1c").strip()

                if not nombre:
                    messagebox.showwarning("Validación", "Debe ingresar un nombre")
                    return

                # Obtener valores según el tipo
                if tipo == "unidad":
                    cantidad = float(entry_cantidad.get())
                    stock_min = float(entry_stock_min.get())
                    ancho_bobina = 0.0
                    dimension_minima = 0.0
                    dimension_disponible = 0.0
                else:  # dimension
                    ancho_bobina = float(entry_ancho_bobina.get())
                    dimension_disponible = float(entry_dimension_disponible.get())
                    dimension_minima = float(entry_dimension_minima.get())
                    cantidad = dimension_disponible  # Para compatibilidad
                    stock_min = dimension_minima

                if material:
                    # Actualizar material existente
                    consultas.actualizar_material(
                        material['id_material'],
                        nombre, cantidad, unidad, stock_min, precio,
                        tipo_material=tipo,
                        sugerencia=sugerencia,
                        ancho_bobina=ancho_bobina,
                        dimension_minima=dimension_minima,
                        dimension_disponible=dimension_disponible
                    )
                    messagebox.showinfo("Éxito", "Material actualizado correctamente")
                else:
                    # Nuevo material
                    consultas.guardar_material(
                        nombre, cantidad, unidad, stock_min, precio,
                        tipo_material=tipo,
                        sugerencia=sugerencia,
                        ancho_bobina=ancho_bobina,
                        dimension_minima=dimension_minima,
                        dimension_disponible=dimension_disponible
                    )
                    messagebox.showinfo("Éxito", f"Material agregado correctamente\nTipo: {tipo}")

                dialogo.destroy()
                self._cargar_materiales()

            except ValueError as e:
                messagebox.showerror("Error", f"Datos inválidos: {str(e)}\nVerifique los campos numéricos.")

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
        """Edita un material existente con confirmación"""
        dialogo_confirm = ctk.CTkToplevel(self)
        dialogo_confirm.title("Confirmar Edición")
        dialogo_confirm.geometry("450x200")
        dialogo_confirm.transient(self)
        dialogo_confirm.grab_set()

        # Centrar ventana
        dialogo_confirm.update_idletasks()
        x = (dialogo_confirm.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialogo_confirm.winfo_screenheight() // 2) - (200 // 2)
        dialogo_confirm.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialogo_confirm,
            text="¿Está seguro de editar este material?",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            dialogo_confirm,
            text=f"Material: {material['nombre_material']}",
            font=ctk.CTkFont(size=14)
        ).pack(pady=5)

        frame_botones = ctk.CTkFrame(dialogo_confirm, fg_color="transparent")
        frame_botones.pack(pady=20)

        def confirmar_edicion():
            dialogo_confirm.destroy()
            self._mostrar_dialogo_material(material)

        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=dialogo_confirm.destroy,
            width=120,
            height=40,
            fg_color="gray"
        )
        btn_cancelar.pack(side="left", padx=10)

        btn_confirmar = ctk.CTkButton(
            frame_botones,
            text="Sí, Editar",
            command=confirmar_edicion,
            width=120,
            height=40,
            fg_color=COLOR_PRIMARY
        )
        btn_confirmar.pack(side="left", padx=10)

    def _confirmar_eliminar_material(self, material):
        """Muestra diálogo de confirmación antes de eliminar material"""
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
            text="¿Está seguro de eliminar este material?",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(30, 10))

        ctk.CTkLabel(
            dialogo,
            text=f"Material: {material['nombre_material']}",
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
                consultas.eliminar_material(material['id_material'])
                messagebox.showinfo("Éxito", "Material eliminado correctamente")
                dialogo.destroy()
                self._cargar_materiales()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el material: {str(e)}")

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
