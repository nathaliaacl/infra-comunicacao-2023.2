import time

def compute_checksum(data):
    checksum = 0
    for byte in data:
        checksum += ord(byte)
    checksum = checksum % 256
    return checksum

def timer_funct(socket, timeout):
    time.sleep(timeout)
    socket.send(b'Tempo limite atingido')