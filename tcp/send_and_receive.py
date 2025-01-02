import socket
import customtkinter as ctk
from tkinter import filedialog, messagebox
from threading import Thread
import os

# Default server configuration
SERVER_HOST = '169.254.221.247'  # Replace with the server's IP address
SERVER_PORT = 22411           # Port to connect to
DEFAULT_RECEIVE_PORT = 22412  # Default receiving port
selected_file_path = None  # Global variable to store the selected file path
selected_receive_path = None
server_running = False
server_socket = None

# Function to select a file to send
def select_file():
    global selected_file_path
    selected_file_path = filedialog.askopenfilename(title="Select a File")
    if selected_file_path:
        messagebox.showinfo("File Selected", f"Selected File: {selected_file_path}")

# Function to send a file to the server
def send_file(file_path, host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            print(f"Connected to {host}:{port}")
            
            # Send the filename first
            filename = os.path.basename(file_path)
            client_socket.sendall(filename.encode('utf-8') + b'\n')
            
            # Send the file content
            with open(file_path, 'rb') as file:
                while chunk := file.read(1024):
                    client_socket.sendall(chunk)

            print("File and name sent successfully")
            messagebox.showinfo("Success", "File and name sent successfully!")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Failed to send file: {e}")

# Function to send the selected file
def send_selected_file():
    if not selected_file_path:
        messagebox.showerror("Error", "No file selected. Please select a file first.")
        return
    host = host_entry.get()
    port = port_entry.get()
    if not host or not port:
        messagebox.showerror("Error", "Please enter both IP address and port.")
        return
    try:
        port = int(port)
    except ValueError:
        messagebox.showerror("Error", "Port must be a number.")
        return
    send_file(selected_file_path, host, port)

# Function to handle receiving a file
def handle_connection(conn, addr, folder_path):
    try:
        print(f"Connection from {addr}")
        filename = conn.recv(1024).decode('utf-8').strip()
        if not filename:
            raise ValueError("No filename received.")
        
        save_path = os.path.join(folder_path, filename)
        print(f"Receiving file: {filename}")

        with open(save_path, 'wb') as file:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                file.write(data)

        print(f"File received and saved to {save_path}")
        messagebox.showinfo("File Received", f"File saved to: {save_path}")
    except Exception as e:
        print(f"Error handling connection: {e}")
    finally:
        conn.close()

# Function to start the receiving server
def start_server(host, port, folder_path):
    global server_running, server_socket
    server_running = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server is listening on {host}:{port}")

        while server_running:
            conn, addr = server_socket.accept()
            thread = Thread(target=handle_connection, args=(conn, addr, folder_path))
            thread.start()

# Function to start the server in a background thread
def start_server_thread(host, port, folder_path):
    thread = Thread(target=start_server, args=(host, port, folder_path))
    thread.daemon = True
    thread.start()

# Function to stop the server
def stop_server():
    global server_running
    server_running = False
    print('server closed.')
    messagebox.showinfo("Server Stopped", "The server has been stopped.")

# GUI Setup
def start_gui():
    root = ctk.CTk()
    root.title("File Transfer")

    # Create tabs
    tab_view = ctk.CTkTabview(root)
    tab_view.pack(expand=True, fill="both")

    send_tab = tab_view.add("Send File")
    receive_tab = tab_view.add("Receive File")

    # Send Tab
    ctk.CTkLabel(send_tab, text="Send File to Server").pack(pady=10)
    host_label = ctk.CTkLabel(send_tab, text="Server IP Address:")
    host_label.pack(pady=5)
    global host_entry
    host_entry = ctk.CTkEntry(send_tab)
    host_entry.insert(0, SERVER_HOST)
    host_entry.pack(pady=5)

    port_label = ctk.CTkLabel(send_tab, text="Server Port:")
    port_label.pack(pady=5)
    global port_entry
    port_entry = ctk.CTkEntry(send_tab)
    port_entry.insert(0, str(SERVER_PORT))
    port_entry.pack(pady=5)

    select_button = ctk.CTkButton(send_tab, text="Select File", command=select_file)
    select_button.pack(pady=10)
    send_button = ctk.CTkButton(send_tab, text="Send File", command=send_selected_file)
    send_button.pack(pady=10)

    send_abort_button = ctk.CTkButton(send_tab, text="Abort", command=lambda: messagebox.showinfo("Abort", "Send operation aborted."))
    send_abort_button.pack(pady=10)

    # Receive Tab
    ctk.CTkLabel(receive_tab, text="Receive File").pack(pady=10)
    receive_host_label = ctk.CTkLabel(receive_tab, text="Host Address:")
    receive_host_label.pack(pady=5)
    receive_host_entry = ctk.CTkEntry(receive_tab)
    receive_host_entry.insert(0, "0.0.0.0")
    receive_host_entry.pack(pady=5)

    receive_port_label = ctk.CTkLabel(receive_tab, text="Port:")
    receive_port_label.pack(pady=5)
    receive_port_entry = ctk.CTkEntry(receive_tab)
    receive_port_entry.insert(0, str(DEFAULT_RECEIVE_PORT))
    receive_port_entry.pack(pady=5)

    def select_folder():
        global selected_receive_path
        selected_receive_path = filedialog.askdirectory()

    def start_receive_server():
        global selected_receive_path, server_running
        if not selected_receive_path:
            messagebox.showerror("Error", "No folder selected.")
            return
        host = receive_host_entry.get()
        try:
            port = int(receive_port_entry.get())
            start_server_thread(host, port, selected_receive_path)
            messagebox.showinfo("Success", "Receiving server started.")
        except ValueError:
            messagebox.showerror("Error", "Invalid port number.")

    select_folder_button = ctk.CTkButton(receive_tab, text='Select Folder', command=select_folder)
    select_folder_button.pack(pady=10)

    start_server_button = ctk.CTkButton(receive_tab, text="Start Server", command=start_receive_server)
    start_server_button.pack(pady=10)

    receive_abort_button = ctk.CTkButton(receive_tab, text="Abort", command=stop_server)
    receive_abort_button.pack(pady=10)

    root.geometry("500x400")
    root.resizable(False, False)
    root.mainloop()

# Main entry point
if __name__ == "__main__":
    start_gui()
