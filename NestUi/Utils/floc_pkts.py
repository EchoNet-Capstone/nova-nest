# This file is generated automatically by the FLOC generator script.
#
# Usage:
#   - Import this module to access the generated Scapy classes, which represent
#     the packet headers defined in the FLOC header file.
#   - The classes (e.g., HeaderCommon, CommandHeader, AckHeader, ResponseHeader) are
#     derived from Scapy's Packet class and can be used to build, send, and dissect packets.
#   - The bind_layers calls at the end automatically bind the correct header types
#     based on the 'type' field in HeaderCommon.
#
from scapy.all import Packet, BitField, ShortField, ByteField, IntField, StrField, PacketField, bind_layers, ByteEnumField


class HeaderCommon(Packet):
	name = "HeaderCommon"
	fields_desc = [
		BitField('ttl', 0, 4),
        ByteEnumField('type', 0, {b'FLOC_COMMAND_TYPE': 1, b'FLOC_ACK_TYPE': 2, b'FLOC_RESPONSE_TYPE': 3}),
        ShortField('nid', 0),
        BitField('pid', 0, 6),
        BitField('res', 0, 2),
        ShortField('dest_addr', 0),
        ShortField('src_addr', 0)
	]

class CommandHeader(HeaderCommon):
	name = "CommandHeader"
	fields_desc = [
		PacketField('common', HeaderCommon(), HeaderCommon),
        ByteField('size', 0)
	]

	def extract_padding(self, s):
		return "", s

class AckHeader(HeaderCommon):
	name = "AckHeader"
	fields_desc = [
		PacketField('common', HeaderCommon(), HeaderCommon),
        ByteField('ack_pid', 0)
	]

	def extract_padding(self, s):
		return "", s

class ResponseHeader(HeaderCommon):
	name = "ResponseHeader"
	fields_desc = [
		PacketField('common', HeaderCommon(), HeaderCommon),
        ByteField('request_pid', 0),
        ByteField('size', 0)
	]

	def extract_padding(self, s):
		return "", s

bind_layers(HeaderCommon, CommandHeader, type=1)
bind_layers(HeaderCommon, AckHeader, type=2)
bind_layers(HeaderCommon, ResponseHeader, type=3)

