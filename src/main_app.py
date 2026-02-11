import tkinter as tk
from tkinter import messagebox
from src.voice_service import VoiceService
from src.auth_dao import AuthDAO

class VoiceAuditApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VoiceAudit - Acceso por Voz")
        self.root.geometry("400x350")

        self.voice_service = VoiceService()
        self.dao = AuthDAO()

        # --- UI Elements ---
        tk.Label(root, text="Usuario:").pack(pady=5)
        self.entry_user = tk.Entry(root)
        self.entry_user.pack(pady=5)

        tk.Button(root, text="🎤 Registrar (Crear Voz)", command=self.registrar).pack(pady=10)
        tk.Button(root, text="🔓 Iniciar Sesión (Validar Voz)", command=self.login).pack(pady=10)
        
        tk.Label(root, text="--- Auditoría ---").pack(pady=10)
        tk.Button(root, text="⚠️ Ver Logs Críticos", command=self.ver_logs).pack(pady=5)
        
        self.log_text = tk.Text(root, height=8, width=45)
        self.log_text.pack(pady=10)

    def registrar(self):
        usuario = self.entry_user.get()
        if not usuario:
            messagebox.showwarning("Error", "Escribe un nombre de usuario")
            return

        # 1. Capturar Voz
        resultado = self.voice_service.escuchar_y_transcribir()
        
        if resultado.get("status") == "ERROR":
            messagebox.showerror("Error Micrófono", resultado.get("motivo"))
            return

        frase = resultado.get("texto")
        if not frase:
            messagebox.showerror("Error", "No se escuchó nada.")
            return

        # 2. Confirmar y Guardar
        if messagebox.askyesno("Confirmar", f"¿Tu frase secreta es: '{frase}'?"):
            self.dao.registrar_usuario(usuario, frase)
            # Log inicial de registro (JSONB)
            self.dao.registrar_log(1, {"evento": "registro", "status": "OK"}) 
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")

    def login(self):
        usuario = self.entry_user.get()
        # 1. Buscar usuario en BD
        datos_usuario = self.dao.obtener_usuario(usuario) # (id, passphrase, intentos)
        
        if not datos_usuario:
            messagebox.showerror("Error", "Usuario no encontrado")
            return

        user_id, frase_real, intentos = datos_usuario

        # 2. Capturar Voz
        resultado = self.voice_service.escuchar_y_transcribir()
        frase_dicha = resultado.get("texto", "")
        confianza = resultado.get("confianza", 0.0)

        # 3. Validar (Lógica de Negocio)
        if frase_dicha == frase_real:
            mensaje = "Acceso Concedido"
            # Guardamos JSONB de éxito
            log_data = {"status": "OK", "confianza": confianza, "latencia": "N/A"}
            messagebox.showinfo("Login", f"¡Bienvenido! (Confianza IA: {confianza:.2f})")
        else:
            mensaje = "Acceso Denegado"
            # Guardamos JSONB de fallo
            log_data = {
                "status": "FAIL", 
                "frase_intentada": frase_dicha, 
                "confianza": confianza
            }
            messagebox.showerror("Login", "Frase incorrecta")

        # 4. Registrar en Auditoría
        self.dao.registrar_log(user_id, log_data)

    def ver_logs(self):
        logs = self.dao.obtener_auditoria_critica()
        self.log_text.delete(1.0, tk.END)
        for user, json_data in logs:
            self.log_text.insert(tk.END, f"User: {user} | {json_data}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAuditApp(root)
    root.mainloop()