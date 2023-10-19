import socket
import threading
from biblio import*
import pickle 
import time

# Escolher nickname
nickname = input("Escolha seu nickname: ")

# Conectando ao servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostname(), 1333))

# Declarando variável do número de sequencia 
num_seq = 0
lock = threading.Lock()
  
# função simula um timer
def timer_callback():
    time.sleep(5)
    print("Tempo limite excedido. Nenhuma resposta do servidor.")

# Recebendo mensgem do servidor
def receive():
    while True:
        try:
            
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
                print('Mensagem não foi entregue corretamente, envie novamente!')
                
        except Exception as e :
            # Close Connection When Error
            print(f"Ocorreu um erro {e}")
            client.close()
            break
        
# Escreve uma mensagem e manda para o servidor
def write():
    flag = 0
    global num_seq
    while True:
        message = '{}: {}'.format(nickname, input(''))
        error1 = input('Deseja que a mensagem tenha erro?[Y/N] ')
        error2 = input('Deseja estourar o timer?[Y/N]')
        
        checksum = compute_checksum(message)
        with lock:
            num_seq += 1
        
        header = [checksum, num_seq, id_cliente, error1, error2]
        
        serialized_header = pickle.dumps(header)
        
        client.send(serialized_header)
        client.send(message.encode('ascii'))            
        
        if error2 == 'Y':   
            if flag == 0:
                response_timer = threading.Thread(target=timer_callback)
                response_timer.start()
                flag = 1
        

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()