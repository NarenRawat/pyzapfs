import os
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivy.core.window import Window
from kivy.properties import (
    NumericProperty,
    StringProperty,
    ObjectProperty,
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.clock import Clock
import multitasking

from tkinter.filedialog import askopenfilenames


class FileViewItem(MDBoxLayout):
    index = None
    filepath = StringProperty("")
    filesize = NumericProperty(0)
    callback = ObjectProperty(lambda x: x)


class FileSelectionScreen(MDScreen):
    total_file_size = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super(FileSelectionScreen, self).__init__(*args, **kwargs)
        Window.bind(on_drop_file=self.on_drop_file)
        self._file_browser_open = False

    def send(self):
        files_rv = self.ids["files_rv"]
        self.manager.current_screen.on_receive(
            {
                x.get("filepath"): x.get("filesize")
                for x in files_rv.data
            }
        )
        self.clear_files_list()

    def clear_files_list(self):
        files_rv = self.ids["files_rv"]
        files_rv.data = []

    def remove_file(self, filedata):
        files_rv = self.ids["files_rv"]
        self.total_file_size -= filedata.get("filesize")
        files_rv.data.remove(filedata)

    def add_files(self, *args):
        for file in args:
            if os.path.isdir(file):
                files = os.listdir(file)
                files = map(lambda f: os.path.join(file, f), files)
                self.add_files(*files)

            elif os.path.isfile(file):
                files_rv = self.ids["files_rv"]
                if file not in map(
                    lambda x: x.get("filepath"), files_rv.data
                ):
                    filesize = os.stat(file).st_size
                    self.total_file_size += filesize
                    files_rv.data.append(
                        {
                            "filepath": file,
                            "filesize": filesize,
                            "callback": self.remove_file,
                        }
                    )

    def on_drop_file(self, widget, filename, x, y):
        self.add_files(filename.decode())

    def on_browse_files_btn(self):
        if not self._file_browser_open:
            self._file_browser_open = True
            self.open_filebrowser()

    @multitasking.task
    def open_filebrowser(self):
        files = askopenfilenames(
            initialdir=os.path.expanduser("~"),
            filetypes=[("All files", "*")],
        )
        self._file_browser_open = False

        Clock.schedule_once(lambda _: self.add_files(*files), 0)


class DropArea(MDCard):
    def __init__(self, *args, **kwargs):
        super(DropArea, self).__init__(*args, **kwargs)
