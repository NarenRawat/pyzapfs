import os

from kivymd.app import MDApp
from libs.uix.baseclass.root import Root
from kivy.clock import Clock
from kivy.core.window import Window

KV_DIR = os.path.join("src", "libs", "uix")

Window.minimum_width = 850
Window.minimum_height = 650

class ZapfsApp(MDApp):
    def __init__(self, *args, **kwargs):
        super(ZapfsApp, self).__init__(*args, **kwargs)
        self.title = "Zapfs"
        self.load_all_kv_files(KV_DIR)
        self.theme_cls.theme_style = "Dark"
        # self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.primary_palette = "Indigo"

    def on_start(self):
        Clock.schedule_once(lambda _: Window.maximize(), 0)

        # dev
        Clock.schedule_once(lambda _: self.change_root_screen("transfer_recv"), 0)

    def change_root_screen(self, screen_name):
        self.root.current = screen_name

    def build(self):
        return Root()


if __name__ == "__main__":
    app = ZapfsApp()
    app.run()
