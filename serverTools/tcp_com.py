# sudo ip addr add 169.254.221.247/24 dev eth0

# INSTRUCTIONS: MAKE SURE TO GO TO THE SERVER AND PERFORM 'hostname -I' and 'ip a'
# once the ip is retrieved, enter it to the host

import socket

class tcp_com:

    def start_server(host='0.0.0.0', port=22411):  # Bind to all available interfaces
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server listening on {host}:{port}")

        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")

        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    print("Client disconnected.")
                    break
                print(f"Received: {data.decode()}")

                response = input("Enter response to client: ")
                conn.sendall(response.encode())
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            conn.close()
            server_socket.close()

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

