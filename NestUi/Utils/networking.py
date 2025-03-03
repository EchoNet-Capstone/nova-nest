# packet_builder.py (VARIABLE LENGTH DATA)
from floc_pkts import *  # Import the generated file
from scapy.all import raw, Raw

MAX_DATA_SIZE = 55
MAX_COMMAND_SIZE = 51
MAX_RESPONSE_SIZE = 54


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
    Build a FLOC packet with variable-length data, padding as needed.
    """
    type_symbolic = get_floc_packet_type(type_val)
    if not type_symbolic:
        raise ValueError(f"Invalid FLOC packet type: {type_val}")

    common_header = FlocHeader(
        ttl=ttl,
        type=type_symbolic,
        nid=nid,
        pid=pid,
        res=0,
        dest_addr=dst,
        src_addr=src
    )

    data_size = len(data)
    max_size, type_str = (
        (MAX_DATA_SIZE, 'Data'),
        (MAX_COMMAND_SIZE, 'Command'),
        (0, 'Ack'),
        (MAX_RESPONSE_SIZE, 'Response'),
    )[type_val]

    if data_size > max_size:
        raise ValueError(f"{type_str} data size exceeds maximum ({max_size} bytes)")

    if type_val == 0:
        # Data packet.
        data_pkt = DataPacket(
            header=DataHeader(size=data_size),  # Set the ACTUAL size
            data=data
        )
        pkt = common_header / data_pkt

    elif type_val == 1:
        # Command packet.
        command_symbolic = get_command_type(cmd_type_val)
        if not command_symbolic:
            raise ValueError(f"Invalid command type: {cmd_type_val}")

        command_pkt = CommandPacket(
            header=CommandHeader(command_type=command_symbolic, size=data_size),  # Set size
            data=data
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
            header=ResponseHeader(request_pid=rsp_pid_val, size=data_size),  # Set size
            data=data
        )
        pkt = common_header / response_pkt
    else:
        raise ValueError(f"Invalid FLOC packet type: {type_val}")

    return raw(pkt)



def build_serial_floc_packet(floc_pkt_bytes: bytes, serial_type_val: str = "B", dest_addr: int = -1) -> bytes:
    """
    Build a Serial FLOC packet.
    """
    serial_type_symbolic = get_serial_floc_packet_type(ord(serial_type_val))
    if not serial_type_symbolic:
        raise ValueError(f"Invlaid Serial FLOC packet type: {serial_type_val}")

    header = SerialFlocHeader(
        type=serial_type_symbolic,
        size=len(floc_pkt_bytes)  # Correct size calculation
    )

    if serial_type_val.upper() == "B":
        pkt = header / Raw(load=floc_pkt_bytes)
    elif serial_type_val.upper() == "U":
        if dest_addr == -1:
            raise ValueError(f"Invalid destination address: {dest_addr}")
        unicast_header = SerialUnicastHeader(dest_addr=dest_addr)
        pkt = header / unicast_header / Raw(load=floc_pkt_bytes)
    else:
        raise ValueError(f"Invalid Serial FLOC packet type: {serial_type_val}")

    return raw(pkt)

# --- Test Cases ---
if __name__ == "__main__":
    # Test with different data lengths.
    pkt1 = build_floc_packet(10, 0, 1, 1, 1, 1, b'abcd')
    print(f"Data Packet (short data): {pkt1}")
    

    pkt_long = build_floc_packet(10, 0, 1, 1, 1, 1, b'A' * 20)
    print(f"Data Packet (longer data): {pkt_long}")

    # Test command
    command_pkt = build_floc_packet(ttl=7, type_val=1, nid=3, pid=2, dst=5, src=6, data=b"c", cmd_type_val=2)
    print(f"Command Packet: {command_pkt}")

    # Test ack
    ack_pkt = build_floc_packet(ttl=5, type_val=2, nid=2, pid=3, dst=4, src=5, data=b"", ack_pid_val=10)
    print(f"Ack Packet: {ack_pkt}")

    #Test response.
    response_pkt = build_floc_packet(ttl=8, type_val=3, nid=4, pid=1, dst=6, src=7, data=b"r" * 5, rsp_pid_val=5)
    print(f"Response Packet: {response_pkt}")


    # Test maximum data length (should work).
    pkt_max = build_floc_packet(10, 0, 1, 1, 1, 1, b'X' * MAX_DATA_SIZE)
    print(f"Data Packet (max data): {pkt_max}")

    # Test exceeding maximum data length (should raise an error).
    try:
        pkt_too_long = build_floc_packet(10, 0, 1, 1, 1, 1, b'Y' * (MAX_DATA_SIZE + 1))
    except ValueError as e:
        print(f"Caught expected error (data too long): {e}")

    serial_pkt_b = build_serial_floc_packet(command_pkt, "B")
    print(f"Serial Broadcast Packet: {serial_pkt_b}")

    serial_pkt_u = build_serial_floc_packet(pkt1, "U", dest_addr=123)
    print(f"Serial Unicast Packet: {serial_pkt_u}")

    try:
        invalid_pkt = build_floc_packet(ttl=5, type_val=99, nid=2, pid=3, dst=4, src=5, data=b"")
    except ValueError as e:
        print(f"Caught expected error (invalid type): {e}")

    try:
        invalid_serial_pkt = build_serial_floc_packet(pkt1, "X")
    except ValueError as e:
        print(f"Caught expected error (invalid serial type): {e}")

    try:
        invalid_serial_pkt = build_serial_floc_packet(pkt1, "U")  # Missing destination address.
    except ValueError as e:
        print(f"Caught expected error (invalid serial type): {e}")

    print('Short Data Packet')
    FlocPacket(pkt1).show()

    print('Long DataPacket')
    FlocPacket(pkt_long).show()

    print('Command Packet')
    FlocPacket(command_pkt).show()

    print('Response Packet)')
    FlocPacket(response_pkt).show()

    print('Max Data Packet')
    FlocPacket(pkt_max).show()

    print('Ack Packet')
    FlocPacket(ack_pkt).show()

    print('Serial Broadcast Command Packet')
    SerialFlocPacket(serial_pkt_b).show()
    
    print('Serial Unicast Data Packet')
    SerialFlocPacket(serial_pkt_u).show()
    