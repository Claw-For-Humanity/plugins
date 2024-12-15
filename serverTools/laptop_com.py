# INSTRUCTIONS: MAKE SURE TO GO TO THE SERVER AND PERFORM 'hostname -I' and 'ip a'
# once the ip is retrieved, enter it to the host

import socket

def client(host='169.254.221.247', port=22411):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Connected to server at {host}:{port}")

    try:
        while True:
            message = input("Enter message to server: ")
            client_socket.sendall(message.encode())
            
            data = client_socket.recv(1024)
            if not data:
                print("Server disconnected.")
                break
            print(f"Server response: {data.decode()}")
    except KeyboardInterrupt:
        print("Client shutting down.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    client()
