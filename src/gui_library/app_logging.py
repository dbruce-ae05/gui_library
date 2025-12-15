import atexit
import json
import logging
import logging.config
import logging.handlers
from pathlib import Path

from src.gui_library.__app_name__ import APP_NAME
from src.gui_library.info import LOGGING_CONFIGURATION_PATH, LOGS_PATH

logger = logging.getLogger(APP_NAME)


class DisableLogging:
    def __enter__(self):
        self.original_level = logging.root.manager.disable
        logging.disable(logging.CRITICAL)

    def __exit__(self):
        logging.disable(self.original_level)


def touch(path: Path):
    if isinstance(path, str):
        path = Path(path)

    with open(path, "w"):
        return


def setup_logging():
    with open(LOGGING_CONFIGURATION_PATH) as f_in:
        config = json.load(f_in)

    log_path_jsonl = Path(LOGS_PATH).joinpath("log.jsonl").absolute()
    log_path_debug = Path(LOGS_PATH).joinpath("log.log").absolute()

    if not Path(log_path_jsonl).exists():
        touch(log_path_jsonl)
    if not Path(log_path_debug).exists():
        touch(log_path_debug)

    config["handlers"]["file_debug"]["filename"] = str(Path(LOGS_PATH).joinpath("log.log").absolute())

    logging.config.dictConfig(config)

    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()  # type: ignore
        atexit.register(queue_handler.listener.stop)  # type: ignore


def main():
    setup_logging()
    logging.basicConfig(level="INFO")
    logger.debug("debug message", extra={"x": "hello"})
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("exception message")


if __name__ == "__main__":
    main()
