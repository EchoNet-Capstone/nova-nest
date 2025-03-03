from PySide6.QtWidgets import (
    QWidget, QLabel, QComboBox, QLineEdit, QPushButton, QGridLayout,
    QGroupBox, QVBoxLayout, QHBoxLayout, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import serial.tools.list_ports
import serial
from ..Utils.nest_serial import send_packet
from ..Utils.networking import build_floc_packet, build_serial_floc_packet

class NuiSerialWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
        
        # Persistent serial connection and timer for monitoring
        self.serial_conn = None
        self.monitor_timer = QTimer(self)
        self.monitor_timer.setInterval(200)  # 200 ms interval for checking incoming data
        self.monitor_timer.timeout.connect(self.read_serial_data)
        
        self.init_ui()
        # Initialize field visibilities based on current selections
        self.update_floc_type_fields()
        self.update_serial_type_fields()

    def init_ui(self):
        # Create a horizontal layout to hold two panels: left (existing UI) and right (serial monitor)
        main_layout = QHBoxLayout(self)
        
        # ------ Left Panel: Existing UI -------
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # ---------- FLOC Packet Group ----------
        floc_group = QGroupBox("FLOC Packet")
        floc_layout = QGridLayout()

        # TTL: Dropdown 1-15 (default 1)
        floc_layout.addWidget(QLabel("TTL:"), 0, 0)
        self.ttl_combo = QComboBox()
        self.ttl_combo.addItems([str(i) for i in range(1, 16)])
        self.ttl_combo.setCurrentIndex(0)
        floc_layout.addWidget(self.ttl_combo, 0, 1)

        # Type: Dropdown for FLOC packet type: 0: Data, 1: Command, 2: Ack, 3: Response
        floc_layout.addWidget(QLabel("Packet Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "0: Data",
            "1: Command",
            "2: Ack",
            "3: Response"
        ])
        self.type_combo.setCurrentIndex(0)
        self.type_combo.currentIndexChanged.connect(self.update_floc_type_fields)
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

        # Data: Text input field (up to 56 characters, not required for Ack)
        floc_layout.addWidget(QLabel("Data:"), 6, 0)
        self.data_edit = QLineEdit()
        self.data_edit.setMaxLength(56)
        floc_layout.addWidget(self.data_edit, 6, 1, 1, 2)

        # Additional fields for specific packet types:
        # Command Type (only for Command packets)
        self.cmd_type_label = QLabel("Command Type:")
        self.cmd_type_combo = QComboBox()
        self.cmd_type_combo.addItems([
            "1: COMMAND_TYPE_1",
            "2: COMMAND_TYPE_2"
        ])
        self.cmd_type_combo.setCurrentIndex(0)
        floc_layout.addWidget(self.cmd_type_label, 7, 0)
        floc_layout.addWidget(self.cmd_type_combo, 7, 1)

        # Ack PID (only for Ack packets)
        self.ack_pid_label = QLabel("Ack PID:")
        self.ack_pid_edit = QLineEdit()
        self.ack_pid_edit.setMaxLength(2)
        floc_layout.addWidget(self.ack_pid_label, 8, 0)
        floc_layout.addWidget(self.ack_pid_edit, 8, 1)

        # Response PID (only for Response packets)
        self.rsp_pid_label = QLabel("Response PID:")
        self.rsp_pid_edit = QLineEdit()
        self.rsp_pid_edit.setMaxLength(2)
        floc_layout.addWidget(self.rsp_pid_label, 9, 0)
        floc_layout.addWidget(self.rsp_pid_edit, 9, 1)

        floc_group.setLayout(floc_layout)
        left_layout.addWidget(floc_group)

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
        left_layout.addWidget(nest_group)

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

        # Serial Type: Dropdown for Broadcast or Unicast
        serial_layout.addWidget(QLabel("Serial Type:"), 2, 0)
        self.serial_type_combo = QComboBox()
        self.serial_type_combo.addItems(["B - Broadcast", "U - Unicast"])
        self.serial_type_combo.currentIndexChanged.connect(self.update_serial_type_fields)
        serial_layout.addWidget(self.serial_type_combo, 2, 1)

        # Destination Address for Unicast (only visible when Serial Type is U)
        self.dest_addr_label = QLabel("Dest Address:")
        self.dest_addr_edit = QLineEdit()
        self.dest_addr_edit.setMaxLength(5)
        serial_layout.addWidget(self.dest_addr_label, 3, 0)
        serial_layout.addWidget(self.dest_addr_edit, 3, 1)

        serial_group.setLayout(serial_layout)
        left_layout.addWidget(serial_group)

        # ---------- Control Buttons ----------
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Update Packet")
        self.update_button.clicked.connect(self.update_packet_display)
        button_layout.addWidget(self.update_button)

        self.send_button = QPushButton("Send Packet")
        self.send_button.clicked.connect(self.on_send_packet)
        button_layout.addWidget(self.send_button)
        left_layout.addLayout(button_layout)
        
        main_layout.addWidget(left_panel)
        
        # ------ Right Panel: Serial Monitor -------
        monitor_group = QGroupBox("Serial Monitor")
        monitor_layout = QVBoxLayout(monitor_group)
        self.serial_toggle_button = QPushButton("Open Serial Port")
        self.serial_toggle_button.clicked.connect(self.toggle_serial_connection)
        monitor_layout.addWidget(self.serial_toggle_button)
        self.monitor_text = QTextEdit()
        self.monitor_text.setReadOnly(True)
        monitor_layout.addWidget(self.monitor_text)
        main_layout.addWidget(monitor_group)

    def refresh_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [port.device for port in ports]
        self.port_combo.clear()
        self.port_combo.addItems(port_list)

    def update_floc_type_fields(self):
        type_str = self.type_combo.currentText()
        type_val = int(type_str.split(":")[0])
        self.cmd_type_label.setVisible(type_val == 1)
        self.cmd_type_combo.setVisible(type_val == 1)
        self.ack_pid_label.setVisible(type_val == 2)
        self.ack_pid_edit.setVisible(type_val == 2)
        self.rsp_pid_label.setVisible(type_val == 3)
        self.rsp_pid_edit.setVisible(type_val == 3)
        self.data_edit.setEnabled(type_val != 2)

    def update_serial_type_fields(self):
        serial_type_str = self.serial_type_combo.currentText()
        self.dest_addr_label.setVisible(serial_type_str.startswith("U"))
        self.dest_addr_edit.setVisible(serial_type_str.startswith("U"))

    def create_floc_packet(self) -> bytes:
        ttl = int(self.ttl_combo.currentText())
        type_val = int(self.type_combo.currentText().split(":")[0])
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

        if type_val == 2:
            data_bytes = b""
        else:
            data_str = self.data_edit.text()[:56]
            data_bytes = data_str.encode('ascii')

        cmd_type_val = -1
        ack_pid_val = -1
        rsp_pid_val = -1

        if type_val == 1:
            try:
                cmd_type_val = int(self.cmd_type_combo.currentText().split(":")[0])
            except ValueError:
                raise ValueError("Invalid Command Type value.")
        elif type_val == 2:
            try:
                ack_pid_val = int(self.ack_pid_edit.text())
            except ValueError:
                raise ValueError("Ack PID must be a valid number.")
        elif type_val == 3:
            try:
                rsp_pid_val = int(self.rsp_pid_edit.text())
            except ValueError:
                raise ValueError("Response PID must be a valid number.")

        return build_floc_packet(ttl, type_val, nid, pid, dst, src, data_bytes,
                                 cmd_type_val=cmd_type_val,
                                 ack_pid_val=ack_pid_val,
                                 rsp_pid_val=rsp_pid_val)

    def update_packet_display(self):
        try:
            floc_packet = self.create_floc_packet()
        except ValueError as e:
            self.packetdata_edit.setPlainText("Error: " + str(e))
            return

        try:
            serial_type_val = self.serial_type_combo.currentText()[0]
            if serial_type_val.upper() == "U":
                try:
                    dest_addr = int(self.dest_addr_edit.text())
                except ValueError:
                    raise ValueError("Destination Address must be a valid number for Unicast.")
            else:
                dest_addr = -1
            nest_packet = build_serial_floc_packet(floc_packet, serial_type_val, dest_addr)
        except ValueError as e:
            self.packetdata_edit.setPlainText("Error: " + str(e))
            return

        self.datasize_edit.setText(str(len(floc_packet)))
        self.packetdata_edit.setPlainText(nest_packet.hex().upper())

    def on_send_packet(self):
        try:
            floc_packet = self.create_floc_packet()
        except ValueError as e:
            self.packetdata_edit.setPlainText("Error: " + str(e))
            return

        try:
            serial_type_val = self.serial_type_combo.currentText()[0]
            if serial_type_val.upper() == "U":
                try:
                    dest_addr = int(self.dest_addr_edit.text())
                except ValueError:
                    raise ValueError("Destination Address must be a valid number for Unicast.")
            else:
                dest_addr = -1
            nest_packet = build_serial_floc_packet(floc_packet, serial_type_val, dest_addr)
        except ValueError as e:
            self.packetdata_edit.setPlainText("Error: " + str(e))
            return

        full_packet = b"$" + nest_packet + b"\r\n"
        serial_port = self.port_combo.currentText()
        try:
            baud_rate = int(self.baud_combo.currentText())
        except ValueError:
            self.packetdata_edit.setPlainText("Invalid baud rate!")
            return

        if self.serial_conn is not None:
            try:
                self.serial_conn.write(full_packet)
                # Directly decode without additional formatting (using latin1 to preserve bytes)
                self.append_monitor_text("Sent: " + full_packet.decode('latin1', errors='replace'))
            except Exception as e:
                self.append_monitor_text("Error sending packet: " + str(e))
                return
        else:
            if send_packet(serial_port, baud_rate, full_packet):
                self.append_monitor_text("Sent: " + full_packet.decode('latin1', errors='replace'))

        try:
            current_pid = int(self.pid_edit.text())
        except ValueError:
            current_pid = 0
        new_pid = (current_pid + 1) % 64
        self.pid_edit.setText(str(new_pid))

    def toggle_serial_connection(self):
        if self.serial_conn is None:
            serial_port = self.port_combo.currentText()
            try:
                baud_rate = int(self.baud_combo.currentText())
            except ValueError:
                self.append_monitor_text("Invalid baud rate!")
                return
            try:
                self.serial_conn = serial.Serial(serial_port, baud_rate, timeout=0.2)
                self.append_monitor_text("Opened serial port: " + serial_port)
                self.serial_toggle_button.setText("Close Serial Port")
                self.monitor_timer.start()
            except Exception as e:
                self.append_monitor_text("Error opening serial port: " + str(e))
        else:
            self.monitor_timer.stop()
            self.serial_conn.close()
            self.serial_conn = None
            self.append_monitor_text("Closed serial port")
            self.serial_toggle_button.setText("Open Serial Port")

    def read_serial_data(self):
        if self.serial_conn and self.serial_conn.in_waiting:
            try:
                data = self.serial_conn.read(self.serial_conn.in_waiting)
                if data:
                    # Instead of custom formatting, decode directly (latin1 preserves byte-to-character mapping)
                    self.append_monitor_text("Received: " + data.decode('latin1', errors='replace'))
            except Exception as e:
                self.append_monitor_text("Error reading serial data: " + str(e))

    def append_monitor_text(self, text):
        self.monitor_text.append(text)
