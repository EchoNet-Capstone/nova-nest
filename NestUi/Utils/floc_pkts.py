# floc_pkts.py (VARIABLE LENGTH DATA)
from scapy.packet import Packet, bind_layers
from scapy.fields import (
    BitField,
    BitEnumField,
    ShortField,
    ByteField,
    PacketField,
    StrLenField,
    ConditionalField
)
from scapy.compat import raw

FLOC_DATA_TYPE = 'FLOC_DATA_TYPE'
FLOC_COMMAND_TYPE = 'FLOC_COMMAND_TYPE'
FLOC_ACK_TYPE = 'FLOC_ACK_TYPE'
FLOC_RESPONSE_TYPE = 'FLOC_RESPONSE_TYPE'

def get_floc_packet_type(value: int) -> str:
    """Converts an integer value to the floc_packet_type enum's string representation."""
    _mapping = {
        0: FLOC_DATA_TYPE,
        1: FLOC_COMMAND_TYPE,
        2: FLOC_ACK_TYPE,
        3: FLOC_RESPONSE_TYPE,
    }
    return _mapping.get(value, '')

COMMAND_TYPE_1 = 'COMMAND_TYPE_1'
COMMAND_TYPE_2 = 'COMMAND_TYPE_2'

def get_command_type(value: int) -> str:
    """Converts an integer value to the command_type enum's string representation."""
    _mapping = {
        1: COMMAND_TYPE_1,
        2: COMMAND_TYPE_2,
    }
    return _mapping.get(value, '')

SERIAL_BROADCAST_TYPE = 'SERIAL_BROADCAST_TYPE'
SERIAL_UNICAST_TYPE = 'SERIAL_UNICAST_TYPE'

def get_serial_floc_packet_type(value: int) -> str:
    """Converts an integer value to the serial_floc_packet_type enum's string representation."""
    _mapping = {
        66: SERIAL_BROADCAST_TYPE,
        85: SERIAL_UNICAST_TYPE,
    }
    return _mapping.get(value, '')



class FlocHeader(Packet):
    name = "FlocHeader"
    fields_desc = [
        BitField('ttl', 0, 4),
        BitEnumField('type', 0, 4, {0: 'FLOC_DATA_TYPE', 1: 'FLOC_COMMAND_TYPE', 2: 'FLOC_ACK_TYPE', 3: 'FLOC_RESPONSE_TYPE'}),
        ShortField('nid', 0),
        BitField('res', 0, 2),
        BitField('pid', 0, 6),
        ShortField('dest_addr', 0),
        ShortField('src_addr', 0)
    ]

    def do_dissect(self, s):
         # Consume exactly one byte for the size field
        self.ttl = s[0] >> 4
        self.type = s[0] & 0b1111
        self.nid = int.from_bytes(s[1:3])
        self.res = s[3] >> 6
        self.pid = s[3] & 0b11_1111
        self.dest_addr = int.from_bytes(s[4:6])
        self.src_addr = int.from_bytes(s[6:8])

        # Return the remaining bytes so that they’re available to the DataPacket
        return s[8:]

    def extract_padding(self, s):
         # Return an empty payload for this header and pass all remaining bytes to the next layer.
         return b"", s

class DataHeader(Packet):
    name = "DataHeader"
    fields_desc = [
        ByteField('size', 0)
    ]

    def do_dissect(self, s):
         # Consume exactly one byte for the size field
         self.size = s[0]
         # Return the remaining bytes so that they’re available to the DataPacket
         return s[1:]

    def extract_padding(self, s):
         # Return an empty payload for this header and pass all remaining bytes to the next layer.
         return b"", s

class CommandHeader(Packet):
    name = "CommandHeader"
    fields_desc = [
        BitEnumField('command_type', 0, 8, {1: 'COMMAND_TYPE_1', 2: 'COMMAND_TYPE_2'}),
        ByteField('size', 0)
    ]

    def do_dissect(self, s):
         # Consume exactly one byte for the size field
         self.command_type = s[0]
         self.size = s[1]
         # Return the remaining bytes so that they’re available to the DataPacket
         return s[2:]

    def extract_padding(self, s):
         # Return an empty payload for this header and pass all remaining bytes to the next layer.
         return b"", s

class AckHeader(Packet):
    name = "AckHeader"
    fields_desc = [
        ByteField('ack_pid', 0)
    ]

    def do_dissect(self, s):
         # Consume exactly one byte for the size field
         self.ack_pid = s[0]
         # Return the remaining bytes so that they’re available to the DataPacket
         return s[1:]

    def extract_padding(self, s):
         # Return an empty payload for this header and pass all remaining bytes to the next layer.
         return b"", s

