import socket
import threading
from biblio import*
import pickle
import time

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostname(), 1333))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []
id_cliente = -1

lock = threading.Lock()

# Sending Messages To All Connected Clients
def broadcast(message, ack):
    for client in clients:     
        client.send(str(ack).encode('ascii'))
        client.send(message)

# Handling Messages From Clients
def handle(client):
    num_seq_esperado = 1
    flag = 0
    while True:
        try:
            # Broadcasting Messages
                        
            ack = 1
            
            serialized_header = client.recv(1024)
            message = client.recv(200)
            
            header = pickle.loads(serialized_header)
            
            checksum = header[0]
            num_seq = header[1]
            cliente_id = header[2]
            error1 = header[3]
            error2 = header[4]
                        
            num_seq = num_seq + (cliente_id * 50)
            
            if flag == 0:
                com_janela = cliente_id * 50
                num_seq_esperado = num_seq_esperado + (cliente_id * 50)
                flag = 1
                
            if num_seq > com_janela:
                
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
                
            if error1 == 'Y':
                ack = 1
                
            if error2 == 'Y':
                time.sleep(6) 
                ack = 1           
             
            if ack == 0:
                broadcast(message, ack)
                with lock:
                    num_seq_esperado += 1   
            else:
                client.send(str(ack).encode('ascii'))
                with lock:
                    num_seq_esperado += 1

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
    global id_cliente
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Conectado com {}".format(str(address)))

        # Request And Store Nickname
        client.send('0'.encode('ascii'))
        client.send('NICK'.encode('ascii'))
        checksum = int(client.recv(1024).decode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        
        checksum1 = compute_checksum(nickname)
        
        if checksum == checksum1:
            
            id_cliente += 1
        
            nicknames.append(nickname)
            clients.append(client)
            #client_id.append(id_cliente)
            
            client.send(str(id_cliente).encode('ascii'))

            # Print And Broadcast Nickname
            print("Nickname é {}".format(nickname))

            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
        else:
            print('Checksum inválido')
        
receive()