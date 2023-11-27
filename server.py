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
    response = ""
    if request == "LIST":
        print("were in LIST!")
        response = "\n".join([f"{record} {records[record]}" for record in records])
    elif request == "DISCOVER":
        mac = parsed_message[1]
        timestamp = datetime.now()

        #print (f"I see that the client with MAC address {mac} is discovering.")
        if mac in records:
            print("Timestamp in records:", records[mac]['timestamp'])
            print("Current time + 60 seconds:", datetime.now() + timedelta(seconds=60))
            if records[mac]['timestamp'] < datetime.now() + timedelta(seconds = 60):
                print("test1")
                print(f"Processing DISCOVER for MAC address: {mac}")
                records[mac]['timestamp'] = timestamp + timedelta(seconds=60)
                print(f"Updated timestamp: {records[mac]['timestamp']}")
                records[mac]['Acked'] = False
                response = f"OFFER: {mac} {records[mac]['ip_address']} {records[mac]['timestamp']}--note this ip has already been assigned to you"
                print("Response:", response)

            elif records[mac]['timestamp'] + timedelta(seconds=60) > datetime.now():
                print("test2")
                records[mac]['Acked'] = True
                response = f"ACKNOWLEDGE : {mac} {records['ip_address']} {records[mac]['timestamp']}"
        else:
            for ip in ip_addresses:        
                if ip not in [record['ip_address'] for record in records.values()]:
                    print("test3")
                    records[mac] = {
                        "ip_address": ip,
                        "timestamp": datetime.now() + timedelta(seconds=60),
                        "Acked": False,
                    }
                    response = f"OFFER: {mac} {ip} {records[mac]['timestamp']} "
                    break

                else:
                    for existing_mac  in records:
                        if records["timestamp"] < datetime.now() - timedelta(seconds=60):
                            print("test4")
                            records[existing_mac] = {
                                "ip_address": ip,
                                "timestamp": timestamp + timedelta(seconds=60),
                                "Acked": False,
                            }
                            response =  f"Assigning to : {existing_mac } {records['ip_address']} with an experation date of {records[mac]['timestamp']} " 
                            print("response")
            if not response:
                response = "DECLINE"
                print("response")

    elif request == "REQUEST":
        mac = parsed_message[1]
        ip_address = parsed_message[2]
        timestamp = parsed_message[3]
        if mac in records and records[mac]["ip_address"] == ip_address:
            if records[mac]["timestamp"] + timedelta(seconds=60) > datetime.now():
                records[mac]["Acked"] = True
                response = (f"ACKNOWLEDGE {mac} {ip_address} {timestamp} \nIP address {ip_address} was assigned to this client, which will be expired at time {records[mac]['timestamp']}")
            else:
                response = ("DECLINE")
        else:
            response = ("DECLINE")  

    elif request == "RELEASE":
        mac = parsed_message[1]
        if mac in records:
            records[mac] = {
                "ip_address" : "",
                "timestamp": datetime.now() + timedelta(seconds=60),
                "Acked": False,
            }
    elif request == "RENEW":
            mac = parsed_message[1]
            print("Inside RENEW case")
            if mac in records:
                records[mac]["timestamp"] = datetime.now() + timedelta(seconds=60)
                records[mac]["Acked"] = True
                response = f"ACKNOWLEDGE {mac} {'ip_address'} {records[mac]['timestamp']}"
            else:
                for ip in ip_addresses:        
                    if ip not in [record['ip_address'] for record in records.values()]:
                        records[mac] = {
                            "ip_address": ip,
                            "timestamp": timestamp + timedelta(seconds=60),
                            "Acked": False,
                        }
                        response = f"OFFER: {mac} {ip} {records[mac]['timestamp']} "
                        print(response)
                    else:
                        for existing_mac in records:
                            if records[existing_mac]["timestamp"] < timestamp - timedelta(seconds=60):
                                records[existing_mac] = {
                                    "ip_address": ip,
                                    "timestamp": timestamp + timedelta(seconds=60),
                                    "Acked": False,
                                }
                                response =  f"OFFER: {mac} {records['ip_address']} {records[mac]['timestamp']} " 
                if not response:
                    response = "DECLINE"
    return response

# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Avoid TIME_WAIT socket lock [DO NOT REMOVE]
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("127.0.0.1", 9000))
print("DHCP Server running...")

try:
    while True:
        message, clientAddress = server.recvfrom(4096)
        parsed_message = parse_message(message)
        #client = f"SERVER: I see that the client with MAC address {parsed_message[1]} is discovering."
        #server.sendto(client.encode(), clientAddress)
        response = dhcp_operation(parsed_message)
        print("success")
        server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()
