import socket
import customtkinter as ctk
from threading import Thread
from tkinter import filedialog, messagebox
import os

# Function to handle the server's communication
def handle_connection(conn, addr, folder_path):
    print(f"Connection from {addr}")
    try:
        # Receive the filename
        filename = conn.recv(1024).decode('utf-8').strip()
        if not filename:
            raise ValueError("No filename received.")
        
        save_path = os.path.join(folder_path, filename)
        print(f"Receiving file: {filename}")

        # Receive the file content
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

# Function to start the server in a separate thread
def start_server(host, port, folder_path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Server is listening on {host}:{port}")

        while True:
            conn, addr = server_socket.accept()
            thread = Thread(target=handle_connection, args=(conn, addr, folder_path))
            thread.start()

# Function to start the server in a background thread
def start_server_thread(host, port, folder_path):
    thread = Thread(target=start_server, args=(host, port, folder_path))
    thread.daemon = True  # Allow the thread to close when the main program exits
    thread.start()

# GUI Setup
def start_gui():
    root = ctk.CTk()

    # Set window title and size
    root.title("File Receiver")
    root.geometry("400x300")
    root.resizable(0, 0)

    # Host input
    host_label = ctk.CTkLabel(root, text="Enter Host (e.g., 0.0.0.0):")
    host_label.pack(pady=5)
    host_entry = ctk.CTkEntry(root)
    host_entry.pack(pady=5)
    host_entry.insert(0, "0.0.0.0")  # Default value

    # Port input
    port_label = ctk.CTkLabel(root, text="Enter Port (e.g., 22411):")
    port_label.pack(pady=5)
    port_entry = ctk.CTkEntry(root)
    port_entry.pack(pady=5)
    port_entry.insert(0, "22411")  # Default value

    # Select folder button
    folder_path = None

    def on_select_folder():
        nonlocal folder_path
        folder_path = filedialog.askdirectory()
        if folder_path:
            messagebox.showinfo("Folder Selected", f"Selected Folder: {folder_path}")

    folder_button = ctk.CTkButton(root, text="Select Folder", command=on_select_folder)
    folder_button.pack(pady=10)

    # Function to get input values and start the server
    def on_start_server():
        host = host_entry.get()
        try:
            port = int(port_entry.get())
            if folder_path:
                start_server_thread(host, port, folder_path)
                messagebox.showinfo("Server Started", f"Server started on {host}:{port}")
            else:
                messagebox.showerror("Error", "Please select a folder for the file destination.")
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")

    # Start server button
    start_button = ctk.CTkButton(root, text="Start Server", command=on_start_server)
    start_button.pack(pady=20)

    root.mainloop()

# Main entry point
if __name__ == "__main__":
    start_gui()
