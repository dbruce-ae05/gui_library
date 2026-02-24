import tkinter
from collections import namedtuple
from datetime import datetime
from time import perf_counter
from tkinter.constants import HORIZONTAL
from tkinter.ttk import Progressbar
from typing import Literal, TypeAlias

StatusBarSide: TypeAlias = Literal["left", "right"]
StatusBarStatus = namedtuple("status", ["timestamp", "message", "side", "style"])


class StatusBar(tkinter.Frame):
    def __init__(self, master, progress_step_size: int = 5):
        super().__init__(master)

        self.master = master
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.grid(sticky="nsew")
        self._start_time: float = float()
        self.progress_step_size: int = progress_step_size

        self.status_log: list = list()

        self.make_widgets()
        # self.update_status("Status Bar Initialized!")

    def make_widgets(self):
        self.left: tkinter.Label = tkinter.Label(self)
        self.right: tkinter.Label = tkinter.Label(self)
        self.progress = Progressbar(self, mode="determinate", length=100, orient=HORIZONTAL)
        self.progress["value"] = 0

        self.regrid()

        self.left.bind("<Double-Button-1>", self.left_double_click)
        self.right.bind("<Double-Button-1>", self.right_double_click)

    def regrid(self):
        self.left.grid(row=0, column=0, sticky="ws")
        self.right.grid(row=0, column=1, sticky="es")

    def update_progress(self, numerator: int, denominator: int, message: str):
        if numerator >= denominator:
            self.clear_progress()

        if denominator <= 0:
            return
        else:
            prog = numerator / denominator * 100

        if prog < self.progress["value"] + self.progress_step_size:
            return

        self.progress.grid(row=0, column=2, sticky="nsew")
        self.columnconfigure(2, weight=1)

        self.progress["value"] = prog
        self.right.config(text=f"{message}, {numerator} / {denominator} ({prog:0.0f}%)")

        self.master.update_idletasks()

    def clear_progress(self):
        self.progress.grid_forget()
        self.progress["value"] = 0
        self.right.grid_forget()
        self.regrid()
        self.columnconfigure(2, weight=0)

    def start_task(self) -> None:
        self._start_time = perf_counter()

    def finish_task(
        self,
        message: str | list,
        style: str = "info.TFrame",
        side: StatusBarSide = "left",
        append_to_log: bool = True,
    ) -> None:
        self._finish_time = perf_counter()

        self.update_status(
            message=f"{message} ({self._finish_time - self._start_time:0.4f} seconds)",
            style=style,
            side=side,
            append_to_log=append_to_log,
        )

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
            self.left.config(text=f"{status.timestamp.strftime('%H:%M:%S')} | {status.message}")
        elif side == "right":
            self.right.config(text=status.message)

    def left_double_click(self, event: tkinter.Event):
        self.master.event_generate("<<StatusBar.DoubleClick.Left>>")

    def right_double_click(self, event: tkinter.Event):
        self.master.event_generate("<<StatusBar.DoubleClick.Right>>")


#
# def log_to_status_bar(path_to_status_bar: list[str]):
#     def inner(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             status_bar.start_task()
#             result = func(*args, **kwargs)
#             status_bar.finish_task(f"{func.__qualname__}")
#             status_bar.update_status(f'')
#             return result
#         return func
#     return inner
