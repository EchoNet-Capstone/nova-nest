import serial
from PySide6.QtWidgets import QMessageBox

# Function to send a packet over serial
def send_packet():
    try:
        # Configure the serial port
        serial_port = "/dev/ttyUSB0" # Update to match your device
        baud_rate = 115200
        timeout = 2

        # Open the serial connection
        with serial.Serial(serial_port, baudrate=baud_rate, timeout=timeout) as ser:
            # Define the packet to send
            packet = b"Hello Heltec!\n"  # Update as per your data
            ser.write(packet)  # Send the packet

            # Provide feedback to the user
            print("Packet sent over serial!") 
            QMessageBox.information(None, "Success", "Packet sent successfully!")

    except serial.SerialException as e:
        print(f"Error sending packet: {e}")
        QMessageBox.critical(None, "Error", f"Failed to send packet:\n{e}")
