import json
from os import path

from kivy.clock import Clock
from kivymd.uix.screenmanager import MDScreenManager
from importlib import import_module


class Root(MDScreenManager):
    def __init__(self, *args, **kwargs):
        super(Root, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.add_screens)

    def add_screens(self, delta):
        with open(path.join("json", "screen_data.json")) as file:
            screens = json.load(file)

        for screen_name, screen_details in screens.items():
            module = import_module(screen_details.get("import"))
            screen_class = getattr(module, screen_details.get("class"))

            screen_options = screen_details.get("options", {})

            screen_object = screen_class(**screen_options)
            screen_object.name = screen_name

            self.add_widget(screen_object)
