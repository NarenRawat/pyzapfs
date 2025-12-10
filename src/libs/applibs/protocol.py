import struct

MAJOR_VERSION = 1
MINOR_VERSION = 0
MAGIC = b"ZAPFS"

MSG_DISCOVER_REQUEST = 1
MSG_DISCOVER_RESPONSE = 2
MSG_TRANSFER = 3

TLV_DISCOVER_RESPONSE_PORT = 1
TLV_DEVICE_NAME = 2
TLV_CONNECTION_PORT = 3
TLV_FILEDATA = 4
TLV_FILECHUNK = 5
TLV_OVERALL_SIZE = 6


_header_format = "!5sBBBL"
_tlv_header = "!BL"
_filedata = "!L"

def create_filedata(filename, size):
    return struct.pack(_filedata, size) + filename.encode()

def parse_filedata(data):
    header_size = struct.calcsize(_filedata)
    size = struct.unpack(_filedata, data[:header_size])

    return (size, data[header_size:].decode())

def get_tlv_header_size():
    return struct.calcsize(_tlv_header)


def create_tlv(t, l, v):
    header = struct.pack(_tlv_header, t, l)

    return header + v


def parse_tlvs(data):
    header_size = get_tlv_header_size()

    tlvs = []

    while data:
        t, l = struct.unpack(_tlv_header, data[:header_size])
        v = data[header_size : header_size + l]
        tlvs.append({"type": t, "length": l, "value": v})
        data = data[header_size + l :]

    return tlvs


def get_header_size():
    return struct.calcsize(_header_format)


def build_packet(msg_type, payload):
    # network-byte order: magic, major ver, minor ver, msg_type, length
    length = len(payload)

    header = struct.pack(
        _header_format,
        MAGIC,
        MAJOR_VERSION,
        MINOR_VERSION,
        msg_type,
        length,
    )

    return header + payload


def parse_packet(packet):
    header_size = struct.calcsize(_header_format)

    magic, major_ver, minor_ver, msg_type, length = struct.unpack(
        _header_format, packet[:header_size]
    )

    return header_size, magic, major_ver, minor_ver, msg_type, length
