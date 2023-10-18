import socket
import threading
from biblio import*
import pickle

# Connection Data
#host = '127.0.0.1'
#port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostname(), 1333))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []

num_seq_esperado = 1
lock = threading.Lock()

# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Handling Messages From Clients
def handle(client):
    global num_seq_esperado
    while True:
        try:
            # Broadcasting Messages
            serialized_header = client.recv(1024)
            message = client.recv(200)
            
            header = pickle.loads(serialized_header)
            
            checksum = int(header[0])
            num_seq = header[1]
            
            checksum1 = compute_checksum(message.decode('ascii'))
            
            if checksum == checksum1 and num_seq == num_seq_esperado:
                broadcast(message)
                with lock:
                    num_seq_esperado += 1
            else:
                print('Checksum inválido, reenvie a mensagem')
                #mandar para o cliente uma flag de erro oara reenviar a mensagem
                break

        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode('ascii'))
            nicknames.remove(nickname)
            break
# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK'.encode('ascii'))
        checksum = int(client.recv(1024).decode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        
        checksum1 = compute_checksum(nickname)
        
        if checksum == checksum1:
        
            nicknames.append(nickname)
            clients.append(client)

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            broadcast("{} joined!".format(nickname).encode('ascii'))
            client.send('Connected to server!'.encode('ascii'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        else:
            print('Checksum inválido')
        
receive()