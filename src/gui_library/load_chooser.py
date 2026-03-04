from functools import partial

import polars

from gui_library.DataFrameChooser import ChooserController


def main():
    df = polars.DataFrame(
        [
            {"iid": "one", "a": 1, "b": 2},
            {"iid": "two", "a": 3, "b": 4},
            {"iid": "three", "a": 5, "b": 6},
        ]
    )
    chooser = ChooserController(dataframe=df)
    chooser.viewer.protocol("WM_DELETE_WINDOW", partial(report, chooser))
    chooser.run()


def report(chooser: ChooserController):
    print("window closed")
    print(chooser.report())
    chooser.viewer.destroy()


if __name__ == "__main__":
    main()
