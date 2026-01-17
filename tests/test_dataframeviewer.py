#!/usr/bin/env python3

from pathlib import Path

import polars

from gui_library.app_logging import setup_logging
from gui_library.DataFrameViewer import show_dataframeviewer

setup_logging()

# def test_dataframeviewer_filter(test_dataframe, test_dataframe_iids, test_dataframe_parents):
#     print(test_dataframe)
#     print(test_dataframe_iids, test_dataframe_parents)
#     show_dataframeviewer(
#         title="Test",
#         df=test_dataframe,
#         filter="by_column",
#         iids=test_dataframe_iids,
#         parents=test_dataframe_parents,
#     )
#


def test_dataframeviewer_large_dataset():
    # path = (
    #     Path("~").expanduser().joinpath("Downloads").joinpath("gov_units_2025").joinpath("Govt_Units_2025_Final.xlsx")
    # )
    path = Path("~").expanduser().joinpath("Downloads").joinpath("gov_units_2025").joinpath("test.csv")

    # df = polars.read_excel(path, sheet_name="General Purpose")
    df = polars.read_csv(path)

    show_dataframeviewer(
        title="Test",
        df=df,
        filter="all",
    )
