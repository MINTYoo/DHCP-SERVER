#!/usr/bin/env python3
import uuid
import socket
from datetime import datetime, timedelta

# Time operations in python
# timestamp = datetime.fromisoformat(isotimestring)

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()
offer = False
# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000


def parse_message(message):
    if isinstance(message, bytes):
        decoded_message = message.decode()
        return decoded_message.split()
    elif isinstance(message, str):
        return message.split()
    else:
        raise ValueError("Invalid message type. Expected bytes or str.")


def checkClientMac(macAdd):
    return macAdd== MAC
      


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(8)  # Set a timeout value in seconds

def send_message(message):
    clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
    response, _ = clientSocket.recvfrom(4096)
    return response.decode()

def checkTimeStamp(time):
    timestamp = datetime.fromisoformat(time)
    expiration_time = datetime.now() + timedelta(seconds=60)

    if timestamp < expiration_time:
        return True
    else:
        return False


def handleDiscover(message):
    response = message[0][:-1]
    clientmac = message[1]
    clientIP = message[2]
    clientTimeStamp = message[3]
    if response == "OFFER":
        if checkClientMac(clientmac):
            if checkTimeStamp(clientTimeStamp): #possible error
                request_message = f"REQUEST {clientmac} {clientIP} {clientTimeStamp}"
                clientSocket.sendto(request_message.encode(), ("127.0.0.1", 9000))
                ACK_response, _ = clientSocket.recvfrom(4096)
                print(f"Received request: {ACK_response.decode()}")
        else:
            print("Timestamp has expired. Exiting.")
            quit()
    elif(response == "ACKNOWLEDGE"):
        if not checkClientMac(clientmac):
            print("Invalid MAC address in ACKNOWLEDGE message. Exiting.")
            quit()
        else:
            #ACK_response, _ = clientSocket.recvfrom(4096) // possible error
            print("Received:", ' '.join(message))
    elif(response == "DECLINE"):
        print("system resources are exhausted. Please try later.")
        quit()
try:
    # Sending DISCOVER message
    discover_message = f"DISCOVER {MAC} "
    print(f"Sending: {discover_message}")
    clientSocket.sendto(discover_message.encode(), ("127.0.0.1", 9000))

    # Print received response
    response, _ = clientSocket.recvfrom(4096)
    print(f"Received : {response.decode()}")
    parsed_message = parse_message(response)
    handleDiscover(parsed_message)
    while True:
        print("Choose an option:")
        print("1. Renew")
        print("2. Release")
        print("3. Quit")

        choice = input("Enter your choice: ")

        if choice == "1":
            Time = f"{parsed_message[3]} {parsed_message[4]}"
            renew_message = f"RENEW {MAC} {parsed_message[2]} {Time}"
            clientSocket.sendto(renew_message.encode(), ("127.0.0.1", 9000))
            renew_response, _ = clientSocket.recvfrom(4096)
            if(renew_response.decode() == "DISCOVER"):
                #send message
                discover_message = f"DISCOVER {MAC} "
                print(f"Sending: {discover_message}")
                clientSocket.sendto(discover_message.encode(), ("127.0.0.1", 9000))

                # Print received response
                response, _ = clientSocket.recvfrom(4096)
                print(f"Received Response: {response.decode()}")
                parsed_message = parse_message(response)
                handleDiscover(parsed_message)
            elif(renew_response.decode() == "OFFER"):
                handleDiscover(parsed_message)
            print(f"Received: {renew_response.decode()}")
        elif choice == "2":
            Time = f"{parsed_message[3]} {parsed_message[4]}"
            release_message = f"RELEASE {MAC} {parsed_message[2]} {Time}"
            clientSocket.sendto(release_message.encode(), ("127.0.0.1", 9000))
            release_response, _ = clientSocket.recvfrom(4096)
            print(f"Received: {release_response.decode()}")
        elif choice == "3":
            print("Quitting the client program.")
            break
        else:
            print("Invalid choice. Please choose a valid option.")
except socket.timeout:
    print("Timeout: No response received from the server.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    clientSocket.close()
