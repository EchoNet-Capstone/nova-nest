from scapy.all import Packet, BitField, ShortField, ByteField, IntField, StrLenField, PacketField, bind_layers, ByteEnumField, BitEnumField, Raw, Padding

from scapy.fields import PacketField

class FixedPacketField(PacketField):
    __slots__ = PacketField.__slots__ + ["fixed_length"]
    def __init__(self, name, default, cls, fixed_length):
        super().__init__(name, default, cls)
        self.fixed_length = fixed_length

    def getfield(self, pkt, s):
        hdr_bytes = s[:self.fixed_length]
        remaining = s[self.fixed_length:]
        hdr = self.cls(hdr_bytes) # Create AND dissect in one step.  Crucial change!
        return hdr, remaining  # Return the header object, remaining bytes

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
        BitField('pid', 0, 6),
        BitField('res', 0, 2),
        ShortField('dest_addr', 0),
        ShortField('src_addr', 0)
    ]

class DataHeader(Packet):
    name = "DataHeader"
    fields_desc = [
        ByteField('size', 0)
    ]

class CommandHeader(Packet):
    name = "CommandHeader"
    fields_desc = [
        BitEnumField('command_type', 0, 8, {1: 'COMMAND_TYPE_1', 2: 'COMMAND_TYPE_2'}),
        ByteField('size', 0)
    ]

class AckHeader(Packet):
    name = "AckHeader"
    fields_desc = [
        ByteField('ack_pid', 0)
    ]

class ResponseHeader(Packet):
    name = "ResponseHeader"
    fields_desc = [
        ByteField('request_pid', 0),
        ByteField('size', 0)
    ]

class DataPacket(Packet):
    name = "DataPacket"
    fields_desc = [
        FixedPacketField('header', DataHeader(), DataHeader, fixed_length=len(DataHeader())), #Removed .build()
        StrLenField('data', b'', length_from=lambda pkt: pkt.header.size)
    ]

class CommandPacket(Packet):
    name = "CommandPacket"
    fields_desc = [
        FixedPacketField('header', CommandHeader(), CommandHeader, fixed_length=len(CommandHeader())), #Removed .build()
        StrLenField('data', b'', length_from=lambda pkt: pkt.header.size)
    ]

class AckPacket(Packet):
    name = "AckPacket"
    fields_desc = [
        FixedPacketField('header', AckHeader(), AckHeader, fixed_length=len(AckHeader())) #Removed .build()
    ]

class ResponsePacket(Packet):
    name = "ResponsePacket"
    fields_desc = [
        FixedPacketField('header', ResponseHeader(), ResponseHeader, fixed_length=len(ResponseHeader())), #Removed .build()
        StrLenField('data', b'', length_from=lambda pkt: pkt.header.size)
    ]

class SerialFlocHeader(Packet):
    name = "SerialFlocHeader"
    fields_desc = [
        BitEnumField('type', 0, 8, {66: 'SERIAL_BROADCAST_TYPE', 85: 'SERIAL_UNICAST_TYPE'}),
        ByteField('size', 0)
    ]

class SerialBroadcastPacket(Packet):
    name = "SerialBroadcastPacket"
    fields_desc = [

    ]

class SerialUnicastPacket(Packet):
    name = "SerialUnicastPacket"
    fields_desc = [
        ShortField('dest_addr', 0)
    ]


bind_layers(FlocHeader, DataPacket, type=0)
bind_layers(FlocHeader, CommandPacket, type=1)
bind_layers(FlocHeader, ResponsePacket, type=3)
bind_layers(SerialFlocHeader, SerialBroadcastPacket, type=66)  # Corrected binding
bind_layers(SerialFlocHeader, SerialUnicastPacket, type=85)    # Corrected binding
bind_layers(SerialBroadcastPacket, FlocHeader) # NEW.
bind_layers(SerialUnicastPacket, FlocHeader)