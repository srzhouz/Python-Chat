import tkinter as tk
from tkinter import font, simpledialog, messagebox, filedialog
import tkinter.tix as tix
import socket
import threading
import os
import time

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

class ChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("RoyalChat")
        self.light_mode = True
        self.configure_gui()
        
        self.custom_font = font.Font(family="Arial", size=12)

        self.users = []
        self.current_user = None
        self.current_user_ip = get_public_ip()
        self.destination_ip = None
        self.server_socket = None
        self.client_socket = None

        self.create_title()
        self.create_widgets()
        self.create_menu()
        self.create_shutdown_button()  # Agregar el botón de apagado
        self.create_toggle_theme_button()  # Agregar el botón de cambio de tema
        self.create_new_chat_button()  # Agregar el botón de nuevo chat

        # Iniciar el servidor en un hilo separado
        threading.Thread(target=self.start_server).start()
        # Iniciar el chequeo de IP en un hilo separado
        threading.Thread(target=self.check_ip_change).start()

    def configure_gui(self):
        if self.light_mode:
            self.master.configure(bg="#f0f0f0")
            self.text_bg = "#f0f0f0"
            self.text_fg = "#333333"
            self.entry_bg = "#ffffff"
            self.entry_fg = "#000000"
            self.button_bg = "#4CAF50"
            self.button_fg = "#ffffff"
        else:
            self.master.configure(bg="#2c2c2c")
            self.text_bg = "#2c2c2c"
            self.text_fg = "#ffffff"
            self.entry_bg = "#3c3c3c"
            self.entry_fg = "#ffffff"
            self.button_bg = "#555555"
            self.button_fg = "#ffffff"

    def toggle_theme(self):
        self.light_mode = not self.light_mode
        self.configure_gui()
        self.update_theme()

    def update_theme(self):
        self.master.configure(bg=self.text_bg)
        self.area_chat.configure(bg=self.text_bg, fg=self.text_fg)
        self.entrada_mensaje.configure(bg=self.entry_bg, fg=self.entry_fg)
        self.boton_enviar.configure(bg=self.button_bg, fg=self.button_fg)
        self.boton_archivo.configure(bg=self.button_bg, fg=self.button_fg)
        self.label_usuarios.configure(bg=self.text_bg, fg=self.text_fg)
        self.theme_button.configure(text="Modo oscuro" if self.light_mode else "Modo claro", bg=self.button_bg, fg=self.button_fg)

    def create_title(self):
        self.title_label = tk.Label(self.master, text="RoyalChat", font=("Arial", 36, "bold"), bg=self.text_bg, fg=self.text_fg)
        self.title_label.pack(pady=20)

        # Mostrar la IP del usuario en la esquina superior derecha como información adicional
        self.ip_label = tk.Label(self.master, text=f"Tu IP: {self.current_user_ip}", font=("Arial", 10), bg=self.text_bg, fg=self.text_fg)
        self.ip_label.place(relx=1.0, rely=0, anchor='ne')

    def create_menu(self):
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.close_application)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        self.master.config(menu=menubar)

    def create_shutdown_button(self):
        frame = tk.Frame(self.master, bg=self.text_bg)
        frame.place(x=15, y=15)

        shutdown_button = tk.Button(frame, text="Salir", command=self.close_application, bg=self.button_bg, fg=self.button_fg)
        shutdown_button.config(font=("Arial", 14, "bold"), relief=tk.FLAT, activebackground=self.button_bg, activeforeground="#ff0000")
        shutdown_button.pack()

    def create_toggle_theme_button(self):
        frame = tk.Frame(self.master, bg=self.text_bg)
        frame.place(relx=1.0, y=15, anchor='ne')

        theme_button = tk.Button(frame, text="Modo oscuro" if self.light_mode else "Modo claro", command=self.toggle_theme, bg=self.button_bg, fg=self.button_fg)
        theme_button.config(font=("Arial", 14, "bold"), relief=tk.FLAT)
        theme_button.pack()
        self.theme_button = theme_button

    def create_new_chat_button(self):
        frame = tk.Frame(self.master, bg=self.text_bg)
        frame.place(x=15, y=75)

        new_chat_button = tk.Button(frame, text="Iniciar nuevo chat", command=self.iniciar_nuevo_chat, bg=self.button_bg, fg=self.button_fg)
        new_chat_button.config(font=("Arial", 14, "bold"), relief=tk.FLAT)
        new_chat_button.pack()

    def iniciar_nuevo_chat(self):
        new_user_ip = simpledialog.askstring("Nuevo Chat", "Ingresa la IP del amigo con el que quieres chatear:")
        if new_user_ip:
            self.destination_ip = new_user_ip
            # Enviar solicitud de chat al destinatario
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.destination_ip, 12345))
            self.client_socket.send("Solicitud de chat".encode())
            response = self.client_socket.recv(1024).decode()
            if response == "Aceptar":
                self.current_user = simpledialog.askstring("Nuevo Chat", "Ingresa un nombre para el chat:")
                if self.current_user:
                    self.users.append(self.current_user)
                    self.lista_usuarios.insert(tk.END, self.current_user)
                    self.area_chat.configure(state=tk.NORMAL)
                    self.area_chat.delete("1.0", tk.END)
                    self.area_chat.insert(tk.END, f"Chat iniciado con {self.current_user}:\n", "other_message")
                    self.area_chat.configure(state=tk.DISABLED)
                    self.entrada_mensaje.configure(state=tk.NORMAL)
            else:
                messagebox.showinfo("Solicitud rechazada", "El usuario ha rechazado tu solicitud de chat.")

    def create_widgets(self):
        def enviar_mensaje():
            if self.current_user and self.destination_ip and self.client_socket:
                mensaje = self.entrada_mensaje.get()
                if mensaje.strip():
                    # Enviar el mensaje al cliente
                    self.client_socket.send(mensaje.encode())
                    # Mostrar el mensaje en el área de chat
                    self.area_chat.configure(state=tk.NORMAL)
                    self.area_chat.insert(tk.END, f"\n", "other_message")
                    self.area_chat.insert(tk.END, f"{self.current_user}: {mensaje}", "user_message")
                    self.area_chat.insert(tk.END, "\n", "other_message")
                    self.area_chat.configure(state=tk.DISABLED)
                    self.entrada_mensaje.delete(0, tk.END)

        def on_select(event):
            selected_index = self.lista_usuarios.curselection()
            if selected_index:
                for i in range(len(self.lista_usuarios.get(0, tk.END))):
                    if i == selected_index[0]:
                        self.lista_usuarios.itemconfig(i, bg=self.button_bg, fg=self.button_fg)
                    else:
                        self.lista_usuarios.itemconfig(i, bg=self.entry_bg, fg=self.entry_fg)

                selected_user = self.users[selected_index[0]]
                self.destination_ip = simpledialog.askstring("Chat con", f"Ingresa la IP de {selected_user}:")
                if self.destination_ip:
                    self.current_user = simpledialog.askstring("Chat con", f"¿Cómo te quieres llamar al chatear con {selected_user}?")
                    if self.current_user:
                        self.area_chat.configure(state=tk.NORMAL)
                        self.area_chat.delete("1.0", tk.END)
                        self.area_chat.insert(tk.END, f"{selected_user}:\n", "other_message")
                        self.area_chat.configure(state=tk.DISABLED)
                        self.entrada_mensaje.configure(state=tk.NORMAL)

        main_frame = tk.Frame(self.master, bg=self.text_bg)
        main_frame.pack(fill=tk.BOTH, expand=True)

        frame_usuarios = tix.Frame(main_frame, bg=self.entry_bg, relief=tk.RAISED, borderwidth=2)
        frame_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20)

        self.label_usuarios = tk.Label(frame_usuarios, text="Usuarios", font=("Arial", 18, "bold"), bg=self.entry_bg, fg=self.button_bg)
        self.label_usuarios.pack(side=tk.TOP, padx=10, pady=5)

        self.lista_usuarios = tk.Listbox(frame_usuarios, width=20, font=("Arial", 14), bg=self.entry_bg, borderwidth=0, selectbackground=self.button_bg, selectforeground=self.button_fg)
        self.lista_usuarios.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=(10, 20))  # Más espacio entre nombres
        self.lista_usuarios.bind('<<ListboxSelect>>', on_select)

        frame_chat = tix.Frame(main_frame, bg=self.text_bg)
        frame_chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.area_chat = tk.Text(frame_chat, width=60, height=20, font=self.custom_font, bg=self.text_bg, fg=self.text_fg, borderwidth=0)
        self.area_chat.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
        self.area_chat.tag_configure("user_message", foreground=self.text_fg, font=self.custom_font, background="#e0f2f1", relief=tix.RAISED, borderwidth=1)
        self.area_chat.tag_configure("other_message", foreground="#666666", font=self.custom_font, background="#f3f3f3", relief=tix.RAISED, borderwidth=1)
        self.area_chat.configure(state=tk.DISABLED)

        frame_entrada = tix.Frame(frame_chat, bg=self.text_bg)
        frame_entrada.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.entrada_mensaje = tk.Entry(frame_entrada, font=self.custom_font, bg=self.entry_bg, fg=self.entry_fg, borderwidth=1, relief=tk.SOLID)
        self.entrada_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.boton_enviar = tk.Button(frame_entrada, text="Enviar", font=("Arial", 14, "bold"), bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, command=enviar_mensaje)
        self.boton_enviar.pack(side=tk.LEFT)

        self.boton_archivo = tk.Button(frame_entrada, text="Archivo", font=("Arial", 14, "bold"), bg=self.button_bg, fg=self.button_fg, relief=tk.FLAT, command=self.enviar_archivo)
        self.boton_archivo.pack(side=tk.LEFT)

    def enviar_archivo(self):
        file_path = filedialog.askopenfilename()
        if file_path and self.client_socket:
            try:
                with open(file_path, "rb") as file:
                    self.client_socket.sendall(file.read())
                messagebox.showinfo("Archivo Enviado", f"El archivo {os.path.basename(file_path)} se ha enviado con éxito.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al enviar el archivo: {e}")

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.current_user_ip, 12345))  # Puerto arbitrario
        self.server_socket.listen(1)
        print("Servidor iniciado, esperando conexión...")
        while True:
            client_socket, address = self.server_socket.accept()
            print("Conexión establecida con:", address)
            message = client_socket.recv(1024).decode()
            if message == "Solicitud de chat":
                response = messagebox.askyesno("Solicitud de chat", f"¿Aceptar solicitud de chat de {address[0]}?")
                if response:
                    client_socket.send("Aceptar".encode())
                    self.client_socket = client_socket
                    threading.Thread(target=self.receive_messages).start()
                else:
                    client_socket.send("Rechazar".encode())
                    client_socket.close()

    def receive_messages(self):
        while True:
            try:
                mensaje = self.client_socket.recv(1024).decode()
                if mensaje:
                    self.area_chat.configure(state=tk.NORMAL)
                    self.area_chat.insert(tk.END, f"\n", "other_message")
                    self.area_chat.insert(tk.END, f"Otro usuario: {mensaje}", "user_message")
                    self.area_chat.insert(tk.END, "\n", "other_message")
                    self.area_chat.configure(state=tk.DISABLED)
            except ConnectionResetError:
                messagebox.showerror("Error", "Se perdió la conexión con el otro usuario.")
                break

    def check_ip_change(self):
        while True:
            new_ip = get_public_ip()
            if new_ip and new_ip != self.current_user_ip:
                self.current_user_ip = new_ip
                self.ip_label.config(text=f"Tu IP: {self.current_user_ip}")
                if self.server_socket:
                    self.server_socket.close()
                threading.Thread(target=self.start_server).start()
            time.sleep(10)

    def close_application(self):
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        if messagebox.askokcancel("Cerrar aplicación", "¿Estás seguro que deseas cerrar la aplicación?"):
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    chat_gui = ChatGUI(root)
    root.mainloop()
