#!/usr/bin/env python3
import socket
from ipaddress import IPv4Interface
from datetime import datetime, timedelta
import signal

def handle_interrupt(signum, frame):
    print("Received Ctrl+C. Closing server...")
    server.close()



# Time operations in python
# isotimestring = datetime.now().isoformat()
# timestamp = datetime.fromisoformat(isotimestring)
# 60secfromnow = timestamp + timedelta(seconds=60)

# Choose a data structure to store your records
records = {} #using a dictionary

# List containing all available IP addresses as strings
ip_addresses = [ip.exploded for ip in IPv4Interface("192.168.45.0/28").network.hosts()]

# Parse the client messages
def parse_message(message):
    return message.decode().split()
    


# Calculate response based on message
def dhcp_operation(parsed_message):
    request = parsed_message[0]
    print(request)
    if request == "LIST":
        return "\n".join([f"{record} {records[record]}" for record in records])
    

    elif request == "DISCOVER":
        mac = parsed_message[1]
        if mac in records:
            record = records[mac]
            if record["timestamp"] + timedelta(seconds=60) > datetime.now():
                record["Acked"] = True
                return print(f"ACKNOWLEDGE {mac} {record['ip_address']} {record['timestamp']}")
            else:
                record["timestamp"] = datetime.now() + timedelta(seconds=60)
                record["Acked"] = False
                return print(f"OFFER {mac} {record['ip_address']} {record['timestamp']}")
        else:
            for ip in ip_addresses:
                 if ip not in [record["ip_address"] for record in records.values()]:
                    records[mac] = {
                        "ip_address": ip,
                        "timestamp": datetime.now() + timedelta(seconds=60),
                        "Acked": False,
            }
            return print(f"OFFER {mac} {ip} {records[mac]['timestamp']}")
        return "DECLINE"
    
    
    elif request == "REQUEST":
        mac = parsed_message[1]
        ip_address = parsed_message[2]
        timestamp = parsed_message[3]
        if mac in records and records[mac]["ip_address"] == ip_address:
            if records[mac]["timestamp"] + timedelta(seconds=60) > datetime.now():
                records[mac]["Acked"] = True
                return f"ACKNOWLEDGE {mac} {ip_address} {timestamp}"
            else:
                return "DECLINE"
        else:
            return "DECLINE"
        

    elif request == "RELEASE":
        mac = parsed_message[1]
        ip_address = parsed_message[2]
        timestamp = parsed_message[3]
        if mac in records:
            records[mac]["timestamp"] = datetime.now()
            records[mac]["Acked"] = False
            return ""
        else:
            return ""
        

    elif request == "RENEW":
        mac = parsed_message[1]
        ip_address = parsed_message[2]
        timestamp = parsed_message[3]
        if mac in records:
            records[mac]["timestamp"] = datetime.now() + timedelta(seconds=60)
            records[mac]["Acked"] = True
            return f"ACKNOWLEDGE {mac} {ip_address} {records[mac]['timestamp']}"
        else:
            for ip in ip_addresses:
                if ip not in [record["ip_address"] for record in records.values()]:
                    records[mac] = {
                    "ip_address": ip,
                    "timestamp": datetime.now() + timedelta(seconds=60),
                    "Acked": False,
                }
                return f"OFFER {mac} {ip} {records[mac]['timestamp']}"
            return "DECLINE"


# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Avoid TIME_WAIT socket lock [DO NOT REMOVE]
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 9000))
print("DHCP Server running...")

try:
    while True:
        message, clientAddress = server.recvfrom(4096)
        print("Received message:", message.decode())
        parsed_message = parse_message(message)
        print("Parsed message:", parsed_message)  # Print parsed message
        response = dhcp_operation(parsed_message)

        server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()
