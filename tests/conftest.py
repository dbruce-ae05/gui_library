import polars
import pytest
from pytest import Config, Item, Parser

from src.gui_library.config import settings_generator


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
def settings():
    return settings_generator()


@pytest.fixture
def test_dataframe():
    data = {
        "column_1": [1, 2, 3, 4, 5],
        "column_2": [1, 3, 5, 7, 9],
        "column_3": [2, 4, 6, 8, 10],
        "column_4": [11, 12, 13, 14, 15],
    }

    return polars.DataFrame(data)
