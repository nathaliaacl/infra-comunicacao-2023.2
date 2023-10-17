import socket
import threading
from biblio import*

# Choosing Nickname
nickname = input("Choose your nickname: ")

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostname(), 1333))

# Listening to Server and Sending Nickname
def receive():
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK': #salvar o nickname
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except Exception as e :
            # Close Connection When Error
            print(f"An error occured! {e}")
            client.close()
            break

def write():
    while True:
        message = '{}: {}'.format(nickname, input(''))
        checksum = str(compute_checksum(message))
        client.send(checksum.encode('ascii'))
        client.send(message.encode('ascii'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()