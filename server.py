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
RememberIP  = {}
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
        client_info_list = []
        for mac, client_info in records.items():
            if client_info['Acked']:
                info_str = f"MAC: {mac}, IP Address: {client_info['ip_address']}, Timestamp: {client_info['timestamp']}, Acked: {client_info['Acked']}"
                client_info_list.append(info_str)
        return '\n'.join(client_info_list)

    elif request == "DISCOVER":
        mac = parsed_message[1]
        timestamp = datetime.now()

        
        #print (f"I see that the client with MAC address {mac} is discovering.")
        if mac in records:
            print("Timestamp in records:", records[mac]['timestamp'])
            print("Current time + 60 seconds:", datetime.now() + timedelta(seconds=60))
            #expired timestamp case
            if records[mac]['timestamp'] < datetime.now():
                print(f"Processing DISCOVER for MAC address: {mac}")
                records[mac]['timestamp'] = timestamp + timedelta(seconds=60)
                print(f"Updated timestamp: {records[mac]['timestamp']}")
                records[mac]['Acked'] = False
                response = f"OFFER: {mac} {records[mac]['ip_address']} {records[mac]['timestamp']}"
                print("Response:", response)
            #non-expired timestamp case
            elif records[mac]['timestamp']  > datetime.now():
                records[mac]['Acked'] = True
                response = f"ACKNOWLEDGE: {mac} {records[mac]['ip_address']} {records[mac]['timestamp']} \nyou will have your previous IP address: {records[mac]['ip_address']}"
        else:
            #get new IP from list else check if any timestamps have expired
            if len(records) == len(ip_addresses):
                response = "DECLINE: No available IP addresses."
            else:
                for ip in ip_addresses:        
                    if ip not in [record['ip_address'] for record in records.values()]:
                        records[mac] = {
                            "ip_address": ip,
                            "timestamp": datetime.now() + timedelta(seconds=60),
                            "Acked": False,
                        }
                        response = f"OFFER: {mac} {ip} {records[mac]['timestamp']} "
                        break

                    else:
                        for existing_mac in records:
                            if records[existing_mac]["timestamp"] < datetime.now():
                                print("test4")
                                records[existing_mac] = {
                                    "ip_address": ip,
                                    "timestamp": timestamp + timedelta(seconds=60),
                                    "Acked": False,
                                }
                                response =  f"Assigning to: {existing_mac } IP:{records[existing_mac]['ip_address']} with an experation date of {records[existing_mac]['timestamp']} " 
                                print("response")
                if not response:
                    response = "DECLINE"
                    print("response")

    elif request == "REQUEST":
        #handle request by checking if mac is in records else decline
        mac = parsed_message[1]
        ip_address = parsed_message[2]
        timestamp = parsed_message[3]
        if mac in records and records[mac]["ip_address"] == ip_address:
            if records[mac]['timestamp'] < datetime.now():
                response = ("DECLINE: Timestamp has expired.")
            else:
            # Timestamp is still valid
                records[mac]["Acked"] = True
                response = (f"ACKNOWLEDGE: {mac} {ip_address} {timestamp} \nIP address {ip_address} was assigned to this client. It will expire at {records[mac]['timestamp']}")
        else:
            response = ("DECLINE")  

    elif request == "RELEASE":
        #handle release by finding it in records
        mac = parsed_message[1]
        if mac in records and records[mac]["Acked"]:
            RememberIP[mac] = {'ip_address': records[mac]['ip_address']}
            records[mac]['ip_address'] = None
            records[mac]['timestamp'] = timedelta(seconds=60) + datetime.now()
            records[mac]['Acked'] =  False  
        elif mac in records and  not records[mac]["Acked"]:
            response = f"IP address from {mac} has already been released"
        else:
            response = f"IP address from {mac} not found in records."

    elif request == "RENEW":
        mac = parsed_message[1]
        timestamp = datetime.now()
        #found record
        if mac in records:
            print("mac found in record")
            print(records[mac])
            print(f"record time {records[mac]['timestamp']}")
            print(f"current time {datetime.now()}")
            #client released IP and we have to retrieve it
            if not records[mac]['Acked'] and records[mac]['timestamp'] > datetime.now() and records[mac]['ip_address'] is None:
                    print("Conditions met for renewal.")
                    records[mac] = {'ip_address': RememberIP[mac]['ip_address']}
                    records[mac]["timestamp"] = datetime.now() + timedelta(seconds=60)
                    records[mac]["Acked"] = True
                    response = f"ACKNOWLEDGE: {mac} {records[mac]['ip_address']} {records[mac]['timestamp']}"
            #lease expired
            elif records[mac]['Acked'] and  datetime.now() > records[mac]['timestamp'] :
                response = "DISCOVER"
                del records[mac]
            else:
            #passes all renew cases
                records[mac]["timestamp"] = datetime.now() + timedelta(seconds=60)
                records[mac]["Acked"] = True
                response = f"ACKNOWLEDGE: {mac} {records[mac]['ip_address']} {records[mac]['timestamp']}"
        else:
            if len(records) == len(ip_addresses):
                response = "DECLINE: No available IP addresses."
            for ip in ip_addresses:
                #check if the IP is not in the records
                if ip not in [record['ip_address'] for record in records.values()]:
                    records[mac] = {
                        "ip_address": ip,
                        "timestamp": timestamp + timedelta(seconds=60),
                        "Acked": False,
                    }
                    response = f"OFFER: {mac} {records[mac]['ip_address']} {records[mac]['timestamp']} "
                    print(response)
                    break
                else:
                    #else check for any expired timestamps from previous clients
                    for existing_mac in records:
                        if records[existing_mac]["timestamp"] < datetime.now():
                            records[existing_mac] = {
                                "ip_address": ip,
                                "timestamp": timestamp + timedelta(seconds=60),
                                "Acked": False,
                            }
                            response = f"OFFER: {mac} {records[existing_mac]['ip_address']} {records[existing_mac]['timestamp']} "
                            break
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
        response = dhcp_operation(parsed_message)
        print("success")
        server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()
