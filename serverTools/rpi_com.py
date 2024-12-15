# sudo ip addr add 169.254.221.247/24 dev eth0



import socket

def start_server(host='0.0.0.0', port=12345):  # Bind to all available interfaces
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

if __name__ == "__main__":
    start_server()
