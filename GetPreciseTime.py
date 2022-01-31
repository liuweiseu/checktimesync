from cmath import nan
from grain import Grain
from datetime import datetime
import socket

EPOCH = datetime(1970,1,1)

g = Grain()

# get the current utc time
now = datetime.utcnow()
host_tai = g.utc2tai(now,EPOCH)

#get the last 10 bits
host_tai_10bits = host_tai & 0x3ff

#get time from quabo
BUFFERSIZE = 1024
IP_PORT = ('192.168.1.100',60001)
server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server.bind(IP_PORT)
data,client_addr = server.recvfrom(BUFFERSIZE)
server.close()

nanosec = (data[10]+data[11]*pow(2,8)+data[12]*pow(2,16)+data[13]*pow(2,24))/pow(10,9)
wr_tai = data[6]+data[7]*pow(2,8)+data[8]*pow(2,16)+data[9]*pow(2,24)
wr_tai_10bits = wr_tai & 0x3ff

if(host_tai_10bits ==0 and wr_tai_10bits == 1023):
    tai_time = host_tai - 1
elif(host_tai_10bits == 0 and wr_tai_10bits == 1):
    tai_time = host_tai + 1
elif(host_tai_10bits == 1023 and wr_tai_10bits == 0):
    tai_time = host_tai + 1
elif(host_tai_10bits == 1 and wr_tai_10bits == 0):
    tai_time = host_tai - 1
else:
    tai_time = host_tai

# add the nanosec
tai_time = tai_time + nanosec