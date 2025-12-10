from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty
from libs.applibs import network, protocol
import struct
import multitasking
import os


class TransferRecvFileItem(MDBoxLayout):
    filename = StringProperty("")
    sent = NumericProperty(0)
    total_size = NumericProperty(0)


class TransferRecvScreen(MDScreen):
    total_files = NumericProperty(0)
    overall_speed = StringProperty("30 MB/s")
    overall_size = NumericProperty(0)
    overall_sent = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super(TransferRecvScreen, self).__init__(*args, **kwargs)
        self.receiver_sock = None
        self.sender_sock = None

    @multitasking.task
    def start_receiving(self):
        files_rv = self.ids["files_rv"]
        os.makedirs("received", exist_ok=True)

        for i, entry in enumerate(files_rv.data):
            filename = entry["filename"]
            filesize = entry["total_size"]

            output_path = os.path.join("received", filename)

            remaining = filesize
            print(f"[+] Receiving: {filename}  ({remaining} bytes)")

            with open(output_path, "wb") as file:
                while remaining > 0:
                    try:
                        chunk = self.sender_sock.recv(min(4096, remaining))
                        if not chunk:
                            raise ConnectionError("Connection closed mid-file.")
                        file.write(chunk)
                        remaining -= len(chunk)

                        # update progress in RV
                        entry["sent"] = entry.get("sent", 0) + len(chunk)
                        files_rv.data[i] = entry      # update visible RV item
                    except BlockingIOError:
                        continue

            print(f"[✓] File saved: {filename}")

        self.sender_sock.close()
        self.receiver_sock.close()

    def on_receive(self, sender_sock, receiver_sock):
        self.receiver_sock = receiver_sock
        self.sender_sock = sender_sock

        try:
            data = self.sender_sock.recv(1024)
            total_data = data

            while len(data) > 0:
                data = self.sender_sock.recv(1024)
                total_data += data

        except BlockingIOError:
            pass

        header_size, *_, length = protocol.parse_packet(total_data)
        payload = total_data[header_size:]
        tlvs = protocol.parse_tlvs(payload)

        for tlv in tlvs:
            if tlv.get("type") == protocol.TLV_OVERALL_SIZE:
                self.overall_size = struct.unpack(
                    "!Q", tlv.get("value")
                )[0]
            elif tlv.get("type") == protocol.TLV_FILEDATA:
                size, filename = protocol.parse_filedata(
                    tlv.get("value")
                )
                self.ids["files_rv"].data.append(
                    {"filename": filename, "total_size": size}
                )
                self.total_files += 1

        Clock.schedule_once(lambda x: self.start_receiving(), 5)

        # self.sender_sock.close()
        # self.receiver_sock.close()

