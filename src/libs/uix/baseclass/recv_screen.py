import socket
from kivymd.uix.screen import MDScreen
from kivymd.uix.widget import MDWidget
from kivy.graphics import Color, Ellipse
from libs.applibs import utils
from kivy.clock import Clock

from kivy.properties import BooleanProperty
from libs.applibs import network, protocol


class RecvScreen(MDScreen):
    searching = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super(RecvScreen, self).__init__(*args, **kwargs)
        self.discover_recv_sock = None
        self.sent_to = []
        self.transfer_sock = None
        self.transfer_started = False
        self.sender_sock = None

    def cleanup(self):
        self.searching = False
        self.discover_recv_sock.close()

    def on_enter(self):
        self.searching = True
        self.transfer_started = False

        self.discover_recv_sock = (
            network.create_udp_broadcast_recv_socket()
        )
        self.discover_recv_sock.setblocking(False)
        self.discover_recv_sock.bind(("", 9000))

        self.transfer_sock = network.create_tcp_socket("", 9500, 5)
        self.transfer_sock.setblocking(False)

        Clock.schedule_interval(self.recv_request, 0)
        Clock.schedule_interval(self.recv_transfer_request, 0)

    def on_leave(self):
        self.searching = False
        self.transfer_started = True
        self.cleanup()

    def recv_transfer_request(self, dt):
        if self.transfer_started:
            return False

        try:
            sock, (addr, port) = self.transfer_sock.accept()
            self.sender_sock = sock
            self.sender_sock.setblocking(False)

            self.transfer_started = True
            self.manager.current = "transfer_recv"
            self.manager.current_screen.on_receive(sock, self.transfer_sock)

        except BlockingIOError:
            pass

    def recv_request(self, dt):
        if not self.searching:
            return False

        try:
            data, (ip, port) = self.discover_recv_sock.recvfrom(1024)
            header_size, *_, length = protocol.parse_packet(data)
            tlvs = protocol.parse_tlvs(
                data[header_size : header_size + length]
            )

            for tlv in tlvs:
                if (
                    tlv.get("type")
                    == protocol.TLV_DISCOVER_RESPONSE_PORT
                ):
                    client_port = int(tlv.get("value").decode())


                    addr = (ip, client_port)
                    if addr in self.sent_to:
                        continue

                    self.sent_to.append(addr)

                    client_sock = network.create_tcp_socket()
                    client_sock.connect(addr)

                    dev_name = socket.gethostname().encode()
                    tlv = protocol.create_tlv(
                        protocol.TLV_DEVICE_NAME,
                        len(dev_name),
                        dev_name,
                    )

                    packet = protocol.build_packet(
                        protocol.MSG_DISCOVER_RESPONSE, tlv
                    )

                    client_sock.sendall(packet)
                    client_sock.close()

        except BlockingIOError:
            pass


class WaitingConnection(MDWidget):
    def __init__(self, *args, **kwargs):
        super(WaitingConnection, self).__init__(*args, **kwargs)
        self.radius_factor = 0

        Clock.schedule_interval(self.animate, 1 / 24)

    def animate(self, dt):
        self.radius_factor += dt

        if self.radius_factor >= 1:
            self.radius_factor = 0

        rad = self.size[0] / 2
        circle_counts = 4
        per_size = rad / circle_counts

        self.canvas.clear()
        with self.canvas:
            for i in range(circle_counts):
                x = self.center_x - per_size * (i + self.radius_factor)
                y = self.center_y - per_size * (i + self.radius_factor)
                s = (2 * per_size) * (i + self.radius_factor)

                t = 1 - s / (2 * rad)
                r, g, b, a = self.theme_cls.onBackgroundColor
                opacity = utils.lerp(0, 0.1, t)

                Color(r, g, b, opacity)
                Ellipse(pos=(x, y), size=(s, s))

                r, g, b, a = self.theme_cls.secondaryColor
                Color(r, g, b, a)

                radius = 70
                x = self.center_x - radius
                y = self.center_y - radius

                Ellipse(pos=(x, y), size=(2 * radius, 2 * radius))

    def draw(self):
        pass
