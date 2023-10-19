import socket
import threading
from biblio import*
import pickle 

# Choosing Nickname
nickname = input("Choose your nickname: ")

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostname(), 1333))

num_seq = 0
lock = threading.Lock()

# Listening to Server and Sending Nickname
def receive():
    global error
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            ack = int(client.recv(1).decode('ascii'))
            
            if ack == 0:            
                message = client.recv(1024).decode('ascii')
                checksum = compute_checksum(nickname)
                if message == 'NICK': #salvar o nickname
                    client.send(str(checksum).encode('ascii'))
                    client.send(nickname.encode('ascii'))
                    global id_cliente
                    id_cliente = int(client.recv(1).decode('ascii'))
                else:
                    print(message)
            else:
                print('Mensagem não foi entregue corretamente')
                
        except Exception as e :
            # Close Connection When Error
            print(f"Ocorreu um erro {e}")
            client.close()
            break

def write():
    global num_seq
    while True:
        message = '{}: {}'.format(nickname, input(''))
        global error
        error = input('Deseja que a mensagem tenha erro?[Y/N] ')
        
        checksum = compute_checksum(message)
        with lock:
            num_seq += 1
        
        header = [checksum, num_seq, id_cliente, error]
        
        serialized_header = pickle.dumps(header)
        
        client.send(serialized_header)
        client.send(message.encode('ascii'))
        

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()