class ResponseHeader(Packet):
    name = "ResponseHeader"
    fields_desc = [
        ByteField('request_pid', 0),
        ByteField('size', 0)
    ]

    def do_dissect(self, s):
         # Consume exactly one byte for the size field
         self.request_pid = s[0]
         self.size = s[1]
         # Return the remaining bytes so that they’re available to the DataPacket
         return s[2:]

    def extract_padding(self, s):
         # Return an empty payload for this header and pass all remaining bytes to the next layer.
         return b"", s

class SerialFlocHeader(Packet):
    name = "SerialFlocHeader"
    fields_desc = [
        BitEnumField('type', 0, 8, {66: 'SERIAL_BROADCAST_TYPE', 85: 'SERIAL_UNICAST_TYPE'}),
        ByteField('size', 0)
    ]

    def do_dissect(self, s):
         # Consume exactly one byte for the size field
         self.type = s[0]
         self.size = s[1]
         # Return the remaining bytes so that they’re available to the DataPacket
         return s[2:]

    def extract_padding(self, s):
         # Return an empty payload for this header and pass all remaining bytes to the next layer.
         return b"", s

class SerialBroadcastHeader(Packet):
    name = "SerialBroadcastHeader"
    fields_desc = [

    ]

    def do_dissect(self, s):
         # Consume exactly one byte for the size field
         # Return the remaining bytes so that they’re available to the DataPacket
         return s

    def extract_padding(self, s):
         # Return an empty payload for this header and pass all remaining bytes to the next layer.
         return b"", s

class SerialUnicastHeader(Packet):
    name = "SerialUnicastHeader"
    fields_desc = [
        ShortField("dest_addr", 0)
    ]

    def do_dissect(self, s):
         # Consume exactly one byte for the size field
         self.dest_addr = int.from_bytes(s[:2],"big")
         # Return the remaining bytes so that they’re available to the DataPacket
         return s[2:]

    def extract_padding(self, s):
         # Return an empty payload for this header and pass all remaining bytes to the next layer.
         return b"", s

class DataPacket(Packet):
    name = "DataPacket"
    fields_desc = [
        PacketField('header', DataHeader(), DataHeader),
        StrLenField('data', b'', length_from=lambda pkt: pkt.header.size)
    ]

class CommandPacket(Packet):
    name = "CommandPacket"
    fields_desc = [
        PacketField('header', CommandHeader(), CommandHeader),
        StrLenField('data', b'', length_from=lambda pkt: pkt.header.size)
    ]

class AckPacket(Packet):
    name = "AckPacket"
    fields_desc = [
        PacketField('header', AckHeader(), AckHeader)
    ]

class ResponsePacket(Packet):
    name = "ResponsePacket"
    fields_desc = [
        PacketField('header', ResponseHeader(), ResponseHeader),
        StrLenField('data', b'', length_from=lambda pkt: pkt.header.size)
    ]

class FlocPacket(Packet):
    name = "FlocPacket"
    fields_desc = [
        PacketField("header", FlocHeader(), FlocHeader),
        ConditionalField(PacketField("data", DataPacket(), DataPacket), lambda pkt: pkt.header.type == 0),
        ConditionalField(PacketField("command", CommandPacket(), CommandPacket), lambda pkt: pkt.header.type == 1),
        ConditionalField(PacketField("response", ResponsePacket(), ResponsePacket), lambda pkt: pkt.header.type == 3),
    ]

class SerialBroadcastPacket(Packet):
    name = "SerialBroadcastPacket"
    fields_desc = [
        PacketField("header", SerialBroadcastHeader(), SerialBroadcastHeader),
        PacketField("floc_packet", FlocPacket(), FlocPacket)
    ]

class SerialUnicastPacket(Packet):
    name = "SerialUnicastPacket"
    fields_desc = [
        PacketField("header", SerialUnicastHeader(), SerialUnicastHeader),
        PacketField("floc_packet", FlocPacket(), FlocPacket)
    ]

class SerialFlocPacket(Packet):
    name = "SerialFlocPacket"
    fields_desc = [
        PacketField("header", SerialFlocHeader(), SerialFlocHeader),
        ConditionalField(PacketField("broadcast", SerialBroadcastPacket(), SerialBroadcastPacket), lambda pkt: pkt.header.type == ord('B')),
        ConditionalField(PacketField("unicast", SerialUnicastPacket(), SerialUnicastPacket), lambda pkt: pkt.header.type == ord('U')),
    ]
bind_layers(SerialFlocHeader, SerialBroadcastHeader, type=ord('B'))
bind_layers(SerialFlocHeader, SerialUnicastHeader, type=ord('U'))
bind_layers(SerialBroadcastHeader, FlocHeader)
bind_layers(SerialUnicastHeader, FlocHeader)
bind_layers(FlocHeader, DataPacket, type=0)
bind_layers(FlocHeader, CommandPacket, type=1)
bind_layers(FlocPacket, ResponsePacket, type=3)