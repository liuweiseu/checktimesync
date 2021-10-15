import time
import serial
import struct
import redis
from influxdb import InfluxDBClient
from signal import signal, SIGINT
from datetime import datetime
from datetime import timezone


uart_port = '/dev/ttyUSB0'
def primaryTimingPacket(data):
    # check the length of data
    if len(data) != 17:
        print(RKEY, ' is malformed ignoring the following data packet')
        print(data)
        print('Packet size is ', len(data))
        return

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
    
    lastTime = str(year)+'-'+str(month)+'-'+str(dayofMonth)+'T'+str(hours)+':'+str(minutes)+':'+str(seconds) + 'Z'
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
    
    utc_time = []
    while utc_time==[] :
        while bytesToRead == 0:
            bytesToRead = ser.inWaiting()
        data += ser.read(bytesToRead)
        dataSize += bytesToRead

        if data[dataSize-1:dataSize] == b'\x03' and data[dataSize-2:dataSize-1] == b'\x10':
            if data[0:1] == b'\x10':
                id = data[1:3]
                if id == b'\x8f\xab':
                    utc_time = primaryTimingPacket(data[2:dataSize-2])
            data = b''
            dataSize = 0
    print(utc_time)
    ser.close()

def __name__ == '__main__':
    GetGPSTime()