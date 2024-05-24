import tkinter as tk

# Configuración del tema oscuro
menu_bg_color = "#171717"   # Color de fondo del menú de usuarios
chat_bg_color = "#212121"   # Color de fondo del recuadro de chat
entry_bg_color = "#2f2f2f"  # Color de fondo del marco para escribir mensajes
text_color = "#FFFFFF"      # Color del texto
highlight_color = "#7289DA" # Color morado para toques
text_size = 12              # Tamaño del texto

class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Chat App")
        self.geometry("1280x720")
        self.configure(bg=chat_bg_color)

        self.create_widgets()

    def create_widgets(self):
        # Crear el marco del menú a la izquierda sin borde y más ancho
        self.menu_frame = tk.Frame(self, bg=menu_bg_color, width=300, bd=0)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Lista de usuarios sin borde y sin separación entre elementos
        self.users_listbox = tk.Listbox(self.menu_frame, bg=menu_bg_color, fg=text_color, selectbackground=highlight_color, selectforeground=text_color, bd=0, highlightthickness=0)
        self.users_listbox.pack(fill=tk.BOTH, expand=True, pady=30, padx=20)  # Sin separación entre elementos
        # Ajustar tamaño de fuente de la lista de usuarios
        self.users_listbox.config(font=("Arial", text_size))
        # Asociar evento de selección de usuario
        self.users_listbox.bind("<<ListboxSelect>>", self.on_user_select)

        # Crear el marco del chat a la derecha sin borde
        self.chat_frame = tk.Frame(self, bg=chat_bg_color, bd=0)
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Cuadro de chat sin borde
        self.chat_text = tk.Text(self.chat_frame, bg=chat_bg_color, fg=text_color, state=tk.DISABLED, wrap=tk.WORD, bd=0, highlightthickness=0)
        self.chat_text.pack(pady=40, padx=10, fill=tk.BOTH, expand=True)
        # Ajustar tamaño de fuente del chat
        self.chat_text.config(font=("Arial", text_size))

        # Crear una etiqueta para mostrar el usuario seleccionado
        self.current_user_label = tk.Label(self, bg=menu_bg_color, fg=text_color, font=("Arial", text_size))
        self.current_user_label.place(relx=0, rely=0, x=225, y=5)  # Alineado con la esquina superior izquierda con 200px de separación izquierda

        # Marco para escribir el mensaje sin borde y con padding
        self.entry_frame = tk.Frame(self.chat_frame, bg=chat_bg_color, bd=0)
        self.entry_frame.pack(fill=tk.X, padx=10, pady=10)

        # Entrada de texto para el mensaje sin borde
        self.message_entry = tk.Entry(self.entry_frame, bg=entry_bg_color, fg=text_color, insertbackground=text_color, bd=0, highlightthickness=0)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 0), pady=(0, 0))  # Padding horizontal de 33px, padding vertical de 22px
        # Asociar evento de presionar Enter
        self.message_entry.bind("<Return>", self.send_message_enter)
        # Ajustar tamaño de fuente de la entrada de texto
        self.message_entry.config(font=("Arial", text_size))

        # Botón de enviar sin borde
        self.send_button = tk.Button(self.entry_frame, text="Enviar", bg=highlight_color, fg=text_color, command=self.send_message, bd=0, highlightthickness=0)
        self.send_button.pack(side=tk.RIGHT, padx=5)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, f"Tú: {message}\n")
            self.chat_text.config(state=tk.DISABLED)
            self.message_entry.delete(0, tk.END)

    def send_message_enter(self, event):
        self.send_message()

    def on_user_select(self, event):
        # Obtener el índice del usuario seleccionado
        selected_index = self.users_listbox.curselection()
        if selected_index:
            # Obtener el texto del usuario seleccionado
            selected_user = self.users_listbox.get(selected_index)
            # Cambiar el texto de la etiqueta del usuario actual
            self.current_user_label.config(text=f"{selected_user}")

if __name__ == "__main__":
    app = ChatApp()

    # Usuarios de prueba
    usuarios_prueba = ["Usuario1", "Usuario2", "Usuario3", "Usuario4", "Usuario5"]
    for usuario in usuarios_prueba:
        app.users_listbox.insert(tk.END, usuario)

    app.mainloop()
