"""
Panel de gestión de inventario
Maneja materiales de unidad y materiales dimensionales (rollos/bobinas)
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

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._crear_encabezado()
        self._crear_alertas()
        self._crear_tabview()
        self._cargar_materiales()

    def _crear_encabezado(self):
        """Crea el encabezado con título y botones"""
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, pady=(0, 10), sticky="ew")

        self.titulo = ctk.CTkLabel(
            frame_titulo,
            text="📦 Gestión de Inventario",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.titulo.pack(side="left")

        ctk.CTkButton(
            frame_titulo,
            text="+ Material Unidad",
            command=lambda: self._mostrar_dialogo_material('unidad'),
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_SUCCESS,
            width=160
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            frame_titulo,
            text="+ Material Dimensional",
            command=lambda: self._mostrar_dialogo_material('dimension'),
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=COLOR_PRIMARY,
            width=180
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            frame_titulo,
            text="🔄 Actualizar",
            command=self._cargar_materiales,
            height=40,
            width=120
        ).pack(side="right", padx=5)

    def _crear_alertas(self):
        """Crea el frame de alertas de stock bajo"""
        self.frame_alertas = ctk.CTkFrame(self, fg_color=COLOR_WARNING, corner_radius=10)
        # Se mostrará solo si hay alertas

    def _crear_tabview(self):
        """Crea las pestañas para materiales de unidad y dimensionales"""
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        self.tab_unidades = self.tabview.add("📦 Materiales por Unidad")
        self.tab_dimensionales = self.tabview.add("📏 Materiales Dimensionales")

        # Configurar cada tab
        self.tab_unidades.grid_rowconfigure(1, weight=1)
        self.tab_unidades.grid_columnconfigure(0, weight=1)
        
        self.tab_dimensionales.grid_rowconfigure(1, weight=1)
        self.tab_dimensionales.grid_columnconfigure(0, weight=1)

        # Descripciones
        ctk.CTkLabel(
            self.tab_unidades,
            text="💡 Materiales que se cuentan por unidades: tazas, llaveros, hojas, tintas...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(
            self.tab_dimensionales,
            text="💡 Materiales con dimensiones: rollos de lona, vinilo, papel tapiz... (ancho × largo)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Scrollable frames
        self.scroll_unidades = ctk.CTkScrollableFrame(self.tab_unidades)
        self.scroll_unidades.grid(row=1, column=0, sticky="nsew", pady=5)
        self.scroll_unidades.grid_columnconfigure(0, weight=1)

        self.scroll_dimensionales = ctk.CTkScrollableFrame(self.tab_dimensionales)
        self.scroll_dimensionales.grid(row=1, column=0, sticky="nsew", pady=5)
        self.scroll_dimensionales.grid_columnconfigure(0, weight=1)

    def _cargar_materiales(self):
        """Carga todos los materiales en sus respectivas pestañas"""
        # Limpiar frames
        for widget in self.scroll_unidades.winfo_children():
            widget.destroy()
        for widget in self.scroll_dimensionales.winfo_children():
            widget.destroy()

        # Obtener materiales
        materiales = consultas.obtener_materiales()
        materiales_bajo_stock = consultas.obtener_materiales_bajo_stock()
        materiales_dim_bajo = consultas.obtener_materiales_dimensionales_bajo_stock()

        # Mostrar alertas
        total_bajo = len(materiales_bajo_stock) + len(materiales_dim_bajo)
        if total_bajo > 0:
            self._mostrar_alertas(materiales_bajo_stock, materiales_dim_bajo)
        else:
            self.frame_alertas.grid_forget()

        # Separar materiales por tipo
        mat_unidades = [m for m in materiales if m.get('tipo_material') == 'unidad']
        mat_dimensionales = [m for m in materiales if m.get('tipo_material') == 'dimension']

        # Cargar tabla de unidades
        self._crear_tabla_unidades(mat_unidades)
        
        # Cargar tabla de dimensionales
        self._crear_tabla_dimensionales(mat_dimensionales)

    def _mostrar_alertas(self, bajo_stock, dim_bajo):
        """Muestra alertas de materiales bajo stock"""
        self.frame_alertas.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

        for widget in self.frame_alertas.winfo_children():
            widget.destroy()

        total = len(bajo_stock) + len(dim_bajo)
        ctk.CTkLabel(
            self.frame_alertas,
            text=f"⚠️ ALERTA: {total} material(es) con stock bajo",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        ).pack(pady=10, padx=15)

        for mat in bajo_stock:
            texto = f"• {mat['nombre_material']}: {mat['cantidad_stock']} {mat['unidad_medida']} (Mín: {mat['stock_minimo']})"
            ctk.CTkLabel(self.frame_alertas, text=texto, text_color="white", font=ctk.CTkFont(size=11)).pack(pady=1, padx=20, anchor="w")

        for mat in dim_bajo:
            texto = f"• {mat['nombre_material']}: {mat['ancho_disponible']}m × {mat['largo_disponible']}m (Mín: {mat['ancho_minimo']}m × {mat['largo_minimo']}m)"
            ctk.CTkLabel(self.frame_alertas, text=texto, text_color="white", font=ctk.CTkFont(size=11)).pack(pady=1, padx=20, anchor="w")

    def _crear_tabla_unidades(self, materiales):
        """Crea la tabla de materiales por unidad"""
        if not materiales:
            ctk.CTkLabel(
                self.scroll_unidades,
                text="No hay materiales por unidad registrados.\nUse '+ Material Unidad' para agregar.",
                text_color="gray"
            ).pack(pady=40)
            return

        # Header
        frame_header = ctk.CTkFrame(self.scroll_unidades, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        headers = ["Material", "Categoría", "Stock", "Mínimo", "Unidad", "Acciones"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(frame_header, text=h, font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=i, padx=8, pady=8)

        for idx, mat in enumerate(materiales):
            self._crear_fila_unidad(mat, idx + 1)

    def _crear_fila_unidad(self, material, fila):
        """Crea una fila para material de unidad"""
        bajo_stock = material['cantidad_stock'] <= material['stock_minimo']
        medio_stock = material['cantidad_stock'] <= material['stock_minimo'] * 1.5

        if bajo_stock:
            fg_color = COLOR_DANGER
        elif medio_stock:
            fg_color = COLOR_WARNING
        else:
            fg_color = "gray25" if fila % 2 == 0 else "gray20"

        frame = ctk.CTkFrame(self.scroll_unidades, fg_color=fg_color)
        frame.grid(row=fila, column=0, sticky="ew", pady=2)
        frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        ctk.CTkLabel(frame, text=material['nombre_material'], font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=8, pady=8)
        ctk.CTkLabel(frame, text=material.get('categoria_material', '-'), font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=8, pady=8)
        ctk.CTkLabel(frame, text=str(material['cantidad_stock']), font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=2, padx=8, pady=8)
        ctk.CTkLabel(frame, text=str(material['stock_minimo']), font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=8, pady=8)
        ctk.CTkLabel(frame, text=material['unidad_medida'], font=ctk.CTkFont(size=11)).grid(row=0, column=4, padx=8, pady=8)

        frame_acciones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_acciones.grid(row=0, column=5, padx=5, pady=5)

        ctk.CTkButton(frame_acciones, text="+ Stock", command=lambda m=material: self._agregar_stock_unidad(m), width=70, height=28, fg_color=COLOR_SUCCESS).pack(side="left", padx=2)
        ctk.CTkButton(frame_acciones, text="Editar", command=lambda m=material: self._mostrar_dialogo_material('unidad', m), width=60, height=28, fg_color=COLOR_PRIMARY).pack(side="left", padx=2)
        ctk.CTkButton(frame_acciones, text="Eliminar", command=lambda m=material: self._eliminar_material(m), width=70, height=28, fg_color=COLOR_DANGER).pack(side="left", padx=2)

    def _crear_tabla_dimensionales(self, materiales):
        """Crea la tabla de materiales dimensionales"""
        if not materiales:
            ctk.CTkLabel(
                self.scroll_dimensionales,
                text="No hay materiales dimensionales registrados.\nUse '+ Material Dimensional' para agregar rollos/bobinas.",
                text_color="gray"
            ).pack(pady=40)
            return

        # Header
        frame_header = ctk.CTkFrame(self.scroll_dimensionales, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        headers = ["Material", "Ancho × Largo", "Mínimos", "Tipo", "Acciones"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(frame_header, text=h, font=ctk.CTkFont(weight="bold"), text_color="white").grid(row=0, column=i, padx=8, pady=8)

        for idx, mat in enumerate(materiales):
            self._crear_fila_dimensional(mat, idx + 1)

    def _crear_fila_dimensional(self, material, fila):
        """Crea una fila para material dimensional"""
        ancho = material.get('ancho_disponible', 0)
        largo = material.get('largo_disponible', 0)
        ancho_min = material.get('ancho_minimo', 0)
        largo_min = material.get('largo_minimo', 0)

        bajo_stock = ancho <= ancho_min or largo <= largo_min
        medio_stock = ancho <= ancho_min * 1.3 or largo <= largo_min * 1.3

        if bajo_stock:
            fg_color = COLOR_DANGER
        elif medio_stock:
            fg_color = COLOR_WARNING
        else:
            fg_color = "gray25" if fila % 2 == 0 else "gray20"

        frame = ctk.CTkFrame(self.scroll_dimensionales, fg_color=fg_color)
        frame.grid(row=fila, column=0, sticky="ew", pady=2)
        frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        ctk.CTkLabel(frame, text=material['nombre_material'], font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=8, pady=8)
        ctk.CTkLabel(frame, text=f"{ancho:.2f}m × {largo:.2f}m", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=1, padx=8, pady=8)
        ctk.CTkLabel(frame, text=f"Min: {ancho_min:.2f}m × {largo_min:.2f}m", font=ctk.CTkFont(size=10)).grid(row=0, column=2, padx=8, pady=8)
        
        tipo = "🔄 Rollo" if material.get('es_continuo', True) else "📐 Plancha"
        ctk.CTkLabel(frame, text=tipo, font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=8, pady=8)

        frame_acciones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_acciones.grid(row=0, column=4, padx=5, pady=5)

        ctk.CTkButton(frame_acciones, text="+ Largo", command=lambda m=material: self._agregar_largo(m), width=70, height=28, fg_color=COLOR_SUCCESS).pack(side="left", padx=2)
        ctk.CTkButton(frame_acciones, text="Editar", command=lambda m=material: self._mostrar_dialogo_material('dimension', m), width=60, height=28, fg_color=COLOR_PRIMARY).pack(side="left", padx=2)
        ctk.CTkButton(frame_acciones, text="Eliminar", command=lambda m=material: self._eliminar_material(m), width=70, height=28, fg_color=COLOR_DANGER).pack(side="left", padx=2)

    # ========== DIÁLOGOS ==========

    def _mostrar_dialogo_material(self, tipo_material, material=None):
        """Muestra diálogo para agregar/editar material"""
        es_edicion = material is not None
        es_dimensional = tipo_material == 'dimension'

        dialogo = ctk.CTkToplevel(self)
        dialogo.title(f"{'Editar' if es_edicion else 'Nuevo'} Material {'Dimensional' if es_dimensional else 'por Unidad'}")
        dialogo.geometry("500x650" if es_dimensional else "500x550")
        dialogo.transient(self)
        dialogo.grab_set()

        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - 250
        y = (dialogo.winfo_screenheight() // 2) - 300
        dialogo.geometry(f"+{x}+{y}")

        scroll = ctk.CTkScrollableFrame(dialogo)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Nombre
        ctk.CTkLabel(scroll, text="Nombre del Material:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10, 5), anchor="w")
        entry_nombre = ctk.CTkEntry(scroll, width=400, placeholder_text="Ej: Lona 13oz, Vinil Adhesivo, Taza Sublimación")
        entry_nombre.pack(pady=5)
        if material:
            entry_nombre.insert(0, material['nombre_material'])

        # Categoría
        ctk.CTkLabel(scroll, text="Categoría:", font=ctk.CTkFont(size=12)).pack(pady=(15, 5), anchor="w")
        categorias = ["Lona", "Vinilo", "Papel", "Tinta", "Sublimación", "Rígido", "Textil", "Otro"]
        combo_categoria = ctk.CTkComboBox(scroll, values=categorias, width=400)
        combo_categoria.pack(pady=5)
        if material and material.get('categoria_material'):
            combo_categoria.set(material['categoria_material'])
        else:
            combo_categoria.set("Otro")

        if es_dimensional:
            # === CAMPOS DIMENSIONALES ===
            frame_dim = ctk.CTkFrame(scroll, fg_color="gray20", corner_radius=10)
            frame_dim.pack(fill="x", pady=15)

            ctk.CTkLabel(frame_dim, text="📏 Dimensiones Actuales", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 5))

            frame_dims = ctk.CTkFrame(frame_dim, fg_color="transparent")
            frame_dims.pack(pady=10, padx=15)

            ctk.CTkLabel(frame_dims, text="Ancho (m):").grid(row=0, column=0, padx=5)
            entry_ancho = ctk.CTkEntry(frame_dims, width=100, placeholder_text="1.50")
            entry_ancho.grid(row=0, column=1, padx=5)

            ctk.CTkLabel(frame_dims, text="Largo (m):").grid(row=0, column=2, padx=15)
            entry_largo = ctk.CTkEntry(frame_dims, width=100, placeholder_text="50.0")
            entry_largo.grid(row=0, column=3, padx=5)

            if material:
                entry_ancho.insert(0, str(material.get('ancho_disponible', 0)))
                entry_largo.insert(0, str(material.get('largo_disponible', 0)))

            # Mínimos
            ctk.CTkLabel(frame_dim, text="⚠️ Mínimos para Alerta", font=ctk.CTkFont(size=12)).pack(pady=(10, 5))

            frame_mins = ctk.CTkFrame(frame_dim, fg_color="transparent")
            frame_mins.pack(pady=10, padx=15)

            ctk.CTkLabel(frame_mins, text="Ancho mín:").grid(row=0, column=0, padx=5)
            entry_ancho_min = ctk.CTkEntry(frame_mins, width=100, placeholder_text="0.5")
            entry_ancho_min.grid(row=0, column=1, padx=5)

            ctk.CTkLabel(frame_mins, text="Largo mín:").grid(row=0, column=2, padx=15)
            entry_largo_min = ctk.CTkEntry(frame_mins, width=100, placeholder_text="5.0")
            entry_largo_min.grid(row=0, column=3, padx=5)

            if material:
                entry_ancho_min.insert(0, str(material.get('ancho_minimo', 0)))
                entry_largo_min.insert(0, str(material.get('largo_minimo', 0)))
            else:
                entry_ancho_min.insert(0, "0.5")
                entry_largo_min.insert(0, "5.0")

            # Tipo de material dimensional
            ctk.CTkLabel(frame_dim, text="Tipo:").pack(pady=(10, 5))
            var_continuo = tk.BooleanVar(value=material.get('es_continuo', True) if material else True)
            frame_tipo = ctk.CTkFrame(frame_dim, fg_color="transparent")
            frame_tipo.pack(pady=(0, 10))
            ctk.CTkRadioButton(frame_tipo, text="🔄 Rollo (largo variable)", variable=var_continuo, value=True).pack(side="left", padx=10)
            ctk.CTkRadioButton(frame_tipo, text="📐 Plancha (dimensiones fijas)", variable=var_continuo, value=False).pack(side="left", padx=10)

        else:
            # === CAMPOS UNIDAD ===
            frame_unidad = ctk.CTkFrame(scroll, fg_color="gray20", corner_radius=10)
            frame_unidad.pack(fill="x", pady=15)

            ctk.CTkLabel(frame_unidad, text="📦 Stock", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 5))

            frame_stock = ctk.CTkFrame(frame_unidad, fg_color="transparent")
            frame_stock.pack(pady=10, padx=15)

            ctk.CTkLabel(frame_stock, text="Cantidad:").grid(row=0, column=0, padx=5)
            entry_cantidad = ctk.CTkEntry(frame_stock, width=100, placeholder_text="100")
            entry_cantidad.grid(row=0, column=1, padx=5)

            ctk.CTkLabel(frame_stock, text="Mínimo:").grid(row=0, column=2, padx=15)
            entry_minimo = ctk.CTkEntry(frame_stock, width=100, placeholder_text="10")
            entry_minimo.grid(row=0, column=3, padx=5)

            if material:
                entry_cantidad.insert(0, str(material.get('cantidad_stock', 0)))
                entry_minimo.insert(0, str(material.get('stock_minimo', 5)))
            else:
                entry_cantidad.insert(0, "0")
                entry_minimo.insert(0, "5")

            ctk.CTkLabel(frame_unidad, text="Precio por unidad (S/):").pack(pady=(10, 5))
            entry_precio = ctk.CTkEntry(frame_unidad, width=150, placeholder_text="0.00")
            entry_precio.pack(pady=(0, 10))
            if material:
                entry_precio.insert(0, str(material.get('precio_por_unidad', 0)))

        # Unidad de medida
        ctk.CTkLabel(scroll, text="Unidad de medida:", font=ctk.CTkFont(size=12)).pack(pady=(15, 5), anchor="w")
        unidades = consultas.obtener_unidades_medida()
        unidades_nombres = [u['abreviacion'] for u in unidades] if unidades else ["m", "unidad", "m²"]
        combo_unidad = ctk.CTkComboBox(scroll, values=unidades_nombres, width=400)
        combo_unidad.pack(pady=5)
        if material:
            combo_unidad.set(material.get('unidad_medida', 'm'))
        else:
            combo_unidad.set("m" if es_dimensional else "unidad")

        # Sugerencia
        ctk.CTkLabel(scroll, text="Sugerencia/Notas:", font=ctk.CTkFont(size=12)).pack(pady=(15, 5), anchor="w")
        text_sugerencia = ctk.CTkTextbox(scroll, width=400, height=60)
        text_sugerencia.pack(pady=5)
        if material and material.get('sugerencia'):
            text_sugerencia.insert("1.0", material['sugerencia'])

        def guardar():
            try:
                nombre = entry_nombre.get().strip()
                categoria = combo_categoria.get()
                unidad = combo_unidad.get()
                sugerencia = text_sugerencia.get("1.0", "end-1c").strip()

                if not nombre:
                    messagebox.showwarning("Validación", "Ingrese el nombre del material")
                    return

                if es_dimensional:
                    ancho = float(entry_ancho.get() or 0)
                    largo = float(entry_largo.get() or 0)
                    ancho_min = float(entry_ancho_min.get() or 0)
                    largo_min = float(entry_largo_min.get() or 0)
                    es_continuo = var_continuo.get()

                    if material:
                        consultas.actualizar_material(
                            material['id_material'], nombre, 0, unidad, 0, 0,
                            tipo_material='dimension', sugerencia=sugerencia,
                            categoria_material=categoria,
                            ancho_disponible=ancho, largo_disponible=largo,
                            ancho_minimo=ancho_min, largo_minimo=largo_min,
                            es_continuo=es_continuo
                        )
                    else:
                        consultas.guardar_material(
                            nombre, 0, unidad, 0, 0,
                            tipo_material='dimension', sugerencia=sugerencia,
                            categoria_material=categoria,
                            ancho_disponible=ancho, largo_disponible=largo,
                            ancho_minimo=ancho_min, largo_minimo=largo_min,
                            es_continuo=es_continuo
                        )
                else:
                    cantidad = float(entry_cantidad.get() or 0)
                    minimo = float(entry_minimo.get() or 5)
                    precio = float(entry_precio.get() or 0)

                    if material:
                        consultas.actualizar_material(
                            material['id_material'], nombre, cantidad, unidad, minimo, precio,
                            tipo_material='unidad', sugerencia=sugerencia,
                            categoria_material=categoria
                        )
                    else:
                        consultas.guardar_material(
                            nombre, cantidad, unidad, minimo, precio,
                            tipo_material='unidad', sugerencia=sugerencia,
                            categoria_material=categoria
                        )

                messagebox.showinfo("Éxito", f"Material {'actualizado' if material else 'creado'} correctamente")
                dialogo.destroy()
                self._cargar_materiales()

            except ValueError as e:
                messagebox.showerror("Error", f"Valores inválidos: {e}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(scroll, text="💾 Guardar", command=guardar, fg_color=COLOR_SUCCESS, height=40, width=200).pack(pady=20)

    def _agregar_stock_unidad(self, material):
        """Agrega stock a un material de unidad"""
        dialogo = ctk.CTkInputDialog(
            text=f"¿Cuántas {material['unidad_medida']} agregar a '{material['nombre_material']}'?",
            title="Agregar Stock"
        )
        cantidad = dialogo.get_input()

        if cantidad:
            try:
                cant = float(cantidad)
                consultas.actualizar_stock_material(material['id_material'], cant, es_dimensional=False)
                messagebox.showinfo("Éxito", f"Se agregaron {cant} {material['unidad_medida']}")
                self._cargar_materiales()
            except ValueError:
                messagebox.showerror("Error", "Cantidad inválida")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _agregar_largo(self, material):
        """Agrega largo a un material dimensional"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Agregar Largo al Rollo")
        dialogo.geometry("400x200")
        dialogo.transient(self)
        dialogo.grab_set()

        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - 200
        y = (dialogo.winfo_screenheight() // 2) - 100
        dialogo.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialogo,
            text=f"Agregar largo a '{material['nombre_material']}'",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            dialogo,
            text=f"Actual: {material.get('ancho_disponible', 0):.2f}m × {material.get('largo_disponible', 0):.2f}m",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=5)

        frame = ctk.CTkFrame(dialogo, fg_color="transparent")
        frame.pack(pady=15)

        ctk.CTkLabel(frame, text="Metros a agregar:").pack(side="left", padx=5)
        entry_largo = ctk.CTkEntry(frame, width=100, placeholder_text="10.0")
        entry_largo.pack(side="left", padx=5)

        def confirmar():
            try:
                largo = float(entry_largo.get())
                consultas.agregar_stock_dimensional(material['id_material'], largo_agregar=largo)
                messagebox.showinfo("Éxito", f"Se agregaron {largo}m de largo")
                dialogo.destroy()
                self._cargar_materiales()
            except ValueError:
                messagebox.showerror("Error", "Valor inválido")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialogo, text="Agregar", command=confirmar, fg_color=COLOR_SUCCESS, height=35).pack(pady=10)

    def _eliminar_material(self, material):
        """Elimina un material"""
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{material['nombre_material']}'?\nEsta acción no se puede deshacer."):
            try:
                consultas.eliminar_material(material['id_material'])
                messagebox.showinfo("Éxito", "Material eliminado")
                self._cargar_materiales()
            except Exception as e:
                messagebox.showerror("Error", str(e))
