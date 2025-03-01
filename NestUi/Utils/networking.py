# Adjust the import below as needed for your project structure.
from floc_pkts import *  # Import the generated file
from scapy.all import raw, Raw

def build_floc_packet(ttl: int,
                      type_val: int, 
                      nid: int, 
                      pid: int, 
                      dst: int, 
                      src: int, 
                      data: bytes, 
                      cmd_type_val: int = -1, 
                      ack_pid_val: int = -1, 
                      rsp_pid_val: int = -1) -> bytes:
    """
    Build a FLOC packet using ScaPy’s composition operator (/).
    
    Parameters:
        ttl (int): Time-to-live value (0-15).
        type_val (int): Packet type value.
                        0 = Data,
                        1 = Command,
                        2 = Ack,
                        3 = Response.
        nid (int): Network ID.
        pid (int): Packet ID.
        dst (int): Destination address.
        src (int): Source address.
        data (bytes): Additional payload data (for Data, Command, or Response packets).
        cmd_type_val (int): (Optional, default -1) Command packet type.
        ack_pid_val (int): (Optional, default -1) Acknowledge packet ID value.
        rsp_pid_val (int): (Optional, default -1) Response packet ID value.
    
    Returns:
        bytes: The raw bytes of the constructed FLOC packet.
    """
    # Validate type using the generated mapping function.
    type_symbolic = get_floc_packet_type(type_val)
    if not type_symbolic:
        raise ValueError(f"Invalid FLOC packet type: {type_val}")

    # Build the common header.
    common_header = FlocHeader(
        ttl=ttl,
        type=type_symbolic,
        nid=nid,
        pid=pid,
        res=0,
        dest_addr=dst,
        src_addr=src
    )

    # Compose the rest of the packet based on type.
    if type_val == 0:
        # Data packet.
        data_pkt = DataPacket(
            header=DataHeader(size=len(data)),
            data=data.ljust(55, b'\x00')[:55]
        )
        pkt = common_header / data_pkt

    elif type_val == 1:
        # Command packet.
        command_symbolic = get_command_type(cmd_type_val)
        if not command_symbolic:
            raise ValueError(f"Invalid command type: {cmd_type_val}")
        command_pkt = CommandPacket(
            header=CommandHeader(command_type=command_symbolic, size=len(data)),
            data=data.ljust(51, b'\x00')[:51]
        )
        pkt = common_header / command_pkt

    elif type_val == 2:
        # Ack packet.
        if ack_pid_val == -1:
            raise ValueError(f"Invalid ack pid value: {ack_pid_val}")
        ack_pkt = AckPacket(
            header=AckHeader(ack_pid=ack_pid_val)
        )
        pkt = common_header / ack_pkt

    elif type_val == 3:
        # Response packet.
        if rsp_pid_val == -1:
            raise ValueError(f"Invalid response pid value: {rsp_pid_val}")
        response_pkt = ResponsePacket(
            header=ResponseHeader(request_pid=rsp_pid_val, size=len(data)),
            data=data.ljust(54, b'\x00')[:54]
        )
        pkt = common_header / response_pkt

    else:
        raise ValueError(f"Invalid FLOC packet type: {type_val}")

    return raw(pkt)


def build_serial_floc_packet(floc_pkt_bytes: bytes, serial_type_val: str = "B", dest_addr: int = -1) -> bytes:
    """
    Build a Serial FLOC packet using ScaPy’s composition operator (/).
    
    Parameters:
        floc_pkt_bytes (bytes): The raw bytes of a FLOC packet.
        type_val (str): "B" for broadcast or "U" for unicast.
        dest_addr (int): (Optional, default -1) Destination address for unicast packet.
    
    Returns:
        bytes: The raw bytes of the constructed Serial FLOC packet.
    """
    # Validate the serial type.
    serial_type_symbolic = get_serial_floc_packet_type(ord(serial_type_val))
    if not serial_type_symbolic:
        raise ValueError(f"Invlaid Serial FLOC packet type: {serial_type_val}")

    header = SerialFlocHeader(
        type=serial_type_symbolic,
        size=len(floc_pkt_bytes)
    )

    if serial_type_val.upper() == "B":
        # For broadcast, compose with SerialBroadcastPacket and a Raw payload.
        pkt = header / SerialBroadcastPacket() / floc_pkt_bytes
    elif serial_type_val.upper() == "U":
        if dest_addr == -1:
            raise ValueError(f"Invalid destination address: {dest_addr}")
        # For unicast, set the destination address in SerialUnicastPacket.
        pkt = header / SerialUnicastPacket(dest_addr=dest_addr) / floc_pkt_bytes
    else:
        raise ValueError(f"Invalid Serial FLOC packet type: {serial_type_val}")

    return raw(pkt)


# --- Test Cases ---
if __name__ == "__main__":
    pkt = build_floc_packet(10, 0, 1, 1, 1, 1, b'abcd')
    print(f"Data Packet: {pkt}")

    serial_pkt_b = build_serial_floc_packet(pkt, "B")
    print(f"Serial Broadcast Packet: {serial_pkt_b}")

    serial_pkt_u = build_serial_floc_packet(pkt, "U", dest_addr=123)
    print(f"Serial Unicast Packet: {serial_pkt_u}")

    ack_pkt = build_floc_packet(ttl=5, type_val=2, nid=2, pid=3, dst=4, src=5, data=b"", ack_pid_val=10)
    print(f"Ack Packet: {ack_pkt}")

    command_pkt = build_floc_packet(ttl=7, type_val=1, nid=3, pid=2, dst=5, src=6, data=b"command data", cmd_type_val=2)
    print(f"Command Packet: {command_pkt}")

    response_pkt = build_floc_packet(ttl=8, type_val=3, nid=4, pid=1, dst=6, src=7, data=b"response data", rsp_pid_val=5)
    print(f"Response Packet: {response_pkt}")

    try:
        invalid_pkt = build_floc_packet(ttl=5, type_val=99, nid=2, pid=3, dst=4, src=5, data=b"")
    except ValueError as e:
        print(f"Caught expected error (invalid type): {e}")

    try:
        invalid_serial_pkt = build_serial_floc_packet(pkt, "X")
    except ValueError as e:
        print(f"Caught expected error (invalid serial type): {e}")

    try:
        invalid_serial_pkt = build_serial_floc_packet(pkt, "U")  # Missing destination address.
    except ValueError as e:
        print(f"Caught expected error (invalid serial type): {e}")
