import tkinter as tk
from tkinter import font, simpledialog, messagebox
import tkinter.tix as tix
import socket
import threading

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
        master.configure(bg="#f0f0f0")

        self.custom_font = font.Font(family="Arial", size=12)

        self.users = ["Rodri", "Ivan B", "Carol", "Jiabo", "Ivan P"]
        self.current_user = None
        self.current_user_ip = get_public_ip()
        self.destination_ip = None
        self.server_socket = None
        self.client_socket = None

        self.create_title()
        self.create_widgets()
        self.create_menu()
        self.create_shutdown_button()  # Agregar el botón de apagado

        # Iniciar el servidor en un hilo separado
        threading.Thread(target=self.start_server).start()

    def create_title(self):
        title_label = tk.Label(self.master, text="RoyalChat", font=("Arial", 36, "bold"), bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=20)

        # Mostrar la IP del usuario en la esquina superior derecha como información adicional
        ip_label = tk.Label(self.master, text=f"Tu IP: {self.current_user_ip}", font=("Arial", 10), bg="#f0f0f0")
        ip_label.place(relx=1.0, rely=0, anchor='ne')

    def create_menu(self):
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.close_application)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        self.master.config(menu=menubar)

    def create_shutdown_button(self):
        frame = tk.Frame(self.master, bg="#ffffff", highlightbackground="#4CAF50", highlightthickness=2)
        frame.place(x=15, y=15)

        shutdown_button = tk.Button(frame, text="Salir", command=self.close_application, bg="#ffffff", fg="#4CAF50")
        shutdown_button.config(font=("Arial", 14, "bold"), relief=tk.FLAT, activebackground="#ffffff", activeforeground="#ff0000")
        shutdown_button.pack()

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
                        self.lista_usuarios.itemconfig(i, bg="#4CAF50", fg="#ffffff")
                    else:
                        self.lista_usuarios.itemconfig(i, bg="#ffffff", fg="#333333")

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

        main_frame = tk.Frame(self.master, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        frame_usuarios = tix.Frame(main_frame, bg="#ffffff", relief=tk.RAISED, borderwidth=2)
        frame_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20)

        label_usuarios = tk.Label(frame_usuarios, text="Usuarios", font=("Arial", 18, "bold"), bg="#ffffff", fg="#4CAF50")
        label_usuarios.pack(side=tk.TOP, padx=10, pady=5)

        self.lista_usuarios = tk.Listbox(frame_usuarios, width=20, font=("Arial", 14), bg="#ffffff", borderwidth=0, selectbackground="#4CAF50", selectforeground="#ffffff")
        self.lista_usuarios.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=(10, 20))  # Más espacio entre nombres
        self.lista_usuarios.bind('<<ListboxSelect>>', on_select)

        for user in self.users:
            self.lista_usuarios.insert(tk.END, user)

        frame_chat = tix.Frame(main_frame, bg="#f0f0f0")
        frame_chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.area_chat = tk.Text(frame_chat, width=60, height=20, font=self.custom_font, bg="#f0f0f0", borderwidth=0)
        self.area_chat.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
        self.area_chat.tag_configure("user_message", foreground="#333333", font=self.custom_font, background="#e0f2f1", relief=tix.RAISED, borderwidth=1)
        self.area_chat.tag_configure("other_message", foreground="#666666", font=self.custom_font, background="#f3f3f3", relief=tix.RAISED, borderwidth=1)
        self.area_chat.configure(state=tk.DISABLED)

        frame_entrada = tix.Frame(frame_chat, bg="#f0f0f0")
        frame_entrada.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.entrada_mensaje = tk.Entry(frame_entrada, font=self.custom_font, bg="#ffffff", borderwidth=1, relief=tk.SOLID)
        self.entrada_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        boton_enviar = tk.Button(frame_entrada, text="Enviar", font=("Arial", 14, "bold"), bg="#4CAF50", fg="#ffffff", relief=tk.FLAT, command=enviar_mensaje)
        boton_enviar.pack(side=tk.LEFT)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.current_user_ip, 12345))  # Puerto arbitrario
        self.server_socket.listen(1)
        print("Servidor iniciado, esperando conexión...")
        self.client_socket, address = self.server_socket.accept()
        print("Conexión establecida con:", address)

        # Hilo para recibir mensajes del cliente
        threading.Thread(target=self.receive_messages).start()

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
