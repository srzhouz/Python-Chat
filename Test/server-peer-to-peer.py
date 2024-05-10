import socket 

#Puerto al que se enviarán los detalles de conexión.
known_port = 5002

#Crear un socket UDP.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#Enlazar el socket a todas las interfaces en el puerto 55555
sock.bind(('0.0.0.0', 55555))

while True:
    clients = []
    
    #Esperar conexiones entrantes de dos clientes.
    while True:
        #Recibir datos y dirección del cliente.
        data, address = sock.recvfrom(128)

        print('connection from: {}'.format(address))
        #Agregar la dirección del cliente a la lista de clientes conectados.
        clients.append(address)

        #Enviar mensaje de 'listo' de vuelta al cliente.
        sock.sendto(b'ready', address)

        #Si se han conectado dos clientes, salir del bucle.
        if len(clients) == 2:
            print(' got 2 clients, sending details to each')
            break

    #Extraer los detalles de cada cliente.
    c1 = clients.pop()
    c1_addr, c1_port = c1
    c2 = clients.pop()
    c2_addr, c2_port = c2

    #Enviar los detalles de conexión (dirección IP y puerto) de un cliente al otro.
    sock.sendto('{} {} {}'.format(c1_addr, c1_port, known_port).encode(), c2)
    sock.sendto('{} {} {}'.format(c2_addr, c2_port, known_port).encode(), c1)
