import socket
import threading
import os
import cv2
import tkinter as tk
from tkinter import filedialog

# Server function to handle incoming file transfers
def server():
    # Create TCP server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 5000))
    s.listen(1)
    print("Server is waiting for connection...")

    # Broadcast the server's IP address using UDP
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_message = socket.gethostbyname(socket.gethostname())  # Get server's IP address
    print(f"Broadcasting IP: {broadcast_message}")

    # Broadcast IP on a specific port
    broadcast_socket.sendto(broadcast_message.encode(), ('<broadcast>', 37020))
    broadcast_socket.close()

    # Accept the connection from the client
    conn, addr = s.accept()
    print(f"Connected by {addr}")

    # Receive the file
    filename = conn.recv(1024).decode()
    with open(filename, 'wb') as f:
        print(f"Receiving {filename}...")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
    print(f"{filename} received.")
    conn.close()

# Client function to send files
def client():
    # Listen for broadcast message to get server's IP
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('', 37020))  # Bind to the port where the server broadcasts
    print("Waiting for server broadcast...")

    # Receive the broadcast message (server IP)
    message, addr = udp_socket.recvfrom(1024)
    server_ip = message.decode()
    print(f"Received server IP: {server_ip}")

    # Connect to the server using the detected IP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, 5000))  # Use the broadcasted IP to connect to the server

    # Open file dialog to select files
    filenames = select_files()
    if not filenames:
        print("No files selected.")
        return

    for filename in filenames:
        s.send(filename.encode())  # Send file name
        with open(filename, 'rb') as f:
            s.sendall(f.read())  # Send file content
        print(f"{filename} sent.")

    s.close()

# Function to open file dialog and select files
def select_files():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    filenames = filedialog.askopenfilenames(title="Select Files")
    return list(filenames)

# Function to stream video (optional)
def stream_video(filename):
    cap = cv2.VideoCapture(filename)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Video Streaming', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Main function to choose between server and client
def main():
    print("Welcome to the Auto-Detect File Sharing Tool!")
    print("1. Run as Server")
    print("2. Send a File (Client)")
    print("3. Stream a Video")

    choice = input("Choose an option (1/2/3): ")

    if choice == '1':
        server()  # Start the server
    elif choice == '2':
        client()  # Start the client
    elif choice == '3':
        filename = select_video()  # File selection dialog opens for video
        if filename:
            stream_video(filename)  # Stream the selected video
        else:
            print("No video file selected.")
    else:
        print("Invalid choice. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    main()
