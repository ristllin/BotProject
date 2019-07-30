import serial
import time
from constants import *
ser_com = "14" #change from "" for constant serial port

def findSerialPorts():
    """ Lists serial port names
        :returns:
        A list of the serial ports available
    """
    all_ports = ['COM%s' % (i + 1) for i in range(256)]
    result = []
    print(">>Scanning com ports...")
    for port in all_ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.serialutil.SerialException):
            pass
    return result

def getUserCom():
    global ser_com
    while ser_com == "" or ser_com == "restart":
        all_coms = findSerialPorts()
        print(">>Available coms are:",all_coms)
        ser_com = input(">>Please choose the relevant one with an int (e.g. '11') or 'restart' for another scan:\n")
        if ser_com != "restart" and not ser_com.isnumeric():
            print(">>>Invalid input")
            ser_com = ""
    ser_com = "com"+ser_com

def main():
    try:
        global ser_com
        print("-=Robohand Terminal=-")
        getUserCom() #updates global ser_com
        print(">>Connecting to",ser_com)
        ser_port = serial.Serial(ser_com,9600)
        print(">>Connection successful")
        while 1:
            try:
                data = ser_port.readline().decode()
                print(">",data)
            except Exception:
                pass
    except Exception as e:
        print(">>>Unexpected error.\n",e,"\n>>>Terminating.")
        exit(1)

def sendCommand(command):
    global ser_com
    if command == 1:
        message = b"1"
    elif command == 2:
        message = b"2"
    elif command == 3:
        message = b"3"
    elif command == 4:
        message = b"4"
    elif command == 5:
        message = b"5"
    # print("debug: message:",message)
    try:
        # if DEBUG: print("debug: sending command:" , message , "on port: ",ser_com)
        ser_port = serial.Serial("com"+ser_com, 9600)
        time.sleep(1)
        # print("Connection successful")
        ser_port.write(message)
        start = time.time()
        current = time.time()
        passed = current-start
        while passed < 1:
            current = time.time()
            data = ser_port.readline().decode()
            # print(">", data)
            passed = current - start
        ser_port.close()
    except FileNotFoundError:
        print("<<<Error: bad port>>>")
    except Exception as e:
        print("<<<Send command Unknown Error>>>")
        print(e)

if __name__ == '__main__':
    main()