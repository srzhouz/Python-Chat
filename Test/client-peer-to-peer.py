import socket
import sys
import threading

#Dirección IP y puerto del servidor de punto de encuentro.
rendezvous = ('147.182.184.215', 55555)

#Conectarse al servidor del punto de encuentro.
print('connecting to rendezvous server')

#Crear un socket UDP y enlazarlo al puerto 50001 para enviar un mensaje de registro al servidor de punto de encuentro.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 50001))
sock.sendto(b'0', rendezvous)

while True:
    #Esperar la respuesta del servidor.
    data = sock.recv(1024).decode()

    #Cuando se recibe 'ready', se habrá registrado con el servidor y se podrá continuar.
    if data.strip() == 'ready':
        print('checked in with server, waiting')
        break

#Obtener la información del par( la IP, puerto orígen y puerto destino desde el servidor).
data = sock.recv(1024).decode()
ip, sport, dport = data.split('')
sport = int(sport)
dport = int(dport)

print('\ngot peer')
print(' ip: {}'.format(ip))
print(' source port: {}'.format(sport))
print(' dest port: {}'.format(dport))


#Hacer el punch hole
#Esto es lo mismo que: echo 'punch hole' | nc -u -p 50001 x.x.x.x 50002
print('punching hole')

#Crear un nuevo socket para enviar un mensaje de perforación al par.
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', sport))
sock.sendto(b'0', (ip, dport))

print('ready to exchange messages\n')

#Escuchar mensajes entrantes del par.
#Esto es lo mismo que: nc -u -l 50001
def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', sport))

    while True:
        data = sock.recv(1024)
        print('\rpeer: {}\n>'.format(data.decode()), end='')

#Iniciar un hilo para la función de escucha.
listener = threading.Thread(target=listen, daemon=True);
listener.start()

#Enviar mensajes al par.
#Esto es lo mismo que: echo 'xxx' | nc -u -p 50002 x.x.x.x 50001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', dport))

while True:
    msg = input('> ')
    sock.sendto(msg.encode(), (ip, sport))
