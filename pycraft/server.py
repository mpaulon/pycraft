import enum
import socket
import struct
import threading

# utilities
import pycraft.utils.hexprint as hexprint
import pycraft.utils.formats as formats
import pycraft.utils.cryptography as cryptography

# packets handling
import pycraft.packets.handshake
import pycraft.packets.status


BUFF = 2097151 # buffer size
HOST = 'localhost'# IP address of host
PORT = 25565 # Port number for client & server to recieve data

class State(enum.Enum):
    HANDSHAKE = 0
    STATUS = 1
    LOGIN = 2

class Client():

    def __init__(self, server, socket, address):
        self.server = server
        self.socket = socket
        self.address = address
        self.state = State.HANDSHAKE
        self.running = True
    
    # https://github.com/wbolster/byteme/blob/master/byteme/leb128.py 
    #TODO: write module in utilities to handle variables formats

    def repl(self, data):
        lenght = formats.varint_to_data(len(data))
        print(f"{self.server.address}:{self.server.port} -> {self.address[0]}:{self.address[1]}")
        hexprint.hexprint(lenght + data)
        self.socket.send(lenght + data)

    def parse_packet(self, data):
        if len(data) == 0:
            print("Empty data")
            return
        print(f"{self.address[0]}:{self.address[1]} -> {self.server.address}:{self.server.port}")
        hexprint.hexprint(data)
        lenght, next_bit = formats.varint_from_data(data)
        if len(data[next_bit:]) != lenght: 
            print(f"Invalid lenght, announced: {lenght}, got {len(data[next_bit:])}")
            # raise ValueError(f"Invalid lenght, announced: {lenght}, got {len(data[next_bit:])}")
        pk_id, next_bit = formats.varint_from_data(data, current=next_bit)
        if pk_id == 0x00 and self.state == State.HANDSHAKE: # new handshake packet
            #TODO: do something with protocol version, address and port
            self.proto_version, address, port, next_state = pycraft.packets.handshake.parse_handshake(self, data[next_bit:])
            self.state = State(next_state)
        elif pk_id == 0x00 and self.state == State.STATUS: # status request packet
            pycraft.packets.status.status(self)
        elif pk_id == 0x01 and self.state == State.STATUS: # ping
            payload = data[next_bit:]
            pycraft.packets.status.pong(self, payload)
        elif pk_id == 0x00 and self.state == State.LOGIN: # login packet
            pycraft.packets.login.encryption_request(self)
        else:
            print(f"Unknown packet in state {self.state}: {hex(pk_id)}")

    def stop(self):
        self.running = False

    def run(self):
        while self.server.running and self.running:
            data = self.socket.recv(BUFF)
            self.parse_packet(data)
            if not data: break
        else:
            self.socket.close()
        print(f"Disconnecting client {self.address[0]}:{self.address[1]}")


class Server():
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.running = False

        # TODO: config
        self.max_players = 10
        self.description = "WIP server"
        self.favicon = None
        # self.private_key, self.public_key = cryptography.genrsakeypair(1024)

    def online_players(self):
        #TODO: online playes
        return 0
    
    def run(self):
        self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.address, self.port))
        self.socket.listen(0)
        self.running = True
        while self.running:
            client_sock, addr = self.socket.accept()
            client = Client(self, client_sock, addr)
            t = threading.Thread(target=client.run)
            t.start()
            t.join()