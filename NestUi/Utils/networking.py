# Adjust the import below as needed for your project structure.
from floc_pkts import HeaderCommon, CommandHeader, AckHeader, ResponseHeader

def build_floc_packet(ttl: int, type_val: int, nid: int, pid: int, dst: int, src: int, data_str: str) -> bytes:
    """
    Build a FLOC packet using the generated Scapy packet classes.

    Parameters:
        ttl (int): Time-to-live value (0-15).
        type_val (int): Packet type value (0-15). Defined types (1, 2, 3) correspond to Command,
                        Ack, and Response packets, respectively.
        nid (int): Network ID.
        pid (int): Packet ID.
        dst (int): Destination address.
        src (int): Source address.
        data_str (str): Additional payload data (up to 56 characters).

    Returns:
        bytes: The raw bytes of the constructed FLOC packet.
    """
    # Create the base header using HeaderCommon fields.
    common_header = HeaderCommon(
        ttl=ttl,
        type=type_val,
        nid=nid,
        pid=pid,
        res=0,
        dest_addr=dst,
        src_addr=src
    )

    # Depending on the type, choose the appropriate Scapy class.
    # For undefined types, default to the common header.
    if type_val == 1:
        # Command packet: set 'size' to the length of the payload.
        pkt = CommandHeader(common=common_header, size=len(data_str))
    elif type_val == 2:
        # Ack packet: set 'ack_pid' to 0 (customize as needed).
        pkt = AckHeader(common=common_header, ack_pid=0)
    elif type_val == 3:
        # Response packet: set 'request_pid' to 0 and 'size' to the payload length.
        pkt = ResponseHeader(common=common_header, request_pid=0, size=len(data_str))
    else:
        # For other types, just use the common header.
        pkt = common_header

    # If there is any additional data, append it as the payload.
    if data_str:
        pkt = pkt / data_str

    # Return the raw bytes of the packet.
    return bytes(pkt)

def build_nest_to_burd_packet(self, floc_packet: bytes) -> bytes:
        """
        Build the NeST-to-BuRD packet.
        The packet is composed of:
          - CMD ID (ASCII 'B')
          - Size (1 byte: length of the FLOC packet)
          - FLOC packet payload.
        """
        cmd_id = ord('B')
        size = len(floc_packet)
        packet = bytes([cmd_id, size]) + floc_packet
        return packet
