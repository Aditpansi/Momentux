import serial
import time

# Establish serial connection (adjust port name as needed)
ser = serial.Serial('/dev/tty.usbmodem14101clear', 9600)  # Replace 'XXXX' with the correct port number

try:
    while True:
        if ser.in_waiting > 0:
            # Read data from Arduino
            data = ser.readline().decode().strip()
            print(data)
            time.sleep(1)  # Optional delay
except KeyboardInterrupt:
    ser.close()  # Close serial connection on KeyboardInterrupt
