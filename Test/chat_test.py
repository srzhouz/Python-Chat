import tkinter as tk
from tkinter import font, simpledialog
import tkinter.tix as tix

class ChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("RoyalChat")
        master.configure(bg="#f0f0f0")

        self.custom_font = font.Font(family="Arial", size=12)

        self.users = ["Rodri", "Ivan B", "Carol", "Jiabo", "Ivan P"]
        self.current_user = None

        self.create_title()
        self.create_widgets()
        self.create_menu()

    def create_title(self):
        title_label = tk.Label(self.master, text="RoyalChat", font=("Arial", 36, "bold"), bg="#f0f0f0", fg="#333333")
        title_label.pack(pady=20)

    def create_menu(self):
        menubar = tk.Menu(self.master)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Salir", command=self.master.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        self.master.config(menu=menubar)

    def create_widgets(self):
        def enviar_mensaje(event=None):  # Modificamos la función para aceptar un evento como argumento
            if self.current_user:
                mensaje = self.entrada_mensaje.get()
                if mensaje.strip():
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

        frame_chat = tix.Frame(main_frame, bg="#f0f0f0")#borde de todo el chat
        frame_chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.area_chat = tk.Text(frame_chat, width=60, height=20, font=self.custom_font, bg="#f0f0f0", borderwidth=0)#fondo chat
        self.area_chat.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
        self.area_chat.tag_configure("user_message", foreground="#333333", font=self.custom_font, background="#e0f2f1", relief=tix.RAISED, borderwidth=1) #color texto mensaje
        self.area_chat.tag_configure("other_message", foreground="#666666", font=self.custom_font, background="#f3f3f3", relief=tix.RAISED, borderwidth=1)
        self.area_chat.configure(state=tk.DISABLED)

        frame_entrada = tix.Frame(frame_chat, bg="#f0f0f0")# fondo borde textarea
        frame_entrada.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.entrada_mensaje = tk.Entry(frame_entrada, font=self.custom_font, bg="#ffffff", borderwidth=1, relief=tk.SOLID) #fondo del textarea
        self.entrada_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        boton_enviar = tk.Button(frame_entrada, text="Enviar", font=("Arial", 14, "bold"), bg="#4CAF50", fg="#ffffff", relief=tk.FLAT, command=enviar_mensaje)
        boton_enviar.pack(side=tk.LEFT)

        # Vinculamos la tecla Enter con la función enviar_mensaje
        self.entrada_mensaje.bind("<Return>", enviar_mensaje)

if __name__ == "__main__":
    root = tk.Tk()
    chat_gui = ChatGUI(root)
    root.mainloop()
