"""
Panel de reportes y estadísticas
Muestra información resumida del sistema
"""
import customtkinter as ctk
from app.config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER,
    COLOR_WARNING,
    ESTADOS_PEDIDO
)
from app.database import consultas


class PanelReportes(ctk.CTkFrame):
    """Panel de reportes y estadísticas"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título
        self.titulo = ctk.CTkLabel(
            self,
            text="📊 Reportes y Estadísticas",
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
        pedidos_activos = [p for p in pedidos if p['estado_pedido'] not in ['Entregado', 'Cancelado']]

        # Tarjetas de resumen
        row = 0

        # Tarjeta 1: Total de Clientes
        self._crear_tarjeta(
            self.scroll_frame,
            "👥 Total de Clientes",
            str(len(clientes)),
            COLOR_PRIMARY,
            row, 0
        )

        # Tarjeta 2: Pedidos Activos
        self._crear_tarjeta(
            self.scroll_frame,
            "📋 Pedidos Activos",
            str(len(pedidos_activos)),
            COLOR_SUCCESS,
            row, 1
        )

        # Tarjeta 3: Alertas de Inventario
        color_alerta = COLOR_DANGER if materiales_bajo_stock else COLOR_SUCCESS
        self._crear_tarjeta(
            self.scroll_frame,
            "⚠️ Alertas de Stock",
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
            text="📊 Pedidos por Estado",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15, padx=15, anchor="w")

        # Contar pedidos por estado
        estados_count = {}
        for estado in ESTADOS_PEDIDO:
            count = len([p for p in pedidos if p['estado_pedido'] == estado])
            if count > 0:
                estados_count[estado] = count

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
            text="📦 Estado del Inventario",
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
            text="🔄 Actualizar Datos",
            command=self._actualizar_dashboard,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLOR_PRIMARY,
            width=200
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_acciones,
            text="📄 Exportar Reporte (Próximamente)",
            command=lambda: None,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="gray",
            width=280,
            state="disabled"
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
        """Recarga los datos del dashboard"""
        # Limpiar frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Recrear dashboard
        self._crear_dashboard()

