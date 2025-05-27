from ..Utils.nest_serial import send_packet
import time
import serial


def send_with_ack(serial_port, baud_rate, data, parent=None, max_retries=5, timeout=2):
    for attempt in range(max_retries):
        send_packet(serial_port, baud_rate, data, parent=parent)
        start = time.time()
        with serial.Serial(serial_port, baudrate=baud_rate, timeout=timeout) as ser:
            while time.time() - start < timeout:
                if ser.in_waiting:
                    response = ser.read(ser.in_waiting).decode('ascii')
                    if b'?Q1\r\n' or b'?S1\r\n' in response:
                        return True
        # If no good response, retry
    return False

def add_buoy_serial_protocol(serial_port, baud_rate, serial_number, did, nid, parent=None):
    # 1. Send serial number
    serial_cmd = f"!Q{serial_number}\r\n".encode('ascii')
    if not send_with_ack(serial_port, baud_rate, serial_cmd, parent):
        print("Failed to send serial number after retries.")
        return False

    # 2. Send device ID and network ID
    did_cmd = f"S{did},{nid}\r\n".encode('ascii')
    if not send_with_ack(serial_port, baud_rate, did_cmd, parent):
        print("Failed to send device/network ID after retries.")
        return False

    # 3. Only now add to DB
    print("Buoy can be added to DB!")
    return True
