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

# Sending DISCOVER message
message = "DISCOVER " + MAC
clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
# LISTENING FOR RESPONSE
message, _ = clientSocket.recvfrom(4096)
message_data = message.decode().split()

if message_data[0] == "OFFER":
    mac = message_data[1]
    offered_ip_add = message_data[2]
    timestamp = message_data[3]
    print(f"Server offered IP address {offered_ip_add} to client with MAC address {mac}.")
     # LISTENING FOR ACKNOWLEDGE OR DECLINE
    ack_response, _ = clientSocket.recvfrom(4096)
    ack_response_data = ack_response.decode().split()

    if ack_response_data[0] == "ACKNOWLEDGE":
        # Extract information from the ACKNOWLEDGE message
        ack_server_mac = ack_response_data[1]
        ack_assigned_ip = ack_response_data[2]
        ack_timestamp = ack_response_data[3]

        # Display relevant information to the user
        print(f"Server acknowledged IP address {ack_assigned_ip} for client with MAC address {ack_server_mac}.")
        
        # TODO: Implement further client logic based on the acknowledged IP address.
    # LISTENING FOR ACKNOWLEDGE OR DECLINE
    ack_response, _ = clientSocket.recvfrom(4096)
    ack_response_data = ack_response.decode().split()

    if ack_response_data[0] == "ACKNOWLEDGE":
        # Extract information from the ACKNOWLEDGE message
        ack_server_mac = ack_response_data[1]
        ack_assigned_ip = ack_response_data[2]
        ack_timestamp = ack_response_data[3]

        # Display relevant information to the user
        print(f"Server acknowledged IP address {ack_assigned_ip} for client with MAC address {ack_server_mac}.")
        
        # TODO: Implement further client logic based on the acknowledged IP address.

        # Simulate sending a RENEW message
        renew_message = f"RENEW {MAC} {ack_assigned_ip} {ack_timestamp}"
        clientSocket.sendto(renew_message.encode(), (SERVER_IP, SERVER_PORT))

        # LISTENING FOR RENEW ACKNOWLEDGE OR DECLINE
        renew_ack_response, _ = clientSocket.recvfrom(4096)
        renew_ack_response_data = renew_ack_response.decode().split()

        if renew_ack_response_data[0] == "ACKNOWLEDGE":
            # Extract information from the RENEW ACKNOWLEDGE message
            renew_ack_server_mac = renew_ack_response_data[1]
            renew_ack_assigned_ip = renew_ack_response_data[2]
            renew_ack_timestamp = renew_ack_response_data[3]

            # Display relevant information to the user
            print(f"Server renewed IP address {renew_ack_assigned_ip} for client with MAC address {renew_ack_server_mac}.")

        elif renew_ack_response_data[0] == "DECLINE":
            # Display a message indicating that the server declined the renew request
            print("Server declined the renew request. Please try again.")

        # Simulate sending a RELEASE message
        release_message = f"RELEASE {MAC} {ack_assigned_ip} {ack_timestamp}"
        clientSocket.sendto(release_message.encode(), (SERVER_IP, SERVER_PORT))

        # Display a message indicating that the client released the IP address
        print(f"Client released IP address {ack_assigned_ip}.")
    elif ack_response_data[0] == "DECLINE":
        # Display a message indicating that the server declined the request
        print("Server declined the request. Please try again.")

clientSocket.close()
