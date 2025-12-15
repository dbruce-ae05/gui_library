import json
import os
import platform
from pathlib import Path

from PyInstaller.__main__ import run as pyin_run

from src.gui_library.__app_name__ import APP_NAME
from src.gui_library.__version__ import __version__
from src.gui_library.config import settings_generator
from src.gui_library.info import APP_NAME_PATH, LOGGING_CONFIGURATION_PATH, LOGS_PATH, PYPROJECT, VERSION_PATH

settings = settings_generator()


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


def delete_logs():
    assert LOGS_PATH
    assert LOGS_PATH.exists()

    files = os.listdir(LOGS_PATH)
    for file in files:
        p = Path(LOGS_PATH).joinpath(file)
        p.unlink()

    p = Path(LOGS_PATH).joinpath("log.log")
    with open(p, "a"):
        pass

    return f"Deleted Log Files: {files}"


def cleanup_spec_files():
    files = [Path(file) for file in os.listdir() if ".spec" in file]
    for file in files:
        print(f"INFO: DELETING {file.resolve}")
        os.remove(file)


def build_executable_gui():
    distpath: str = "dist/other"

    if "linux" in platform.system().lower():
        distpath = "dist/linux"

    if "windows" in platform.system().lower():
        distpath = "dist/windows"

    if "darwin" in platform.system().lower():
        distpath = "dist/macos"

    distpath = f"{distpath}{__version__}"

    pyin_run(
        [
            "src/gui_library/load_gui.py",
            "--onedir",
            "--windowed",
            "--add-data=src/gui_library/*:.",
            "--add-data=pyproject.toml:.",
            "--noconfirm",
            f"--name={APP_NAME}",
            f"--distpath={distpath}",
            # f'--hidden-import=',
        ]
    )

    cleanup_spec_files()
