import polars

from src.gui_library.DataFrameChooser import ChooserController


def test_chooser():
    df = polars.DataFrame(
        [
            {"iid": "one", "a": 1, "b": 2},
            {"iid": "two", "a": 3, "b": 4},
            {"iid": "three", "a": 5, "b": 6},
        ]
    )
    chooser = ChooserController(dataframe=df)
    chooser.run()
