import tkinter as tk

def enviar_mensaje():
    mensaje = entrada_mensaje.get()
    if mensaje.strip():
        area_chat.insert(tk.END, f"Tú: {mensaje}")
        entrada_mensaje.delete(0, tk.END)

def recibir_mensaje(remitente, mensaje):
    area_chat.insert(tk.END, f"{remitente}: {mensaje}")
    
ventana = tk.Tk()
ventana.title("Chat")

frame_usuarios = tk.Frame(ventana)
frame_usuarios.pack(side=tk.LEFT, fill=tk.BOTH)

lista_usuarios = tk.Listbox(frame_usuarios, width=20)
lista_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

lista_usuarios.insert(tk.END, "Usuario 1")
lista_usuarios.insert(tk.END, "Usuario 2")
lista_usuarios.insert(tk.END, "Usuario 3")

frame_chat = tk.Frame(ventana)
frame_chat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

area_chat = tk.Text(frame_chat, width=60, height=20)
area_chat.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

entrada_mensaje = tk.Entry(frame_chat)
entrada_mensaje.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10, expand=True)

boton_enviar = tk.Button(frame_chat, text="Enviar", command=enviar_mensaje)
boton_enviar.pack(side=tk.LEFT, padx=10, pady=10)

ventana.mainloop()
