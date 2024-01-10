#!/usr/bin/env python3
import uuid
import socket
from datetime import datetime

# Time operations in python
# timestamp = datetime.fromisoformat(isotimestring)

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
        print("Choose an option:")
        print("1. List")
        print("2. Quit")

        choice = input("Enter your choice: ")
        if choice == "1":
            List = "LIST"
            clientSocket.sendto(List.encode(), ("127.0.0.1", 9000))
            list_response, _ = clientSocket.recvfrom(4096)
            print(f"list_response: {list_response.decode()}")
        elif choice == "2":
            print("Quitting the client program.")
            break
        else:
            print("Invalid choice. Please choose a valid option.")
clientSocket.close()
