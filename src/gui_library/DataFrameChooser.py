import tkinter
from dataclasses import dataclass, field

import polars

from gui_library.DataFrameViewer import DataFrameViewerApp


@dataclass
class ChooserModel:
    df: polars.DataFrame = field(init=True, default_factory=polars.DataFrame)

    def __post_init__(self):
        if "selected" not in self.df.columns:
            self.df = self.df.with_columns(polars.lit(False).alias("selected"))

    def select(self, iids: tuple[str, ...]):
        data: list = list()
        for row in self.df.iter_rows(named=True):
            if row["iid"] in iids:
                row["selected"] = not row["selected"]
            data.append(row)

        self.df = polars.DataFrame(data)

    def get_values(self, iid: str) -> tuple:
        return self.df.filter(polars.col("iid") == iid).drop(["iid", "treepath", "parent"])[0].row()[1:]


@dataclass
class ChooserController:
    model: ChooserModel = field(init=False)
    viewer: DataFrameViewerApp = field(init=False)
    dataframe: polars.DataFrame = field(init=True, default_factory=polars.DataFrame)

    def __post_init__(self):
        self.model = ChooserModel(df=self.dataframe)
        self.viewer = DataFrameViewerApp(
            title="DataFrame Chooser",
            df=self.model.df,
        )
        self.make_bindings()

    def run(self):
        self.viewer.mainloop()

    def make_bindings(self):
        self.viewer.dfv.treeview.bind("<KeyRelease-space>", self.select)
        self.viewer.dfv.treeview.bind("<Double-Button-1>", self.select)

    def select(self, event: tkinter.Event):
        selections: tuple = self.viewer.dfv.treeview.selection()
        self.model.select(selections)

        for selection in selections:
            print(selection)
            print(self.model.get_values(selection))
            self.viewer.dfv.treeview.item(selection, values=self.model.get_values(selection))

    def report(self):
        return list(self.model.df.filter(polars.col("selected")).get_column("iid"))
