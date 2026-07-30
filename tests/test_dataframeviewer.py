#!/usr/bin/env python3
from pathlib import Path

import polars

from gui_library.DataFrameViewer import DataFrameViewerApp

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


# def test_dataframeviewer_large_dataset():
#     # path = (
#     #     Path("~").expanduser().joinpath("Downloads").joinpath("gov_units_2025").joinpath("Govt_Units_2025_Final.xlsx")
#     # )
#     path = Path(__file__).parent.joinpath("test.csv")
#
#     df = polars.read_csv(path)
#
#     show_dataframeviewer(
#         title="Test",
#         df=df,
#         filter="all",
#     )
#


def test_dataframeviewer_nested_dataset():
    path = Path(__file__).parent.joinpath("test_nested.csv")

    df = polars.read_csv(path).fill_null(str())

    # show_dataframeviewer(
    #     title="Test",
    #     df=df,
    #     filter="all",
    # )

    print(df)
    app = DataFrameViewerApp(title="Test By Column", filters="by_column")
    app.dfv.update_data(df)
    # app.dfv.dfv.update_data(df)
    app.mainloop()


def test_dataframeviewer_nested_data_filter_all():
    path = Path(__file__).parent.joinpath("test_nested.csv")

    df = polars.read_csv(path).fill_null(str())

    # show_dataframeviewer(
    #     title="Test",
    #     df=df,
    #     filter="all",
    # )

    print(df)
    app = DataFrameViewerApp(title="Test All", filters="all")
    app.dfv.update_data(df)
    # app.dfv.dfv.update_data(df)
    app.mainloop()
