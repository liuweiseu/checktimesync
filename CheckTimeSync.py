#! /usr/bin/python

import time
import serial
from datetime import datetime, timezone
import socket
import paramiko
import struct

uart_port = '/dev/ttyUSB0'
host_ip = '192.168.1.100'
port = 60001
wrs_ip = '192.168.1.254'

# this is the offset time between tai and utc
leap_sec = 37
# this is the offset time between gps and utc
gps_sec  = 18
"""
The code is for getting time from GPS Resceiver.
The GPS receiver should be connected to the host computer via a USB port,
which is shown as /dev/ttyUSBx.
"""
def primaryTimingPacket(data):
    # check the length of data
    if len(data) != 17:
        return
    BYTEORDER = 'big'
    # get time info from the data packet
    seconds = int.from_bytes(data[10:11], byteorder=BYTEORDER, signed=False)
    minutes = int.from_bytes(data[11:12], byteorder=BYTEORDER, signed=False)
    hours = int.from_bytes(data[12:13], byteorder=BYTEORDER, signed=False)
    dayofMonth = int.from_bytes(data[13:14], byteorder=BYTEORDER, signed=False)
    month = int.from_bytes(data[14:15], byteorder=BYTEORDER, signed=False)
    year = int.from_bytes(data[15:17], byteorder=BYTEORDER, signed=False)
    # there is no nanosec info from GPS receiver, so nanosec value is set to 0 here
    lastTime = datetime(year, month, dayofMonth, hours, minutes, seconds, 0).replace(tzinfo=timezone.utc)
    return lastTime.timestamp() - gps_sec

def GetGPSTime(port):
# configure the serial connections (the parameters differs on the device you are connecting to)
    ser = serial.Serial(
        port=port,
        baudrate=9600,
        timeout=1,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    if not ser.isOpen():
        ser.open()

    data = b''
    dataSize = 0
    bytesToRead = 0
    timestamp = False
    gps_time = []
    recv_byte = 0
    last_recv_byte = 0
    recv_state = True

    while(recv_state):
        # get gps packets from uart port
        while bytesToRead == 0:
            bytesToRead = ser.inWaiting()
        recv_byte = ser.read(bytesToRead)
        if(recv_byte == b'\x10' and last_recv_byte == b'\x10'):
            pass
        else:
            if(timestamp == False):
                t_host = time.time()
                timestamp = True
            data += recv_byte
            dataSize += bytesToRead
        last_recv_byte = recv_byte
        bytesToRead = 0

        # deal with the data packet, if the packet ends with \x10\x03
        if data[dataSize-1:dataSize] == b'\x03' and data[dataSize-2:dataSize-1] == b'\x10':
            if data[0:1] == b'\x10':
                id = data[1:3]
                if id == b'\x8f\xab':
                    gps_time = primaryTimingPacket(data[2:dataSize-2])
            data = b''
            dataSize = 0
            timestamp = False
            recv_state = False

    ser.close()
    return gps_time, t_host

"""
The code is for getting time from the host computer and quabo.
"""
def GetQuaboTime(host_ip, port):
    BUFFERSIZE = 1024
    IP_PORT = (host_ip,port)
    server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server.bind(IP_PORT)
    data,client_addr = server.recvfrom(BUFFERSIZE)
    server.close()

    t_host = time.time()
    nanosec = struct.unpack("<I", data[10:14])[0]
    wr_tai = struct.unpack("<I", data[6:10])[0]
    wr_tai_10bits = wr_tai & 0x3ff
    #covert utc to tai
    host_tai = time.time() + leap_sec
    #covert tai back to utc
    t_quabo = (int(host_tai) & 0xFFFFFFFFFFFFFC00) + wr_tai_10bits + nanosec/1000000000 -leap_sec
    
    return t_quabo, t_host

"""
The code is for getting time from WRS.
"""
def SSH_Init(wrs_ip):
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(wrs_ip,username='root',password='')
    return ssh

def GetWRSTime(ssh):
    cmd0 = "/wr/bin/wr_date get"

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd0)
    r0=ssh_stdout.read()
    t_host = time.time()
    
    r0_str=str(r0, encoding = "utf-8")
    s=r0_str.split(' ')
    wrs_time = float(s[0]) - leap_sec
    ssh.close()
    del(ssh,ssh_stdin, ssh_stdout, ssh_stderr)
    return wrs_time, t_host

if __name__ == '__main__':
    print('===============================================================')
    print('Please make sure:')
    print('1. The dev name of the GPS receiver is'.ljust(46,' '),uart_port)
    print('2. The IP address of the host computer is'.ljust(46,' '),host_ip)
    print('3. The port for quabo packets is'.ljust(46,' '),str(port))
    print('4. The IP address of WRS is'.ljust(46,' '),wrs_ip)
    print('===============================================================')
    print('Time Checking Result(UTC TIME):')
    ssh = SSH_Init(wrs_ip)
    gps_time,t_host = GetGPSTime(uart_port)
    #t_quabo, t_host1 = GetQuaboTime(host_ip, port)
    t_quabo = 0
    t_host1 = 0
    wrs_time, t_host00 = GetWRSTime(ssh)
    #t_quabo, t_host1 = GetQuaboTime(host_ip, port)
    print('GPS Time'.ljust(20, ' '),':',gps_time)
    print('GPS Timestamp'.ljust(20,' '),':',t_host,'\n')
    print('Quabo Time'.ljust(20,' '),':',t_quabo)
    print('Quabo Timestamp'.ljust(20,' '),':',t_host1,'\n')
    print('WRS Time'.ljust(20, ' '),':',wrs_time)
    print('WRS Timestamp'.ljust(20,' '),':',t_host00,'\n')

