#! /usr/bin/python

import time
import serial
from datetime import datetime
from datetime import timezone
import socket
from datetime import datetime
import paramiko

uart_port = '/dev/ttyUSB0'
host_ip = '192.168.1.100'
port = 60001
wrs_ip = '10.0.1.36'

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
    tvUTC = str(datetime.now(timezone.utc))
    
    timeofWeek = int.from_bytes(data[1:5], byteorder=BYTEORDER, signed=False)
    
    weekNumber = int.from_bytes(data[5:7], byteorder=BYTEORDER, signed=False)
    
    UTCOffset = int.from_bytes(data[7:9], byteorder=BYTEORDER, signed=True)
    
    timingFlag = int.from_bytes(data[9:10], byteorder=BYTEORDER, signed=False)

    time = timingFlag & 0x01
    PPS = (timingFlag & 0x02) >> 1
    timeSet = (timingFlag & 0x04) >> 2
    UTCinfo = (timingFlag & 0x08) >> 3
    timeFrom = (timingFlag & 0x10) >> 4
    
    seconds = int.from_bytes(data[10:11], byteorder=BYTEORDER, signed=False)
    minutes = int.from_bytes(data[11:12], byteorder=BYTEORDER, signed=False)
    hours = int.from_bytes(data[12:13], byteorder=BYTEORDER, signed=False)
    dayofMonth = int.from_bytes(data[13:14], byteorder=BYTEORDER, signed=False)
    month = int.from_bytes(data[14:15], byteorder=BYTEORDER, signed=False)
    year = int.from_bytes(data[15:17], byteorder=BYTEORDER, signed=False)
    
    lastTime = str(year)+'-'+str(month)+'-'+str(dayofMonth)+' '+str(hours)+':'+str(minutes)+':'+str(seconds) + '.000'
    return lastTime

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
    
    gps_time = []
    while gps_time==[] :
        while bytesToRead == 0:
            bytesToRead = ser.inWaiting()
        data += ser.read(bytesToRead)
        dataSize += bytesToRead

        if data[dataSize-1:dataSize] == b'\x03' and data[dataSize-2:dataSize-1] == b'\x10':
            if data[0:1] == b'\x10':
                id = data[1:3]
                if id == b'\x8f\xab':
                    gps_time = primaryTimingPacket(data[2:dataSize-2])
            data = b''
            dataSize = 0
    ser.close()
    return gps_time

"""
The code is for getting time from the host computer and quabo.
"""
def GetQuaboTime(host_ip, port):
    BUFFERSIZE = 1024
    IP_PORT = (host_ip,port)
    server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server.bind(IP_PORT)
    data,client_addr = server.recvfrom(BUFFERSIZE)
    t_host = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    nanosec = (data[10]+data[11]*pow(2,8)+data[12]*pow(2,16)+data[13]*pow(2,24))
    t_quabo = t_host.split('.')[0]+'.'+str(nanosec)
    return t_host, t_quabo

"""
The code is for getting time from WRS.
"""
def GetWRSTime(wrs_ip):
    cmd = "/wr/bin/wr_date get"
    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(wrs_ip,username='root',password='')
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
    result=ssh_stdout.read()
    result_str=str(result, encoding = "utf-8")
    s=result_str.split(' ')
    d = s[3].split('\n')
    wrs_time = d[1] + ' ' +s[4]
    ssh.close()
    del(ssh,ssh_stdin, ssh_stdout, ssh_stderr)
    return wrs_time

if __name__ == '__main__':
    print('===============================================================')
    print('Please make sure:')
    print('1. The dev name of the GPS receiver is'.ljust(46,' '),uart_port)
    print('2. The IP address of the host computer is'.ljust(46,' '),host_ip)
    print('3. The port for quabo packets is'.ljust(46,' '),str(port))
    print('4. The IP address of WRS is'.ljust(46,' '),wrs_ip)
    print('===============================================================')
    print('Time Checking Result(UTC TIME):')
    gps_time = GetGPSTime(uart_port)
    print('GPS Time'.ljust(20, ' '),':',gps_time)
    t_host,t_quabo = GetQuaboTime(host_ip, port)
    print('Host Computer Time'.ljust(20,' '),':',t_host)
    print('Quabo Time'.ljust(20,' '),':',t_quabo)
    wrs_time = GetWRSTime(wrs_ip)
    print('WRS Time'.ljust(20, ' '),':',wrs_time)
