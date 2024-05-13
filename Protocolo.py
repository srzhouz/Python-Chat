import socket
import threading
import queue
import random

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"Mensaje recibido: {data.decode('utf-8')}")

    client_socket.close()

def main():
    host = '127.0.0.1'
    port = 5555

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((host, port))

    server_socket.listen(5)
    print(f"[*] Escuchando en {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"[*] Conexión aceptada de {client_address[0]}:{client_address[1]}")

        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
