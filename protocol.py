import json
import struct
import logging

#usign the length of the message to read the message and convert them to data
def read_n_bytes(read, n):
    data = bytearray(read(n))
    while len(data) < n:
        data += read(n - len(data))
    assert len(data) == n
    return data

#read message from the socket and convert them to json
def read_message(read):
    # read message size as a four-byte integer value in network order
    size = struct.unpack('!i', read_n_bytes(read, 4))[0]
    # read message as json data
    message = json.loads(read_n_bytes(read, size))
    pass # logging.debug(f'read message: {message}')
    return message

#write message to the socket and convert them to json
def write_message(write, message):
    pass # logging.debug(f'write message: {message}')
    data = json.dumps(message).encode()
    write(struct.pack('!i', len(data)) + data)

