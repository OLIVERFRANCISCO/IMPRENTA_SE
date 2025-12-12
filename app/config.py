"""
Configuración global de la aplicación
Contiene constantes, rutas y configuraciones del sistema
"""
import os
from pathlib import Path

# ========== RUTAS DEL PROYECTO ==========
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = BASE_DIR / "imprenta.db"

# ========== CONFIGURACIÓN DE LA INTERFAZ ==========
# Colores del tema
COLOR_PRIMARY = "#1f538d"
COLOR_SECONDARY = "#3a7ebf"
COLOR_SUCCESS = "#2ecc71"
COLOR_WARNING = "#f39c12"
COLOR_DANGER = "#e74c3c"
COLOR_BG_DARK = "#2b2b2b"
COLOR_BG_LIGHT = "#f0f0f0"
COLOR_TEXT = "#ffffff"
COLOR_TEXT_DARK = "#000000"

# Tamaños de ventana
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 600

# Fuentes
FONT_TITLE = ("Segoe UI", 24, "bold")
FONT_SUBTITLE = ("Segoe UI", 18, "bold")
FONT_NORMAL = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 10)

# ========== CONFIGURACIÓN DEL SISTEMA EXPERTO ==========
# Márgenes de ganancia (%)
MARGEN_GANANCIA_MINIMO = 30
MARGEN_GANANCIA_NORMAL = 50
MARGEN_GANANCIA_PREMIUM = 70

# Tiempos de producción (horas)
TIEMPO_PRODUCCION_BASE = 24
TIEMPO_COMPRA_MATERIAL = 48
TIEMPO_DISEÑO = 4

# Alertas de inventario
STOCK_MINIMO_PORCENTAJE = 20
STOCK_CRITICO_PORCENTAJE = 10

# Estados de pago
ESTADOS_PAGO = [
    "Pendiente",
    "A cuenta",
    "Cancelado"
]

# Estados de pedido
ESTADOS_PEDIDO = [
    "Pendiente",
    "En Proceso",
    "En producción",
    "Listo",
    "Entregado",
    "Cancelado"
]

# ========== REGLAS DE NEGOCIO ==========
# Tipos de trabajo
TIPOS_TRABAJO = {
    "MERCHANDISING": "Merchandising",
    "FORMATOS": "Formatos",
    "RECUERDOS": "Recuerdos",
    "GIGANTOGRAFIA": "Gigantografía",
    "FORMATERIA": "Formatiería"
}

# Tipos de máquinas
TIPOS_MAQUINA = {
    "PEQUEÑA": "Impresora Pequeña",
    "GRANDE": "Impresora Grande/Plotter",
    "LAMINADORA": "Laminadora"
}

# ========== VALIDACIONES ==========
# Dimensiones máximas (metros)
ANCHO_MAXIMO_IMPRESORA_PEQUENA = 0.45
ANCHO_MAXIMO_PLOTTER = 1.60
LARGO_MAXIMO = 50

# Configuración de máquinas
ANCHO_MAXIMO_MAQUINA = 2.5  # metros para gigantografías

# Horarios de entrega permitidos
HORA_ENTREGA_MINIMA = 8  # 8:00 AM
HORA_ENTREGA_MAXIMA = 20  # 8:00 PM

# Horas mínimas de anticipación para pedidos
HORAS_MINIMAS_ANTICIPACION = 24

# ========== MENSAJES ==========
MSG_ERROR_CONEXION_DB = "Error al conectar con la base de datos"
MSG_EXITO_GUARDAR = "Datos guardados correctamente"
MSG_ERROR_VALIDACION = "Por favor complete todos los campos requeridos"
MSG_STOCK_BAJO = "⚠️ Alerta: Material por agotarse"
MSG_STOCK_CRITICO = "🔴 Crítico: Material agotado"

