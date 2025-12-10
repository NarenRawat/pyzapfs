from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, NumericProperty


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

    def on_receive(self, sender_sock, receiver_sock):
        print("Hello")
        self.receiver_sock = receiver_sock
        self.sender_sock = sender_sock

        data = self.sender_sock.recv(1024)
        total_data = data

        while len(data) > 0:
            data = self.sender_sock.recv(1024)
            total_data += data

        print(total_data)


        self.sender_sock.close()
        self.receiver_sock.close()
