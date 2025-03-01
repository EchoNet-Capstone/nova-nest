# Adjust the import below as needed for your project structure.
from ..Utils.floc_pkts import *  # Import the generated file
from scapy.all import raw

def build_floc_packet(ttl: int,
                       type_val: int, 
                       nid: int, 
                       pid: int, 
                       dst: int, 
                       src: int, 
                       data: bytes, 
                       cmd_type_val: int = -1, 
                       ack_pid_val: int = -1, 
                       rsp_pid_val:int = -1) -> bytes:
    """
    Build a FLOC packet using the generated Scapy packet classes.

    Parameters:
        ttl (int): Time-to-live value (0-15).
        type_val (int): Packet type value.  Defined types:
                        1 = Command,
                        2 = Ack,
                        3 = Response.
        nid (int): Network ID.
        pid (int): Packet ID.
        dst (int): Destination address.
        src (int): Source address.
        data (bytes): Additional payload data (for Command or Response packets).
        cmd_type_val (int): (Optional, default -1) Command packet type.
        ack_pid_val (int): (Optional, default -1) Acknowledge packet ID value.
        rsp_pid_val (int): (Optional, default -1) Response packed ID value.

    Returns:
        bytes: The raw bytes of the constructed FLOC packet.
    """
    # --- Use the generated function to get the symbolic type ---
    type_symbolic = get_floc_packet_type(type_val)
    if not type_symbolic:  # Handle invalid type_val
        raise ValueError(f"Invalid FLOC packet type: {type_val}")

    # Build the common header.
    common_header = HeaderCommon(
        ttl=ttl,
        type=type_symbolic,  # Use the symbolic name here!
        nid=nid,
        pid=pid,
        res=0,
        dest_addr=dst,
        src_addr=src
    )
    if type_val == 0:
        # General data packet:
        data_hdr = DataHeader(
            size=len(data)
        )
        data_fixed= data.ljust(55, b'\x00')[:55]
        data_pkt = DataPacket(
            header = data_hdr,
            data=data_fixed
        )
        pkt = FlocPacket(
            header=common_header,
            data=data_pkt
        )
    if type_val == 1:
        # Command packet:
        command_type_symbolic = get_command_type(cmd_type_val) # And get its symbolic representation
        if not command_type_symbolic:
            raise ValueError(f"Invalid command type: {cmd_type_val}")

        command_hdr = CommandHeader(
            command_type=command_type_symbolic,  # Use symbolic name
            size=len(data)
        )
        data_fixed = data.ljust(51, b'\x00')[:51]
        command_pkt = CommandPacket(
            header=command_hdr,
            data=data_fixed
        )
        pkt = FlocPacket(
            header=common_header,
            command=command_pkt
        )
    elif type_val == 2:
        # Ack packet:
        if ack_pid_val == -1:
            raise ValueError(f"Invalid akc pid value: {cmd_type_val}")
        ack_hdr = AckHeader(
            ack_pid=ack_pid_val  # Use the numerical value directly (AckHeader doesn't have an enum)
        )
        ack_pkt = AckPacket(
            header=ack_hdr
        )
        pkt = FlocPacket(
            header=common_header,
            ack=ack_pkt
        )
    elif type_val == 3:
        # Response packet:
        rsp_pid_val = 0  # Example - Replace with the actual request_pid
        response_hdr = ResponseHeader(
            request_pid=rsp_pid_val,  # Use numerical value (no enum)
            size=len(data)
        )
        data_fixed = data.ljust(54, b'\x00')[:54]
        response_pkt = ResponsePacket(
            header=response_hdr,
            data=data_fixed
        )
        pkt = FlocPacket(
            header=common_header,
            response=response_pkt
        )
    else:
        #  FlocPacket can handle only common_header, but it's better to raise an error
        raise ValueError(f"Invalid FLOC packet type: {type_val}")

    return raw(pkt)


def build_serial_floc_packet(floc_pkt_bytes: bytes, type_val: str = "B", dest_addr: int = -1) -> bytes:
    """
    Build a Serial FLOC packet.

    Parameters:
        floc_pkt_bytes (bytes): The raw bytes of a FLOC packet.
        packet_type (str): "B" for broadcast or "U" for unicast.
        dest_addr (int): (Optional defaults to -1) Destination address for unicast packet.

    Returns:
        bytes: The raw bytes of the constructed Serial FLOC packet.
    """

    # --- Use the generated function to get symbolic type ---
    serial_type_symbolic = get_serial_floc_packet_type(ord(type_val))
    if not serial_type_symbolic:
        raise ValueError(f"Invalid Serial FLOC packet type: {type_val}")

    header = SerialFlocHeader(
        type=serial_type_symbolic,
        size=len(floc_pkt_bytes)
    )

    if type_val.upper() == "B":
        broadcast_pkt = SerialBroadcastPacket() / floc_pkt_bytes
        pkt = SerialFlocPacket(
            header=header,
            broadcast=broadcast_pkt
        )
    elif type_val.upper() == "U":
        if dest_addr == -1:
            raise ValueError(f"Invalid destination address: {dest_addr}")
        
        unicast_pkt = SerialUnicastPacket(dest_addr) / floc_pkt_bytes  # dest_addr example
        pkt = SerialFlocPacket(
            header=header,
            unicast=unicast_pkt
        )
    else:
        raise ValueError("Invalid Serial FLOC packet type: {type_val}")

    return raw(pkt)