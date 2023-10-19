def compute_checksum(data):
    checksum = 0
    for byte in data:
        checksum += ord(byte)
    checksum = checksum % 256
    return checksum