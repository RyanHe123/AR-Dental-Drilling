import socket
import numpy as np
from scipy.spatial.transform import Rotation
from SupportiveFunctions import build_transformation
if __name__ == "__main__":
    HOST = '10.203.161.65'  
    PORT = 12345 

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()      
    print(f"Server listening on {HOST}:{PORT}")

    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    with client_socket:
        print(f"Connected by {client_address}")
        while True:
            data = client_socket.recv(1024)
            if not data:
                continue
            else:
                datastr = str(data, encoding='utf-8')
                print(datastr)