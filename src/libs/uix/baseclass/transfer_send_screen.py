from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from libs.applibs import network, protocol
import struct
import os


class TransferSendFileItem(MDBoxLayout):
    filename = StringProperty("")
    sent = NumericProperty(0)
    total_size = NumericProperty(0)


class TransferSendScreen(MDScreen):
    total_files = NumericProperty(0)
    overall_speed = StringProperty("0 KB/s")
    overall_size = NumericProperty(0)
    overall_sent = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super(TransferSendScreen, self).__init__(*args, **kwargs)
        self.server_ip = ""

    def on_receive(self, sever_ip, data):
        self.server_ip = sever_ip

        to_send = b""

        byte_overall_size = struct.pack("!L", self.overall_size)

        to_send += protocol.create_tlv(
            protocol.TLV_OVERALL_SIZE,
            len(byte_overall_size),
            byte_overall_size,
        )

        for file, size in data.items():
            self.ids["files_rv"].data.append(
                {"filename": file, "total_size": size, "sent": 0}
            )
            self.overall_size += size
            self.total_files += 1

            filedata = protocol.create_filedata(os.path.basename(file), size)

            to_send += protocol.create_tlv(protocol.TLV_FILEDATA, len(filedata), filedata)

        packet = protocol.build_packet(protocol.MSG_TRANSFER, to_send)

        print(self.server_ip)
        self.transfer_sock = network.create_tcp_socket()
        addr = (self.server_ip, 9500)

        self.transfer_sock.connect(addr)
        self.transfer_sock.sendall(packet)