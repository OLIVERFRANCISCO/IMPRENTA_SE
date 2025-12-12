"""
Panel de Administración del Sistema
Gestión de usuarios, roles y permisos
Solo accesible para administradores
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


class PanelAdmin(ctk.CTkFrame):
    """
    Panel de administración con tabs para gestión de:
    - Usuarios
    - Roles
    - Permisos
    """
    
    # Lista de paneles disponibles en el sistema
    PANELES_SISTEMA = [
        ('panel_pedidos', 'Gestión de Pedidos'),
        ('panel_pedidos_clientes', 'Visualización de Pedidos'),
        ('panel_clientes', 'Gestión de Clientes'),
        ('panel_servicios', 'Gestión de Servicios'),
        ('panel_inventario', 'Gestión de Inventario'),
        ('panel_maquinas', 'Gestión de Máquinas'),
        ('panel_reportes', 'Reportes y Estadísticas')
    ]
    
    # Tipos de permisos disponibles
    TIPOS_PERMISOS = ['ver', 'crear', 'editar', 'eliminar']
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Verificar que sea admin
        if not auth_service.is_admin():
            self._mostrar_acceso_denegado()
            return
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._crear_header()
        self._crear_tabs()
    
    def _toggle_password(self, entry, button):
        """Alterna entre mostrar y ocultar contraseña"""
        if entry.cget("show") == "●":
            entry.configure(show="")
            button.configure(text="👁️‍🗨️")
        else:
            entry.configure(show="●")
            button.configure(text="👁️")
    
    def _mostrar_acceso_denegado(self):
        """Muestra mensaje de acceso denegado"""
        ctk.CTkLabel(
            self,
            text="🚫 Acceso Denegado",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_DANGER
        ).pack(expand=True)
        
        ctk.CTkLabel(
            self,
            text="Solo los administradores pueden acceder a este panel",
            font=ctk.CTkFont(size=14)
        ).pack()
    
    def _crear_header(self):
        """Crea el encabezado del panel"""
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.grid(row=0, column=0, pady=(0, 20), padx=10, sticky="ew")
        frame_header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_header,
            text="⚙️ Panel de Administración",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=COLOR_PRIMARY
        ).grid(row=0, column=0, sticky="w")
        
        # Mostrar usuario actual
        usuario_actual = auth_service.get_username()
        ctk.CTkLabel(
            frame_header,
            text=f"👤 {usuario_actual} (Admin)",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).grid(row=0, column=1, sticky="e")
    
    def _crear_tabs(self):
        """Crea el sistema de pestañas"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Crear pestañas
        self.tab_usuarios = self.tabview.add("👤 Usuarios")
        self.tab_roles = self.tabview.add("🎭 Roles")
        self.tab_permisos = self.tabview.add("🔐 Permisos")
        
        # Configurar cada tab
        self._configurar_tab_usuarios()
        self._configurar_tab_roles()
        self._configurar_tab_permisos()
    
    # ==================== TAB USUARIOS ====================
    
    def _configurar_tab_usuarios(self):
        """Configura la pestaña de gestión de usuarios"""
        self.tab_usuarios.grid_rowconfigure(1, weight=1)
        self.tab_usuarios.grid_columnconfigure(0, weight=1)
        
        # Botones de acción
        frame_acciones_usuarios = ctk.CTkFrame(self.tab_usuarios, fg_color="transparent")
        frame_acciones_usuarios.grid(row=0, column=0, pady=10, sticky="ew")
        
        ctk.CTkButton(
            frame_acciones_usuarios,
            text="➕ Nuevo Usuario",
            command=self._crear_usuario,
            height=40,
            fg_color=COLOR_SUCCESS,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_acciones_usuarios,
            text="🔄 Actualizar",
            command=self._cargar_usuarios,
            height=40,
            width=120
        ).pack(side="left", padx=5)
        
        # Tabla de usuarios
        self.scroll_usuarios = ctk.CTkScrollableFrame(self.tab_usuarios)
        self.scroll_usuarios.grid(row=1, column=0, sticky="nsew")
        self.scroll_usuarios.grid_columnconfigure(0, weight=1)
        
        self._cargar_usuarios()
    
    def _cargar_usuarios(self):
        """Carga y muestra la lista de usuarios"""
        # Limpiar
        for widget in self.scroll_usuarios.winfo_children():
            widget.destroy()
        
        # Obtener usuarios
        usuarios = consultas_auth.obtener_usuarios()
        
        if not usuarios:
            ctk.CTkLabel(
                self.scroll_usuarios,
                text="No hay usuarios registrados",
                font=ctk.CTkFont(size=14)
            ).pack(pady=20)
            return
        
        # Encabezados
        frame_header = ctk.CTkFrame(self.scroll_usuarios, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        headers = ["ID", "Usuario", "Rol", "Último Acceso", "Estado", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                frame_header,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=10)
        
        # Filas de usuarios
        for idx, usuario in enumerate(usuarios):
            self._crear_fila_usuario(usuario, idx + 1)
    
    def _crear_fila_usuario(self, usuario, fila):
        """Crea una fila con datos de usuario"""
        color = "gray25" if fila % 2 == 0 else "gray20"
        frame_fila = ctk.CTkFrame(self.scroll_usuarios, fg_color=color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        # ID
        ctk.CTkLabel(frame_fila, text=str(usuario['id'])).grid(row=0, column=0, padx=10, pady=10)
        
        # Username
        ctk.CTkLabel(
            frame_fila,
            text=usuario['username'],
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, padx=10, pady=10)
        
        # Rol
        ctk.CTkLabel(frame_fila, text=usuario['nombre_rol']).grid(row=0, column=2, padx=10, pady=10)
        
        # Último acceso
        ultimo_acceso = usuario.get('ultimo_acceso', 'Nunca')
        if ultimo_acceso and ultimo_acceso != 'Nunca':
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(ultimo_acceso)
                ultimo_acceso = dt.strftime('%d/%m/%Y %H:%M')
            except:
                pass
        ctk.CTkLabel(frame_fila, text=ultimo_acceso, font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=10, pady=10)
        
        # Estado
        estado = "✓ Activo" if usuario.get('activo', True) else "✗ Inactivo"
        color_estado = COLOR_SUCCESS if usuario.get('activo', True) else COLOR_DANGER
        ctk.CTkLabel(
            frame_fila,
            text=estado,
            text_color=color_estado,
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=4, padx=10, pady=10)
        
        # Acciones
        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=5, padx=10, pady=5)
        
        ctk.CTkButton(
            frame_acciones,
            text="✏️",
            command=lambda u=usuario: self._editar_usuario(u),
            width=40,
            height=30,
            fg_color=COLOR_PRIMARY
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            frame_acciones,
            text="🔑",
            command=lambda u=usuario: self._cambiar_password_usuario(u),
            width=40,
            height=30,
            fg_color=COLOR_WARNING
        ).pack(side="left", padx=2)
        
        if usuario['nombre_rol'].lower() != 'admin':  # No eliminar admins
            ctk.CTkButton(
                frame_acciones,
                text="🗑️",
                command=lambda u=usuario: self._eliminar_usuario(u),
                width=40,
                height=30,
                fg_color=COLOR_DANGER
            ).pack(side="left", padx=2)
    
    def _crear_usuario(self):
        """Muestra diálogo para crear usuario"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Usuario")
        dialogo.geometry("450x500")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (500 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(dialogo)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="➕ Nuevo Usuario", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        # Username
        ctk.CTkLabel(frame, text="Nombre de Usuario *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_username = ctk.CTkEntry(frame, width=380, height=40, placeholder_text="Mínimo 3 caracteres")
        entry_username.pack(padx=10, pady=(5, 15))
        entry_username.focus()
        
        # Password
        ctk.CTkLabel(frame, text="Contraseña *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        frame_password = ctk.CTkFrame(frame, fg_color="transparent")
        frame_password.pack(padx=10, pady=(5, 15))
        entry_password = ctk.CTkEntry(frame_password, width=330, height=40, placeholder_text="Mínimo 6 caracteres", show="●")
        entry_password.pack(side="left", padx=(0, 5))
        btn_toggle_password = ctk.CTkButton(
            frame_password,
            text="👁️",
            command=lambda: self._toggle_password(entry_password, btn_toggle_password),
            width=40,
            height=40,
            fg_color="gray"
        )
        btn_toggle_password.pack(side="left")
        
        # Confirmar password
        ctk.CTkLabel(frame, text="Confirmar Contraseña *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        frame_password2 = ctk.CTkFrame(frame, fg_color="transparent")
        frame_password2.pack(padx=10, pady=(5, 15))
        entry_password2 = ctk.CTkEntry(frame_password2, width=330, height=40, placeholder_text="Repetir contraseña", show="●")
        entry_password2.pack(side="left", padx=(0, 5))
        btn_toggle_password2 = ctk.CTkButton(
            frame_password2,
            text="👁️",
            command=lambda: self._toggle_password(entry_password2, btn_toggle_password2),
            width=40,
            height=40,
            fg_color="gray"
        )
        btn_toggle_password2.pack(side="left")
        
        # Rol
        ctk.CTkLabel(frame, text="Rol *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        roles = consultas_auth.obtener_roles()
        combo_rol = ctk.CTkComboBox(
            frame,
            values=[r['nombre_rol'] for r in roles],
            width=380,
            height=40
        )
        combo_rol.pack(padx=10, pady=(5, 15))
        if roles:
            combo_rol.set(roles[0]['nombre_rol'])
        
        # Label error
        label_error = ctk.CTkLabel(frame, text="", text_color=COLOR_DANGER, wraplength=360)
        label_error.pack(pady=10)
        
        def guardar():
            username = entry_username.get().strip()
            password = entry_password.get()
            password2 = entry_password2.get()
            rol_nombre = combo_rol.get()
            
            if not username or len(username) < 3:
                label_error.configure(text="❌ El username debe tener al menos 3 caracteres")
                return
            
            if not password or len(password) < 6:
                label_error.configure(text="❌ La contraseña debe tener al menos 6 caracteres")
                return
            
            if password != password2:
                label_error.configure(text="❌ Las contraseñas no coinciden")
                return
            
            # Buscar ID del rol
            rol_id = None
            for rol in roles:
                if rol['nombre_rol'] == rol_nombre:
                    rol_id = rol['id']
                    break
            
            try:
                id_usuario = consultas_auth.crear_usuario(username, password, rol_id)
                dialogo.destroy()
                self._cargar_usuarios()
                messagebox.showinfo("Éxito", f"Usuario '{username}' creado correctamente")
            except Exception as e:
                label_error.configure(text=f"❌ {str(e)}")
        
        # Botones
        frame_btn = ctk.CTkFrame(frame, fg_color="transparent")
        frame_btn.pack(pady=15)
        
        ctk.CTkButton(
            frame_btn,
            text="✓ Guardar",
            command=guardar,
            width=150,
            height=40,
            fg_color=COLOR_SUCCESS
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_btn,
            text="✗ Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray"
        ).pack(side="left", padx=5)
    
    def _editar_usuario(self, usuario):
        """Muestra diálogo para editar usuario"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Editar Usuario")
        dialogo.geometry("450x500")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (400 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(dialogo)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="✏️ Editar Usuario", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        # Username
        ctk.CTkLabel(frame, text="Nombre de Usuario *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_username = ctk.CTkEntry(frame, width=380, height=40)
        entry_username.insert(0, usuario['username'])
        entry_username.pack(padx=10, pady=(5, 15))
        
        # Rol
        ctk.CTkLabel(frame, text="Rol *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        roles = consultas_auth.obtener_roles()
        combo_rol = ctk.CTkComboBox(
            frame,
            values=[r['nombre_rol'] for r in roles],
            width=380,
            height=40
        )
        combo_rol.set(usuario['nombre_rol'])
        combo_rol.pack(padx=10, pady=(5, 15))
        
        # Estado
        ctk.CTkLabel(frame, text="Estado", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        switch_activo = ctk.CTkSwitch(frame, text="Usuario Activo")
        if usuario.get('activo', True):
            switch_activo.select()
        switch_activo.pack(padx=10, pady=(5, 15), anchor="w")
        
        # Label error
        label_error = ctk.CTkLabel(frame, text="", text_color=COLOR_DANGER, wraplength=360)
        label_error.pack(pady=10)
        
        def guardar():
            username = entry_username.get().strip()
            rol_nombre = combo_rol.get()
            activo = 1 if switch_activo.get() else 0
            
            if not username or len(username) < 3:
                label_error.configure(text="❌ El username debe tener al menos 3 caracteres")
                return
            
            # Buscar ID del rol
            rol_id = None
            for rol in roles:
                if rol['nombre_rol'] == rol_nombre:
                    rol_id = rol['id']
                    break
            
            try:
                consultas_auth.actualizar_usuario(
                    usuario['id'],
                    username=username,
                    rol_id=rol_id,
                    activo=activo
                )
                dialogo.destroy()
                self._cargar_usuarios()
                messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
            except Exception as e:
                label_error.configure(text=f"❌ {str(e)}")
        
        # Botones
        frame_btn = ctk.CTkFrame(frame, fg_color="transparent")
        frame_btn.pack(pady=15)
        
        ctk.CTkButton(
            frame_btn,
            text="✓ Guardar",
            command=guardar,
            width=150,
            height=40,
            fg_color=COLOR_SUCCESS
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_btn,
            text="✗ Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray"
        ).pack(side="left", padx=5)
    
    def _cambiar_password_usuario(self, usuario):
        """Muestra diálogo para cambiar contraseña"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Cambiar Contraseña")
        dialogo.geometry("450x350")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (350 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(dialogo)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"🔑 Cambiar Contraseña\n{usuario['username']}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Nueva password
        ctk.CTkLabel(frame, text="Nueva Contraseña *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        frame_password = ctk.CTkFrame(frame, fg_color="transparent")
        frame_password.pack(padx=10, pady=(5, 15))
        entry_password = ctk.CTkEntry(frame_password, width=330, height=40, placeholder_text="Mínimo 6 caracteres", show="●")
        entry_password.pack(side="left", padx=(0, 5))
        btn_toggle_password = ctk.CTkButton(
            frame_password,
            text="👁️",
            command=lambda: self._toggle_password(entry_password, btn_toggle_password),
            width=40,
            height=40,
            fg_color="gray"
        )
        btn_toggle_password.pack(side="left")
        entry_password.focus()
        
        # Confirmar
        ctk.CTkLabel(frame, text="Confirmar Contraseña *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        frame_password2 = ctk.CTkFrame(frame, fg_color="transparent")
        frame_password2.pack(padx=10, pady=(5, 15))
        entry_password2 = ctk.CTkEntry(frame_password2, width=330, height=40, placeholder_text="Repetir contraseña", show="●")
        entry_password2.pack(side="left", padx=(0, 5))
        btn_toggle_password2 = ctk.CTkButton(
            frame_password2,
            text="👁️",
            command=lambda: self._toggle_password(entry_password2, btn_toggle_password2),
            width=40,
            height=40,
            fg_color="gray"
        )
        btn_toggle_password2.pack(side="left")
        
        # Label error
        label_error = ctk.CTkLabel(frame, text="", text_color=COLOR_DANGER, wraplength=360)
        label_error.pack(pady=10)
        
        def guardar():
            password = entry_password.get()
            password2 = entry_password2.get()
            
            if not password or len(password) < 6:
                label_error.configure(text="❌ La contraseña debe tener al menos 6 caracteres")
                return
            
            if password != password2:
                label_error.configure(text="❌ Las contraseñas no coinciden")
                return
            
            try:
                consultas_auth.actualizar_usuario(usuario['id'], password=password)
                dialogo.destroy()
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
            except Exception as e:
                label_error.configure(text=f"❌ {str(e)}")
        
        # Botones
        frame_btn = ctk.CTkFrame(frame, fg_color="transparent")
        frame_btn.pack(pady=15)
        
        ctk.CTkButton(
            frame_btn,
            text="✓ Cambiar",
            command=guardar,
            width=150,
            height=40,
            fg_color=COLOR_SUCCESS
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_btn,
            text="✗ Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray"
        ).pack(side="left", padx=5)
    
    def _eliminar_usuario(self, usuario):
        """Elimina un usuario (soft delete)"""
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el usuario '{usuario['username']}'?\n\n"
            "El usuario será desactivado y no podrá iniciar sesión."
        ):
            try:
                consultas_auth.eliminar_usuario(usuario['id'])
                self._cargar_usuarios()
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el usuario:\n{str(e)}")
    
    # ==================== TAB ROLES ====================
    
    def _configurar_tab_roles(self):
        """Configura la pestaña de gestión de roles"""
        self.tab_roles.grid_rowconfigure(1, weight=1)
        self.tab_roles.grid_columnconfigure(0, weight=1)
        
        # Botones de acción
        frame_acciones_roles = ctk.CTkFrame(self.tab_roles, fg_color="transparent")
        frame_acciones_roles.grid(row=0, column=0, pady=10, sticky="ew")
        
        ctk.CTkButton(
            frame_acciones_roles,
            text="➕ Nuevo Rol",
            command=self._crear_rol,
            height=40,
            fg_color=COLOR_SUCCESS,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_acciones_roles,
            text="🔄 Actualizar",
            command=self._cargar_roles,
            height=40,
            width=120
        ).pack(side="left", padx=5)
        
        # Tabla de roles
        self.scroll_roles = ctk.CTkScrollableFrame(self.tab_roles)
        self.scroll_roles.grid(row=1, column=0, sticky="nsew")
        self.scroll_roles.grid_columnconfigure(0, weight=1)
        
        self._cargar_roles()
    
    def _cargar_roles(self):
        """Carga y muestra la lista de roles"""
        # Limpiar
        for widget in self.scroll_roles.winfo_children():
            widget.destroy()
        
        # Obtener roles
        roles = consultas_auth.obtener_roles()
        
        if not roles:
            ctk.CTkLabel(
                self.scroll_roles,
                text="No hay roles registrados",
                font=ctk.CTkFont(size=14)
            ).pack(pady=20)
            return
        
        # Encabezados
        frame_header = ctk.CTkFrame(self.scroll_roles, fg_color=COLOR_PRIMARY)
        frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame_header.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        headers = ["ID", "Nombre del Rol", "Total Usuarios", "Total Permisos", "Acciones"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                frame_header,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            ).grid(row=0, column=i, padx=10, pady=10)
        
        # Filas de roles
        for idx, rol in enumerate(roles):
            self._crear_fila_rol(rol, idx + 1)
    
    def _crear_fila_rol(self, rol, fila):
        """Crea una fila con datos de rol"""
        color = "gray25" if fila % 2 == 0 else "gray20"
        frame_fila = ctk.CTkFrame(self.scroll_roles, fg_color=color)
        frame_fila.grid(row=fila, column=0, sticky="ew", pady=2)
        frame_fila.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        # ID
        ctk.CTkLabel(frame_fila, text=str(rol['id'])).grid(row=0, column=0, padx=10, pady=10)
        
        # Nombre
        ctk.CTkLabel(
            frame_fila,
            text=rol['nombre_rol'],
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, padx=10, pady=10)
        
        # Total usuarios
        ctk.CTkLabel(frame_fila, text=str(rol.get('total_usuarios', 0))).grid(row=0, column=2, padx=10, pady=10)
        
        # Total permisos
        ctk.CTkLabel(frame_fila, text=str(rol.get('total_permisos', 0))).grid(row=0, column=3, padx=10, pady=10)
        
        # Acciones
        frame_acciones = ctk.CTkFrame(frame_fila, fg_color="transparent")
        frame_acciones.grid(row=0, column=4, padx=10, pady=5)
        
        ctk.CTkButton(
            frame_acciones,
            text="✏️",
            command=lambda r=rol: self._editar_rol(r),
            width=40,
            height=30,
            fg_color=COLOR_PRIMARY
        ).pack(side="left", padx=2)
        
        # Solo permitir eliminar roles personalizados (no admin ni empleado)
        if rol['nombre_rol'].lower() not in ['admin', 'empleado']:
            ctk.CTkButton(
                frame_acciones,
                text="🗑️",
                command=lambda r=rol: self._eliminar_rol(r),
                width=40,
                height=30,
                fg_color=COLOR_DANGER
            ).pack(side="left", padx=2)
    
    def _crear_rol(self):
        """Muestra diálogo para crear rol"""
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Nuevo Rol")
        dialogo.geometry("400x250")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (250 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(dialogo)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="➕ Nuevo Rol", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        # Nombre del rol
        ctk.CTkLabel(frame, text="Nombre del Rol *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_nombre = ctk.CTkEntry(frame, width=330, height=40, placeholder_text="Ej: Vendedor, Operario")
        entry_nombre.pack(padx=10, pady=(5, 15))
        entry_nombre.focus()
        
        # Label error
        label_error = ctk.CTkLabel(frame, text="", text_color=COLOR_DANGER, wraplength=310)
        label_error.pack(pady=10)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            
            if not nombre or len(nombre) < 3:
                label_error.configure(text="❌ El nombre debe tener al menos 3 caracteres")
                return
            
            try:
                consultas_auth.crear_rol(nombre)
                dialogo.destroy()
                self._cargar_roles()
                messagebox.showinfo("Éxito", f"Rol '{nombre}' creado correctamente")
            except Exception as e:
                label_error.configure(text=f"❌ {str(e)}")
        
        # Botones
        frame_btn = ctk.CTkFrame(frame, fg_color="transparent")
        frame_btn.pack(pady=15)
        
        ctk.CTkButton(
            frame_btn,
            text="✓ Crear",
            command=guardar,
            width=150,
            height=40,
            fg_color=COLOR_SUCCESS
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_btn,
            text="✗ Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray"
        ).pack(side="left", padx=5)
    
    def _editar_rol(self, rol):
        """Muestra diálogo para editar rol"""
        # No permitir editar admin o empleado
        if rol['nombre_rol'].lower() in ['admin', 'empleado']:
            messagebox.showwarning(
                "Acción No Permitida",
                "No se pueden editar los roles base del sistema (Admin y Empleado)"
            )
            return
        
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Editar Rol")
        dialogo.geometry("400x350")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Centrar
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialogo.winfo_screenheight() // 2) - (250 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(dialogo)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="✏️ Editar Rol", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        # Nombre del rol
        ctk.CTkLabel(frame, text="Nombre del Rol *", font=ctk.CTkFont(size=13)).pack(anchor="w", padx=10)
        entry_nombre = ctk.CTkEntry(frame, width=330, height=40)
        entry_nombre.insert(0, rol['nombre_rol'])
        entry_nombre.pack(padx=10, pady=(5, 15))
        
        # Label error
        label_error = ctk.CTkLabel(frame, text="", text_color=COLOR_DANGER, wraplength=310)
        label_error.pack(pady=10)
        
        def guardar():
            nombre = entry_nombre.get().strip()
            
            if not nombre or len(nombre) < 3:
                label_error.configure(text="❌ El nombre debe tener al menos 3 caracteres")
                return
            
            try:
                consultas_auth.actualizar_rol(rol['id'], nombre)
                dialogo.destroy()
                self._cargar_roles()
                messagebox.showinfo("Éxito", "Rol actualizado correctamente")
            except Exception as e:
                label_error.configure(text=f"❌ {str(e)}")
        
        # Botones
        frame_btn = ctk.CTkFrame(frame, fg_color="transparent")
        frame_btn.pack(pady=15)
        
        ctk.CTkButton(
            frame_btn,
            text="✓ Guardar",
            command=guardar,
            width=150,
            height=40,
            fg_color=COLOR_SUCCESS
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_btn,
            text="✗ Cancelar",
            command=dialogo.destroy,
            width=120,
            height=40,
            fg_color="gray"
        ).pack(side="left", padx=5)
    
    def _eliminar_rol(self, rol):
        """Elimina un rol"""
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el rol '{rol['nombre_rol']}'?\n\n"
            "Esta acción no se puede deshacer."
        ):
            try:
                consultas_auth.eliminar_rol(rol['id'])
                self._cargar_roles()
                messagebox.showinfo("Éxito", "Rol eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el rol:\n{str(e)}")
    
    # ==================== TAB PERMISOS ====================
    
    def _configurar_tab_permisos(self):
        """Configura la pestaña de gestión de permisos"""
        self.tab_permisos.grid_rowconfigure(1, weight=1)
        self.tab_permisos.grid_columnconfigure(0, weight=1)
        
        # Selector de rol
        frame_selector = ctk.CTkFrame(self.tab_permisos, fg_color="transparent")
        frame_selector.grid(row=0, column=0, pady=10, sticky="ew", padx=10)
        
        ctk.CTkLabel(
            frame_selector,
            text="Seleccione un rol para configurar sus permisos:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        roles = consultas_auth.obtener_roles()
        self.combo_rol_permisos = ctk.CTkComboBox(
            frame_selector,
            values=[r['nombre_rol'] for r in roles if r['nombre_rol'].lower() != 'admin'],
            width=200,
            height=40,
            command=self._cargar_permisos_rol
        )
        self.combo_rol_permisos.pack(side="left", padx=10)
        if len(roles) > 1:
            # Seleccionar "empleado" por defecto si existe
            for r in roles:
                if r['nombre_rol'].lower() == 'empleado':
                    self.combo_rol_permisos.set(r['nombre_rol'])
                    break
        
        ctk.CTkButton(
            frame_selector,
            text="💾 Guardar Cambios",
            command=self._guardar_permisos,
            height=40,
            width=150,
            fg_color=COLOR_SUCCESS
        ).pack(side="right", padx=10)
        
        # Área de permisos
        self.scroll_permisos = ctk.CTkScrollableFrame(self.tab_permisos)
        self.scroll_permisos.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Diccionario para almacenar checkboxes
        self.permisos_checkboxes = {}
        
        self._cargar_permisos_rol()
    
    def _cargar_permisos_rol(self, *args):
        """Carga los permisos del rol seleccionado"""
        # Limpiar
        for widget in self.scroll_permisos.winfo_children():
            widget.destroy()
        
        self.permisos_checkboxes = {}
        
        rol_nombre = self.combo_rol_permisos.get()
        if not rol_nombre:
            return
        
        # Buscar ID del rol
        roles = consultas_auth.obtener_roles()
        rol_id = None
        for rol in roles:
            if rol['nombre_rol'] == rol_nombre:
                rol_id = rol['id']
                break
        
        if not rol_id:
            return
        
        # Obtener permisos actuales
        permisos_actuales = consultas_auth.obtener_permisos_por_rol(rol_id)
        permisos_set = {(p['panel'], p['permiso']) for p in permisos_actuales}
        
        # Crear matriz de permisos
        for panel_id, panel_nombre in self.PANELES_SISTEMA:
            frame_panel = ctk.CTkFrame(self.scroll_permisos, fg_color="gray20", corner_radius=10)
            frame_panel.pack(fill="x", pady=10, padx=10)
            
            # Título del panel
            ctk.CTkLabel(
                frame_panel,
                text=panel_nombre,
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(anchor="w", padx=15, pady=(15, 10))
            
            # Checkboxes de permisos
            frame_checks = ctk.CTkFrame(frame_panel, fg_color="transparent")
            frame_checks.pack(fill="x", padx=15, pady=(0, 15))
            
            self.permisos_checkboxes[panel_id] = {}
            
            for permiso in self.TIPOS_PERMISOS:
                check = ctk.CTkCheckBox(
                    frame_checks,
                    text=permiso.capitalize(),
                    font=ctk.CTkFont(size=13)
                )
                check.pack(side="left", padx=10)
                
                # Marcar si tiene el permiso
                if (panel_id, permiso) in permisos_set:
                    check.select()
                
                self.permisos_checkboxes[panel_id][permiso] = check
    
    def _guardar_permisos(self):
        """Guarda los permisos configurados"""
        rol_nombre = self.combo_rol_permisos.get()
        if not rol_nombre:
            messagebox.showwarning("Advertencia", "Seleccione un rol")
            return
        
        # Buscar ID del rol
        roles = consultas_auth.obtener_roles()
        rol_id = None
        for rol in roles:
            if rol['nombre_rol'] == rol_nombre:
                rol_id = rol['id']
                break
        
        if not rol_id:
            return
        
        # Construir diccionario de permisos
        permisos_dict = {}
        for panel_id, checkboxes in self.permisos_checkboxes.items():
            permisos_dict[panel_id] = []
            for permiso, checkbox in checkboxes.items():
                if checkbox.get():
                    permisos_dict[panel_id].append(permiso)
        
        try:
            consultas_auth.configurar_permisos_rol(rol_id, permisos_dict)
            messagebox.showinfo("Éxito", f"Permisos del rol '{rol_nombre}' guardados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar los permisos:\n{str(e)}")
