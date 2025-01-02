import socket
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import time

# Default server configuration
SERVER_HOST = '169.254.221.247'  # Replace with the server's IP address
SERVER_PORT = 22411           # Port to connect to

selected_file_path = None  # Global variable to store the selected file path
is_connecting = False  # Flag to control the animation

def select_file():
    """Open a file dialog to select a file."""
    global selected_file_path
    selected_file_path = filedialog.askopenfilename(title="Select a File")
    if selected_file_path:
        messagebox.showinfo("File Selected", f"Selected File: {selected_file_path}")

def connect_with_animation(file_path, host, port):
    """Attempt connection with dot animation."""
    global is_connecting
    is_connecting = True
    
    # Start the animation in a separate thread
    threading.Thread(target=dot_animation).start()

    try:
        send_file(file_path, host, port)
    finally:
        is_connecting = False  # Stop the animation

def dot_animation():
    """Show a dot animation while connecting."""
    dots = ["", ".", "..", "..."]
    while is_connecting:
        for dot in dots:
            connecting_label.configure(text=f"Connecting{dot}")
            time.sleep(0.5)  # Adjust the speed of the animation

def send_file(file_path, host, port):
    """Send the specified file and its name to the server."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(5)  # Set timeout to 5 seconds
            try:
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
            except socket.timeout:
                print("Connection timed out.")
                messagebox.showerror("Timeout Error", "Connection timed out after 5 seconds.")
            except socket.error as e:
                print(f"Connection error: {e}")
                messagebox.showerror("Connection Error", f"Failed to connect to the server: {e}")
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", f"Failed to send file: {e}")

def send_selected_file():
    """Send the previously selected file to the server."""
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

    # Start the connection process with animation
    threading.Thread(target=connect_with_animation, args=(selected_file_path, host, port)).start()

# Create the GUI
ctk.set_appearance_mode("System")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

root = ctk.CTk()
root.title("File Sender")

# Add instructions label
label = ctk.CTkLabel(root, text="Select a file to send to the server", font=("Ubuntu", 14))
label.pack(pady=10)

# Add input fields for IP address and port
host_label = ctk.CTkLabel(root, text="Server IP Address:", font=("Ubuntu", 12))
host_label.pack(pady=5)
host_entry = ctk.CTkEntry(root, placeholder_text="Enter IP address", font=("Ubuntu", 12))
host_entry.insert(0, SERVER_HOST)
host_entry.pack(pady=5)

port_label = ctk.CTkLabel(root, text="Server Port:", font=("Ubuntu", 12))
port_label.pack(pady=5)
port_entry = ctk.CTkEntry(root, placeholder_text="Enter port", font=("Ubuntu", 12))
port_entry.insert(0, str(SERVER_PORT))
port_entry.pack(pady=5)

# Add a button to select a file
select_button = ctk.CTkButton(root, text="Select File", command=select_file, font=("Ubuntu", 12))
select_button.pack(pady=10)

# Add a button to send the selected file
send_button = ctk.CTkButton(root, text="Send File", command=send_selected_file, font=("Ubuntu", 12))
send_button.pack(pady=10)

# Add a label for connection animation
connecting_label = ctk.CTkLabel(root, text="", font=("Ubuntu", 12))
connecting_label.pack(pady=10)

# Run the GUI event loop
root.geometry("400x400")
root.mainloop()
