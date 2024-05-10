import socket
import threading

# Función para escuchar mensajes entrantes
def listen(sock):
    while True:
        # Recibe datos y dirección del remitente
        data, addr = sock.recvfrom(1024)
        # Muestra el mensaje recibido junto con la dirección del remitente
        print('\rMensaje recibido de {}: {}'.format(addr, data.decode()), end='')

# Función principal
def main():
    # Dirección y puerto local del cliente
    local_addr = ('0.0.0.0', 50001)

    # Crear un socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Enlazar el socket a la dirección y puerto local
    sock.bind(local_addr)

    # Hilo para escuchar mensajes entrantes
    listener = threading.Thread(target=listen, args=(sock,), daemon=True)
    listener.start()

    # Dirección y puerto del otro cliente
    remote_addr = ('147.182.184.215', 50002)  # Cambiar a la dirección y puerto del otro cliente

    while True:
        # Solicitar al usuario que ingrese un mensaje
        message = input('> ')
        # Enviar el mensaje al otro cliente utilizando la dirección y puerto remotos
        sock.sendto(message.encode(), remote_addr)

# Ejecutar la función principal si este archivo es el programa principal
if __name__ == "__main__":
    main()
