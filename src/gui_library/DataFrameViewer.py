from tkinter import BooleanVar, Checkbutton, Event, EventType, Tk, font
from tkinter.constants import CENTER, END, E, W
from tkinter.ttk import Entry, Frame, Scrollbar, Treeview
from typing import Any, Callable, Literal, TypeAlias
from uuid import uuid4

import polars
from treelib.node import Node
from treelib.tree import Tree

from gui_library.StatusBar import StatusBar

DataFrameViewerFilterTypes: TypeAlias = Literal["all", "by_column"]


class DataFrameViewer(Frame):
    def __init__(
        self,
        parent,
        df: polars.DataFrame = polars.DataFrame(),
        iids: list | None = None,
        parents: list | None = None,
        callback: Callable[[int, int, str], None] | None = None,
    ):
        super().__init__(parent)

        self.parent = parent
        self.iids = iids
        self.callback = callback
        self.df = df
        self.columns_to_drop = {"iid", "parent", "tag"}
        self.drop_columns = self.columns_to_drop.intersection(set(self.df.columns))
        self.df_dropped_columns = self.df.drop(self.drop_columns)
        self.sort: dict[str, bool] = {column: False for column in self.df.columns}

        self.make_widgets()
        self.make_bindings()

        self.update_data(df=df)
        self.autoalign_columns()
        self.autofit_columns()

    def make_widgets(self):
        self.scrollbar = Scrollbar(self, orient="vertical")

        self.treeview = Treeview(self, yscrollcommand=self.scrollbar.set)
        self.treeview.grid(row=0, column=0, rowspan=1, columnspan=1, padx=0, pady=0, sticky="nsew")

        self.scrollbar.configure(command=self.treeview.yview)
        self.scrollbar.grid(row=0, column=1, rowspan=2, columnspan=1, padx=0, pady=0, sticky="nsew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def make_bindings(self):
        self.treeview.bind("<Shift-Down>", self.treeview_shift_down)
        self.treeview.bind("<Shift-Up>", self.treeview_shift_up)

    def clear(self):
        self.treeview.delete(*self.treeview.get_children())

    def get_dataframe_copy(self):
        return self.df.clone()

    def update_data(self, df: polars.DataFrame):
        self.clear()

        if df.is_empty():
            return

        self.df = df
        self.drop_columns = self.columns_to_drop.intersection(set(self.df.columns))
        self.df_dropped_columns = self.df.drop(self.drop_columns)

        if set(self.sort.keys()) != {column for column in self.df_dropped_columns.columns}:
            self.sort: dict[str, bool] = {column: False for column in self.df_dropped_columns.columns}

        cols = [col for col in self.df_dropped_columns.columns]
        cols = [(f"#{i}", col) for i, col in enumerate(cols)]

        if len(cols) > 0:
            self.treeview["columns"] = cols[1:]
        else:
            self.treeview["columns"] = cols

        for name, text in cols:
            self.treeview.column(name, stretch=True)
            self.treeview.heading(name, text=text, command=lambda col=text: self.sort_df(col))

        denominator = self.df.shape[0]
        for numerator, row in enumerate(self.df.iter_rows(named=True)):
            iid = uuid4().hex
            parent = ""
            tag = ""
            if "iid" in row.keys():
                iid = row.pop("iid")
            if "parent" in row.keys():
                parent = row.pop("parent")
            if "tag" in row.keys():
                tag = row.pop("tag")

            values = list(row.values())
            text = values[0]
            if len(values) > 0:
                values = values[1:]

            if not text:
                text = ""

            values = ["" if v is None else v for v in values]

            self.treeview.insert(parent=parent, index=END, text=text, values=values, iid=iid, tags=tag)

            if self.callback:
                self.callback(numerator, denominator, "Updating Treeview")

        if self.callback:
            self.callback(denominator, denominator, "Finished Updating Treeview")

        self.autofit_columns()
        self.autoalign_columns()

    def sort_df(self, column: str):
        self.sort[column] = not self.sort[column]
        self.df = self.df.sort(column, descending=self.sort[column])
        self.update_data(df=self.df)

    def autofit_columns(self):
        df = self.df_dropped_columns
        f = font.nametofont("TkDefaultFont")
        bf = font.Font(family="Helvetica", size=12, weight="bold")
        self.col_widths = dict()

        for col in df.columns:
            self.col_widths[col] = int(bf.measure(str(col)) * 1.2)

        for row in df.iter_rows(named=True):
            for key, value in row.items():
                if key in df.columns:
                    old_width = self.col_widths[key]
                    new_width = int(f.measure(str(value)) * 1.2)
                    self.col_widths[key] = max(old_width, new_width)

        for i, width in enumerate(self.col_widths.values()):
            self.treeview.column(f"#{i}", width=width)

    def autoalign_columns(self):
        df = self.df_dropped_columns
        for i, dtype in enumerate(df.dtypes):
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

    def treeview_shift_down(self, event: Event):
        tree: Treeview = event.widget  # type: ignore
        cur_item = tree.focus()

        next_item = tree.next(cur_item)

        tree.focus(next_item)

        tree.selection_add([cur_item, next_item])

        # Stop propagating this event to other handlers!
        return "break"

    def treeview_shift_up(self, event: Event):
        tree: Treeview = event.widget  # type: ignore
        cur_item = tree.focus()

        prev_item = tree.prev(cur_item)

        tree.focus(prev_item)

        tree.selection_add([prev_item, cur_item])

        # Stop propagating this event to other handlers!
        return "break"

    def treeview_event_handler(self, treeview: Treeview, event: Event, double: bool = False):
        if event.type == EventType.ButtonPress and event.num == 1 and double:
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

    def on_return(self, event: Event):
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


class DataFrameViewerApp(Tk):
    def __init__(
        self,
        title: str,
        df: polars.DataFrame,
        iids: list | None = None,
        parents: list | None = None,
        filters: DataFrameViewerFilterTypes = "all",
    ):
        super().__init__()
        self.title(title)
        self.df = df
        self.iids = iids
        self.parents = parents
        self.filters = filters

        if self.iids is None:
            self.iids = [str(uuid4()) for _ in range(self.df.shape[0])]

        if self.parents is None:
            self.parents = ["" for _ in range(self.df.shape[0])]

        if len(self.iids) != self.df.shape[0]:
            raise ValueError(f"length of iids: {len(self.iids)}, expected: {self.df.shape[0]}")

        if len(self.parents) != self.df.shape[0]:
            raise ValueError(f"length of parents: {len(self.parents)}, expected: {self.df.shape[0]}")

        if "iid" not in self.df.columns:
            self.df = self.df.insert_column(index=0, column=polars.Series(name="iid", values=self.iids))

        if "parents" not in self.df.columns:
            self.df = self.df.insert_column(index=1, column=polars.Series(name="parent", values=self.parents))

        self.update_family_tree()

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

        self.dfv = DataFrameViewer(self, df=self.df)
        self.dfv.grid(row=1, column=0, rowspan=1, columnspan=len(self.df.columns), sticky="nsew", padx=5, pady=2)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.columnconfigure(0, weight=1)

        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, rowspan=1, columnspan=len(self.df.columns) + 1, sticky="nsew")
        self.status_bar.update_status("Initialized Status Bar")

        self.bind("<<StatusBar.DoubleClick.Left>>", self.show_status_log)
        self.bind("<<StatusBar.DoubleClick.Right>>", self.show_status_log)

    def show_status_log(self, event: Event):
        df = polars.DataFrame(self.status_bar.status_log)
        show_dataframeviewer(title="Status Log", df=df)

    def make_all_filters(self):
        self.checkmarks: dict[str, Checkbutton] = dict()
        self.checkmarkvalues: dict[str, BooleanVar] = dict()

        self.entry: Entry = Entry(master=self)
        self.entry.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="nsew", padx=5, pady=2)

        df = self.df.drop(["iid", "parent", "treepath"])
        for i, col in enumerate(df.columns):
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

        df = self.df.drop(["iid", "parent", "treepath"])
        for i, col in enumerate(df.columns):
            self.column_entries[col] = Entry(master=self)  # , width=self.dfv.col_widths[col])
            self.column_entries[col].grid(row=0, column=i, rowspan=1, columnspan=1, padx=0, pady=2, sticky="nsew")
            self.columnconfigure(i, weight=1)
            self.column_entries[col].bind("<KeyRelease>", self.update_filter)

    def make_bindings(self):
        pass

    def update_filter(self, event: Event | None = None):
        filter_dict: dict = {
            "all": self.update_all_filter,
            "by_column": self.update_by_column_filter,
        }
        results = filter_dict[self.filters]()

        treepaths = set(results["treepath"].to_list())
        keys: list[str] = list()
        treepath: str
        for treepath in treepaths:
            keys.extend(treepath.split("|"))

        df_keys: polars.DataFrame = polars.DataFrame({"iid": keys})

        keys = list(set(keys))
        # results = self.df.filter(polars.col("iid").str.contains_any(keys))
        # results = self.df.filter(polars.col("iid").is_in(keys))

        if results.shape[0]:
            results = self.df.join(df_keys, on="iid", how="inner")
            results = results.drop(["treepath"])
        else:
            results = polars.DataFrame()

        self.status_bar.update_status(f"{results.shape[0]} matches out of {self.df.shape[0]} lines")
        self.dfv.update_data(df=results)

    def update_all_filter(self) -> polars.DataFrame:
        pattern = self.entry.get()

        if not pattern:
            return self.df

        filter_columns = [key for key, value in self.checkmarkvalues.items() if value.get()]

        results = self.df
        if pattern:
            results = self.df.filter(
                polars.any_horizontal(polars.col(filter_columns).cast(polars.String).str.contains(f"(?i){pattern}"))
            )

        return results

    def update_by_column_filter(self) -> polars.DataFrame:
        patterns = {key: value.get() for key, value in self.column_entries.items() if value.get()}

        results = self.df

        if not any(patterns.values()):
            return results

        filters: list = list()
        for col, pattern in patterns.items():
            filters.append(polars.col(col).cast(polars.String).str.contains(f"(?i){pattern}"))

        if filters:
            results = self.df.filter(filters)

        return results

    def update_family_tree(self):
        if "treepath" in self.df.columns:
            self.df = self.df.drop(["treepath"])

        tree = Tree()
        root = Node(identifier="")
        tree.add_node(root)

        for row in self.df.iter_rows(named=True):
            node = Node(identifier=row["iid"])
            parent = row["parent"]
            tree.add_node(node, parent=parent)

        path_to_leaves = {leafpath[-1]: "|".join(leafpath[1:]) for leafpath in tree.paths_to_leaves()}
        paths: dict[str, str] = dict()
        for row in self.df.iter_rows(named=True):
            paths[row["iid"]] = path_to_leaves.get(row["iid"], row["iid"])

        self.df = self.df.insert_column(index=0, column=polars.Series(name="treepath", values=paths.values()))

    def dfv_event_handler(self, event: Event):
        pass


def show_dataframeviewer(
    title: str = "Polars DataFrame Viewer",
    df: polars.DataFrame = polars.DataFrame(),
    filter: DataFrameViewerFilterTypes = "all",
    iids: list | None = None,
    parents: list | None = None,
):
    app = DataFrameViewerApp(df=df, title=title, filters=filter, parents=parents, iids=iids)
    app.mainloop()
