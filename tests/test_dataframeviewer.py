from gui_library.DataFrameViewer import show_dataframeviewer


def test_dataframeviewer_filter(test_dataframe):
    show_dataframeviewer(title="Test", df=test_dataframe, filter="by_column")
