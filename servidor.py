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


lock = threading.Lock()

# Sending Messages To All Connected Clients
def broadcast(message, ack):
    for client in clients:     
        client.send(str(ack).encode('ascii'))
        client.send(message)

# Handling Messages From Clients
def handle(client):
    num_seq_esperado = 1
    com_janela = 0
    fin_janela = 4
    while True:
        try:
            # Broadcasting Messages
            ack = 1
            
            serialized_header = client.recv(1024)
            message = client.recv(200)
            
            header = pickle.loads(serialized_header)
            
            checksum = header[0]
            num_seq = header[1]            
            
            if num_seq > com_janela and num_seq < fin_janela: 
                
                checksum1 = compute_checksum(message.decode('ascii'))
                
                if num_seq == num_seq_esperado:
                    if checksum == checksum1:
                        ack = 0
                    else:
                        print('Checksum inválido, reenvie a mensagem!')                        
                else:
                    print(f'Pacote de numero {num_seq_esperado} perdido!')                    
                      
            else:
                print("Pacote fora da janela, espere para reenviar")
             
            if ack == 0:
                broadcast(message, ack)
                with lock:
                    num_seq_esperado += 1    
                com_janela += 1
                fin_janela += 1 
            else:
                client.send(str(ack).encode('ascii'))

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
        client.send('0'.encode('ascii'))
        client.send('NICK'.encode('ascii'))
        checksum = int(client.recv(1024).decode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        
        checksum1 = compute_checksum(nickname)
        
        if checksum == checksum1:
        
            nicknames.append(nickname)
            clients.append(client)

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            #client.send('0'.encode('ascii'))           
            #broadcast("{} joined!".format(nickname).encode('ascii'))
            #client.send('0'.encode('ascii'))
            #client.send('Connected to server!'.encode('ascii'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        else:
            print('Checksum inválido')
        
receive()