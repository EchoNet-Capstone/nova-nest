import serial
from PyQt6.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QPushButton

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

# Create the main GUI window
class SerialPacketSender(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set up the layout
        layout = QVBoxLayout()

        # Create a button
        send_button = QPushButton("Send Packet", self)
        send_button.clicked.connect(send_packet)  # Connect the button click to the function

        # Add the button to the layout
        layout.addWidget(send_button)

        # Set the layout for the main window
        self.setLayout(layout)

        # Configure the main window
        self.setWindowTitle("Serial Packet Sender")
        self.resize(300, 150)