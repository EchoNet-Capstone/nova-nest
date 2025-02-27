import serial
from PySide6.QtWidgets import QMessageBox

def send_packet(serial_port, baud_rate, data):
    try:
        timeout = 2
        # Open the serial connection with the specified port and baud rate
        with serial.Serial(serial_port, baudrate=baud_rate, timeout=timeout) as ser:
            ser.write(data)
            print("Packet sent over serial!")
            QMessageBox.information(None, "Success", "Packet sent successfully!")
            return True
    except serial.SerialException as e:
        print(f"Error sending packet: {e}")
        QMessageBox.critical(None, "Error", f"Failed to send packet:\n{e}")
        return False
