from ..Utils.nest_serial import *
from PySide6.QtWidgets import QWidget, QMessageBox, QVBoxLayout, QPushButton

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