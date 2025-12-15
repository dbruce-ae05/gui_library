import os
import sysconfig
import tomllib
from pathlib import Path

from src.gui_library.library import find

thispath = Path(__file__).parent

PROJECT_ROOT = find("pyproject.toml", return_parent=True, return_path_not_found=thispath)
PROJECT_TOML = find("pyproject.toml", return_parent=False, return_path_not_found=PROJECT_ROOT)
VERSION_PATH = find("__version__.py", return_parent=False, return_path_not_found=PROJECT_ROOT)
CONFIG_PATH = find("settings.toml", return_parent=False, return_path_not_found=PROJECT_ROOT)
APP_NAME_PATH = find("__app_name__.py", return_parent=False, return_path_not_found=PROJECT_ROOT)
LOGGING_CONFIGURATION_PATH = find(
    "logging_configuration.json",
    return_parent=False,
    return_path_not_found=PROJECT_ROOT,
)
LOGS_PATH = find("logs", return_parent=False, return_path_not_found=PROJECT_ROOT)

USER_SCRIPTS_PATH = sysconfig.get_path("scripts", f"{os.name}_user")

if PROJECT_ROOT is None:
    exit

assert PROJECT_TOML

if Path(PROJECT_TOML).exists():
    with PROJECT_TOML.open("rb") as toml_file:
        PYPROJECT = tomllib.load(toml_file)
