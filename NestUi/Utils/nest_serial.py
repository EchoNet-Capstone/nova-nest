import serial
from PySide6.QtWidgets import QMessageBox

def send_packet(serial_port, baud_rate, data, ser=None, parent=None):
    """
    Send data over a serial port.
    
    If 'ser' (a serial.Serial instance) is provided, it is used to write the data.
    Otherwise, a new connection is opened and closed.
    
    The 'parent' parameter is used as the parent widget for any popup messages.
    """
    try:
        if ser is None:
            timeout = 2
            with serial.Serial(serial_port, baudrate=baud_rate, timeout=timeout) as ser_temp:
                ser_temp.write(data)
        else:
            ser.write(data)
        print("Packet sent over serial!")
        QMessageBox.information(parent, "Success", "Packet sent successfully!")
        return True
    except serial.SerialException as e:
        print(f"Error sending packet: {e}")
        QMessageBox.critical(parent, "Error", f"Failed to send packet:\n{e}")
        return False
