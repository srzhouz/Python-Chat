import tkinter as tk
from tkinter import font, simpledialog, messagebox, filedialog
import socket
import threading
import os
import time

# Función para obtener la IP pública del usuario
def get_public_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print("Error al obtener la IP pública:", e)
        return None

# Clase principal para la interfaz gráfica del chat
class ChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("EnygmaChat")
        self.light_mode = True  # Modo claro por defecto
        self.status = "offline"  # Estado inicial offline
        self.configure_gui()

        # Fuentes personalizadas para los textos
        self.custom_font = font.Font(family="Helvetica", size=12)
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")

        self.users = {}  # Diccionario para guardar usuarios y sus estados
        self.current_user = None
        self.current_user_ip = get_public_ip()
        self.destination_ip = None
        self.server_socket = None
        self.client_socket = None
        self.current_chat_user = None

        # Creación de los elementos de la interfaz gráfica
        self.create_title()
        self.create_widgets()
        self.create_menu()
        self.create_theme_and_shutdown_buttons()
        self.create_new_chat_button()
        self.create_status_button()

        # Inicio de los hilos para el servidor y para verificar cambios de IP
        threading.Thread(target=self.start_server).start()
        threading.Thread(target=self.check_ip_change).start()

    # Configuración inicial de la GUI
    def configure_gui(self):
        if self.light_mode:
            self.master.configure(bg="#e0e0e0")
            self.text_bg = "#ffffff"
            self.text_fg = "#333333"
            self.entry_bg = "#ffffff"
            self.entry_fg = "#000000"
            self.button_bg = "#008CBA"
            self.button_fg = "#ffffff"
            self.highlight_color = "#00BFFF"
            self.status_online_bg = "#4CAF50"
            self.status_offline_bg = "#F44336"
        else:
            self.master.configure(bg="#212121")
            self.text_bg = "#2f2f2f"
            self.text_fg = "#FFFFFF"
            self.entry_bg = "#2f2f2f"
            self.entry_fg = "#FFFFFF"
            self.button_bg = "#7289DA"
            self.button_fg = "#FFFFFF"
            self.highlight_color = "#7289DA"
            self.status_online_bg = "#4CAF50"
            self.status_offline_bg = "#F44336"

    # Método para alternar entre modos claro y oscuro
    def toggle_theme(self):
        self.light_mode = not self.light_mode
        self.configure_gui()
        self.update_theme()

    # Actualización de los elementos de la GUI según el modo de color
    def update_theme(self):
        self.master.configure(bg=self.master.cget("bg"))
        self.area_chat.configure(bg=self.text_bg, fg=self.text_fg)
        self.entrada_mensaje.configure(bg=self.entry_bg, fg=self.entry_fg, insertbackground=self.text_fg)
        self.boton_enviar.configure(bg=self.button_bg, fg=self.button_fg)
        self.boton_archivo.configure(bg=self.button_bg, fg=self.button_fg)
        self.label_usuarios.configure(bg=self.master.cget("bg"), fg=self.text_fg)
        self.theme_button.configure(text="Modo oscuro" if self.light_mode else "Modo claro", bg=self.button_bg, fg=self.button_fg)
        self.title_label.configure(bg=self.master.cget("bg"), fg=self.text_fg)
        self.ip_label.configure(bg=self.master.cget("bg"), fg=self.text_fg)
        self.lista_usuarios.configure(bg=self.entry_bg, fg=self.text_fg, selectbackground=self.highlight_color, selectforeground="#ffffff")
        self.boton_nuevo_chat.configure(bg=self.button_bg, fg=self.button_fg)
        self.boton_estado.configure(bg=self.button_bg, fg=self.button_fg)
        self.status_indicator.configure(bg=self.status_online_bg if self.status == "online" else self.status_offline_bg)
        self.shutdown_button.configure(bg=self.button_bg, fg=self.button_fg)
        self.update_user_list()

    # Creación del título y la etiqueta de IP en la interfaz
    def create_title(self):
        title_frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        title_frame.pack(fill=tk.X)

        self.title_label = tk.Label(title_frame, text="EnygmaChat", font=self.title_font, bg=self.master.cget("bg"), fg=self.text_fg)
        self.title_label.pack(pady=10, anchor='center')

        self.ip_label = tk.Label(title_frame, text=f"Tu IP: {self.current_user_ip}", font=("Arial", 10), bg=self.master.cget("bg"), fg=self.text_fg)
        self.ip_label.pack(anchor='ne')

    # Creación del menú de archivo con opción para salir
    def create_menu(self):
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.close_application)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        self.master.config(menu=menubar)

    # Botones para cambiar el tema y cerrar la aplicación
    def create_theme_and_shutdown_buttons(self):
        frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        frame.place(relx=1.0, y=15, anchor='ne')

        self.theme_button = tk.Button(frame, text="Modo oscuro" if self.light_mode else "Modo claro", command=self.toggle_theme, bg=self.button_bg, fg=self.button_fg)
        self.theme_button.config(font=("Arial", 14, "bold"), relief=tk.FLAT)
        self.theme_button.pack(side=tk.RIGHT)

        self.shutdown_button = tk.Button(frame, text="Salir", command=self.close_application, bg=self.button_bg, fg=self.button_fg)
        self.shutdown_button.config(font=("Arial", 14, "bold"), relief=tk.FLAT)
        self.shutdown_button.pack(side=tk.RIGHT)

    # Botón para cambiar el estado en línea
    def create_status_button(self):
        frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        frame.place(x=15, y=15)

        self.boton_estado = tk.Button(frame, text="Cambiar Estado", command=self.cambiar_estado, bg=self.button_bg, fg=self.button_fg)
        self.boton_estado.config(font=("Arial", 12, "bold"), relief=tk.FLAT)
        self.boton_estado.pack(side=tk.LEFT, padx=5)

        self.status_indicator = tk.Label(frame, width=2, height=1, bg=self.status_offline_bg, relief=tk.SOLID)
        self.status_indicator.pack(side=tk.LEFT, padx=5)

    # Botón para iniciar un nuevo chat
    def create_new_chat_button(self):
        frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        frame.place(x=15, y=75)

        self.boton_nuevo_chat = tk.Button(frame, text="Iniciar nuevo chat", command=self.iniciar_nuevo_chat, bg=self.button_bg, fg=self.button_fg)
        self.boton_nuevo_chat.config(font=("Arial", 14, "bold"), relief=tk.FLAT)
        self.boton_nuevo_chat.pack()

    # Método para cambiar el estado en línea del usuario
    def cambiar_estado(self):
        self.status = "online" if self.status == "offline" else "offline"
        self.status_indicator.configure(bg=self.status_online_bg if self.status == "online" else self.status_offline_bg)
        self.broadcast_status()

    # Enviar el estado actual a otros usuarios
    def broadcast_status(self):
        if self.client_socket:
            try:
                self.client_socket.send(f"STATUS:{self.current_user}:{self.status}".encode())
                self.update_user_list()
            except Exception as e:
                print(f"Error al enviar estado: {e}")

    # Método para iniciar un nuevo chat solicitando el nombre y la IP del usuario destino
    def iniciar_nuevo_chat(self):
        user_name = simpledialog.askstring("Nuevo Chat", "Ingresa tu nombre:")
        if not user_name:
            messagebox.showerror("Error", "Debes ingresar un nombre.")
            return
        
        self.current_user = user_name
        new_user_ip = simpledialog.askstring("Nuevo Chat", "Ingresa la IP del amigo con el que quieres chatear:")
        if new_user_ip:
            self.destination_ip = new_user_ip
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((self.destination_ip, 12345))
                self.client_socket.send(f"REQUEST_CHAT:{self.current_user_ip}:{self.current_user}".encode())
                response = self.client_socket.recv(1024).decode()
                if response.startswith("ACCEPT:"):
                    other_user_name = response.split(":")[1]
                    self.users[other_user_name] = {'ip': self.destination_ip, 'status': 'online'}
                    self.update_user_list()
                    self.area_chat.configure(state=tk.NORMAL)
                    self.area_chat.delete("1.0", tk.END)
                    self.area_chat.insert(tk.END, f"Chat iniciado con {other_user_name} ({self.destination_ip}):\n", "other_message")
                    self.area_chat.configure(state=tk.DISABLED)
                    self.entrada_mensaje.configure(state=tk.NORMAL)
                    threading.Thread(target=self.receive_messages).start()
                else:
                    messagebox.showinfo("Solicitud rechazada", "El usuario ha rechazado tu solicitud de chat.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo conectar con {new_user_ip}: {e}")

    # Creación de los elementos de la interfaz para el chat y los usuarios
    def create_widgets(self):
        def enviar_mensaje():
            if self.current_user and self.destination_ip and self.client_socket:
                mensaje = self.entrada_mensaje.get()
                if mensaje.strip():
                    self.client_socket.send(mensaje.encode())
                    self.area_chat.configure(state=tk.NORMAL)
                    self.area_chat.insert(tk.END, f"Tú: {mensaje}\n", "user_message")
                    self.area_chat.configure(state=tk.DISABLED)
                    self.entrada_mensaje.delete(0, tk.END)

        main_frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        main_frame.pack(fill=tk.BOTH, expand=True)

        frame_usuarios = tk.Frame(main_frame, bg=self.entry_bg, relief=tk.RAISED, borderwidth=2)
        frame_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20)

        self.label_usuarios = tk.Label(frame_usuarios, text="Usuarios", font=("Arial", 18, "bold"), bg=self.entry_bg, fg=self.highlight_color)
        self.label_usuarios.pack(side=tk.TOP, padx=10, pady=5)

        self.lista_usuarios = tk.Listbox(frame_usuarios, width=30, font=("Arial", 14), bg=self.entry_bg, borderwidth=0, selectbackground=self.highlight_color, selectforeground="#ffffff")
        self.lista_usuarios.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=(10, 20))

        frame_chat = tk.Frame(main_frame, bg=self.master.cget("bg"))
        frame_chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.area_chat = tk.Text(frame_chat, width=60, height=20, font=self.custom_font, bg=self.text_bg, fg=self.text_fg, borderwidth=0)
        self.area_chat.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
        self.area_chat.tag_configure("user_message", foreground=self.text_fg, font=self.custom_font, background=self.highlight_color, relief=tk.RAISED, borderwidth=1)
        self.area_chat.tag_configure("other_message", foreground="#666666", font=self.custom_font, background=self.text_bg, relief=tk.RAISED, borderwidth=1)
        self.area_chat.configure(state=tk.DISABLED)

        frame_entrada = tk.Frame(frame_chat, bg=self.master.cget("bg"))
        frame_entrada.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.entrada_mensaje = tk.Entry(frame_entrada, font=self.custom_font, bg=self.entry_bg, fg=self.entry_fg, borderwidth=1, relief=tk.SOLID)
        self.entrada_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.boton_enviar = tk.Button(frame_entrada, text="Enviar", font=("Arial", 14, "bold"), bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, command=enviar_mensaje)
        self.boton_enviar.pack(side=tk.LEFT)

        self.boton_archivo = tk.Button(frame_entrada, text="Archivo", font=("Arial", 14, "bold"), bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, command=self.enviar_archivo)
        self.boton_archivo.pack(side=tk.LEFT)

    # Método para enviar un archivo a través del chat
    def enviar_archivo(self):
        file_path = filedialog.askopenfilename()
        if file_path and self.client_socket:
            try:
                with open(file_path, "rb") as file:
                    self.client_socket.sendall(file.read())
                messagebox.showinfo("Archivo Enviado", f"El archivo {os.path.basename(file_path)} se ha enviado con éxito.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al enviar el archivo: {e}")

    # Método para iniciar el servidor del chat
    def start_server(self):
        while True:
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind((self.current_user_ip, 12345))
                self.server_socket.listen(1)
                print("Servidor iniciado, esperando conexión...")
                client_socket, address = self.server_socket.accept()
                print("Conexión establecida con:", address)
                threading.Thread(target=self.handle_client, args=(client_socket, address)).start()
            except OSError:
                time.sleep(1)

    # Manejo de las conexiones de los clientes
    def handle_client(self, client_socket, address):
        message = client_socket.recv(1024).decode()
        if message.startswith("REQUEST_CHAT:"):
            _, ip, user_name = message.split(":")
            response = messagebox.askyesno("Solicitud de chat", f"{user_name} ({ip}) quiere iniciar un chat. ¿Aceptar?")
            if response:
                self.current_chat_user = user_name
                self.users[user_name] = {'ip': ip, 'status': 'online'}
                client_socket.send(f"ACCEPT:{self.current_user}".encode())
                self.client_socket = client_socket
                self.update_user_list()
                self.area_chat.configure(state=tk.NORMAL)
                self.area_chat.delete("1.0", tk.END)
                self.area_chat.insert(tk.END, f"Chat iniciado con {user_name} ({ip}):\n", "other_message")
                self.area_chat.configure(state=tk.DISABLED)
                self.entrada_mensaje.configure(state=tk.NORMAL)
                threading.Thread(target=self.receive_messages).start()
            else:
                client_socket.send("REJECT".encode())
                client_socket.close()
        elif message.startswith("STATUS:"):
            _, user_name, status = message.split(":")
            if user_name in self.users:
                self.users[user_name]['status'] = status
                self.update_user_list()

    # Recepción de mensajes del otro usuario
    def receive_messages(self):
        while True:
            try:
                mensaje = self.client_socket.recv(1024).decode()
                if mensaje:
                    self.area_chat.configure(state=tk.NORMAL)
                    self.area_chat.insert(tk.END, f"{self.current_chat_user}: {mensaje}\n", "other_message")
                    self.area_chat.configure(state=tk.DISABLED)
            except ConnectionResetError:
                messagebox.showerror("Error", "Se perdió la conexión con el otro usuario.")
                break

    # Verificación de cambios en la IP pública
    def check_ip_change(self):
        while True:
            new_ip = get_public_ip()
            if new_ip and new_ip != self.current_user_ip:
                self.current_user_ip = new_ip
                self.update_ip_label()
                if self.server_socket:
                    self.server_socket.close()
                threading.Thread(target=self.start_server).start()
            time.sleep(10)

    # Actualización de la etiqueta de IP
    def update_ip_label(self):
        self.ip_label.config(text=f"Tu IP: {self.current_user_ip}")

    # Cierre de la aplicación y los sockets
    def close_application(self):
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        if messagebox.askokcancel("Cerrar aplicación", "¿Estás seguro que deseas cerrar la aplicación?"):
            self.master.destroy()

    # Actualización de la lista de usuarios en la interfaz
    def update_user_list(self):
        self.lista_usuarios.delete(0, tk.END)
        for user, info in self.users.items():
            color = self.status_online_bg if info['status'] == 'online' else self.status_offline_bg
            display_text = f"{user} ({'🟢' if info['status'] == 'online' else '🔴'})"
            self.lista_usuarios.insert(tk.END, display_text)
            self.lista_usuarios.itemconfig(tk.END, {'fg': color})

if __name__ == "__main__":
    root = tk.Tk()
    chat_gui = ChatGUI(root)
    root.mainloop()
