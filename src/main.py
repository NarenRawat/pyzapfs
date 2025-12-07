import os

from kivymd.app import MDApp
from libs.uix.baseclass.root import Root

KV_DIR = os.path.join("src", "libs", "uix", "kv")


class ZapfsApp(MDApp):
    def __init__(self, *args, **kwargs):
        super(ZapfsApp, self).__init__(*args, **kwargs)
        self.title = "Zapfs"
        self.load_all_kv_files(KV_DIR)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Olive"

    def change_root_screen(self, screen_name):
        self.root.current = screen_name

    def build(self):
        return Root()


if __name__ == "__main__":
    app = ZapfsApp()
    app.run()
