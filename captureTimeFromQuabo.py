import socket

BUFFERSIZE = 1024
IP_PORT = ('192.168.1.100',60001)

server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.bind(IP_PORT)

data,client_addr = server.recvfrom(BUFFERSIZE)

nanosec = (data[10]+data[11]*pow(2,8)+data[12]*pow(2,16)+data[13]*pow(2,24))/pow(10,9)

print(nanosec) 
