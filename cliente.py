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
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            checksum = compute_checksum(nickname)
            if message == 'NICK': #salvar o nickname
                client.send(str(checksum).encode('ascii'))
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except Exception as e :
            # Close Connection When Error
            print(f"An error occured! {e}")
            client.close()
            break

def write():
    global num_seq
    while True:
        message = '{}: {}'.format(nickname, input(''))
        
        checksum = compute_checksum(message)
        with lock:
            num_seq += 1
        
        header = [checksum, num_seq]
        
        serialized_header = pickle.dumps(header)
        
        client.send(serialized_header)
        client.send(message.encode('ascii'))
        

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()