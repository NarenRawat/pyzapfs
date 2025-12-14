from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from libs.applibs import network, protocol, utils
import struct
import os
import multitasking
import time


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
        self.filedata = None
        self.transfer_sock = None
        self.start_time = 0
        self.speed_update_event = None

    def update_progress(self, sent, i, v):
        self.overall_sent += sent
        v["sent"] += sent
        files_rv = self.ids["files_rv"]
        files_rv.data.pop(i)
        files_rv.data.insert(i, v)

    def update_speed(self, dt):
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            speed = self.overall_sent / elapsed
            self.overall_speed = utils.hr_size(speed) + "/s"

    @multitasking.task
    def start_sending(self):
        self.start_time = time.time()
        self.speed_update_event = Clock.schedule_interval(
            self.update_speed, 1
        )

        files_rv = self.ids["files_rv"]
        self.transfer_sock.setblocking(False)

        for i, v in enumerate(files_rv.data):
            with open(v.get("filename"), "rb") as file:

                byte_read = file.read(1024)

                while len(byte_read) > 0:
                    try:
                        # send chunk
                        self.transfer_sock.sendall(byte_read)

                        sent_now = len(byte_read)

                        # correct lambda capturing (fixes progress stuck < 100)
                        Clock.schedule_once(
                            lambda dt, sent=sent_now, index=i, item=v:
                                self.update_progress(sent, index, item),
                            0
                        )

                        # next chunk
                        byte_read = file.read(1024)

                    except BlockingIOError:
                        continue

            # force a final UI sync so the bar hits exactly 100%
            Clock.schedule_once(
                lambda dt, index=i, item=v:
                    self.update_progress(0, index, item),
                0
            )

        if self.speed_update_event:
            self.speed_update_event.cancel()
        self.transfer_sock.close()

    def on_receive(self, server_ip, data):
        self.server_ip = server_ip
        self.filedata = data

        to_send = b""

        for file, size in data.items():
            self.ids["files_rv"].data.append(
                {"filename": file, "total_size": size, "sent": 0}
            )

            self.overall_size += size
            self.total_files += 1

            filedata = protocol.create_filedata(
                os.path.basename(file), size
            )

            to_send += protocol.create_tlv(
                protocol.TLV_FILEDATA, len(filedata), filedata
            )

        byte_overall_size = struct.pack("!Q", self.overall_size)
        to_send += protocol.create_tlv(
            protocol.TLV_OVERALL_SIZE,
            len(byte_overall_size),
            byte_overall_size,
        )

        packet = protocol.build_packet(protocol.MSG_TRANSFER, to_send)

        self.transfer_sock = network.create_tcp_socket()
        addr = (self.server_ip, 9500)

        self.transfer_sock.connect(addr)
        self.transfer_sock.sendall(packet)
        self.transfer_sock.sendall(b"")

        Clock.schedule_once(lambda x: self.start_sending(), 5)
