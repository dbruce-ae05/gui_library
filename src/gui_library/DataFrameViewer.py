import tkinter
from tkinter import font
from tkinter.constants import CENTER, END, E, W
from tkinter.ttk import Frame, Treeview
from typing import Any
from uuid import uuid4

import polars


class DataFrameViewer(Frame):
    def __init__(self, parent, df: polars.DataFrame = polars.DataFrame()):
        super().__init__(parent)

        self.parent = parent
        self.df = df

        self.treeview = Treeview(self)
        self.treeview.grid(sticky="nsew")
        # self.treeview.bind("<<TreeviewSelect>>", self.treeview_select)
        # self.treeview.bind("<Double-Button-1>", self.treeview_doubleclick)
        # self.treeview.bind("<Button-1>", self.treeview_leftclick)
        # self.treeview.bind("<Button-2>", self.treeview_middleclick)
        # self.treeview.bind("<Button-3>", self.treeview_rightclick)
        # self.treeview.bind("<FocusIn>", self.treeview_focus)
        # self.treeview.bind("<Key>", self.treeview_keypress)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.update_data(df)
        self.autoalign_columns()
        self.autofit_columns()

    def clear(self):
        self.treeview.delete(*self.treeview.get_children())

    def update_data(self, df: polars.DataFrame):
        self.clear()

        if df.is_empty():
            return

        self.df = df
        cols = self.df.columns

        cols = [(f"#{i}", col) for i, col in enumerate(cols)]

        if len(cols) > 0:
            self.treeview["columns"] = cols[1:]
        else:
            self.treeview["columns"] = cols

        for name, text in cols:
            self.treeview.column(name, stretch=True)
            self.treeview.heading(name, text=text)

        for row in self.df.iter_rows(named=True):
            iid = str(uuid4())

            values = list(row.values())
            text = values[0]
            if len(values) > 0:
                values = values[1:]

            if not text:
                text = ""

            values = ["" if v is None else v for v in values]

            self.treeview.insert(
                parent="", index=END, text=text, values=values, iid=iid
            )

    def autofit_columns(self):
        f = font.nametofont("TkDefaultFont")
        bf = font.Font(family="Helvetica", size=12, weight="bold")
        col_widths = dict()

        for col in self.df.columns:
            col_widths[col] = int(bf.measure(str(col)) * 1.2)

        for row in self.df.iter_rows(named=True):
            for key, value in row.items():
                if key in self.df.columns:
                    old_width = col_widths[key]
                    new_width = int(f.measure(str(value)) * 1.2)
                    col_widths[key] = max(old_width, new_width)

        for i, width in enumerate(col_widths.values()):
            self.treeview.column(f"#{i}", width=width)

    def autoalign_columns(self):
        for i, dtype in enumerate(self.df.dtypes):
            if "float" in str(dtype).lower() or "int" in str(dtype).lower():
                anchor = E
            elif "bool" in str(dtype).lower():
                anchor = CENTER
            else:
                anchor = W

            self.treeview.column(f"#{i}", anchor=anchor)

    def focus(self) -> Any:
        return self.treeview.focus()

    def selection(self) -> tuple[str, ...]:
        return self.treeview.selection()

    def treeview_select(self, event: tkinter.Event):
        self.parent.treeview_select(event)

    def treeview_doubleclick(self, event: tkinter.Event):
        self.parent.dfv_event_handler(event, double=True)

    def treeview_keypress(self, event: tkinter.Event):
        self.parent.dfv_event_handler(event)

    def treeview_leftclick(self, event: tkinter.Event):
        self.parent.dfv_event_handler(event)

    def treeview_middleclick(self, event: tkinter.Event):
        self.parent.dfv_event_handler(event)

    def treeview_rightclick(self, event: tkinter.Event):
        self.parent.dfv_event_handler(event)

    def treeview_focus(self, event: tkinter.Event):
        self.parent.dfv_event_handler(event)


class DataFrameViewerApp(tkinter.Tk):
    def __init__(self, title: str, df: polars.DataFrame):
        super().__init__()
        self.title(title)
        DataFrameViewer(self, df).grid(sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def dfv_event_handler(self, event: tkinter.Event):
        pass


def show_dataframeviewer(
    title: str = "Polars DataFrame Viewer", df: polars.DataFrame = polars.DataFrame()
):
    app = DataFrameViewerApp(df=df, title=title)
    app.mainloop()
