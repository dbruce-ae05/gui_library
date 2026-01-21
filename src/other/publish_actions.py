import json

from gui_library.info import APP_NAME_PATH, LOGGING_CONFIGURATION_PATH, PYPROJECT, VERSION_PATH


def sync_version():
    version = PYPROJECT["project"]["version"]
    message = f'__version__ = "{version}"'

    assert VERSION_PATH

    with open(VERSION_PATH, "w") as f:
        f.write(message)
    return message


def sync_logging_level() -> str:
    log_level = PYPROJECT["project"]["logging_level"]
    message = f"LOGGING_LEVEL = {log_level}"

    assert LOGGING_CONFIGURATION_PATH

    with open(LOGGING_CONFIGURATION_PATH, "r") as f:
        config = json.load(f)

    config["loggers"]["root"]["level"] = f"{log_level}"

    with open(LOGGING_CONFIGURATION_PATH, "w") as f:
        json.dump(config, f, indent=4)

    return message


def sync_application_name() -> str:
    app_name = PYPROJECT["project"]["name"]
    message = f'APP_NAME = "{app_name}"'

    assert APP_NAME_PATH

    with open(APP_NAME_PATH, "w") as f:
        f.write(message)
    return message


def sync_with_pyproject() -> list:
    results = list()
    results.append(sync_version())
    # results.append(sync_logging_level())
    results.append(sync_application_name())
    return results
