import tkinter as tk
from tkinter import font, simpledialog

class ChatGUI:
    def __init__(self, master):
        self.master = master
        master.title("Chat")
        master.configure(bg="#f0f0f0")

        self.custom_font = font.Font(family="Roboto", size=12)

        self.users = ["Rodri", "Ivan B", "Carol", "Jiabo", "Ivan P"]
        self.current_user = None

        self.create_widgets()

    def create_widgets(self):
        def enviar_mensaje():
            if self.current_user:
                mensaje = self.entrada_mensaje.get()
                if mensaje.strip():
                    self.area_chat.insert(tk.END, f"{self.current_user}: {mensaje}\n", "other_message")
                    self.entrada_mensaje.delete(0, tk.END)

        def on_select(event):
            selected_index = self.lista_usuarios.curselection()
            if selected_index:
                selected_user = self.users[selected_index[0]]
                self.current_user = simpledialog.askstring("Chat con", f"¿Cómo te quieres llamar al chatear con {selected_user}?")
                if self.current_user:
                    self.area_chat.delete("1.0", tk.END)
                    self.area_chat.insert(tk.END, f"{selected_user}:\n", "other_message")
                    self.entrada_mensaje.configure(state=tk.NORMAL)

        main_frame = tk.Frame(self.master, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        frame_usuarios = tk.Frame(main_frame, bg="#ffffff", relief=tk.RAISED, borderwidth=1)
        frame_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, padx=20, pady=20)

        self.lista_usuarios = tk.Listbox(frame_usuarios, width=20, font=self.custom_font, bg="#f0f0f0", borderwidth=0)
        self.lista_usuarios.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
        self.lista_usuarios.bind('<<ListboxSelect>>', on_select)

        for user in self.users:
            self.lista_usuarios.insert(tk.END, user)

        frame_chat = tk.Frame(main_frame, bg="#f0f0f0")
        frame_chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.area_chat = tk.Text(frame_chat, width=60, height=20, font=self.custom_font, bg="#f0f0f0", borderwidth=0)
        self.area_chat.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
        self.area_chat.tag_configure("user_message", foreground="#333333", font=self.custom_font)
        self.area_chat.tag_configure("other_message", foreground="#666666", font=self.custom_font)

        frame_entrada = tk.Frame(frame_chat, bg="#f0f0f0")
        frame_entrada.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.entrada_mensaje = tk.Entry(frame_entrada, font=self.custom_font, bg="#f0f0f0", borderwidth=1, relief=tk.SOLID)
        self.entrada_mensaje.pack(side=tk.LEFT, fill=tk.X, expand=True)

        boton_enviar = tk.Button(frame_entrada, text="Enviar", font=self.custom_font, bg="#4CAF50", fg="#ffffff", command=enviar_mensaje)
        boton_enviar.pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    root = tk.Tk()
    chat_gui = ChatGUI(root)
    root.mainloop()
