import tkinter as tk
from tkinter import font, simpledialog, messagebox, filedialog
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
        master.title("EnygmaChat")
        self.light_mode = True
        self.status = "offline"
        self.configure_gui()

        self.custom_font = font.Font(family="Helvetica", size=12)
        self.title_font = font.Font(family="Helvetica", size=24, weight="bold")

        self.users = {}
        self.current_user = None
        self.current_user_ip = get_public_ip()
        self.destination_ip = None
        self.server_socket = None
        self.client_socket = None
        self.current_chat_user = None

        self.create_title()
        self.create_widgets()
        self.create_menu()
        self.create_user_buttons()
        self.create_theme_and_shutdown_buttons()
        self.create_status_button()

        threading.Thread(target=self.start_server).start()
        threading.Thread(target=self.check_ip_change).start()

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

    def toggle_theme(self):
        self.light_mode = not self.light_mode
        self.configure_gui()
        self.update_theme()

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
        self.boton_agregar.configure(bg=self.button_bg, fg=self.button_fg)
        self.boton_modificar.configure(bg=self.button_bg, fg=self.button_fg)
        self.boton_eliminar.configure(bg=self.button_bg, fg=self.button_fg)
        self.boton_estado.configure(bg=self.button_bg, fg=self.button_fg)
        self.status_indicator.configure(bg=self.status_online_bg if self.status == "online" else self.status_offline_bg)
        self.shutdown_button.configure(bg=self.button_bg, fg=self.button_fg)
        self.update_user_list()

    def create_title(self):
        title_frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        title_frame.pack(fill=tk.X)

        self.title_label = tk.Label(title_frame, text="EnygmaChat", font=self.title_font, bg=self.master.cget("bg"), fg=self.text_fg)
        self.title_label.pack(pady=10, anchor='center')

        self.ip_label = tk.Label(title_frame, text=f"Tu IP: {self.current_user_ip}", font=("Arial", 10), bg=self.master.cget("bg"), fg=self.text_fg)
        self.ip_label.pack(anchor='ne')

    def create_menu(self):
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.close_application)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        self.master.config(menu=menubar)

    def create_theme_and_shutdown_buttons(self):
        frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        frame.place(relx=1.0, y=15, anchor='ne')

        self.theme_button = tk.Button(frame, text="Modo oscuro" if self.light_mode else "Modo claro", command=self.toggle_theme, bg=self.button_bg, fg=self.button_fg)
        self.theme_button.config(font=("Arial", 14, "bold"), relief=tk.FLAT)
        self.theme_button.pack(side=tk.RIGHT)

        self.shutdown_button = tk.Button(frame, text="Salir", command=self.close_application, bg=self.button_bg, fg=self.button_fg)
        self.shutdown_button.config(font=("Arial", 14, "bold"), relief=tk.FLAT)
        self.shutdown_button.pack(side=tk.RIGHT)

    def create_status_button(self):
        frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        frame.place(x=15, y=15)

        self.boton_estado = tk.Button(frame, text="Cambiar Estado", command=self.cambiar_estado, bg=self.button_bg, fg=self.button_fg)
        self.boton_estado.config(font=("Arial", 12, "bold"), relief=tk.FLAT)
        self.boton_estado.pack(side=tk.LEFT, padx=5)

        self.status_indicator = tk.Label(frame, width=2, height=1, bg=self.status_offline_bg, relief=tk.SOLID)
        self.status_indicator.pack(side=tk.LEFT, padx=5)

    def create_user_buttons(self):
        frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        frame.place(x=15, y=75)

        self.boton_agregar = tk.Button(frame, text="Agregar usuario", command=self.agregar_usuario, bg=self.button_bg, fg=self.button_fg)
        self.boton_agregar.config(font=("Arial", 12, "bold"), relief=tk.FLAT)
        self.boton_agregar.pack(side=tk.LEFT, padx=5)

        self.boton_modificar = tk.Button(frame, text="Modificar usuario", command=self.modificar_usuario, bg=self.button_bg, fg=self.button_fg)
        self.boton_modificar.config(font=("Arial", 12, "bold"), relief=tk.FLAT)
        self.boton_modificar.pack(side=tk.LEFT, padx=5)

        self.boton_eliminar = tk.Button(frame, text="Eliminar usuario", command=self.eliminar_usuario, bg=self.button_bg, fg=self.button_fg)
        self.boton_eliminar.config(font=("Arial", 12, "bold"), relief=tk.FLAT)
        self.boton_eliminar.pack(side=tk.LEFT, padx=5)

    def cambiar_estado(self):
        self.status = "online" if self.status == "offline" else "offline"
        self.broadcast_status()
        self.status_indicator.configure(bg=self.status_online_bg if self.status == "online" else self.status_offline_bg)
        self.update_user_list()

    def broadcast_status(self):
        for user, info in self.users.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((info['ip'], 12345))
                s.send(f"STATUS:{self.current_user_ip}:{self.status}".encode())
                s.close()
            except Exception as e:
                print(f"Error al enviar estado a {user}: {e}")

    def agregar_usuario(self):
        user_name = simpledialog.askstring("Agregar Usuario", "Ingresa el nombre del usuario:")
        user_ip = simpledialog.askstring("Agregar Usuario", "Ingresa la IP del usuario:")
        if user_name and user_ip:
            self.send_chat_request(user_name, user_ip)

    def send_chat_request(self, user_name, user_ip):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((user_ip, 12345))
            s.send(f"REQUEST_CHAT:{self.current_user_ip}:{user_name}".encode())
            response = s.recv(1024).decode()
            if response.startswith("ACCEPT"):
                chat_name = response.split(":")[1]
                self.users[chat_name] = {'ip': user_ip, 'status': 'online'}
                self.update_user_list()
                messagebox.showinfo("Solicitud aceptada", f"{chat_name} ha aceptado la solicitud de chat.")
            else:
                messagebox.showinfo("Solicitud rechazada", f"{user_name} ha rechazado la solicitud de chat.")
            s.close()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar la solicitud a {user_name}: {e}")

    def modificar_usuario(self):
        selected_index = self.lista_usuarios.curselection()
        if selected_index:
            selected_user = self.lista_usuarios.get(selected_index).split(" (")[0]
            new_name = simpledialog.askstring("Modificar Usuario", "Ingresa el nuevo nombre del usuario:", initialvalue=selected_user)
            new_ip = simpledialog.askstring("Modificar Usuario", "Ingresa la nueva IP del usuario:", initialvalue=self.users[selected_user]['ip'])
            if new_name and new_ip:
                self.users[new_name] = {'ip': new_ip, 'status': self.users[selected_user]['status']}
                if new_name != selected_user:
                    del self.users[selected_user]
                self.update_user_list()

    def eliminar_usuario(self):
        selected_index = self.lista_usuarios.curselection()
        if selected_index:
            selected_user = self.lista_usuarios.get(selected_index).split(" (")[0]
            del self.users[selected_user]
            self.update_user_list()

    def create_widgets(self):
        def enviar_mensaje():
            if self.current_chat_user and self.client_socket:
                mensaje = self.entrada_mensaje.get()
                if mensaje.strip():
                    self.client_socket.send(mensaje.encode())
                    self.area_chat.configure(state=tk.NORMAL)
                    self.area_chat.insert(tk.END, f"Tú: {mensaje}\n", "user_message")
                    self.area_chat.configure(state=tk.DISABLED)
                    self.entrada_mensaje.delete(0, tk.END)

        def on_select(event):
            selected_index = self.lista_usuarios.curselection()
            if selected_index:
                selected_user = self.lista_usuarios.get(selected_index).split(" (")[0]
                self.current_chat_user = selected_user
                self.destination_ip = self.users[selected_user]['ip']
                self.area_chat.configure(state=tk.NORMAL)
                self.area_chat.delete("1.0", tk.END)
                self.area_chat.insert(tk.END, f"Chat con {selected_user}:\n", "other_message")
                self.area_chat.configure(state=tk.DISABLED)
                self.entrada_mensaje.configure(state=tk.NORMAL)
                # Conectar al usuario seleccionado
                try:
                    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client_socket.connect((self.destination_ip, 12345))
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo conectar con {selected_user}: {e}")

        main_frame = tk.Frame(self.master, bg=self.master.cget("bg"))
        main_frame.pack(fill=tk.BOTH, expand=True)

        frame_usuarios = tk.Frame(main_frame, bg=self.entry_bg, relief=tk.RAISED, borderwidth=2)
        frame_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20)

        self.label_usuarios = tk.Label(frame_usuarios, text="Usuarios", font=("Arial", 18, "bold"), bg=self.entry_bg, fg=self.highlight_color)
        self.label_usuarios.pack(side=tk.TOP, padx=10, pady=5)

        self.lista_usuarios = tk.Listbox(frame_usuarios, width=30, font=("Arial", 14), bg=self.entry_bg, borderwidth=0, selectbackground=self.highlight_color, selectforeground="#ffffff")
        self.lista_usuarios.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=(10, 20))
        self.lista_usuarios.bind('<<ListboxSelect>>', on_select)

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

    def handle_client(self, client_socket, address):
        message = client_socket.recv(1024).decode()
        if message.startswith("REQUEST_CHAT:"):
            _, ip, user_name = message.split(":")
            response = messagebox.askyesno("Solicitud de chat", f"{user_name} ({ip}) quiere iniciar un chat. ¿Aceptar?")
            if response:
                chat_name = simpledialog.askstring("Nombre del Chat", "¿Cómo quieres llamar a este chat?")
                self.users[chat_name] = {'ip': ip, 'status': 'online'}
                self.update_user_list()
                client_socket.send(f"ACCEPT:{chat_name}".encode())
                self.client_socket = client_socket
                threading.Thread(target=self.receive_messages).start()
            else:
                client_socket.send("REJECT".encode())
                client_socket.close()
        elif message.startswith("STATUS:"):
            _, ip, status = message.split(":")
            for user, info in self.users.items():
                if info['ip'] == ip:
                    self.users[user]['status'] = status
                    self.update_user_list()
                    break
        else:
            self.client_socket = client_socket
            threading.Thread(target=self.receive_messages).start()

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

    def update_ip_label(self):
        self.ip_label.config(text=f"Tu IP: {self.current_user_ip}")

    def close_application(self):
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        if messagebox.askokcancel("Cerrar aplicación", "¿Estás seguro que deseas cerrar la aplicación?"):
            self.master.destroy()

    def update_user_list(self):
        self.lista_usuarios.delete(0, tk.END)
        for user, info in self.users.items():
            display_text = f"{user} ({'🟢' if info['status'] == 'online' else '🔴'})"
            self.lista_usuarios.insert(tk.END, display_text)

if __name__ == "__main__":
    root = tk.Tk()
    chat_gui = ChatGUI(root)
    root.mainloop()
