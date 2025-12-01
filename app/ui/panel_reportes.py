"""
Panel de reportes y estadísticas
Muestra dashboard con información general del sistema
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER,
    ESTADOS_PEDIDO
)
from app.database import consultas
from app.logic.exportacion import exportar_a_csv, exportar_a_excel, exportar_a_pdf


class PanelReportes(ctk.CTkFrame):
    """Panel de reportes y estadísticas"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título
        self.titulo = ctk.CTkLabel(
            self,
            text="Reportes y Estadísticas",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.titulo.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Contenedor scrollable
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._crear_dashboard()

    def _crear_dashboard(self):
        """Crea el dashboard con tarjetas de estadísticas"""

        # Obtener datos
        clientes = consultas.obtener_clientes()
        materiales = consultas.obtener_materiales()
        materiales_bajo_stock = consultas.obtener_materiales_bajo_stock()
        pedidos = consultas.obtener_pedidos()

        # Función auxiliar para acceder de forma segura a sqlite3.Row
        def get_field(row, field, default=None):
            try:
                return row[field] if row[field] is not None else default
            except (KeyError, IndexError):
                return default

        pedidos_activos = [p for p in pedidos if get_field(p, 'estado_nombre') not in ['Entregado', 'Cancelado']]

        # Tarjetas de resumen
        row = 0

        # Tarjeta 1: Total de Clientes
        self._crear_tarjeta(
            self.scroll_frame,
            "Total de Clientes",
            str(len(clientes)),
            COLOR_PRIMARY,
            row, 0
        )

        # Tarjeta 2: Pedidos Activos
        self._crear_tarjeta(
            self.scroll_frame,
            "Pedidos Activos",
            str(len(pedidos_activos)),
            COLOR_SUCCESS,
            row, 1
        )

        # Tarjeta 3: Alertas de Inventario
        color_alerta = COLOR_DANGER if materiales_bajo_stock else COLOR_SUCCESS
        self._crear_tarjeta(
            self.scroll_frame,
            "Alertas de Stock",
            str(len(materiales_bajo_stock)),
            color_alerta,
            row, 2
        )

        row += 1

        # Sección: Pedidos por Estado
        frame_pedidos_estado = ctk.CTkFrame(self.scroll_frame)
        frame_pedidos_estado.grid(row=row, column=0, columnspan=3, pady=20, padx=10, sticky="ew")

        ctk.CTkLabel(
            frame_pedidos_estado,
            text="Pedidos por Estado",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15, padx=15, anchor="w")

        # Contar pedidos por estado
        estados_count = {}
        estados_disponibles = consultas.obtener_estados_pedidos()
        for estado_obj in estados_disponibles:
            estado_nombre = estado_obj['nombre']
            count = len([p for p in pedidos if get_field(p, 'estado_nombre') == estado_nombre])
            if count > 0:
                estados_count[estado_nombre] = count

        if estados_count:
            for estado, count in estados_count.items():
                frame_barra = ctk.CTkFrame(frame_pedidos_estado, fg_color="transparent")
                frame_barra.pack(fill="x", padx=15, pady=5)

                ctk.CTkLabel(
                    frame_barra,
                    text=f"{estado}:",
                    font=ctk.CTkFont(size=12),
                    width=200,
                    anchor="w"
                ).pack(side="left")

                ctk.CTkLabel(
                    frame_barra,
                    text=str(count),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLOR_PRIMARY
                ).pack(side="left", padx=10)
        else:
            ctk.CTkLabel(
                frame_pedidos_estado,
                text="No hay pedidos registrados",
                text_color="gray"
            ).pack(pady=10, padx=15)

        row += 1

        # Sección: Materiales más usados (simulado)
        frame_materiales = ctk.CTkFrame(self.scroll_frame)
        frame_materiales.grid(row=row, column=0, columnspan=3, pady=20, padx=10, sticky="ew")

        ctk.CTkLabel(
            frame_materiales,
            text="Estado del Inventario",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15, padx=15, anchor="w")

        for material in materiales[:5]:  # Top 5
            frame_mat = ctk.CTkFrame(frame_materiales, fg_color="transparent")
            frame_mat.pack(fill="x", padx=15, pady=5)

            stock_porcentaje = (material['cantidad_stock'] / (material['stock_minimo'] * 2)) * 100 if material['stock_minimo'] > 0 else 100
            stock_porcentaje = min(100, stock_porcentaje)

            color_barra = COLOR_SUCCESS if stock_porcentaje > 50 else COLOR_WARNING if stock_porcentaje > 20 else COLOR_DANGER

            ctk.CTkLabel(
                frame_mat,
                text=f"{material['nombre_material']}:",
                font=ctk.CTkFont(size=12),
                width=200,
                anchor="w"
            ).pack(side="left")

            progress = ctk.CTkProgressBar(frame_mat, width=300, height=20, progress_color=color_barra)
            progress.set(stock_porcentaje / 100)
            progress.pack(side="left", padx=10)

            ctk.CTkLabel(
                frame_mat,
                text=f"{material['cantidad_stock']} {material['unidad_medida']}",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(side="left", padx=5)

        row += 1

        # Botones de acciones
        frame_acciones = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        frame_acciones.grid(row=row, column=0, columnspan=3, pady=30, padx=10)

        ctk.CTkButton(
            frame_acciones,
            text="Actualizar Datos",
            command=self._actualizar_dashboard,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLOR_PRIMARY,
            width=200
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_acciones,
            text="Exportar Reporte",
            command=self._exportar_reporte,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLOR_SUCCESS,
            width=200
        ).pack(side="left", padx=10)

    def _crear_tarjeta(self, parent, titulo, valor, color, row, col):
        """Crea una tarjeta de estadística"""
        frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=15)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(
            frame,
            text=titulo,
            font=ctk.CTkFont(size=14),
            text_color="white"
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            frame,
            text=valor,
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="white"
        ).pack(pady=(5, 20))

    def _actualizar_dashboard(self):
        """Actualiza todos los datos del dashboard"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self._crear_dashboard()

    def _exportar_reporte(self):
        """Muestra diálogo para exportar el reporte"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Exportar Reporte")
        dialogo.geometry("500x400")
        dialogo.transient(self)
        dialogo.grab_set()

        # Centrar ventana
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (400 // 2)
        dialogo.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialogo,
            text="Exportar Reporte del Sistema",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)

        ctk.CTkLabel(
            dialogo,
            text="Seleccione el formato de exportación:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)

        # Variable para formato
        formato_var = ctk.StringVar(value="excel")

        # Radio buttons para formato
        frame_formato = ctk.CTkFrame(dialogo)
        frame_formato.pack(pady=10)

        ctk.CTkRadioButton(
            frame_formato,
            text="Excel (.xlsx) - Recomendado",
            variable=formato_var,
            value="excel"
        ).pack(pady=5, anchor="w", padx=20)

        ctk.CTkRadioButton(
            frame_formato,
            text="PDF (.pdf)",
            variable=formato_var,
            value="pdf"
        ).pack(pady=5, anchor="w", padx=20)

        ctk.CTkRadioButton(
            frame_formato,
            text="CSV (.csv)",
            variable=formato_var,
            value="csv"
        ).pack(pady=5, anchor="w", padx=20)

        # Botón para seleccionar directorio
        ctk.CTkLabel(
            dialogo,
            text="Seleccione dónde guardar el archivo:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(20, 10))

        frame_directorio = ctk.CTkFrame(dialogo)
        frame_directorio.pack(pady=10, padx=20, fill="x")

        directorio_var = ctk.StringVar(value="")

        entry_directorio = ctk.CTkEntry(
            frame_directorio,
            textvariable=directorio_var,
            width=300,
            placeholder_text="Haga clic en Examinar..."
        )
        entry_directorio.pack(side="left", padx=5)

        def seleccionar_directorio():
            directorio = filedialog.askdirectory(title="Seleccionar carpeta de destino")
            if directorio:
                directorio_var.set(directorio)

        ctk.CTkButton(
            frame_directorio,
            text="Examinar",
            command=seleccionar_directorio,
            width=100
        ).pack(side="left", padx=5)

        # Frame de botones
        frame_botones = ctk.CTkFrame(dialogo, fg_color="transparent")
        frame_botones.pack(pady=20)

        def exportar():
            formato = formato_var.get()
            directorio = directorio_var.get()

            if not directorio:
                messagebox.showwarning("Validación", "Debe seleccionar un directorio")
                return

            try:
                # Preparar datos del reporte
                from datetime import datetime
                import os

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                # Obtener datos
                clientes = consultas.obtener_clientes()
                materiales = consultas.obtener_materiales()
                pedidos = consultas.obtener_pedidos()
                servicios = consultas.obtener_servicios()

                # Preparar datos para exportación
                datos = []

                # Sección 1: Resumen general
                datos.append(["=== REPORTE DEL SISTEMA ===", "", ""])
                datos.append(["Fecha:", datetime.now().strftime('%d/%m/%Y %H:%M'), ""])
                datos.append(["", "", ""])
                datos.append(["ESTADÍSTICAS GENERALES", "", ""])
                datos.append(["Total de Clientes:", len(clientes), ""])
                datos.append(["Total de Pedidos:", len(pedidos), ""])
                datos.append(["Total de Servicios:", len(servicios), ""])
                datos.append(["Total de Materiales:", len(materiales), ""])
                datos.append(["", "", ""])

                # Sección 2: Materiales con stock bajo
                materiales_bajo = consultas.obtener_materiales_bajo_stock()
                datos.append(["ALERTAS DE INVENTARIO", "", ""])
                datos.append(["Material", "Stock Actual", "Stock Mínimo"])
                for mat in materiales_bajo:
                    datos.append([mat['nombre_material'], mat['cantidad_stock'], mat['stock_minimo']])

                columnas = ["Categoría", "Valor", "Detalle"]

                # Crear nombre de archivo
                extensiones = {"excel": "xlsx", "pdf": "pdf", "csv": "csv"}
                nombre_archivo = f"reporte_sistema_{timestamp}.{extensiones[formato]}"
                ruta_completa = os.path.join(directorio, nombre_archivo)

                # Exportar según formato
                if formato == "csv":
                    exito = exportar_a_csv(datos, columnas, ruta_completa)
                elif formato == "excel":
                    exito = exportar_a_excel(datos, columnas, ruta_completa, "Reporte del Sistema")
                else:  # pdf
                    exito = exportar_a_pdf(datos, columnas, ruta_completa, "Reporte del Sistema", 'portrait')

                if exito:
                    messagebox.showinfo("Éxito", f"Reporte exportado correctamente:\n{ruta_completa}")
                    dialogo.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo exportar el reporte")

            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")

        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray"
        )
        btn_cancelar.pack(side="left", padx=10)

        btn_exportar = ctk.CTkButton(
            frame_botones,
            text="Exportar",
            command=exportar,
            width=120,
            height=40,
            fg_color=COLOR_SUCCESS
        )
        btn_exportar.pack(side="left", padx=10)