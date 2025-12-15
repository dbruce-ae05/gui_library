import tkinter
from collections import namedtuple
from datetime import datetime
from tkinter.constants import HORIZONTAL
from tkinter.ttk import Progressbar
from typing import Literal, TypeAlias

StatusBarSide: TypeAlias = Literal["left", "right"]
StatusBarStatus = namedtuple("status", ["timestamp", "message", "side", "style"])


class StatusBar(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.grid(sticky="nsew")

        self.status_log: list = list()

        self.make_widgets()
        self.update_status("Status Bar Initialized!")

    def make_widgets(self):
        self.left: tkinter.Label = tkinter.Label(self)
        self.right: tkinter.Label = tkinter.Label(self)

        self.regrid()

        self.left.bind("<Double-Button-1>", self.left_double_click)
        self.right.bind("<Double-Button-1>", self.right_double_click)

    def regrid(self):
        self.left.grid(row=0, column=0, sticky="ws")
        self.right.grid(row=0, column=1, sticky="es")

    def update_progress(self, numerator: int, denominator: int, message: str):
        if not self.progress:
            self.progress = Progressbar(
                self, mode="determinate", length=100, orient=HORIZONTAL
            )

        self.progress.grid(row=0, column=2, sticky="nsew")
        self.columnconfigure(2, weight=1)

        if denominator == 0:
            prog = 0
        else:
            prog = round(numerator / denominator * 100, 1)

        self.progress["value"] = prog
        self.right.config(text=f"{message}, {numerator} / {denominator} ({prog}%)")

    def clear_progress(self):
        if self.progress:
            self.progress.grid_forget()
            self.progress.destroy()

        status_log = self.status_log
        self.destroy()
        self.__init__(self.master)
        self.status_log = status_log

    def update_status(
        self,
        message: str | list,
        style: str = "info.TFrame",
        side: StatusBarSide = "left",
        append_to_log: bool = True,
    ):
        if isinstance(message, list):
            message = " | ".join(message)

        status = StatusBarStatus(datetime.now(), message, side, style)

        if append_to_log:
            self.status_log.append(status)

        if side == "left":
            self.left.config(
                text=f"{status.timestamp.strftime('%H:%M:%S')} | {status.message}"
            )
        elif side == "right":
            self.right.config(text=status.message)

    def left_double_click(self, event: tkinter.Event):
        self.master.event_generate("<<StatusBar.DoubleClick.Left>>")

    def right_double_click(self, event: tkinter.Event):
        self.master.event_generate("<<StatusBar.DoubleClick.Right>>")
