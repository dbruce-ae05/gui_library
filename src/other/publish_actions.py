from gui_library.info import APP_NAME_PATH, PYPROJECT, VERSION_PATH


def sync_version():
    version = PYPROJECT["project"]["version"]
    message = f'__version__ = "{version}"'

    assert VERSION_PATH

    with open(VERSION_PATH, "w") as f:
        f.write(message)
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
