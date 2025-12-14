"""
Pantalla de Login
Permite a los usuarios autenticarse en el sistema
"""
import customtkinter as ctk
from tkinter import messagebox
from app.config import (
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    COLOR_DANGER,
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)
from app.database.consultas_auth import autenticar_usuario
from app.logic.auth_service import auth_service


class LoginWindow(ctk.CTk):
    """
    Ventana de login del sistema
    
    Permite autenticación de usuarios y redirige
    según el rol a la interfaz correspondiente
    """
    
    def __init__(self):
        super().__init__()
        
        self.title("Sistema de Gestión Imprenta - Login")
        self.geometry("500x650")
        self.resizable(False, False)
        
        # Configurar tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Centrar ventana
        self._centrar_ventana()
        
        # Variable para almacenar resultado
        self.login_exitoso = False
        
        # Crear interfaz
        self._crear_interfaz()
    
    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = 500
        height = 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _crear_interfaz(self):
        """Crea la interfaz del login"""
        
        # Contenedor principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Logo/Título
        ctk.CTkLabel(
            main_frame,
            text="🖨️",
            font=ctk.CTkFont(size=72)
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            main_frame,
            text="Sistema de Gestión",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLOR_PRIMARY
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            main_frame,
            text="Imprenta Expert",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(0, 40))
        
        # Frame del formulario
        form_frame = ctk.CTkFrame(main_frame, fg_color="gray20", corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título del formulario
        ctk.CTkLabel(
            form_frame,
            text="Iniciar Sesión",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(30, 30))
        
        # Campo Usuario
        ctk.CTkLabel(
            form_frame,
            text="Usuario",
            font=ctk.CTkFont(size=14),
            anchor="w"
        ).pack(padx=40, pady=(0, 5), fill="x")
        
        self.entry_username = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ingrese su usuario",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.entry_username.pack(padx=40, pady=(0, 20), fill="x")
        self.entry_username.focus()
        
        # Campo Contraseña
        ctk.CTkLabel(
            form_frame,
            text="Contraseña",
            font=ctk.CTkFont(size=14),
            anchor="w"
        ).pack(padx=40, pady=(0, 5), fill="x")
        
        self.entry_password = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ingrese su contraseña",
            show="●",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.entry_password.pack(padx=40, pady=(0, 10), fill="x")
        
        # Label de error
        self.label_error = ctk.CTkLabel(
            form_frame,
            text="",
            text_color=COLOR_DANGER,
            font=ctk.CTkFont(size=12),
            wraplength=380
        )
        self.label_error.pack(pady=(0, 15))
        
        # Botón Ingresar
        self.btn_login = ctk.CTkButton(
            form_frame,
            text="Ingresar",
            command=self._intentar_login,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            corner_radius=10
        )
        self.btn_login.pack(padx=40, pady=(10, 30), fill="x")
        
        # Bind Enter key
        self.entry_password.bind("<Return>", lambda e: self._intentar_login())
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus())
        
        # Footer
        ctk.CTkLabel(
            main_frame,
            text="Sistema Experto de Gestión • v2.0.0",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(side="bottom", pady=(10, 0))
    
    def _intentar_login(self):
        """Procesa el intento de login"""
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        
        # Validar campos
        if not username:
            self.label_error.configure(text="❌ Por favor ingrese su usuario")
            self.entry_username.focus()
            return
        
        if not password:
            self.label_error.configure(text="❌ Por favor ingrese su contraseña")
            self.entry_password.focus()
            return
        
        # Deshabilitar botón mientras procesa
        self.btn_login.configure(state="disabled", text="Verificando...")
        self.label_error.configure(text="")
        self.update()
        
        try:
            # Autenticar usuario
            usuario = autenticar_usuario(username, password)
            
            if usuario:
                # Login exitoso
                auth_service.login(usuario)
                self.login_exitoso = True
                
                # Mensaje de bienvenida
                messagebox.showinfo(
                    "Login Exitoso",
                    f"¡Bienvenido {usuario['username']}!\n\n"
                    f"Rol: {usuario['nombre_rol']}"
                )
                
                # Cerrar ventana de login
                self.destroy()
            else:
                # Credenciales inválidas
                self.label_error.configure(
                    text="❌ Usuario o contraseña incorrectos"
                )
                self.entry_password.delete(0, "end")
                self.entry_password.focus()
                self.btn_login.configure(state="normal", text="Ingresar")
        
        except Exception as e:
            self.label_error.configure(
                text=f"❌ Error al iniciar sesión: {str(e)}"
            )
            self.btn_login.configure(state="normal", text="Ingresar")


def mostrar_login():
    """
    Muestra la ventana de login y retorna si fue exitoso
    
    Returns:
        bool: True si el login fue exitoso
    """
    login_window = LoginWindow()
    login_window.mainloop()
    return login_window.login_exitoso
