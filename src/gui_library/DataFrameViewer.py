import tkinter
from tkinter import BooleanVar, Checkbutton, font
from tkinter.constants import CENTER, END, E, W
from tkinter.ttk import Entry, Frame, Treeview
from typing import Any, Literal, TypeAlias
from uuid import uuid4

import polars

from gui_library.StatusBar import StatusBar

DataFrameViewerFilterTypes: TypeAlias = Literal["all", "by_column"]


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

            self.treeview.insert(parent="", index=END, text=text, values=values, iid=iid)

    def autofit_columns(self):
        f = font.nametofont("TkDefaultFont")
        bf = font.Font(family="Helvetica", size=12, weight="bold")
        self.col_widths = dict()

        for col in self.df.columns:
            self.col_widths[col] = int(bf.measure(str(col)) * 1.2)

        for row in self.df.iter_rows(named=True):
            for key, value in row.items():
                if key in self.df.columns:
                    old_width = self.col_widths[key]
                    new_width = int(f.measure(str(value)) * 1.2)
                    self.col_widths[key] = max(old_width, new_width)

        for i, width in enumerate(self.col_widths.values()):
            self.treeview.column(f"#{i}", width=width)

    def autoalign_columns(self):
        for i, dtype in enumerate(self.df.dtypes):
            if "float" in str(dtype).lower() or "int" in str(dtype).lower():
                anchor = E
            elif "bool" in str(dtype).lower():
                anchor = CENTER
            else:
                anchor = W

            print(f"{i}, anchor={anchor}")
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

    def treeview_event_handler(self, treeview: Treeview, event: tkinter.Event, double: bool = False):
        if event.type == tkinter.EventType.ButtonPress and event.num == 1 and double:
            try:
                self.entrypopup.destroy()
            except AttributeError:
                pass

            rowid = treeview.identify_row(event.y)
            column = treeview.identify_column(event.x)

            if not rowid:
                return

            x, y, width, height = treeview.bbox(item=rowid, column=column)
            x += treeview.winfo_x()  # type: ignore
            pady = height // 2  # type:ignore

            row = treeview.item(rowid)
            column = int(column.replace("#", ""))
            if column == 0:
                text = row["text"]
            else:
                text = row["values"][column - 1]

            self.entrypopup = TableEntryPopup(
                parent=self,
                treeview=treeview,
                iid=rowid,
                column=column,
                text=text,
            )

            self.entrypopup.place(
                x=x,
                y=y + pady,  # type: ignore
                width=width,
                height=height,
                anchor="w",
            )


class TableEntryPopup(Entry):
    def __init__(self, parent, treeview, iid, column, text, **kw):
        super().__init__(treeview, **kw)
        self.parent = parent
        self.tv = treeview
        self.iid = iid
        self.column = column
        self.text = text

        self.insert(0, text)
        self["exportselection"] = False

        self.focus_force()
        self.select_all()
        self.bind("<Return>", self.on_return)
        self.bind("<Tab>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", lambda *ignore: self.destroy())

    def on_return(self, event: tkinter.Event):
        rowid = self.tv.focus()
        new_val = self.get()

        if self.column == 0:
            self.tv.item(rowid, text=new_val)
        else:
            vals = self.tv.item(rowid, "values")
            vals = list(vals)
            vals[self.column - 1] = new_val
            self.tv.item(rowid, values=vals)

        self.parent.entrypopup_write(rowid, self.tv.item(rowid))
        self.destroy()

    def select_all(self, *ignore):
        self.selection_range(0, "end")
        return "break"
        # self.tree.bind("<Key>", self.keypress_event_handler)


class DataFrameViewerApp(tkinter.Tk):
    def __init__(self, title: str, df: polars.DataFrame, filters: DataFrameViewerFilterTypes = "all"):
        super().__init__()
        self.title(title)
        self.df = df
        self.filters = filters
        self.dfv = DataFrameViewer(self, self.df)

        self.make_widgets()
        self.make_bindings()
        self.update_filter()

    # TODO: add feature for returning the selected rows in the viewer - also add some indicator for what rows are selected

    def make_widgets(self):
        filter_dict: dict = {
            "all": self.make_all_filters,
            "by_column": self.make_by_column_filters,
        }
        filter_dict[self.filters]()

        self.dfv.grid(row=1, column=0, rowspan=1, columnspan=len(self.df.columns) + 1, sticky="nsew", padx=5, pady=2)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)

        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, rowspan=1, columnspan=len(self.df.columns) + 1, sticky="nsew")
        self.status_bar.update_status("Initialized Status Bar")

    def make_all_filters(self):
        self.checkmarks: dict[str, Checkbutton] = dict()
        self.checkmarkvalues: dict[str, BooleanVar] = dict()

        self.entry: Entry = Entry(master=self)
        self.entry.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="nsew", padx=5, pady=2)

        for i, col in enumerate(self.df.columns):
            self.checkmarkvalues[col] = BooleanVar(self)
            self.checkmarks[col] = Checkbutton(
                self,
                text=col,
                variable=self.checkmarkvalues[col],
                command=self.update_filter,
            )
            self.checkmarks[col].select()
            self.checkmarks[col].grid(row=0, column=i + 1, rowspan=1, columnspan=1, padx=5, pady=2, sticky="nsew")
            self.columnconfigure(i + 1, weight=0)

        self.entry.bind("<KeyRelease>", self.update_filter)

    def make_by_column_filters(self):
        self.column_entries: dict[str, Entry] = dict()

        for i, col in enumerate(self.df.columns):
            self.column_entries[col] = Entry(master=self)  # , width=self.dfv.col_widths[col])
            self.column_entries[col].grid(
                row=0, column=i, rowspan=1, columnspan=1, padx=0, pady=2, sticky="nsew", ipadx=self.dfv.col_widths[col]
            )
            self.columnconfigure(i, weight=1)
            self.column_entries[col].bind("<KeyRelease>", self.update_filter)

    def make_bindings(self):
        pass

    def update_filter(self, event: tkinter.Event | None = None):
        filter_dict: dict = {
            "all": self.update_all_filter,
            "by_column": self.update_by_column_filter,
        }
        results = filter_dict[self.filters]()

        self.status_bar.update_status(f"{results.shape[0]} results")
        self.dfv.update_data(df=results)

    def update_all_filter(self) -> polars.DataFrame:
        filter_columns = [key for key, value in self.checkmarkvalues.items() if value.get()]
        pattern = self.entry.get()

        results = self.df
        if pattern:
            results = self.df.filter(
                polars.any_horizontal(polars.col(filter_columns).cast(polars.String).str.contains(f"(?i){pattern}"))
            )

        return results

    def update_by_column_filter(self):
        patterns = {key: value.get() for key, value in self.column_entries.items() if value.get()}

        results = self.df
        filters: list = list()
        for col, pattern in patterns.items():
            filters.append(polars.col(col).cast(polars.String).str.contains(f"(?i){pattern}"))

        if filters:
            results = self.df.filter(filters)

        return results

    def dfv_event_handler(self, event: tkinter.Event):
        pass


def show_dataframeviewer(
    title: str = "Polars DataFrame Viewer",
    df: polars.DataFrame = polars.DataFrame(),
    filter: DataFrameViewerFilterTypes = "all",
):
    app = DataFrameViewerApp(df=df, title=title, filters=filter)
    app.mainloop()
