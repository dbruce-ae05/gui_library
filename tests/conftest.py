import polars
import pytest
from pytest import Config, Item, Parser


def pytest_addoption(parser: Parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_configure(config: Config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config: Config, items: list[Item]):
    if config.getoption("--runslow"):
        # -- runslow given in cli, do not skip slow tests
        return

    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture
def test_dataframe() -> polars.DataFrame:
    data = {
        "column_0": ["line 1", "line 2", "line 3", "line 4", "line 5"],
        "column_1": [1, 2, 3, 4, 5],
        "column_2": [1, 3, 5, 7, 9],
        "column_3": [2, 4, 6, 8, 10],
        "column_4": [11, 12, 13, 14, 15],
        "column_5": ["one", "two", "three", "four", "five"],
        "column_6": ["six", "seven", "eight", "nine", "ten"],
    }

    return polars.DataFrame(data)


@pytest.fixture
def test_dataframe_iids(test_dataframe: polars.DataFrame) -> list:
    # return [str(uuid.uuid4()) for _ in range(test_dataframe.shape[0])]
    return ["a", "b", "c", "d", "e"]


@pytest.fixture
def test_dataframe_parents(test_dataframe_iids: list) -> list:
    # return [random.choice(test_dataframe_iids) for _ in range(len(test_dataframe_iids))]
    # return ["", "", "", "", ""]
    return ["", "a", "", "b", "b"]
