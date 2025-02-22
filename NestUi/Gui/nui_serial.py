import serial.tools.list_ports
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel
)
from ..Utils.nest_serial import send_packet  # Import the send_packet function

class SerialPacketSender(QWidget):
    def __init__(self):
        super(SerialPacketSender, self).__init__()
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Label for the ASCII data input
        data_label = QLabel("Enter ASCII Data:")
        main_layout.addWidget(data_label)

        # Horizontal layout for the editable dropdown and send button
        input_layout = QHBoxLayout()
        self.data_input = QComboBox()
        self.data_input.setEditable(True)
        # Set the fixed size for the text input to display 70 characters
        fm = self.data_input.fontMetrics()
        text_input_fixed_width = fm.horizontalAdvance('0' * 70)
        text_input_fixed_height = self.data_input.sizeHint().height()
        self.data_input.setFixedSize(text_input_fixed_width, text_input_fixed_height)
        input_layout.addWidget(self.data_input)

        send_button = QPushButton("Send Packet")
        send_button.clicked.connect(self.handle_send_packet)
        send_button.setFixedSize(send_button.sizeHint())
        input_layout.addWidget(send_button)
        main_layout.addLayout(input_layout)

        # Dropdown for selecting the serial port
        port_label = QLabel("Select Serial Port:")
        main_layout.addWidget(port_label)
        self.port_dropdown = QComboBox()
        for port in serial.tools.list_ports.comports():
            self.port_dropdown.addItem(port.device)
        self.port_dropdown.setFixedSize(self.port_dropdown.sizeHint())
        main_layout.addWidget(self.port_dropdown)

        # Dropdown for selecting baud rate from common options
        baud_label = QLabel("Select Baud Rate:")
        main_layout.addWidget(baud_label)
        self.baud_dropdown = QComboBox()
        common_baud_rates = ["9600", "19200", "38400", "57600", "115200"]
        for rate in common_baud_rates:
            self.baud_dropdown.addItem(rate)
        self.baud_dropdown.setFixedSize(self.baud_dropdown.sizeHint())
        main_layout.addWidget(self.baud_dropdown)
        
        self.setLayout(main_layout)
        self.setWindowTitle("Serial Packet Sender")
        
        # Ensure the layout calculates the proper size and then fix it
        self.adjustSize()
        self.setFixedSize(self.size())

    def handle_send_packet(self):
        ascii_data = self.data_input.currentText()
        serial_port = self.port_dropdown.currentText()
        baud_rate = int(self.baud_dropdown.currentText())
        send_packet(serial_port, baud_rate, ascii_data)
        # Save the entered ASCII data in the dropdown if not already present
        if ascii_data and ascii_data not in [self.data_input.itemText(i) for i in range(self.data_input.count())]:
            self.data_input.addItem(ascii_data)
