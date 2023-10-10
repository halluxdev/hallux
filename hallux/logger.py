import logging
import os

import colorlog

logger = logging.getLogger("hallux_logger")

log_level = os.environ.get("LOG_LEVEL", logging.WARNING)

logger.setLevel(log_level)

# Create a console handler
handler = logging.StreamHandler()
handler.setLevel(log_level)

stupid_var = "unused"

# Create a formatter
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "MESSAGE": "black",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={},
    style="%",
)

# Add the formatter to the handler
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


def message(msg: str, *args, **kwargs):
    print(msg, *args, **kwargs)


logger.message = message

# Now you can log messages with various severity levels like this:
# logger.debug("debug message")
# logger.info("info message")
# logger.warning("warning message")
# logger.error("error message")
# logger.critical("critical message")
