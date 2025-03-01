from PySide6.QtWidgets import (
    QWidget, QLabel, QComboBox, QLineEdit, QPushButton, QGridLayout,
    QGroupBox, QVBoxLayout, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import serial.tools.list_ports
from ..Utils.nest_serial import send_packet
from ..Utils.networking import build_floc_packet, build_serial_floc_packet
from scapy.all import Packet

class NuiSerialWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set a smaller font for the entire widget
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # ---------- FLOC Packet Group ----------
        floc_group = QGroupBox("FLOC Packet")
        floc_layout = QGridLayout()

        # TTL: Dropdown 1-15 (default 1)
        floc_layout.addWidget(QLabel("TTL:"), 0, 0)
        self.ttl_combo = QComboBox()
        self.ttl_combo.addItems([str(i) for i in range(1, 16)])
        self.ttl_combo.setCurrentIndex(0)
        floc_layout.addWidget(self.ttl_combo, 0, 1)

        # Type: Dropdown 0-15 (default 1; note 1-3 are defined types)
        floc_layout.addWidget(QLabel("Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems([str(i) for i in range(0, 16)])
        self.type_combo.setCurrentIndex(1)
        floc_layout.addWidget(self.type_combo, 1, 1)

        # PID: Editable field (max 2 digits). Default value "0".
        floc_layout.addWidget(QLabel("PID:"), 2, 0)
        self.pid_edit = QLineEdit("0")
        self.pid_edit.setMaxLength(2)
        floc_layout.addWidget(self.pid_edit, 2, 1)

        # NID: Editable ComboBox (up to 5 digits) with dropdown for previous entries
        floc_layout.addWidget(QLabel("NID:"), 3, 0)
        self.nid_combo = QComboBox()
        self.nid_combo.setEditable(True)
        self.nid_combo.setInsertPolicy(QComboBox.NoInsert)
        self.nid_combo.setMaxVisibleItems(10)
        self.nid_combo.lineEdit().setMaxLength(5)
        floc_layout.addWidget(self.nid_combo, 3, 1)

        # DST: Editable ComboBox (up to 5 digits) with dropdown for previous entries
        floc_layout.addWidget(QLabel("DST:"), 4, 0)
        self.dst_combo = QComboBox()
        self.dst_combo.setEditable(True)
        self.dst_combo.setInsertPolicy(QComboBox.NoInsert)
        self.dst_combo.setMaxVisibleItems(10)
        self.dst_combo.lineEdit().setMaxLength(5)
        floc_layout.addWidget(self.dst_combo, 4, 1)

        # SRC: Editable ComboBox (up to 5 digits) with dropdown for previous entries
        floc_layout.addWidget(QLabel("SRC:"), 5, 0)
        self.src_combo = QComboBox()
        self.src_combo.setEditable(True)
        self.src_combo.setInsertPolicy(QComboBox.NoInsert)
        self.src_combo.setMaxVisibleItems(10)
        self.src_combo.lineEdit().setMaxLength(5)
        floc_layout.addWidget(self.src_combo, 5, 1)

        # Data: Text input field (up to 56 characters, not required)
        floc_layout.addWidget(QLabel("Data:"), 6, 0)
        self.data_edit = QLineEdit()
        self.data_edit.setMaxLength(56)
        floc_layout.addWidget(self.data_edit, 6, 1, 1, 2)

        floc_group.setLayout(floc_layout)
        main_layout.addWidget(floc_group)

        # ---------- NeST to BuRD Packet Group ----------
        nest_group = QGroupBox("NeST to BuRD Packet")
        nest_layout = QGridLayout()

        # CMD ID: Non-editable field showing "B - Broadcast"
        nest_layout.addWidget(QLabel("CMD ID:"), 0, 0)
        self.cmd_id_edit = QLineEdit("B - Broadcast")
        self.cmd_id_edit.setReadOnly(True)
        nest_layout.addWidget(self.cmd_id_edit, 0, 1)

        # DataSize: Non-editable field to show FLOC packet size
        nest_layout.addWidget(QLabel("DataSize:"), 1, 0)
        self.datasize_edit = QLineEdit()
        self.datasize_edit.setReadOnly(True)
        nest_layout.addWidget(self.datasize_edit, 1, 1)

        # Data: Scrollable text field (read-only) for the NeST to BuRD packet data.
        nest_layout.addWidget(QLabel("Data:"), 2, 0)
        self.packetdata_edit = QTextEdit()
        self.packetdata_edit.setReadOnly(True)
        self.packetdata_edit.setMaximumWidth(600)
        nest_layout.addWidget(self.packetdata_edit, 2, 1, 1, 2)

        nest_group.setLayout(nest_layout)
        main_layout.addWidget(nest_group)

        # ---------- Serial Configuration Group ----------
        serial_group = QGroupBox("Serial Configuration")
        serial_layout = QGridLayout()

        # Serial Port: Dropdown showing active serial ports
        serial_layout.addWidget(QLabel("Serial Port:"), 0, 0)
        self.port_combo = QComboBox()
        self.refresh_serial_ports()
        serial_layout.addWidget(self.port_combo, 0, 1)

        # Baud Rate: Dropdown with common baud rates
        serial_layout.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["4800", "9600", "19200", "38400", "57600", "115200"])
        self.baud_combo.setCurrentText("9600")
        serial_layout.addWidget(self.baud_combo, 1, 1)

        serial_group.setLayout(serial_layout)
        main_layout.addWidget(serial_group)

        # ---------- Control Buttons ----------
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Update Packet")
        self.update_button.clicked.connect(self.update_packet_display)
        button_layout.addWidget(self.update_button)

        self.send_button = QPushButton("Send Packet")
        self.send_button.clicked.connect(self.on_send_packet)
        button_layout.addWidget(self.send_button)
        main_layout.addLayout(button_layout)

    def refresh_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.port_combo.clear()
        self.port_combo.addItems(port_list)

    def create_floc_packet(self) -> bytes:
        """
        Build a FLOC packet using the generated Scapy classes.
        Depending on the 'Type' field, an appropriate header is instantiated.
        Any additional data from the UI is added as payload.
        """
        # Retrieve values from the UI fields
        ttl = int(self.ttl_combo.currentText())
        type_val = int(self.type_combo.currentText())
        try:
            pid = int(self.pid_edit.text())
        except ValueError:
            raise ValueError("PID must be a valid number.")
        try:
            nid = int(self.nid_combo.currentText())
        except ValueError:
            raise ValueError("NID must be a valid number.")
        try:
            dst = int(self.dst_combo.currentText())
        except ValueError:
            raise ValueError("DST must be a valid number.")
        try:
            src = int(self.src_combo.currentText())
        except ValueError:
            raise ValueError("SRC must be a valid number.")
        data_str = self.data_edit.text()[:56]  # enforce 56-character max

        return build_floc_packet(ttl, type_val, nid, pid, dst, src, data_str.encode('ascii'))


    def update_packet_display(self):
        try:
            floc_packet = self.create_floc_packet()
        except ValueError as e:
            self.packetdata_edit.setPlainText("Error: " + str(e))
            return

        nest_packet = build_serial_floc_packet(floc_packet)
        self.datasize_edit.setText(str(len(floc_packet)))
        # Display the packet data in hexadecimal for readability
        self.packetdata_edit.setPlainText(nest_packet.hex().upper())

    def on_send_packet(self):
        try:
            floc_packet = self.create_floc_packet()
        except ValueError as e:
            self.packetdata_edit.setPlainText("Error: " + str(e))
            return

        nest_packet = build_serial_floc_packet(floc_packet)
        # Prepend '$' and append "\r\n" to the packet
        full_packet = b"$" + nest_packet + b"\r\n"
        serial_port = self.port_combo.currentText()
        try:
            baud_rate = int(self.baud_combo.currentText())
        except ValueError:
            self.packetdata_edit.setPlainText("Invalid baud rate!")
            return

        if send_packet(serial_port, baud_rate, full_packet):
            # If send_packet doesn't raise an exception, assume success:
            self.packetdata_edit.setPlainText("Sent: " + full_packet.hex().upper())
            # Update the PID only after a successful send
            current_pid = int(self.pid_edit.text())
            new_pid = (current_pid + 1) % 64
            self.pid_edit.setText(str(new_pid))
