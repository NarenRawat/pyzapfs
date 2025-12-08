import socket
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivy.properties import (
    StringProperty,
    BooleanProperty,
    ObjectProperty,
    ListProperty,
)
from kivy.clock import Clock
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior

from libs.applibs import network
from libs.applibs import protocol


class ReceiverItem(
    RectangularRippleBehavior, ButtonBehavior, MDBoxLayout
):
    index = None
    device_name = StringProperty("")
    ip = StringProperty("")


class ReceiverFindScreen(MDScreen):
    searching = BooleanProperty(False)
    search_indicator = ObjectProperty(None)
    receivers = ListProperty([])
    receiver_rv = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(ReceiverFindScreen, self).__init__(*args, **kwargs)
        self.broadcast_socket = None
        self.discover_reponse_sock = None
        self.discover_packet = None

    def cleanup(self):
        self.searching = False
        self.discover_reponse_sock.close()
        self.broadcast_socket.close()

    def discover_receivers(self, dt):
        if not self.searching:
            return

        try:
            sock, (addr, port) = self.discover_reponse_sock.accept()
            # recv_sock = network.create_tcp_socket(addr, port)
            # recv_sock.connect((addr, port))
            data = sock.recv(1024)
            total_data = data

            while len(data) > 0:
                data = sock.recv(1024)
                total_data += data

            print(f"{total_data=}")
            header_size, *_, length = protocol.parse_packet(total_data)

            tlvs = protocol.parse_tlvs(
                total_data[header_size : header_size + length]
            )
            print(tlvs)
            for tlv in tlvs:
                print(tlv)
                if tlv.get("type") == protocol.TLV_DEVICE_NAME:
                    r_data = {
                        "device_name": tlv.get("value").decode(),
                        "ip": addr,
                    }
                    print(r_data)
                    self.receivers.append(r_data)

        except BlockingIOError:
            pass

    def on_enter(self):
        self.searching = True
        self.search_indicator.start()

        self.broadcast_socket = network.create_udp_broadcast_socket()
        self.discover_reponse_sock = network.create_tcp_socket(
            "", 0, 50
        )
        self.discover_reponse_sock.setblocking(False)

        port = self.discover_reponse_sock.getsockname()[1]
        port = str(port).encode()

        self.discover_packet = protocol.build_packet(
            protocol.DISCOVER_REQUEST,
            protocol.create_tlv(
                protocol.TLV_DISCOVER_RESPONSE_PORT, len(port), port
            ),
        )

        Clock.schedule_interval(self.send_broadcast, 1)
        Clock.schedule_interval(self.discover_receivers, 0)

    def on_receivers(self, widget, items):
        self.receiver_rv.data = self.receivers

    def on_leave(self):
        self.searching = False
        self.cleanup()

    def send_broadcast(self, dt):
        if not self.searching:
            self.search_indicator.stop()
            return False

        network.send_broadcast(
            self.broadcast_socket, self.discover_packet
        )

    def on_cancel_search_btn(self):
        self.searching = False

    def on_receive(self, filesdata):
        pass
        # print(filesdata)
