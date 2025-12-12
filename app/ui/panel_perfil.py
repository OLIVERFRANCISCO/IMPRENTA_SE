"""
Panel de Perfil de Usuario
Permite al usuario editar su nombre de usuario y contraseña
"""
import customtkinter as ctk
from tkinter import messagebox
from app.config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_WARNING,
    COLOR_DANGER
)
from app.database import consultas_auth
from app.logic.auth_service import auth_service


class PanelPerfil(ctk.CTkFrame):
    """
    Panel para que el usuario edite su perfil
    - Cambiar nombre de usuario
    - Cambiar contraseña
    """
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Verificar autenticación
        if not auth_service.is_authenticated():
            self._mostrar_no_autenticado()
            return
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._crear_interfaz()
    
    def _mostrar_no_autenticado(self):
        """Muestra mensaje si no hay usuario autenticado"""
        ctk.CTkLabel(
            self,
            text="❌ No hay sesión activa",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLOR_DANGER
        ).pack(expand=True)
    
    def _crear_interfaz(self):
        """Crea la interfaz del panel de perfil"""
        # Contenedor principal con scroll
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self._crear_header(scroll_frame)
        
        # Información del usuario actual
        self._crear_info_usuario(scroll_frame)
        
        # Sección editar username
        self._crear_seccion_username(scroll_frame)
        
        # Sección cambiar contraseña
        self._crear_seccion_password(scroll_frame)
    
    def _crear_header(self, parent):
        """Crea el encabezado del panel"""
        frame_header = ctk.CTkFrame(parent, fg_color="transparent")
        frame_header.grid(row=0, column=0, pady=(0, 30), sticky="ew")
        
        ctk.CTkLabel(
            frame_header,
            text="👤 Mi Perfil",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            frame_header,
            text="Administra tu información personal",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack(anchor="w", pady=(5, 0))
    
    def _crear_info_usuario(self, parent):
        """Muestra información actual del usuario"""
        usuario_actual = auth_service.get_usuario_actual()
        
        frame_info = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"), corner_radius=10)
        frame_info.grid(row=1, column=0, pady=(0, 30), sticky="ew", padx=10)
        
        # Título
        ctk.CTkLabel(
            frame_info,
            text="📋 Información Actual",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Grid para datos
        info_grid = ctk.CTkFrame(frame_info, fg_color="transparent")
        info_grid.pack(fill="x", padx=20, pady=(0, 20))
        info_grid.grid_columnconfigure(1, weight=1)
        
        # Username
        ctk.CTkLabel(
            info_grid,
            text="Usuario:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        
        ctk.CTkLabel(
            info_grid,
            text=usuario_actual['username'],
            font=ctk.CTkFont(size=13)
        ).grid(row=0, column=1, sticky="w", pady=5)
        
        # Rol
        ctk.CTkLabel(
            info_grid,
            text="Rol:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 10))
        
        ctk.CTkLabel(
            info_grid,
            text=usuario_actual['nombre_rol'],
            font=ctk.CTkFont(size=13),
            text_color=COLOR_PRIMARY
        ).grid(row=1, column=1, sticky="w", pady=5)
        
        # Fecha de registro
        if usuario_actual.get('fecha_creacion'):
            from datetime import datetime
            try:
                fecha = datetime.fromisoformat(usuario_actual['fecha_creacion'])
                fecha_str = fecha.strftime('%d/%m/%Y')
            except:
                fecha_str = "No disponible"
        else:
            fecha_str = "No disponible"
        
        ctk.CTkLabel(
            info_grid,
            text="Miembro desde:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=2, column=0, sticky="w", pady=5, padx=(0, 10))
        
        ctk.CTkLabel(
            info_grid,
            text=fecha_str,
            font=ctk.CTkFont(size=13)
        ).grid(row=2, column=1, sticky="w", pady=5)
    
    def _crear_seccion_username(self, parent):
        """Crea sección para cambiar username"""
        frame_username = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"), corner_radius=10)
        frame_username.grid(row=2, column=0, pady=(0, 20), sticky="ew", padx=10)
        
        # Título
        ctk.CTkLabel(
            frame_username,
            text="✏️ Cambiar Nombre de Usuario",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Contenido
        content_frame = ctk.CTkFrame(frame_username, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            content_frame,
            text="Nuevo nombre de usuario *",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=(10, 5))
        
        self.entry_nuevo_username = ctk.CTkEntry(
            content_frame,
            width=400,
            height=40,
            placeholder_text="Mínimo 3 caracteres"
        )
        self.entry_nuevo_username.pack(anchor="w", pady=(0, 10))
        
        # Label de error
        self.label_error_username = ctk.CTkLabel(
            content_frame,
            text="",
            text_color=COLOR_DANGER,
            wraplength=380
        )
        self.label_error_username.pack(anchor="w", pady=(0, 10))
        
        # Botón guardar
        ctk.CTkButton(
            content_frame,
            text="💾 Guardar Username",
            command=self._guardar_username,
            height=40,
            width=200,
            fg_color=COLOR_SUCCESS
        ).pack(anchor="w", pady=(10, 0))
    
    def _crear_seccion_password(self, parent):
        """Crea sección para cambiar contraseña"""
        frame_password = ctk.CTkFrame(parent, fg_color=("gray85", "gray20"), corner_radius=10)
        frame_password.grid(row=3, column=0, pady=(0, 20), sticky="ew", padx=10)
        
        # Título
        ctk.CTkLabel(
            frame_password,
            text="🔒 Cambiar Contraseña",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Contenido
        content_frame = ctk.CTkFrame(frame_password, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Contraseña actual
        ctk.CTkLabel(
            content_frame,
            text="Contraseña actual *",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=(10, 5))
        
        frame_actual = ctk.CTkFrame(content_frame, fg_color="transparent")
        frame_actual.pack(fill="x", pady=(0, 15))
        
        self.entry_password_actual = ctk.CTkEntry(
            frame_actual,
            width=400,
            height=40,
            placeholder_text="Contraseña actual",
            show="●"
        )
        self.entry_password_actual.pack(side="left", padx=(0, 10))
        
        self.btn_mostrar_actual = ctk.CTkButton(
            frame_actual,
            text="👁️",
            command=lambda: self._toggle_password(self.entry_password_actual, self.btn_mostrar_actual),
            width=40,
            height=40,
            fg_color="gray"
        )
        self.btn_mostrar_actual.pack(side="left")
        
        # Nueva contraseña
        ctk.CTkLabel(
            content_frame,
            text="Nueva contraseña *",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=(0, 5))
        
        frame_nueva = ctk.CTkFrame(content_frame, fg_color="transparent")
        frame_nueva.pack(fill="x", pady=(0, 15))
        
        self.entry_password_nueva = ctk.CTkEntry(
            frame_nueva,
            width=400,
            height=40,
            placeholder_text="Mínimo 6 caracteres",
            show="●"
        )
        self.entry_password_nueva.pack(side="left", padx=(0, 10))
        
        self.btn_mostrar_nueva = ctk.CTkButton(
            frame_nueva,
            text="👁️",
            command=lambda: self._toggle_password(self.entry_password_nueva, self.btn_mostrar_nueva),
            width=40,
            height=40,
            fg_color="gray"
        )
        self.btn_mostrar_nueva.pack(side="left")
        
        # Confirmar nueva contraseña
        ctk.CTkLabel(
            content_frame,
            text="Confirmar nueva contraseña *",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=(0, 5))
        
        frame_confirmar = ctk.CTkFrame(content_frame, fg_color="transparent")
        frame_confirmar.pack(fill="x", pady=(0, 15))
        
        self.entry_password_confirmar = ctk.CTkEntry(
            frame_confirmar,
            width=400,
            height=40,
            placeholder_text="Repetir contraseña",
            show="●"
        )
        self.entry_password_confirmar.pack(side="left", padx=(0, 10))
        
        self.btn_mostrar_confirmar = ctk.CTkButton(
            frame_confirmar,
            text="👁️",
            command=lambda: self._toggle_password(self.entry_password_confirmar, self.btn_mostrar_confirmar),
            width=40,
            height=40,
            fg_color="gray"
        )
        self.btn_mostrar_confirmar.pack(side="left")
        
        # Label de error
        self.label_error_password = ctk.CTkLabel(
            content_frame,
            text="",
            text_color=COLOR_DANGER,
            wraplength=380
        )
        self.label_error_password.pack(anchor="w", pady=(0, 10))
        
        # Botón guardar
        ctk.CTkButton(
            content_frame,
            text="🔐 Cambiar Contraseña",
            command=self._guardar_password,
            height=40,
            width=200,
            fg_color=COLOR_WARNING
        ).pack(anchor="w", pady=(10, 0))
    
    def _toggle_password(self, entry, button):
        """Muestra/oculta contraseña"""
        if entry.cget("show") == "●":
            entry.configure(show="")
            button.configure(text="👁️‍🗨️")
        else:
            entry.configure(show="●")
            button.configure(text="👁️")
    
    def _guardar_username(self):
        """Guarda el nuevo username"""
        nuevo_username = self.entry_nuevo_username.get().strip()
        usuario_actual = auth_service.get_usuario_actual()
        
        # Limpiar mensaje de error
        self.label_error_username.configure(text="")
        
        # Validaciones
        if not nuevo_username:
            self.label_error_username.configure(text="❌ El nombre de usuario no puede estar vacío")
            return
        
        if len(nuevo_username) < 3:
            self.label_error_username.configure(text="❌ El nombre de usuario debe tener al menos 3 caracteres")
            return
        
        if nuevo_username == usuario_actual['username']:
            self.label_error_username.configure(text="⚠️ Este ya es tu nombre de usuario actual")
            return
        
        # Intentar actualizar
        try:
            consultas_auth.actualizar_usuario(
                usuario_actual['id'],
                username=nuevo_username
            )
            
            # Actualizar sesión
            usuario_actualizado = consultas_auth.obtener_usuario_por_id(usuario_actual['id'])
            auth_service.login(usuario_actualizado)
            
            # Limpiar campo
            self.entry_nuevo_username.delete(0, 'end')
            
            messagebox.showinfo(
                "Éxito",
                f"Tu nombre de usuario ha sido actualizado a '{nuevo_username}'"
            )
            
            # Recargar interfaz
            for widget in self.winfo_children():
                widget.destroy()
            self._crear_interfaz()
            
        except Exception as e:
            self.label_error_username.configure(text=f"❌ {str(e)}")
    
    def _guardar_password(self):
        """Guarda la nueva contraseña"""
        password_actual = self.entry_password_actual.get()
        password_nueva = self.entry_password_nueva.get()
        password_confirmar = self.entry_password_confirmar.get()
        usuario_actual = auth_service.get_usuario_actual()
        
        # Limpiar mensaje de error
        self.label_error_password.configure(text="")
        
        # Validaciones
        if not password_actual or not password_nueva or not password_confirmar:
            self.label_error_password.configure(text="❌ Todos los campos son obligatorios")
            return
        
        if len(password_nueva) < 6:
            self.label_error_password.configure(text="❌ La nueva contraseña debe tener al menos 6 caracteres")
            return
        
        if password_nueva != password_confirmar:
            self.label_error_password.configure(text="❌ Las contraseñas no coinciden")
            return
        
        # Intentar cambiar contraseña
        try:
            consultas_auth.cambiar_password(
                usuario_actual['id'],
                password_actual,
                password_nueva
            )
            
            # Limpiar campos
            self.entry_password_actual.delete(0, 'end')
            self.entry_password_nueva.delete(0, 'end')
            self.entry_password_confirmar.delete(0, 'end')
            
            messagebox.showinfo(
                "Éxito",
                "Tu contraseña ha sido actualizada correctamente"
            )
            
        except Exception as e:
            self.label_error_password.configure(text=f"❌ {str(e)}")
